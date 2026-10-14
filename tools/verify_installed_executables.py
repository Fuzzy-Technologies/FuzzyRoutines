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
import importlib.metadata
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECTROOT = Path(__file__).resolve().parents[1]
EXAMPLEROOT = PROJECTROOT / "examples" / "migration"
COMPATIBILITYGUIDE = PROJECTROOT / "docs" / "COMPATIBILITY.md"
CANONICALROOT = PROJECTROOT / "docs" / "site" / "content" / "en"


def ParseArguments(arguments=None):
    """Parse the required isolated artifact directory."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact-directory",
        required=True,
        type=Path,
        help="new directory that receives captured stdout and JSON reports",
    dest = 'artifactDirectory')
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


def LoadCanonicalGuideExamples(contentRoot=CANONICALROOT):
    """Discover every canonical English Python fence in deterministic page order."""

    examples = {}
    for pagePath in sorted(contentRoot.rglob("*.md")):
        relativePath = pagePath.relative_to(contentRoot).with_suffix("")
        pageName = "-".join(relativePath.parts)
        snippets = re.findall(r"```python\n(.*?)```", pagePath.read_text(encoding="utf-8"), flags=re.DOTALL)
        for snippetIndex, snippet in enumerate(snippets, start=1):
            examples[f"canonical-{pageName}-{snippetIndex}"] = snippet
    if not examples:
        raise RuntimeError("canonical English documentation contains no Python examples")
    return examples


def RunCanonicalGuideExamples(artifactDirectory, environment):
    """Execute every English snippet and all nine scenarios against an installed artifact."""

    results = {}
    for name, snippet in LoadCanonicalGuideExamples().items():
        results[name] = RunCommand(
            name,
            [sys.executable, "-I", "-c", snippet + "\nprint('canonical example: PASS')\n"],
            artifactDirectory,
            environment,
            expectJson=False,
        )
    report = RunCommand(
        "worked-scenarios",
        [sys.executable, "-I", str(PROJECTROOT / "examples" / "guide.py")],
        artifactDirectory,
        environment,
    )
    expectedScenarios = {"temperature", "risk", "sensors", "alarm", "alpha-cuts", "centroid", "scale-audit", "custom", "universal-fuzzy-scale"}
    if set(report) != expectedScenarios:
        raise RuntimeError("worked-scenarios did not execute the complete documented scenario set")
    results["worked-scenarios"] = sorted(report)
    results["public-symbol-example-coverage"] = RunCommand(
        "public-symbol-example-coverage",
        [
            sys.executable, "-I", str(PROJECTROOT / "tools/guide_example_coverage.py"),
            "--require-installed", "--check-index", "--output",
            str(artifactDirectory / "api-example-coverage.json"),
        ],
        artifactDirectory,
        environment,
    )
    return results


def RunAgentRecipes(artifactDirectory, environment):
    """Verify documented standalone recipes against the actual installed candidate.

    The exact installed version is passed explicitly, so this gate can test a
    development wheel without changing the public released-version instructions.
    Every subprocess uses isolated imports and persists parseable JSON evidence.
    """

    installedVersion = importlib.metadata.version("fuzzyroutines")
    results = {}
    scenarios = (
        ("agent-universal-scale", "universal-fuzzy-scale", "0.2", ["Low"]),
        ("agent-risk-high", "risk", "75", ["High"]),
        ("agent-risk-abstention", "risk", "17", []),
    )

    for name, scenario, value, expectedTerms in scenarios:
        outputPath = artifactDirectory / f"{name}.json"
        report = RunCommand(
            name,
            [sys.executable, "-I", str(PROJECTROOT / "examples/agent_recipe.py"),
             "--expect-version", installedVersion, "--scenario", scenario,
             "--value", value, "--output", str(outputPath)],
            artifactDirectory,
            environment,
        )

        if report != json.loads(outputPath.read_text(encoding="utf-8")):
            raise RuntimeError(f"{name} stdout differs from the requested JSON artifact")

        if report["environment"]["fuzzyroutines"] != installedVersion:
            raise RuntimeError(f"{name} did not execute the installed candidate")

        if report["result"]["selectedTerms"] != expectedTerms or not report["checks"]["passed"]:
            raise RuntimeError(f"{name} failed its expected numerical outcome")

        results[name] = {"version": installedVersion, "selectedTerms": expectedTerms,
                         "maximumAbsoluteError": report["checks"]["maximumAbsoluteError"]}

    return results


def Main(arguments=None):
    """Execute clean-install evidence and return zero after a complete pass."""

    parsedArguments = ParseArguments(arguments)
    artifactDirectory = parsedArguments.artifactDirectory.resolve()
    repositoryEntries = frozenset(path.name for path in PROJECTROOT.iterdir())
    artifactDirectory.mkdir(parents=True, exist_ok=False)
    environment = BuildEnvironment()
    packagePath = VerifyPackageOrigin(artifactDirectory, environment)

    results = {
        "agent-recipes": RunAgentRecipes(artifactDirectory, environment),
        "consumer-scale-migration": RunJsonEntryPoint(
            "consumer-scale-migration",
            [
                sys.executable, "-I", str(PROJECTROOT / "tools/consumer_scale_migration.py"),
                "--fixture", str(PROJECTROOT / "tests/fixtures/consumer_scale_migration.json"),
                "--check-current",
            ],
            artifactDirectory,
            environment,
        ),
        "fuzzy-inference": RunCommand(
            "fuzzy-inference",
            [sys.executable, "-I", str(PROJECTROOT / "examples/inference.py")],
            artifactDirectory,
            environment,
        ),
        "canonical-guide-examples": RunCanonicalGuideExamples(artifactDirectory, environment),
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
                "10000",
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
