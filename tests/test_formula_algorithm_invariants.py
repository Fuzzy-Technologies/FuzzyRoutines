# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Reference evidence for formula branches and numerical invariants."""

import math
import re
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

PROJECTROOT = Path(__file__).resolve().parents[1]
INVARIANTDOCUMENT = PROJECTROOT / "docs" / "mathematics" / "source-algorithm-invariants.md"


def test_SourceInvariantMapKeepsCanonicalLocalReferencesResolvable():
    document = INVARIANTDOCUMENT.read_text(encoding="utf-8")
    targets = re.findall(r"\[[^]]+\]\(([^)]+)\)", document)

    localTargets = tuple(target for target in targets if "://" not in target)

    assert localTargets

    for target in localTargets:
        assert (INVARIANTDOCUMENT.parent / target).resolve().is_file(), target


@pytest.mark.parametrize("alpha", [0.25, 0.5, 0.75])
@pytest.mark.parametrize("grade", [0.0, 0.125, 0.5, 0.875, 1.0])
def test_ParabolicNegationSatisfiesItsImplicitEquation(alpha, grade):
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
    with pytest.raises(ValueError):
        FuzzyNOTParabolic(0.5, invalidAlpha)


def test_LogisticStableBranchesMatchReferenceAndSaturateWithoutOverflow():
    membershipFunction = MFunction("logistic", a=2.0, b=1.0)

    assert membershipFunction.mju(1.0) == 0.5
    assert membershipFunction.mju(1.5) == pytest.approx(1 / (1 + math.exp(-1.0)))
    assert membershipFunction.mju(0.5) == pytest.approx(math.exp(-1.0) / (1 + math.exp(-1.0)))
    assert membershipFunction.mju(1e308) == 1.0
    assert membershipFunction.mju(-1e308) == 0.0


def test_HarringtonGuardMatchesFormulaAtBoundaryAndRejectsInvalidDomain():
    membershipFunction = MFunction("harringtonDesirability")
    overflowBoundary = -math.log(float.fromhex("0x1.fffffffffffffp+1023"))

    assert membershipFunction.mju(0.0) == pytest.approx(math.exp(-1.0))
    assert membershipFunction.mju(math.nextafter(overflowBoundary, -math.inf)) == 0.0
    assert membershipFunction.mju(overflowBoundary) == 0.0

    with pytest.raises(ValueError):
        membershipFunction.mju(math.nan)


def test_UniformSamplingRetainsExactEndpointsAndWeakBoundary():
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
    universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
    fuzzySet = ScalarFuzzySet(universe, lambda coordinate: coordinate)

    with pytest.raises((TypeError, ValueError)):
        SampleAlphaCut(fuzzySet, 0.5, IntegrationDomain(0.0, 1.0), invalidCount)
