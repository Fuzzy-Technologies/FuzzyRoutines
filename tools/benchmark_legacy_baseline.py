# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Capture reproducible timing observations for the unmodified legacy API.

This tool records an informational baseline. It writes JSON to stdout and only
creates a file when `--output` names an explicit artifact path. It does not
make performance claims and must not be used to justify an optimization
without a comparable before/after run.
"""


import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path

try:
    from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction, UniversalFuzzyScale

except ModuleNotFoundError as error:
    if error.name != "fuzzyroutines":
        raise

    repositoryRoot = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repositoryRoot))
    from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction, UniversalFuzzyScale


def BuildBellMembership():
    """Build the representative historical bell membership function."""

    return MFunction("bell", a=0.17, b=0.23, c=0.34)


def BuildFuzzySet():
    """Build the representative historical set and compute its centroid."""

    return FuzzySet(
        membershipFunction=BuildBellMembership(),
        supportSet=(0.17, 0.40),
        linguisticName="LegacyBenchmark",
    )


def Measure(operation, iterations, repeats):
    """Return per-operation wall-clock samples in microseconds."""
    operation()
    samples = []

    for _ in range(repeats):
        started = time.perf_counter()

        for _ in range(iterations):
            operation()

        elapsed = time.perf_counter() - started
        samples.append((elapsed / iterations) * 1000000.0)

    return {
        "iterations_per_repeat": iterations,
        "repeats": repeats,
        "samples_us": samples,
        "median_us": statistics.median(samples),
        "minimum_us": min(samples),
        "maximum_us": max(samples),
    }


def BuildReport(repeats):
    """Build the complete historical timing and host-environment report."""

    membership = BuildBellMembership()
    scale = UniversalFuzzyScale()
    lookup = scale.Fuzzy(0.5)

    if lookup["name"] != "Med":
        raise RuntimeError("Unexpected UniversalFuzzyScale lookup result")

    benchmarks = {
        "bell_membership_evaluation": Measure(
            lambda: membership.mju(0.22),
            iterations=200000,
            repeats=repeats,
        ),
        "fuzzy_set_construction_and_centroid": Measure(
            BuildFuzzySet,
            iterations=100,
            repeats=repeats,
        ),
        "universal_scale_construction": Measure(
            UniversalFuzzyScale,
            iterations=25,
            repeats=repeats,
        ),
        "universal_scale_lookup": Measure(
            lambda: scale.Fuzzy(0.5),
            iterations=100000,
            repeats=repeats,
        ),
    }

    return {
        "benchmark": "fuzzyroutines-legacy-performance-baseline",
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "benchmarks": benchmarks,
    }


def ParseArguments(arguments=None):
    """Parse repeat count and optional explicit output path."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repeats",
        type=int,
        default=7,
        help="number of timing samples per benchmark (default: 7)",
    )
    parser.add_argument(
        "--output",
        help="optional path for the JSON report; stdout is always written",
    )
    return parser.parse_args(arguments)


def Main(arguments=None):
    """Emit the baseline report and return zero after successful output."""

    arguments = ParseArguments(arguments)

    if arguments.repeats < 3:
        raise ValueError("--repeats must be at least 3")

    report = BuildReport(arguments.repeats)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)

    if arguments.output:
        with open(arguments.output, "w", encoding="utf-8") as outputFile:
            outputFile.write(rendered)
            outputFile.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
