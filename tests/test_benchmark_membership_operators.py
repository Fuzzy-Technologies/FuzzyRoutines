# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Tests for the reproducible membership and operator benchmark suite."""

import pytest

from tools.benchmark_membership_operators import BuildBenchmarkReport


EXPECTEDWORKLOADS = {
    "membership_hyperbolic",
    "membership_bell",
    "membership_parabolic",
    "membership_triangle",
    "membership_trapezium",
    "membership_exponential",
    "membership_sigmoidal",
    "membership_desirability",
    "tnorm_logic",
    "tnorm_algebraic",
    "tnorm_boundary",
    "tnorm_drastic",
    "sconorm_logic",
    "sconorm_algebraic",
    "sconorm_boundary",
    "sconorm_drastic",
}


def test_BenchmarkReportCapturesAllRequiredScalarWorkloads():
    report = BuildBenchmarkReport(iterations=1, repeats=7, warmups=1)

    assert report["benchmark"] == "fuzzyroutines-membership-and-operator-scalar"
    assert report["configuration"]["timer"] == "time.perf_counter_ns"
    assert set(report["results"]) == EXPECTEDWORKLOADS, (
        "The benchmark must cover every supported membership and operator family."
    )

    for result in report["results"].values():
        assert result["unit"] == "nanoseconds_per_operation"
        assert len(result["raw_samples"]) == 7, (
            "The benchmark protocol requires at least seven recorded samples."
        )
        assert result["parity_passed"] is True, (
            "A timing report is invalid unless its numerical parity gate passes."
        )
        assert result["minimum"] <= result["median"] <= result["maximum"]
        assert result["interquartile_range"] >= 0.0


@pytest.mark.parametrize(
    ("iterations", "repeats", "warmups", "message"),
    (
        (0, 7, 1, "iterations"),
        (1, 6, 1, "repeats"),
        (1, 7, 0, "warmups"),
    ),
)
def test_BenchmarkReportRejectsNonReproducibleConfiguration(
    iterations,
    repeats,
    warmups,
    message,
):
    with pytest.raises(ValueError, match=message):
        BuildBenchmarkReport(
            iterations=iterations,
            repeats=repeats,
            warmups=warmups,
        )
