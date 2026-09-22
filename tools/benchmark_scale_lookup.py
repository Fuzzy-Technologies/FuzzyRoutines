# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Benchmark legacy scale construction and repeated lookup.

The command writes one JSON report to stdout. `--output` may additionally
write the same report to an explicit artifact path; no repository file is
created implicitly. Invalid sample counts or unwritable paths fail with a
nonzero process exit code.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tracemalloc
from pathlib import Path
from statistics import median
from time import perf_counter_ns

from fuzzyroutines.FuzzyRoutines import FuzzyScale, UniversalFuzzyScale

MINIMUMSAMPLES = 7
LOOKUPSAMPLES = 100
SCALES = {"default": FuzzyScale, "universal": UniversalFuzzyScale}
REPOSITORYROOT = Path(__file__).resolve().parents[1]


def Measure(workload, sampleCount=MINIMUMSAMPLES, summarizeResult=None):
    """Measure a workload and retain one optionally summarized result."""

    if sampleCount < MINIMUMSAMPLES:
        raise ValueError(f"sampleCount must be at least {MINIMUMSAMPLES}")

    durationSamples = []
    peakBytesSamples = []
    firstResult = None

    for sampleIndex in range(sampleCount):
        tracemalloc.start()
        start = perf_counter_ns()
        sampleResult = workload()
        durationSamples.append(perf_counter_ns() - start)
        _, peakBytes = tracemalloc.get_traced_memory()
        peakBytesSamples.append(peakBytes)
        tracemalloc.stop()

        if sampleIndex == 0:
            firstResult = sampleResult

    if summarizeResult is not None:
        firstResult = summarizeResult(firstResult)

    return {
        "duration_ns": durationSamples,
        "median_ns": median(durationSamples),
        "min_ns": min(durationSamples),
        "max_ns": max(durationSamples),
        "peak_bytes": peakBytesSamples,
        "median_peak_bytes": median(peakBytesSamples),
        "result": firstResult,
    }


def SummarizeScale(scale):
    """Return stable JSON-safe evidence about a constructed scale."""

    return {
        "class": type(scale).__name__,
        "level_count": len(scale.levels),
    }


def BuildLookupWorkload(scale):
    """Instrument one scale to count membership evaluations per lookup."""

    evaluationCount = {"value": 0}

    for level in scale.levels:
        original = level["fSet"].mFunction.mju

        def Counted(value, original=original):
            """Count and delegate one membership evaluation."""

            evaluationCount["value"] += 1
            return original(value)

        level["fSet"].mFunction.mju = Counted

    def Lookup():
        """Perform a fixed batch and return stable lookup evidence."""

        evaluationCount["value"] = 0
        selectedName = None

        for _ in range(LOOKUPSAMPLES):
            selectedName = scale.Fuzzy(0.5)["name"]

        return {
            "selected_level": selectedName,
            "lookups_per_sample": LOOKUPSAMPLES,
            "membership_evaluations": evaluationCount["value"],
        }

    return Lookup


def BuildReport(sampleCount=MINIMUMSAMPLES):
    """Build construction and repeated-lookup evidence for each scale."""

    workloads = {}

    for scaleName, scaleClass in SCALES.items():
        scale = scaleClass()
        workloads[scaleName] = {
            "construction": Measure(scaleClass, sampleCount, SummarizeScale),
            "repeated_lookup": Measure(BuildLookupWorkload(scale), sampleCount),
        }

    return {
        "method": "perf_counter_ns with per-sample tracemalloc peak bytes",
        "sample_count": sampleCount,
        "python": sys.version,
        "platform": platform.platform(),
        "environment": GetEnvironment(),
        "workloads": workloads,
    }


def GetEnvironment():
    """Collect interpreter, host, package, and source-revision evidence."""

    try:
        packageVersion = importlib.metadata.version("fuzzyroutines")

    except importlib.metadata.PackageNotFoundError:
        packageVersion = "uninstalled-source-tree"

    return {
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "package_version": packageVersion,
        "git": GetGitMetadata(),
    }


def GetGitMetadata():
    """Return commit and dirty state when the checkout is available."""

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

    return {
        "commit": commitResult.stdout.strip() if commitResult.returncode == 0 else None,
        "dirty": bool(dirtyResult.stdout.strip()) if dirtyResult.returncode == 0 else None,
    }


def ParseArguments(arguments=None):
    """Parse the shell-visible benchmark configuration."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--samples",
        type=int,
        default=MINIMUMSAMPLES,
        help=f"measured samples per workload (minimum and default: {MINIMUMSAMPLES})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="optional JSON artifact path; stdout is always written",
    )
    return parser.parse_args(arguments)


def Main(arguments=None):
    """Emit a complete report and return zero after successful serialization."""

    parsedArguments = ParseArguments(arguments)
    report = BuildReport(parsedArguments.samples)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)

    if parsedArguments.output is not None:
        parsedArguments.output.write_text(f"{rendered}\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
