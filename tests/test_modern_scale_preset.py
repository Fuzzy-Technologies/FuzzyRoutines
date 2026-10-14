# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Independent formula and compatibility evidence for the modern preset."""

import math
from dataclasses import FrozenInstanceError

import pytest

from fuzzyroutines import (
    Centroid,
    CreateUniversalFuzzyScale,
    FuzzificationPolicy,
    LinguisticScale,
    LinguisticTerm,
    UniversalFuzzyScaleDomains,
    UniversalFuzzyScalePolicy,
)
from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale


def RisingShoulder(coordinate, left, right):
    """Evaluate the historical quadratic definition independently of the API."""

    if coordinate <= left:
        return 0.0

    if coordinate >= right:
        return 1.0

    if coordinate <= (left + right) / 2:
        return 2 * ((coordinate - left) / (right - left)) ** 2

    return 1 - 2 * ((right - coordinate) / (right - left)) ** 2


def ReferenceGrades(coordinate):
    """Return five grades from the independent piecewise formulas."""

    bells = tuple(
        min(RisingShoulder(coordinate, left, coreLeft),
            1 - RisingShoulder(coordinate, coreRight, coreRight + coreLeft - left))
        for left, coreLeft, coreRight in ((0.17, 0.23, 0.34), (0.34, 0.40, 0.60), (0.60, 0.66, 0.77))
    )

    return (1 / (1 + (8 * coordinate) ** 20), *bells, RisingShoulder(coordinate, 0.77, 0.95))


def test_PresetMatchesIndependentFormulasAndFacadeIncludingAdjacentFloats():
    """Protect original coefficients, binary64 winners and closed endpoint semantics."""

    scale = CreateUniversalFuzzyScale()
    legacy = UniversalFuzzyScale()
    policy = UniversalFuzzyScalePolicy()
    knots = (0, 0.125, 0.17, 0.20, 0.23, 0.34, 0.37, 0.40, 0.60, 0.63, 0.66, 0.77, 0.80, 0.81, 0.83, 0.86, 0.95, 1)
    coordinates = {index / 1000 for index in range(1001)}
    coordinates.update(point for knot in knots for point in (math.nextafter(knot, -math.inf), knot, math.nextafter(knot, math.inf)) if 0 <= point <= 1)

    for coordinate in sorted(coordinates):
        result = scale.Fuzzify(coordinate, policy)
        grades = tuple(item.grade for item in result.memberships)
        # Equivalent shoulder expressions differ by a few binary64 roundings.
        assert grades == pytest.approx(ReferenceGrades(coordinate), abs=1e-12, rel=0), (
            f"Historical membership formula changed at {coordinate!r}."
        )
        assert grades == tuple(level["fSet"].mFunction.mju(coordinate) for level in legacy.levels)
        assert result.selectedTerms[0].name == legacy.Fuzzy(coordinate)["name"]


def test_PresetRetainsOrderImmutabilityAndSeparateWindows():
    """Keep windows separate from common term universes and mutable facade state."""

    scale = CreateUniversalFuzzyScale()
    domains = UniversalFuzzyScaleDomains()
    legacy = UniversalFuzzyScale()
    assert tuple(term.name for term in scale.terms) == ("Min", "Low", "Med", "High", "Max")
    assert tuple((domain.left, domain.right) for domain in domains) == tuple(level["fSet"].supportSet for level in legacy.levels)

    for term, domain, previous in zip(scale.terms, domains, legacy.levels, strict=True):
        assert term.fuzzySet.universe.Contains(0) and term.fuzzySet.universe.Contains(1)
        assert Centroid(term.fuzzySet, domain) == previous["fSet"].Defuz()

        with pytest.raises(FrozenInstanceError):
            term.name = "Changed"

    with pytest.raises(FrozenInstanceError):
        scale.terms = ()

    legacy.levels[0]["fSet"].mFunction.parameters = {"a": 1, "b": 2, "c": 0}
    assert scale.terms[0].fuzzySet.Membership(0.5) == pytest.approx(1 / (1 + 4**20), abs=0, rel=1e-15)


def test_PresetPreservesWeakCoverageAndDoesNotChangeGenericPolicy():
    """Keep the Min tail and strict confidence threshold visible to applications."""

    scale = CreateUniversalFuzzyScale()
    result = scale.Fuzzify(0.17, UniversalFuzzyScalePolicy())
    assert 0 < result.confidence < 0.003
    assert result.selectedTerms[0].name == "Min"
    assert not scale.Fuzzify(0.17, FuzzificationPolicy(minimumConfidence=0.1)).isMatch
    assert FuzzificationPolicy().tiePolicy == "first"
    duplicateScale = LinguisticScale((scale.terms[0], LinguisticTerm("Duplicate", scale.terms[0].fuzzySet)))
    assert duplicateScale.Fuzzify(0.125).selectedTerms[0].name == "Min"
    assert duplicateScale.Fuzzify(0.125, UniversalFuzzyScalePolicy()).selectedTerms[0].name == "Duplicate"
    assert UniversalFuzzyScalePolicy().tieTolerance == 0


@pytest.mark.parametrize("coordinate", (-0.1, 1.1, math.nextafter(0, -math.inf), math.nextafter(1, math.inf), math.nan, math.inf, -math.inf))
def test_PresetRejectsOutOfUniverseAndNonFiniteInput(coordinate):
    """Reject invalid normalized coordinates instead of clipping or extending them."""

    with pytest.raises(ValueError):
        CreateUniversalFuzzyScale().Fuzzify(coordinate, UniversalFuzzyScalePolicy())


@pytest.mark.parametrize("coordinate", (True, None, "0.5", 1j))
def test_PresetRejectsNonRealInput(coordinate):
    """Keep booleans and implicit string conversions outside the scalar contract."""

    with pytest.raises(TypeError):
        CreateUniversalFuzzyScale().Fuzzify(coordinate)
