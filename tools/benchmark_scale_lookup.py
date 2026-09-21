# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Reproducible scalar baseline for legacy scale construction and lookup."""

from __future__ import annotations

import json
import platform
import sys
import tracemalloc
from statistics import median
from time import perf_counter_ns

from fuzzyroutines.FuzzyRoutines import FuzzyScale, UniversalFuzzyScale

MINIMUMSAMPLES = 7
LOOKUPSAMPLES = 100
SCALES = {"default": FuzzyScale, "universal": UniversalFuzzyScale}


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
    evaluationCount = {"value": 0}

    for level in scale.levels:
        original = level["fSet"].mFunction.mju

        def Counted(value, original=original):
            evaluationCount["value"] += 1
            return original(value)

        level["fSet"].mFunction.mju = Counted

    def Lookup():
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
        "workloads": workloads,
    }


def Main():
    report = BuildReport()
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    Main()
