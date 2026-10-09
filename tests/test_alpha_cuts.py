# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Executable contracts for exact and sampled weak alpha-cuts."""

import math
from dataclasses import FrozenInstanceError
from itertools import pairwise

import pytest

from fuzzyroutines import (
    AlphaCut,
    ContinuousUniverse,
    DiscreteRegion,
    DiscreteUniverse,
    IntegrationDomain,
    SampleAlphaCut,
    SampledAlphaCut,
    ScalarFuzzySet,
)


def BuildDiscreteSet(points, grades):
    """Build a discrete scalar fuzzy set from aligned point and grade tuples."""

    gradeByPoint = dict(zip(points, grades, strict=True))
    return ScalarFuzzySet(DiscreteUniverse(points), gradeByPoint.__getitem__)


def BuildContinuousSet(membershipFunction):
    """Build a continuous set on the closed unit interval."""

    return ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True),
        membershipFunction,
    )


def test_AlphaCutUsesWeakBoundaryConvention():
    """Verify that alpha cut uses weak boundary convention."""

    fuzzySet = BuildDiscreteSet(
        (0.0, 0.25, 0.5, 0.75, 1.0),
        (0.0, 0.49, 0.5, 0.51, 1.0),
    )

    cut = AlphaCut(fuzzySet, 0.5)

    assert cut == DiscreteRegion((0.5, 0.75, 1.0)), (
        "A coordinate exactly on alpha must belong to the weak alpha-cut."
    )


def test_AlphaZeroIsTheCompleteDeclaredDiscreteUniverse():
    """Verify that alpha zero is the complete declared discrete universe."""

    fuzzySet = BuildDiscreteSet((-1.0, 0.0, 1.0), (0.0, 0.4, 1.0))

    assert AlphaCut(fuzzySet, 0).points == fuzzySet.universe.points, (
        "Every valid membership grade is at least zero, so A_0 must equal X."
    )


def test_AlphaOneIsTheExactDiscreteCore():
    """Verify that alpha one is the exact discrete core."""

    fuzzySet = BuildDiscreteSet((-1.0, 0.0, 1.0), (0.999999999, 1.0, 0.0))

    assert AlphaCut(fuzzySet, 1).points == (0.0,), (
        "A_1 must include only grades exactly equal to one; no tolerance is implicit."
    )


def test_ExactDiscreteAlphaCutsAreNested():
    """Verify that exact discrete alpha cuts are nested."""

    fuzzySet = BuildDiscreteSet(
        (0.0, 0.25, 0.5, 0.75, 1.0),
        (0.0, 0.25, 0.5, 0.75, 1.0),
    )
    thresholds = (0.0, 0.25, 0.5, 0.75, 1.0)
    cuts = tuple(set(AlphaCut(fuzzySet, alpha).points) for alpha in thresholds)

    for lowerCut, higherCut in pairwise(cuts):
        assert higherCut <= lowerCut, (
            "For beta >= alpha, the invariant A_beta subseteq A_alpha must hold."
        )


def test_ExactAlphaCutFailsClosedForContinuousCallables():
    """Verify that exact alpha cut fails closed for continuous callables."""

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate)

    with pytest.raises(TypeError, match="exact alpha cuts require a DiscreteUniverse"):
        AlphaCut(fuzzySet, 0.5)


def test_SampledContinuousCutRecordsBoundaryAndProvenance():
    """Verify that sampled continuous cut records boundary and provenance."""

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate)
    analysisDomain = IntegrationDomain(0.0, 1.0)

    cut = SampleAlphaCut(fuzzySet, 0.5, analysisDomain, sampleCount=5)

    assert cut == SampledAlphaCut(
        alpha=0.5,
        analysisDomain=analysisDomain,
        sampleCount=5,
        coordinates=(0.0, 0.25, 0.5, 0.75, 1.0),
        grades=(0.0, 0.25, 0.5, 0.75, 1.0),
        cutSamples=DiscreteRegion((0.5, 0.75, 1.0)),
    )
    assert cut.method == "uniform-grid"
    assert not cut.isExact, "A finite grid must never claim exact continuous geometry."


def test_SampledAlphaZeroAndOneSemanticsAreExplicitlyLimitedToTheGrid():
    """Verify that sampled alpha zero and one semantics are explicitly limited to the
    grid.
    """

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate)
    analysisDomain = IntegrationDomain(0.0, 1.0)

    zeroCut = SampleAlphaCut(fuzzySet, 0.0, analysisDomain, sampleCount=3)
    oneCut = SampleAlphaCut(fuzzySet, 1.0, analysisDomain, sampleCount=3)

    assert zeroCut.cutSamples.points == zeroCut.coordinates, (
        "Every valid sampled grade belongs to the sampled zero-cut."
    )
    assert oneCut.cutSamples.points == (1.0,), (
        "The sampled one-cut must retain only observed grades exactly equal to one."
    )


def test_SampledAlphaCutsAreNestedOnTheSameGrid():
    """Verify that sampled alpha cuts are nested on the same grid."""

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate * coordinate)
    analysisDomain = IntegrationDomain(0.0, 1.0)
    thresholds = (0.0, 0.25, 0.5, 0.75, 1.0)
    cuts = tuple(
        set(SampleAlphaCut(fuzzySet, alpha, analysisDomain, sampleCount=9).cutSamples.points)
        for alpha in thresholds
    )

    for lowerCut, higherCut in pairwise(cuts):
        assert higherCut <= lowerCut, (
            "Sampled weak cuts on an identical grid must preserve alpha-cut nesting."
        )


@pytest.mark.parametrize("alpha", [-0.1, 1.1, math.nan, math.inf, True, "0.5"])
def test_AlphaCutRejectsInvalidThresholds(alpha):
    """Verify that alpha cut rejects invalid thresholds."""

    fuzzySet = BuildDiscreteSet((0.0, 1.0), (0.0, 1.0))

    with pytest.raises((TypeError, ValueError)):
        AlphaCut(fuzzySet, alpha)


@pytest.mark.parametrize("invalidGrade", [-0.1, 1.1, math.nan, math.inf, True])
def test_ExactAlphaCutFailsClosedForInvalidMembershipGrades(invalidGrade):
    """Verify that exact alpha cut fails closed for invalid membership grades."""

    fuzzySet = BuildDiscreteSet((0.0, 1.0), (0.0, invalidGrade))

    with pytest.raises((TypeError, ValueError)):
        AlphaCut(fuzzySet, 0.0)


@pytest.mark.parametrize("invalidGrade", [-0.1, 1.1, math.nan, math.inf, True])
def test_SampledAlphaCutFailsClosedForInvalidMembershipGrades(invalidGrade):
    """Verify that sampled alpha cut fails closed for invalid membership grades."""

    fuzzySet = BuildContinuousSet(
        lambda coordinate: invalidGrade if coordinate == 0.5 else coordinate
    )

    with pytest.raises((TypeError, ValueError)):
        SampleAlphaCut(fuzzySet, 0.0, IntegrationDomain(0.0, 1.0), sampleCount=3)


@pytest.mark.parametrize("sampleCount", [True, 1.5, "5"])
def test_SampledAlphaCutRejectsNonIntegerCounts(sampleCount):
    """Verify that sampled alpha cut rejects noninteger counts."""

    with pytest.raises(TypeError, match="sampleCount"):
        SampleAlphaCut(
            BuildContinuousSet(lambda coordinate: coordinate),
            0.5,
            IntegrationDomain(0.0, 1.0),
            sampleCount=sampleCount,
        )


def test_SampledAlphaCutRequiresAtLeastTwoPoints():
    """Verify that sampled alpha cut requires at least two points."""

    with pytest.raises(ValueError, match="at least two"):
        SampleAlphaCut(
            BuildContinuousSet(lambda coordinate: coordinate),
            0.5,
            IntegrationDomain(0.0, 1.0),
            sampleCount=1,
        )


def test_SampledAlphaCutDomainMustLieInsideTheContinuousUniverse():
    """Verify that sampled alpha cut domain must lie inside the continuous universe."""

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate)

    with pytest.raises(ValueError, match="entirely within"):
        SampleAlphaCut(
            fuzzySet,
            0.5,
            IntegrationDomain(-0.1, 1.0),
            sampleCount=3,
        )


def test_SampledAlphaCutRejectsDiscreteUniverses():
    """Verify that sampled alpha cut rejects discrete universes."""

    fuzzySet = BuildDiscreteSet((0.0, 1.0), (0.0, 1.0))

    with pytest.raises(TypeError, match="ContinuousUniverse"):
        SampleAlphaCut(fuzzySet, 0.5, IntegrationDomain(0.0, 1.0), sampleCount=3)


def test_AlphaCutOperationsRequireScalarFuzzySets():
    """Verify that alpha cut operations require scalar fuzzy sets."""

    with pytest.raises(TypeError, match="ScalarFuzzySet"):
        AlphaCut(object(), 0.5)

    with pytest.raises(TypeError, match="ScalarFuzzySet"):
        SampleAlphaCut(object(), 0.5, IntegrationDomain(0.0, 1.0))


def test_SampledAlphaCutResultIsImmutable():
    """Verify that sampled alpha cut result is immutable."""

    cut = SampleAlphaCut(
        BuildContinuousSet(lambda coordinate: coordinate),
        0.5,
        IntegrationDomain(0.0, 1.0),
        sampleCount=3,
    )

    with pytest.raises(FrozenInstanceError):
        cut.alpha = 0.25
