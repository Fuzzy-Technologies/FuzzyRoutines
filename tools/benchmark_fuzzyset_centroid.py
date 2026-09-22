# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Benchmark legacy fuzzy-set construction and centroid recalculation.

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

from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

MINIMUMSAMPLES = 7
SHAPES = {
    "hyperbolic": {"a": 7, "b": 4, "c": 0},
    "bell": {"a": 0.35, "b": 0.5, "c": 0.6},
    "triangle": {"a": 0.0, "b": 1.0, "c": 0.5},
    "parabolic": {"a": 0.0, "b": 1.0},
}
REPOSITORYROOT = Path(__file__).resolve().parents[1]


def BuildFuzzySet(shapeName):
    """Construct one representative mutable legacy fuzzy set."""

    membershipFunction = MFunction(shapeName, **SHAPES[shapeName])
    return FuzzySet(membershipFunction, supportSet=(0.0, 1.0), linguisticName=shapeName)


def Measure(workload, sampleCount=MINIMUMSAMPLES):
    """Measure independent duration and peak-allocation samples."""

    if sampleCount < MINIMUMSAMPLES:
        raise ValueError(f"sampleCount must be at least {MINIMUMSAMPLES}")

    durationSamples = []
    peakBytesSamples = []

    for _ in range(sampleCount):
        tracemalloc.start()
        start = perf_counter_ns()
        workload()
        durationSamples.append(perf_counter_ns() - start)
        _, peakBytes = tracemalloc.get_traced_memory()
        peakBytesSamples.append(peakBytes)
        tracemalloc.stop()

    return {
        "duration_ns": durationSamples,
        "median_ns": median(durationSamples),
        "min_ns": min(durationSamples),
        "max_ns": max(durationSamples),
        "peak_bytes": peakBytesSamples,
        "median_peak_bytes": median(peakBytesSamples),
    }


def BuildReport(sampleCount=MINIMUMSAMPLES):
    """Build construction and centroid evidence for every configured shape."""

    workloads = {}

    for shapeName in SHAPES:
        fuzzySet = BuildFuzzySet(shapeName)
        workloads[shapeName] = {
            "construction": Measure(
                lambda selectedShape=shapeName: BuildFuzzySet(selectedShape),
                sampleCount,
            ),
            "centroid_recalculation": Measure(fuzzySet._Defuz, sampleCount),
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
