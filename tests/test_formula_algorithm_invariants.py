# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Reference evidence for formula branches and numerical invariants."""

import math
import re
from fractions import Fraction
from pathlib import Path

import pytest

from fuzzyroutines import (
    ContinuousUniverse,
    IntegrationDomain,
    NegationPolicy,
    SampleAlphaCut,
    ScalarFuzzySet,
)
from fuzzyroutines.FuzzyRoutines import FuzzyNOTParabolic, MFunction
from fuzzyroutines.membership import Gaussian, Logistic, Trapezoid, Triangle

PROJECTROOT = Path(__file__).resolve().parents[1]
INVARIANTDOCUMENT = PROJECTROOT / "docs" / "mathematics" / "source-algorithm-invariants.md"


def test_SourceInvariantMapKeepsCanonicalLocalReferencesResolvable():
    """Verify that source invariant map keeps canonical local references resolvable."""

    document = INVARIANTDOCUMENT.read_text(encoding="utf-8")
    targets = re.findall(r"\[[^]]+\]\(([^)]+)\)", document)

    localTargets = tuple(target for target in targets if "://" not in target)

    assert localTargets

    for target in localTargets:
        assert (INVARIANTDOCUMENT.parent / target).resolve().is_file(), target


@pytest.mark.parametrize("alpha", [0.25, 0.5, 0.75])
@pytest.mark.parametrize("grade", [0.0, 0.125, 0.5, 0.875, 1.0])
def test_ParabolicNegationSatisfiesItsImplicitEquation(alpha, grade):
    """Verify that parabolic negation satisfies its implicit equation."""

    result = FuzzyNOTParabolic(grade, alpha)

    leftSide = 2 * alpha - grade - result
    rightSide = (2 * alpha - 1) * (result - grade) ** 2

    assert result == pytest.approx(
        NegationPolicy("parabolic", alpha).Evaluate(grade),
        abs=1e-15,
        rel=0.0,
    )
    assert leftSide == pytest.approx(rightSide, abs=1e-15, rel=0.0)


@pytest.mark.parametrize("invalidAlpha", [math.nan, -math.inf, 0.249999, 0.750001, math.inf])
def test_ParabolicNegationRejectsValuesOutsideDerivedAlphaDomain(invalidAlpha):
    """Verify that parabolic negation rejects values outside derived alpha domain."""

    with pytest.raises(ValueError):
        FuzzyNOTParabolic(0.5, invalidAlpha)


def test_LogisticStableBranchesMatchReferenceAndSaturateWithoutOverflow():
    """Verify that logistic stable branches match reference and saturate without overflow."""

    membershipFunction = MFunction("logistic", a=2.0, b=1.0)

    assert membershipFunction.mju(1.0) == 0.5
    assert membershipFunction.mju(1.5) == pytest.approx(1 / (1 + math.exp(-1.0)))
    assert membershipFunction.mju(0.5) == pytest.approx(math.exp(-1.0) / (1 + math.exp(-1.0)))
    assert membershipFunction.mju(1e308) == 1.0
    assert membershipFunction.mju(-1e308) == 0.0


@pytest.mark.parametrize('apiKind', ["modern", "legacy"])
@pytest.mark.parametrize(
    ("family", "coordinates", 'expectedGrades'),
    [
        ("triangle_rising", (0.0, 5e307, 1e308), (0.5, 0.75, 1.0)),
        ("triangle_falling", (0.0, 7.5e307), (0.5, 0.25)),
        ("trapezoid_rising", (0.0, 5e307), (0.5, 0.75)),
        ("trapezoid_falling", (0.0, 5e307), (0.5, 0.25)),
    ],
)
def test_ExtremeLinearRampsPreserveFiniteRatios(apiKind, family, coordinates, expectedGrades):
    """Opposite extreme endpoints retain the independently known ramp grades."""

    modernFunctions = {
        "triangle_rising": Triangle(-1e308, 1e308, 1e308),
        "triangle_falling": Triangle(-1.7e308, -1.5e308, 1.5e308),
        "trapezoid_rising": Trapezoid(-1e308, 1e308, 1.2e308, 1.5e308),
        "trapezoid_falling": Trapezoid(-1.5e308, -1.2e308, -1e308, 1e308),
    }
    legacyFunctions = {
        "triangle_rising": MFunction("triangle", a=-1e308, b=1e308, c=1e308),
        "triangle_falling": MFunction("triangle", a=-1.7e308, b=1.5e308, c=-1.5e308),
        "trapezoid_rising": MFunction("trapezium", a=-1e308, b=1.5e308, c=1e308, d=1.2e308),
        "trapezoid_falling": MFunction("trapezium", a=-1.5e308, b=1e308, c=-1.2e308, d=-1e308),
    }
    evaluator = modernFunctions[family] if apiKind == "modern" else legacyFunctions[family].mju

    for coordinate, expectedGrade in zip(coordinates, expectedGrades, strict=True):
        actualGrade = evaluator(coordinate)
        assert math.isfinite(actualGrade), "A finite linear ramp must not return NaN"
        assert actualGrade == pytest.approx(expectedGrade), "Endpoint subtraction lost the ramp ratio"


@pytest.mark.parametrize('apiKind', ["modern", "legacy"])
@pytest.mark.parametrize("center", [-1e308, 1e308])
def test_GaussianExtremeDifferencePreservesTwoSigmaGrade(apiKind, center):
    """A two-standard-deviation distance stays positive despite raw overflow."""

    evaluator = (
        Gaussian(center, 1e308)
        if apiKind == "modern"
        else MFunction("gaussian", a=center, b=1e308).mju
    )
    actualGrade = evaluator(-center)

    assert actualGrade == pytest.approx(math.exp(-2.0)), "Two-sigma Gaussian grade was lost to overflow"


@pytest.mark.parametrize('apiKind', ["modern", "legacy"])
@pytest.mark.parametrize("midpoint", [-1e308, 1e308])
@pytest.mark.parametrize("slope", [-1e-308, 1e-308])
def test_LogisticExtremeDifferencePreservesFiniteExponent(apiKind, midpoint, slope):
    """Small slopes preserve the finite signed exponent across extreme inputs."""

    evaluator = (
        Logistic(slope, midpoint)
        if apiKind == "modern"
        else MFunction("logistic", a=slope, b=midpoint).mju
    )
    expectedExponent = -2.0 if (midpoint > 0) == (slope > 0) else 2.0
    expectedGrade = 1 / (1 + math.exp(-expectedExponent))

    assert evaluator(-midpoint) == pytest.approx(expectedGrade), "Finite logistic exponent incorrectly saturated"


def test_ExtremeRationalParametersRetainTheirExactDifferenceArithmetic():
    """Registered real inputs need no float conversion merely to detect infinity."""

    magnitude = Fraction(10**308)
    triangle = Triangle(-magnitude, magnitude, magnitude)
    gaussian = Gaussian(-magnitude, magnitude)
    logistic = Logistic(1 / magnitude, -magnitude)

    assert triangle(Fraction(0)) == Fraction(1, 2), "Exact rational ramp arithmetic changed"
    assert gaussian(magnitude) == pytest.approx(math.exp(-2.0))
    assert logistic(magnitude) == pytest.approx(1 / (1 + math.exp(-2.0)))


def test_HarringtonGuardMatchesFormulaAtBoundaryAndRejectsInvalidDomain():
    """Verify that harrington guard matches formula at boundary and rejects invalid
    domain.
    """

    membershipFunction = MFunction("harringtonDesirability")
    overflowBoundary = -math.log(float.fromhex("0x1.fffffffffffffp+1023"))

    assert membershipFunction.mju(0.0) == pytest.approx(math.exp(-1.0))
    assert membershipFunction.mju(math.nextafter(overflowBoundary, -math.inf)) == 0.0
    assert membershipFunction.mju(overflowBoundary) == 0.0

    with pytest.raises(ValueError):
        membershipFunction.mju(math.nan)


@pytest.mark.parametrize(
    ("functionName", "parameters", "coordinate"),
    [
        ("hyperbolic", {"a": 1.0, "b": 2.0, "c": 0.0}, 1e308),
        ("bell", {"a": -1e308, "b": 0.0, "c": 1e308}, 1.5e308),
        ("parabolic", {"a": -1e308, "b": 1e308}, 0.0),
    ],
)
def test_HistoricalDirectFormulasExposeExtremeIntermediateOverflow(
    functionName,
    parameters,
    coordinate,
):
    """Verify that historical direct formulas expose extreme intermediate overflow."""

    membershipFunction = MFunction(functionName, **parameters)

    with pytest.raises(OverflowError):
        membershipFunction.mju(coordinate)


def test_UniformSamplingRetainsExactEndpointsAndWeakBoundary():
    """Verify that uniform sampling retains exact endpoints and weak boundary."""

    universe = ContinuousUniverse(0.1, 0.9, leftClosed=True, rightClosed=True)
    fuzzySet = ScalarFuzzySet(universe, lambda coordinate: coordinate)
    analysisDomain = IntegrationDomain(0.1, 0.9)

    sampledCut = SampleAlphaCut(fuzzySet, 0.5, analysisDomain, sampleCount=7)

    assert sampledCut.coordinates[0] == analysisDomain.left
    assert sampledCut.coordinates[-1] == analysisDomain.right
    assert sampledCut.cutSamples.points == tuple(
        coordinate
        for coordinate, grade in zip(sampledCut.coordinates, sampledCut.grades, strict=True)
        if grade >= 0.5
    )


@pytest.mark.parametrize("invalidCount", [True, 1, 2.5])
def test_UniformSamplingRejectsInvalidResolution(invalidCount):
    """Verify that uniform sampling rejects invalid resolution."""

    universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
    fuzzySet = ScalarFuzzySet(universe, lambda coordinate: coordinate)

    with pytest.raises((TypeError, ValueError)):
        SampleAlphaCut(fuzzySet, 0.5, IntegrationDomain(0.0, 1.0), invalidCount)
