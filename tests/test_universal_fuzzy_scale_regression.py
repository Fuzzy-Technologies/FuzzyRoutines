# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Regression tests for the historical UniversalFuzzyScale research preset."""

import pytest

from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale


EXPECTEDLEVELS = (
    ("Min", "Hyperbolic", {"a": 8, "b": 20, "c": 0}, (0.0, 0.23), 0.06333697923354091),
    ("Low", "Bell", {"a": 0.17, "b": 0.23, "c": 0.34}, (0.17, 0.4), 0.28500000000000003),
    ("Med", "Bell", {"a": 0.34, "b": 0.4, "c": 0.6}, (0.34, 0.66), 0.49999999999999956),
    ("High", "Bell", {"a": 0.6, "b": 0.66, "c": 0.77}, (0.6, 0.83), 0.7149999999999982),
    ("Max", "Parabolic", {"a": 0.77, "b": 0.95}, (0.77, 1.0), 0.9252400129145878),
)

FUZZYCASES = (
    (0.0, "Min"),
    (0.2, "Low"),
    (0.4, "Med"),
    (0.7, "High"),
    (0.9, "Max"),
)


def test_UniversalFuzzyScalePresetStructureAndCentroids():
    scale = UniversalFuzzyScale()

    assert scale.name == "FuzzyScale", "The historical preset name is part of its regression contract."
    assert [level["name"] for level in scale.levels] == [item[0] for item in EXPECTEDLEVELS], (
        "The historical UniversalFuzzyScale level order changed."
    )

    for level, expected in zip(scale.levels, EXPECTEDLEVELS, strict=True):
        expectedName, expectedFunctionName, expectedParameters, expectedSupport, expectedCentroid = expected
        fuzzySet = level["fSet"]

        assert level["name"] == expectedName, "A historical UniversalFuzzyScale level name changed."
        assert fuzzySet.mFunction.name == expectedFunctionName, (
            f"{expectedName!r} no longer uses its historical membership family."
        )
        assert fuzzySet.mFunction.parameters == expectedParameters, (
            f"{expectedName!r} membership parameters changed."
        )
        assert fuzzySet.supportSet == expectedSupport, f"{expectedName!r} support changed."
        assert fuzzySet.Defuz() == pytest.approx(expectedCentroid, abs=1e-12, rel=0.0), (
            f"{expectedName!r} historical centroid changed."
        )


@pytest.mark.parametrize(("realValue", "expectedName"), FUZZYCASES)
def test_UniversalFuzzyScaleFuzzySelection(realValue, expectedName):
    scale = UniversalFuzzyScale()

    actualLevel = scale.Fuzzy(realValue)

    assert actualLevel["name"] == expectedName, (
        f"UniversalFuzzyScale returned {actualLevel['name']!r} instead of {expectedName!r} "
        f"for {realValue!r}."
    )


def test_UniversalFuzzyScaleLevelNamesRemainAvailable():
    scale = UniversalFuzzyScale()

    assert set(scale.levelsNames) == {"Min", "Low", "Med", "High", "Max"}, (
        "The case-sensitive UniversalFuzzyScale name map changed."
    )
    assert set(scale.levelsNamesUpper) == {"MIN", "LOW", "MED", "HIGH", "MAX"}, (
        "The case-insensitive UniversalFuzzyScale name map changed."
    )
