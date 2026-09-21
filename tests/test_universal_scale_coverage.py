# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Tests for the deterministic UniversalFuzzyScale coverage diagnostic."""

import pytest

from tools.report_universal_scale_coverage import BuildCoverageReport


def test_UniversalFuzzyScaleCoverageReportIdentifiesWeakIntervals():
    report = BuildCoverageReport(gridPoints=1001, weakThreshold=0.5)

    assert report["preset"] == "UniversalFuzzyScale"
    assert report["domain"] == [0.0, 1.0]
    assert report["grid_points"] == 1001
    assert report["minimum_of_maximum_membership"] == pytest.approx(
        0.0018943253761053826,
        abs=1e-12,
        rel=0.0,
    ), "The coverage diagnostic must freeze the current historical preset."
    assert report["minimum_locations"] == [0.171], (
        "The minimum coverage location changed and requires deliberate review."
    )
    assert report["weak_coverage_intervals"] == [
        {"start": 0.126, "end": 0.199, "point_count": 74},
        {"start": 0.801, "end": 0.859, "point_count": 59},
    ], "Weak coverage regions must be explicit diagnostic output."


@pytest.mark.parametrize(
    ("gridPoints", "weakThreshold", "message"),
    (
        (1, 0.5, "gridPoints"),
        (1001, 0.0, "weakThreshold"),
        (1001, 1.0, "weakThreshold"),
    ),
)
def test_UniversalFuzzyScaleCoverageReportRejectsInvalidConfiguration(
    gridPoints,
    weakThreshold,
    message,
):
    with pytest.raises(ValueError, match=message):
        BuildCoverageReport(gridPoints=gridPoints, weakThreshold=weakThreshold)
