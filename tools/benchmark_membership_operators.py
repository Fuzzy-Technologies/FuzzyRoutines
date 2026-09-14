"""Benchmark legacy membership functions and fuzzy operators reproducibly.

The tool is deliberately dependency-free and records raw per-operation samples,
environment metadata, and independent numerical-parity checks. It reports
observations only; a performance claim requires comparison with a named
baseline in the same environment under the benchmark protocol.
"""

import argparse
import importlib.metadata
import json
import math
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

from fuzzyroutines.FuzzyRoutines import MFunction, SCoNorm, TNorm


DEFAULTITERATIONS = 10000
DEFAULTREPEATS = 7
DEFAULTWARMUPS = 1
PARITYTOLERANCE = 1e-12
REPOSITORYROOT = Path(__file__).resolve().parents[1]


def BuildBenchmarkReport(iterations=DEFAULTITERATIONS, repeats=DEFAULTREPEATS, warmups=DEFAULTWARMUPS):
    """Return reproducible scalar timing observations and parity results."""
    ValidateConfiguration(iterations, repeats, warmups)
    workloads = BuildWorkloads()
    results = {}

    for workload in workloads:
        results[workload["name"]] = Measure(
            operation=workload["operation"],
            parityCheck=workload["parity_check"],
            iterations=iterations,
            repeats=repeats,
            warmups=warmups,
        )

    return {
        "benchmark": "fuzzyroutines-membership-and-operator-scalar",
        "environment": GetEnvironment(),
        "configuration": {
            "iterations_per_repeat": iterations,
            "repeats": repeats,
            "warmups": warmups,
            "timer": "time.perf_counter_ns",
            "parity_tolerance": PARITYTOLERANCE,
        },
        "results": results,
    }


def ValidateConfiguration(iterations, repeats, warmups):
    """Reject measurement settings that cannot satisfy the benchmark protocol."""
    if iterations < 1:
        raise ValueError("iterations must be at least 1.")

    if repeats < 7:
        raise ValueError("repeats must be at least 7 for a reproducible median and IQR.")

    if warmups < 1:
        raise ValueError("warmups must be at least 1.")


def BuildWorkloads():
    """Build explicit membership and operator workloads with parity oracles."""
    return BuildMembershipWorkloads() + BuildOperatorWorkloads()


def BuildMembershipWorkloads():
    """Build one scalar workload for every supported legacy membership family."""
    cases = (
        ("membership_hyperbolic", "hyperbolic", {"a": 2.0, "b": 2.0, "c": 0.0}, 0.5, 0.5),
        ("membership_bell", "bell", {"a": 0.0, "b": 0.25, "c": 0.5}, 0.125, 0.5),
        ("membership_parabolic", "parabolic", {"a": 0.2, "b": 0.8}, 0.5, 0.5),
        ("membership_triangle", "triangle", {"a": 0.1, "b": 0.9, "c": 0.4}, 0.25, 0.5),
        ("membership_trapezium", "trapezium", {"a": 0.1, "b": 0.9, "c": 0.3, "d": 0.7}, 0.2, 0.5),
        ("membership_exponential", "exponential", {"a": 0.5, "b": 0.25}, 0.75, math.exp(-0.5)),
        ("membership_sigmoidal", "sigmoidal", {"a": 2.0, "b": 0.5}, 0.5, 0.5),
        ("membership_desirability", "desirability", {}, 0.0, math.exp(-1.0)),
    )
    workloads = []

    for name, identifier, parameters, inputValue, expectedValue in cases:
        membershipFunction = MFunction(identifier, **parameters)

        def Operation(function=membershipFunction, value=inputValue):
            return function.mju(value)

        def ParityCheck(operation=Operation, expected=expectedValue):
            return math.isclose(
                operation(),
                expected,
                abs_tol=PARITYTOLERANCE,
                rel_tol=0.0,
            )

        workloads.append(
            {
                "name": name,
                "operation": Operation,
                "parity_check": ParityCheck,
            }
        )

    return workloads


def BuildOperatorWorkloads():
    """Build one scalar workload for every supported t-norm and s-norm family."""
    cases = (
        ("logic", 0.25, 0.75, 0.25, 0.75),
        ("algebraic", 0.25, 0.75, 0.1875, 0.8125),
        ("boundary", 0.75, 0.75, 0.5, 1.0),
        ("drastic", 1.0, 0.25, 0.25, 1.0),
    )
    workloads = []

    for normType, leftValue, rightValue, expectedTNorm, expectedSCoNorm in cases:
        def TNormOperation(
            left=leftValue,
            right=rightValue,
            family=normType,
        ):
            return TNorm(left, right, normType=family)

        def SCoNormOperation(
            left=leftValue,
            right=rightValue,
            family=normType,
        ):
            return SCoNorm(left, right, normType=family)

        def TNormParityCheck(operation=TNormOperation, expected=expectedTNorm):
            return math.isclose(
                operation(),
                expected,
                abs_tol=PARITYTOLERANCE,
                rel_tol=0.0,
            )

        def SCoNormParityCheck(operation=SCoNormOperation, expected=expectedSCoNorm):
            return math.isclose(
                operation(),
                expected,
                abs_tol=PARITYTOLERANCE,
                rel_tol=0.0,
            )

        workloads.extend(
            (
                {
                    "name": f"tnorm_{normType}",
                    "operation": TNormOperation,
                    "parity_check": TNormParityCheck,
                },
                {
                    "name": f"sconorm_{normType}",
                    "operation": SCoNormOperation,
                    "parity_check": SCoNormParityCheck,
                },
            )
        )

    return workloads


def Measure(operation, parityCheck, iterations, repeats, warmups):
    """Measure one scalar operation after its numerical-parity gate succeeds."""
    for _ in range(warmups):
        operation()

    if not parityCheck():
        raise RuntimeError(
            "Benchmark parity failed before timing; performance without numerical parity is invalid."
        )

    samples = []

    for _ in range(repeats):
        startedAt = time.perf_counter_ns()

        for _ in range(iterations):
            operation()

        elapsedNs = time.perf_counter_ns() - startedAt
        samples.append(elapsedNs / iterations)

    lowerQuartile, _, upperQuartile = statistics.quantiles(
        samples,
        n=4,
        method="inclusive",
    )

    return {
        "unit": "nanoseconds_per_operation",
        "raw_samples": samples,
        "median": statistics.median(samples),
        "minimum": min(samples),
        "maximum": max(samples),
        "interquartile_range": upperQuartile - lowerQuartile,
        "parity_passed": True,
    }


def GetEnvironment():
    """Collect the local environment fields required by the benchmark protocol."""
    return {
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "memory_bytes": GetMemoryBytes(),
        "package_version": GetPackageVersion(),
        "git": GetGitMetadata(),
    }


def GetMemoryBytes():
    """Return physical memory where the platform exposes it without dependencies."""
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")

    except (AttributeError, OSError, ValueError):
        return None


def GetPackageVersion():
    """Return installed package version without making installation a requirement."""
    try:
        return importlib.metadata.version("fuzzyroutines")

    except importlib.metadata.PackageNotFoundError:
        return "uninstalled-source-tree"


def GetGitMetadata():
    """Return commit and dirty-state metadata when the source tree has Git available."""
    try:
        commitResult = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPOSITORYROOT,
            capture_output=True,
            check=False,
            text=True,
        )
        dirtyResult = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPOSITORYROOT,
            capture_output=True,
            check=False,
            text=True,
        )

    except OSError:
        return {"commit": None, "dirty": None}

    commit = commitResult.stdout.strip() if commitResult.returncode == 0 else None
    dirty = bool(dirtyResult.stdout.strip()) if dirtyResult.returncode == 0 else None

    return {"commit": commit, "dirty": dirty}


def ParseArguments():
    """Parse benchmark command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULTITERATIONS,
        help=f"operations per timed sample (default: {DEFAULTITERATIONS})",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=DEFAULTREPEATS,
        help=f"measured timing samples per workload (default: {DEFAULTREPEATS})",
    )
    parser.add_argument(
        "--warmups",
        type=int,
        default=DEFAULTWARMUPS,
        help=f"warm-up operations before each workload (default: {DEFAULTWARMUPS})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="optional JSON output path; stdout is always written",
    )
    return parser.parse_args()


def Main():
    """Render one reproducible benchmark report."""
    arguments = ParseArguments()
    report = BuildBenchmarkReport(
        iterations=arguments.iterations,
        repeats=arguments.repeats,
        warmups=arguments.warmups,
    )
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)

    if arguments.output is not None:
        arguments.output.write_text(f"{rendered}\n", encoding="utf-8")


if __name__ == "__main__":
    Main()
