"""Reproducible scalar baseline for legacy FuzzySet construction and centroid work."""

from __future__ import annotations

import json
import platform
import sys
import tracemalloc
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


def BuildFuzzySet(shapeName):
    membershipFunction = MFunction(shapeName, **SHAPES[shapeName])
    return FuzzySet(membershipFunction, supportSet=(0.0, 1.0), linguisticName=shapeName)


def Measure(workload, sampleCount=MINIMUMSAMPLES):
    if sampleCount < MINIMUMSAMPLES:
        raise ValueError("sampleCount must be at least {}".format(MINIMUMSAMPLES))

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
    workloads = {}

    for shapeName in SHAPES:
        fuzzySet = BuildFuzzySet(shapeName)
        workloads[shapeName] = {
            "construction": Measure(lambda: BuildFuzzySet(shapeName), sampleCount),
            "centroid_recalculation": Measure(fuzzySet._Defuz, sampleCount),
        }

    return {
        "method": "perf_counter_ns with per-sample tracemalloc peak bytes",
        "sample_count": sampleCount,
        "python": sys.version,
        "platform": platform.platform(),
        "workloads": workloads,
    }


def Main():
    report = BuildReport()
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    Main()
