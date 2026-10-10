# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Regression tests for the historical UniversalFuzzyScale research preset."""

import pytest

from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale

EXPECTEDLEVELS = (
    ("Min", "Hyperbolic", {"a": 8, "b": 20, "c": 0}, (0.0, 0.23), 0.0632789828672755),
    ("Low", "Bell", {"a": 0.17, "b": 0.23, "c": 0.34}, (0.17, 0.4), 0.28500000000000003),
    ("Med", "Bell", {"a": 0.34, "b": 0.4, "c": 0.6}, (0.34, 0.66), 0.5000000000000001),
    ("High", "Bell", {"a": 0.6, "b": 0.66, "c": 0.77}, (0.6, 0.83), 0.7150000000000001),
    ("Max", "Parabolic", {"a": 0.77, "b": 0.95}, (0.77, 1.0), 0.9251785714285713),
)

FUZZYCASES = (
    (0.0, "Min"),
    (0.2, "Low"),
    (0.4, "Med"),
    (0.7, "High"),
    (0.9, "Max"),
)


def test_UniversalFuzzyScalePresetStructureAndCentroids():
    """Preserve declared universal-scale levels, ordering and centroid reference values."""

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
            f"{expectedName!r} corrected centroid changed."
        )


@pytest.mark.parametrize(("realValue", "expectedName"), FUZZYCASES)
def test_UniversalFuzzyScaleFuzzySelection(realValue, expectedName):
    """Preserve universal-scale winning labels on the fixed historical input grid."""

    scale = UniversalFuzzyScale()

    actualLevel = scale.Fuzzy(realValue)

    assert actualLevel["name"] == expectedName, (
        f"UniversalFuzzyScale returned {actualLevel['name']!r} instead of {expectedName!r} "
        f"for {realValue!r}."
    )


def test_UniversalFuzzyScaleLevelNamesRemainAvailable():
    """Verify that universal fuzzy scale level names remain available."""

    scale = UniversalFuzzyScale()

    assert set(scale.levelsNames) == {"Min", "Low", "Med", "High", "Max"}, (
        "The case-sensitive UniversalFuzzyScale name map changed."
    )
    assert set(scale.levelsNamesUpper) == {"MIN", "LOW", "MED", "HIGH", "MAX"}, (
        "The case-insensitive UniversalFuzzyScale name map changed."
    )


@pytest.mark.parametrize(("coordinate", "expected"), ((0.37, "Low"), (0.63, "High"), (0.81, "High")))
def test_UniversalGuidePreservesFloatingPointWinner(coordinate, expected):
    """Protect near-tie migration semantics instead of rounding the grades."""

    import runpy
    from pathlib import Path

    from fuzzyroutines import FuzzificationPolicy

    guide = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/guide.py"))
    result = guide["UniversalScale"]().Fuzzify(coordinate, FuzzificationPolicy(tiePolicy="last"))
    assert result.selectedTerms[0].name == expected
    assert UniversalFuzzyScale().Fuzzy(coordinate)["name"] == expected


def test_UniversalGuideDeclaresBoundaryAndTailDifferences():
    """Keep closed normalized bounds and reject accidental legacy-window clipping."""

    import runpy
    from pathlib import Path

    guide = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/guide.py"))
    scale = guide["UniversalScale"]()
    historical = UniversalFuzzyScale()
    assert scale.Fuzzify(0).selectedTerms[0].name == "Min"
    assert scale.Fuzzify(1).selectedTerms[0].name == "Max"
    assert scale.terms[0].fuzzySet.Membership(0.5) == pytest.approx(1 / (1 + 4**20), rel=1e-12, abs=0)

    for coordinate, label in ((-0.1, "Min"), (1.1, "Max")):
        assert historical.Fuzzy(coordinate)["name"] == label

        with pytest.raises(ValueError, match="universe"):
            scale.Fuzzify(coordinate)
