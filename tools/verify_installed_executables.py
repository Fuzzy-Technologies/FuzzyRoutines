# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Verify examples and benchmarks against the active installed distribution.

The command runs every user-facing example and benchmark from a new explicit
artifact directory with `PYTHONPATH` removed. JSON stdout is persisted and
parsed, benchmark `--output` files are compared with stdout, and the package
origin must reside under the active interpreter prefix. The command creates
only `--artifact-directory` and its contents, performs no network access,
prints a JSON summary to stdout, and returns nonzero when any contract fails.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECTROOT = Path(__file__).resolve().parents[1]
EXAMPLEROOT = PROJECTROOT / "examples" / "migration"
COMPATIBILITYGUIDE = PROJECTROOT / "docs" / "COMPATIBILITY.md"


def ParseArguments(arguments=None):
    """Parse the required isolated artifact directory."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact-directory",
        required=True,
        type=Path,
        help="new directory that receives captured stdout and JSON reports",
    )
    return parser.parse_args(arguments)


def BuildEnvironment():
    """Return an environment that cannot resolve the source tree via overrides."""

    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


def LoadCompatibilityGuideExamples():
    """Return every Python snippet from the canonical compatibility guide."""

    guideText = COMPATIBILITYGUIDE.read_text(encoding="utf-8")
    examples = tuple(re.findall(r"```python\n(.*?)```", guideText, flags=re.DOTALL))

    if not examples:
        raise RuntimeError("docs/COMPATIBILITY.md contains no Python examples")

    return examples


def RunCommand(name, command, artifactDirectory, environment, expectJson=True):
    """Run one entry point and persist its externally observable streams."""

    completedProcess = subprocess.run(
        command,
        cwd=artifactDirectory,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    stdoutPath = artifactDirectory / f"{name}.stdout"
    stderrPath = artifactDirectory / f"{name}.stderr"
    stdoutPath.write_text(completedProcess.stdout, encoding="utf-8")
    stderrPath.write_text(completedProcess.stderr, encoding="utf-8")

    if completedProcess.returncode != 0:
        raise RuntimeError(
            f"{name} failed with exit code {completedProcess.returncode}; "
            f"inspect {stdoutPath} and {stderrPath}"
        )

    if expectJson:
        return json.loads(completedProcess.stdout)

    if not completedProcess.stdout.strip():
        raise RuntimeError(f"{name} produced no stdout evidence")

    return {"stdout_bytes": len(completedProcess.stdout.encode("utf-8"))}


def VerifyPackageOrigin(artifactDirectory, environment):
    """Prove imports resolve from the active environment rather than the checkout."""

    probe = RunCommand(
        "installed-package-origin",
        [
            sys.executable,
            "-c",
            (
                "import fuzzyroutines, json, sys; "
                "print(json.dumps({'package': fuzzyroutines.__file__, 'prefix': sys.prefix}))"
            ),
        ],
        artifactDirectory,
        environment,
    )
    packagePath = Path(probe["package"]).resolve()
    environmentPrefix = Path(probe["prefix"]).resolve()

    if not packagePath.is_relative_to(environmentPrefix):
        raise RuntimeError(
            f"fuzzyroutines resolved outside the active environment: {packagePath}"
        )

    return str(packagePath)


def RunJsonEntryPoint(name, command, artifactDirectory, environment):
    """Run a JSON CLI and compare stdout with its explicit output artifact."""

    outputPath = artifactDirectory / f"{name}.json"
    stdoutReport = RunCommand(
        name,
        [*command, "--output", str(outputPath)],
        artifactDirectory,
        environment,
    )
    artifactReport = json.loads(outputPath.read_text(encoding="utf-8"))

    if stdoutReport != artifactReport:
        raise RuntimeError(f"{name} stdout differs from its --output artifact")

    return sorted(stdoutReport)


def RunCompatibilityGuideExamples(artifactDirectory, environment):
    """Execute guide snippets against only the active installed package."""

    results = {}

    for exampleIndex, example in enumerate(LoadCompatibilityGuideExamples(), start=1):
        verification = (
            "\nassert abs(centroid - 0.5) < 1e-12\n"
            if "centroid =" in example
            else ""
        )
        command = example + verification + "\nprint('compatibility guide example: PASS')\n"
        exampleName = f"compatibility-guide-example-{exampleIndex}"
        results[exampleName] = RunCommand(
            exampleName,
            [sys.executable, "-I", "-c", command],
            artifactDirectory,
            environment,
            expectJson=False,
        )

    return results


def Main(arguments=None):
    """Execute clean-install evidence and return zero after a complete pass."""

    parsedArguments = ParseArguments(arguments)
    artifactDirectory = parsedArguments.artifact_directory.resolve()
    repositoryEntries = frozenset(path.name for path in PROJECTROOT.iterdir())
    artifactDirectory.mkdir(parents=True, exist_ok=False)
    environment = BuildEnvironment()
    packagePath = VerifyPackageOrigin(artifactDirectory, environment)

    results = {
        "compatibility-guide-examples": RunCompatibilityGuideExamples(
            artifactDirectory,
            environment,
        ),
        "historical-migration": sorted(
            RunCommand(
                "historical-migration",
                [sys.executable, str(EXAMPLEROOT / "historical_compatibility.py")],
                artifactDirectory,
                environment,
            )
        ),
        "modern-migration": sorted(
            RunCommand(
                "modern-migration",
                [sys.executable, str(EXAMPLEROOT / "modern_supported.py")],
                artifactDirectory,
                environment,
            )
        ),
        "bundled-compatibility": RunCommand(
            "bundled-compatibility",
            [sys.executable, "-m", "fuzzyroutines.Examples"],
            artifactDirectory,
            environment,
            expectJson=False,
        ),
        "benchmark-centroid": RunJsonEntryPoint(
            "benchmark-centroid",
            [
                sys.executable,
                str(PROJECTROOT / "tools" / "benchmark_fuzzyset_centroid.py"),
                "--samples",
                "7",
            ],
            artifactDirectory,
            environment,
        ),
        "benchmark-legacy": RunJsonEntryPoint(
            "benchmark-legacy",
            [
                sys.executable,
                str(PROJECTROOT / "tools" / "benchmark_legacy_baseline.py"),
                "--repeats",
                "3",
            ],
            artifactDirectory,
            environment,
        ),
        "benchmark-membership-operators": RunJsonEntryPoint(
            "benchmark-membership-operators",
            [
                sys.executable,
                str(PROJECTROOT / "tools" / "benchmark_membership_operators.py"),
                "--iterations",
                "1",
                "--repeats",
                "7",
                "--warmups",
                "1",
            ],
            artifactDirectory,
            environment,
        ),
        "benchmark-scale": RunJsonEntryPoint(
            "benchmark-scale",
            [
                sys.executable,
                str(PROJECTROOT / "tools" / "benchmark_scale_lookup.py"),
                "--samples",
                "7",
            ],
            artifactDirectory,
            environment,
        ),
    }
    addedRepositoryEntries = frozenset(path.name for path in PROJECTROOT.iterdir()) - repositoryEntries

    if addedRepositoryEntries:
        raise RuntimeError(
            "entry points created repository-root artifacts: "
            + ", ".join(sorted(addedRepositoryEntries))
        )

    summary = {
        "artifact_directory": str(artifactDirectory),
        "installed_package": packagePath,
        "results": results,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
