# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Capture reproducible timing observations for the unmodified legacy API.

This tool records an informational baseline.  It does not make performance
claims and must not be used to justify an optimization without a comparable
before/after run.
"""

from __future__ import print_function

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction, UniversalFuzzyScale


def build_bell_membership():
    return MFunction("bell", **{"a": 0.17, "b": 0.23, "c": 0.34})


def build_fuzzy_set():
    return FuzzySet(
        membershipFunction=build_bell_membership(),
        supportSet=(0.17, 0.40),
        linguisticName="LegacyBenchmark",
    )


def measure(operation, iterations, repeats):
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


def build_report(repeats):
    membership = build_bell_membership()
    scale = UniversalFuzzyScale()
    lookup = scale.Fuzzy(0.5)

    if lookup["name"] != "Med":
        raise RuntimeError("Unexpected UniversalFuzzyScale lookup result")

    benchmarks = {
        "bell_membership_evaluation": measure(
            lambda: membership.mju(0.22),
            iterations=200000,
            repeats=repeats,
        ),
        "fuzzy_set_construction_and_centroid": measure(
            build_fuzzy_set,
            iterations=100,
            repeats=repeats,
        ),
        "universal_scale_construction": measure(
            UniversalFuzzyScale,
            iterations=25,
            repeats=repeats,
        ),
        "universal_scale_lookup": measure(
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


def parse_arguments():
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
    return parser.parse_args()


def main():
    arguments = parse_arguments()

    if arguments.repeats < 3:
        raise ValueError("--repeats must be at least 3")

    report = build_report(arguments.repeats)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)

    if arguments.output:
        with open(arguments.output, "w") as output_file:
            output_file.write(rendered)
            output_file.write("\n")


if __name__ == "__main__":
    main()
