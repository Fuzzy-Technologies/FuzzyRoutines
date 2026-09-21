# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Report deterministic coverage diagnostics for the legacy UniversalFuzzyScale.

This diagnostic never retunes the preset. It evaluates the historical five-level
scale on an explicit grid over [0, 1] and records where no level has a strong
membership grade. The default threshold of 0.5 is a reporting convention, not
a mathematical quality assertion.
"""

import argparse
import json
from pathlib import Path

from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale


DEFAULTGRIDPOINTS = 1001
DEFAULTWEAKTHRESHOLD = 0.5


def BuildCoverageReport(gridPoints=DEFAULTGRIDPOINTS, weakThreshold=DEFAULTWEAKTHRESHOLD):
    """Return deterministic coverage and overlap diagnostics for the legacy preset."""
    if gridPoints < 2:
        raise ValueError("gridPoints must be at least 2 so [0, 1] has two endpoints.")

    if not 0.0 < weakThreshold < 1.0:
        raise ValueError("weakThreshold must be strictly inside (0, 1).")

    scale = UniversalFuzzyScale()
    pointRecords = []

    for index in range(gridPoints):
        realValue = index / (gridPoints - 1)
        membershipValues = {
            level["name"]: level["fSet"].mFunction.mju(realValue)
            for level in scale.levels
        }
        maximumMembership = max(membershipValues.values())
        pointRecords.append(
            {
                "real_value": realValue,
                "maximum_membership": maximumMembership,
                "membership_values": membershipValues,
            }
        )

    minimumMembership = min(record["maximum_membership"] for record in pointRecords)
    minimumLocations = [
        record["real_value"]
        for record in pointRecords
        if record["maximum_membership"] == minimumMembership
    ]
    weakIntervals = BuildWeakIntervals(pointRecords, weakThreshold)

    return {
        "preset": "UniversalFuzzyScale",
        "domain": [0.0, 1.0],
        "grid_points": gridPoints,
        "weak_membership_threshold": weakThreshold,
        "minimum_of_maximum_membership": minimumMembership,
        "minimum_locations": minimumLocations,
        "weak_coverage_intervals": weakIntervals,
        "levels": [level["name"] for level in scale.levels],
    }


def BuildWeakIntervals(pointRecords, weakThreshold):
    """Group consecutive weak-coverage grid points into deterministic intervals."""
    intervals = []
    startRecord = None
    pointCount = 0

    previousRecord = None

    for record in pointRecords:
        isWeak = record["maximum_membership"] < weakThreshold

        if isWeak and startRecord is None:
            startRecord = record
            pointCount = 1

        elif isWeak:
            pointCount += 1

        elif startRecord is not None:
            intervals.append(
                {
                    "start": startRecord["real_value"],
                    "end": previousRecord["real_value"],
                    "point_count": pointCount,
                }
            )
            startRecord = None
            pointCount = 0

        previousRecord = record

    if startRecord is not None:
        intervals.append(
            {
                "start": startRecord["real_value"],
                "end": pointRecords[-1]["real_value"],
                "point_count": pointCount,
            }
        )

    return intervals


def ParseArguments():
    """Parse deterministic coverage-report command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grid-points",
        type=int,
        default=DEFAULTGRIDPOINTS,
        help=f"number of inclusive [0, 1] grid points (default: {DEFAULTGRIDPOINTS})",
    )
    parser.add_argument(
        "--weak-threshold",
        type=float,
        default=DEFAULTWEAKTHRESHOLD,
        help=f"diagnostic maximum-membership threshold (default: {DEFAULTWEAKTHRESHOLD})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="optional JSON output path; stdout is always written",
    )
    return parser.parse_args()


def Main():
    """Render one UniversalFuzzyScale coverage report."""
    arguments = ParseArguments()
    report = BuildCoverageReport(
        gridPoints=arguments.grid_points,
        weakThreshold=arguments.weak_threshold,
    )
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)

    if arguments.output is not None:
        arguments.output.write_text(f"{rendered}\n", encoding="utf-8")


if __name__ == "__main__":
    Main()
