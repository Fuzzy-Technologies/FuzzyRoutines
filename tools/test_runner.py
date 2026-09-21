# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Run the complete pytest suite with deterministic process isolation.

The runner keeps pytest execution in the active Python SDK, distributes
parallel-safe tests with pytest-xdist, executes shared-resource tests in a
separate serial phase, and aggregates both phases from JUnit XML evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

DEFAULTMAXWORKERS = 12
DEFAULTTIMEOUT = 60.0
SUCCESSCODES = frozenset((0, 5))
TIMEOUTTOKENS = ("timed out", "pytest-timeout")
SERIALMARKER = "serial: requires an exclusive shared resource and runs outside the parallel phase"


@dataclass(frozen=True)
class RunnerConfiguration:
    """Store the repository-owned limits used by the test runner."""

    maxWorkers: int = DEFAULTMAXWORKERS
    timeout: float = DEFAULTTIMEOUT


@dataclass(frozen=True)
class ExecutionPhase:
    """Describe one isolated pytest subprocess invocation."""

    name: str
    markerExpression: str | None
    workers: int


@dataclass(frozen=True)
class PhaseResult:
    """Store the deterministic evidence extracted from one pytest phase."""

    name: str
    returnCode: int
    total: int
    passed: int
    failed: int
    skipped: int
    timeout: int
    duration: float
    processErrors: int


def LoadProjectConfiguration(projectRoot: Path) -> RunnerConfiguration:
    """Load the test-runner limits from ``pyproject.toml`` when present."""

    configurationPath = projectRoot / "pyproject.toml"

    if not configurationPath.exists():
        return RunnerConfiguration()

    with configurationPath.open("rb") as configurationFile:
        projectConfiguration = tomllib.load(configurationFile)

    runnerConfiguration = (
        projectConfiguration.get("tool", {})
        .get("fuzzyroutines", {})
        .get("test-runner", {})
    )
    maxWorkers = runnerConfiguration.get("max-workers", DEFAULTMAXWORKERS)
    timeout = runnerConfiguration.get("timeout", DEFAULTTIMEOUT)

    if not isinstance(maxWorkers, int) or isinstance(maxWorkers, bool) or maxWorkers < 1:
        raise ValueError("test-runner max-workers must be a positive integer")

    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("test-runner timeout must be a positive number")

    return RunnerConfiguration(maxWorkers=maxWorkers, timeout=float(timeout))


def ResolveJobs(requestedJobs: str, maxWorkers: int, cpuCount: int | None = None) -> int:
    """Resolve ``auto`` or an explicit worker count against the project cap."""

    availableCpus = os.cpu_count() if cpuCount is None else cpuCount
    availableCpus = max(1, availableCpus or 1)

    if requestedJobs == "auto":
        return min(availableCpus, maxWorkers)

    try:
        requestedWorkers = int(requestedJobs)

    except ValueError as exception:
        raise ValueError("--jobs must be 'auto' or a positive integer") from exception

    if requestedWorkers < 1:
        raise ValueError("--jobs must be 'auto' or a positive integer")

    if requestedWorkers > maxWorkers:
        raise ValueError(f"--jobs cannot exceed the configured maximum of {maxWorkers}")

    return requestedWorkers


def BuildPhases(serialOnly: bool, workers: int) -> tuple[ExecutionPhase, ...]:
    """Build the parallel-safe and shared-resource execution phases."""

    if serialOnly:
        return (ExecutionPhase(name="serial-all", markerExpression=None, workers=0),)

    return (
        ExecutionPhase(name="parallel", markerExpression="not serial", workers=workers),
        ExecutionPhase(name="serial", markerExpression="serial", workers=0),
    )


def BuildPytestCommand(
    phase: ExecutionPhase,
    reportPath: Path,
    phaseTempRoot: Path,
    timeout: float,
    failFast: bool,
    testTargets: tuple[str, ...],
) -> list[str]:
    """Build one explicit pytest command using the active interpreter."""

    timeoutMethod = "signal" if os.name == "posix" else "thread"
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "xdist.plugin",
        "-p",
        "pytest_timeout",
        "-p",
        "no:cacheprovider",
        "--strict-markers",
        "-o",
        f"markers={SERIALMARKER}",
        "--junitxml",
        str(reportPath),
        "--basetemp",
        str(phaseTempRoot),
        "--timeout",
        str(timeout),
        "--timeout-method",
        timeoutMethod,
        "-n",
        str(phase.workers),
    ]

    if phase.workers:
        command.extend(("--dist", "loadscope", "--max-worker-restart", "0"))

    if phase.markerExpression is not None:
        command.extend(("-m", phase.markerExpression))

    if failFast:
        command.append("-x")

    command.extend(testTargets)
    return command


def ParseJunitReport(reportPath: Path) -> dict[str, int]:
    """Classify JUnit test cases without depending on completion order."""

    counters = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "timeout": 0,
        "process_errors": 0,
    }

    if not reportPath.exists():
        return counters

    reportRoot = ElementTree.parse(reportPath).getroot()

    for testCase in reportRoot.iter("testcase"):
        counters["total"] += 1
        skipped = testCase.find("skipped")
        failure = testCase.find("failure")
        error = testCase.find("error")

        if skipped is not None:
            counters["skipped"] += 1

        elif failure is not None or error is not None:
            failureElement = failure if failure is not None else error
            failureText = " ".join(
                (
                    failureElement.get("message", ""),
                    failureElement.text or "",
                    failureElement.get("type", ""),
                )
            ).lower()

            if any(token in failureText for token in TIMEOUTTOKENS):
                counters["timeout"] += 1

            elif error is not None:
                counters["process_errors"] += 1

            else:
                counters["failed"] += 1

        else:
            counters["passed"] += 1

    return counters


def RunPhase(
    phase: ExecutionPhase,
    sessionRoot: Path,
    timeout: float,
    failFast: bool,
    testTargets: tuple[str, ...],
    projectRoot: Path,
) -> PhaseResult:
    """Execute one pytest phase and return structured result evidence."""

    phaseRoot = sessionRoot / phase.name
    phaseRoot.mkdir(parents=True, exist_ok=True)
    reportPath = phaseRoot / "junit.xml"
    phaseTempRoot = phaseRoot / "temp"
    command = BuildPytestCommand(
        phase=phase,
        reportPath=reportPath,
        phaseTempRoot=phaseTempRoot,
        timeout=timeout,
        failFast=failFast,
        testTargets=testTargets,
    )
    environment = os.environ.copy()
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["FUZZYROUTINES_TEST_SESSION_ROOT"] = str(sessionRoot)
    environment["FUZZYROUTINES_TEST_PHASE"] = phase.name
    environment["TMPDIR"] = str(phaseRoot)
    environment["TEMP"] = str(phaseRoot)
    environment["TMP"] = str(phaseRoot)
    environment.pop("PYTEST_ADDOPTS", None)

    print(f"TEST_PHASE name={phase.name} workers={phase.workers} timeout={timeout:g}", flush=True)
    startedAt = time.monotonic()
    completedProcess = subprocess.run(command, cwd=projectRoot, env=environment, check=False)
    duration = time.monotonic() - startedAt
    counters = ParseJunitReport(reportPath)
    processErrors = counters.pop("process_errors")

    if (
        completedProcess.returncode not in SUCCESSCODES
        and counters["failed"] == 0
        and counters["timeout"] == 0
        and processErrors == 0
    ):
        processErrors = 1

    return PhaseResult(
        name=phase.name,
        returnCode=completedProcess.returncode,
        duration=duration,
        processErrors=processErrors,
        **counters,
    )


def AggregateResults(results: tuple[PhaseResult, ...], duration: float) -> dict[str, int | float]:
    """Aggregate phase evidence into a stable machine-readable schema."""

    return {
        "duration": round(duration, 3),
        "failed": sum(result.failed for result in results),
        "passed": sum(result.passed for result in results),
        "process_errors": sum(result.processErrors for result in results),
        "skipped": sum(result.skipped for result in results),
        "timeout": sum(result.timeout for result in results),
        "total": sum(result.total for result in results),
    }


def ParseArguments(arguments: list[str] | None, configuration: RunnerConfiguration) -> argparse.Namespace:
    """Parse the public test-runner command-line contract."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", default="auto", help="worker count: auto or a positive integer")
    parser.add_argument(
        "--timeout",
        type=float,
        default=configuration.timeout,
        help="per-test timeout in seconds",
    )
    parser.add_argument("--serial", action="store_true", dest="serialOnly", help="run the entire suite serially")
    parser.add_argument("--fail-fast", action="store_true", dest="failFast", help="stop after the first failure")
    parser.add_argument("testTargets", nargs="*", help="optional pytest paths or node identifiers")
    parsedArguments = parser.parse_args(arguments)

    try:
        parsedArguments.resolvedJobs = ResolveJobs(
            requestedJobs=parsedArguments.jobs,
            maxWorkers=configuration.maxWorkers,
        )

    except ValueError as exception:
        parser.error(str(exception))

    if parsedArguments.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    return parsedArguments


def Main(arguments: list[str] | None = None) -> int:
    """Run all selected tests and return the deterministic aggregate exit code."""

    projectRoot = Path(__file__).resolve().parents[1]

    try:
        configuration = LoadProjectConfiguration(projectRoot)

    except ValueError as exception:
        print(f"test runner configuration error: {exception}", file=sys.stderr)
        return 2

    parsedArguments = ParseArguments(arguments, configuration)
    phases = BuildPhases(parsedArguments.serialOnly, parsedArguments.resolvedJobs)
    results: list[PhaseResult] = []
    startedAt = time.monotonic()

    with tempfile.TemporaryDirectory(prefix="fuzzyroutines-tests-") as sessionDirectory:
        sessionRoot = Path(sessionDirectory)

        for phase in phases:
            result = RunPhase(
                phase=phase,
                sessionRoot=sessionRoot,
                timeout=parsedArguments.timeout,
                failFast=parsedArguments.failFast,
                testTargets=tuple(parsedArguments.testTargets),
                projectRoot=projectRoot,
            )
            results.append(result)

            if parsedArguments.failFast and result.returnCode not in SUCCESSCODES:
                break

    summary = AggregateResults(tuple(results), time.monotonic() - startedAt)
    print("TEST_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)

    return int(any(result.returnCode not in SUCCESSCODES for result in results))


if __name__ == "__main__":
    raise SystemExit(Main())
