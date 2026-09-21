# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Contracts for the reproducible fuzzy-set centroid benchmark."""

from tools.benchmark_fuzzyset_centroid import BuildReport, MINIMUMSAMPLES, Measure, SHAPES


def test_BenchmarkFuzzySetReportCoversRepresentativeShapes():
    report = BuildReport()

    assert report["sample_count"] == MINIMUMSAMPLES
    assert set(report["workloads"]) == set(SHAPES)

    for workload in report["workloads"].values():
        assert set(workload) == {"construction", "centroid_recalculation"}

        for measurement in workload.values():
            assert len(measurement["duration_ns"]) == MINIMUMSAMPLES
            assert len(measurement["peak_bytes"]) == MINIMUMSAMPLES
            assert measurement["min_ns"] <= measurement["median_ns"] <= measurement["max_ns"]
            assert measurement["median_peak_bytes"] >= 0


def test_BenchmarkFuzzySetRejectsInsufficientSamples():
    try:
        Measure(lambda: None, MINIMUMSAMPLES - 1)

    except ValueError:
        pass

    else:
        raise AssertionError("expected an explicit sample-count error")
