"""Executable contracts for exact and sampled fuzzy-set properties."""

import math

import pytest

from fuzzyroutines import (
    ContinuousInterval,
    ContinuousRegion,
    ContinuousUniverse,
    DeriveProperties,
    DiscreteUniverse,
    IntegrationDomain,
    SampleProperties,
)
from fuzzyroutines.FuzzyRoutines import MFunction


def test_TrianglePropertiesDistinguishSupportClosureCoreAndBoundary():
    membershipFunction = MFunction("triangle", a=0.0, b=2.0, c=1.0)

    properties = DeriveProperties(membershipFunction, ContinuousUniverse())

    assert properties.isExact, "Analytical family geometry must be marked exact."
    assert properties.positiveSupport == ContinuousRegion((ContinuousInterval(0.0, 2.0),))
    assert properties.supportClosure == ContinuousRegion(
        (ContinuousInterval(0.0, 2.0, True, True),)
    )
    assert properties.core == ContinuousRegion((ContinuousInterval(1.0, 1.0, True, True),))
    assert properties.boundary == ContinuousRegion(
        (ContinuousInterval(0.0, 1.0), ContinuousInterval(1.0, 2.0))
    )
    assert properties.height == 1.0, "A triangle containing its apex must be normal."


def test_GaussianSupportRemainsRealLineDespiteFloatingPointUnderflow():
    membershipFunction = MFunction("gaussian", a=0.0, b=1.0)

    properties = DeriveProperties(membershipFunction, ContinuousUniverse())

    assert membershipFunction.mju(1.0e6) == 0.0, "The regression setup must reach float underflow."
    assert properties.positiveSupport.Contains(1.0e6), (
        "Analytical Gaussian support must not be inferred from underflowed evaluations."
    )
    assert properties.supportClosure == ContinuousRegion((ContinuousInterval(),))
    assert properties.core == ContinuousRegion((ContinuousInterval(0.0, 0.0, True, True),))
    assert properties.height == 1.0, "A Gaussian universe containing its centre must have height one."


def test_ShoulderPropertiesRetainUnboundedSupportAndCore():
    membershipFunction = MFunction("sShoulder", a=0.0, b=1.0)

    properties = DeriveProperties(membershipFunction, ContinuousUniverse())

    assert properties.positiveSupport == ContinuousRegion((ContinuousInterval(0.0, None),))
    assert properties.core == ContinuousRegion((ContinuousInterval(1.0, None, True, False),))
    assert properties.boundary == ContinuousRegion((ContinuousInterval(0.0, 1.0),))
    assert properties.height == 1.0, "The right shoulder attains full membership from b onward."


def test_LogisticCanHaveHeightOneWithAnEmptyCore():
    membershipFunction = MFunction("logistic", a=2.0, b=0.0)

    properties = DeriveProperties(membershipFunction, ContinuousUniverse())

    assert properties.core.isEmpty, "A logistic function never attains membership one at finite x."
    assert properties.boundary == ContinuousRegion((ContinuousInterval(),))
    assert properties.height == 1.0, "The logistic height is the supremum approached at +infinity."


def test_BoundedLogisticUniverseProducesANonNormalSet():
    membershipFunction = MFunction("logistic", a=2.0, b=0.0)
    universe = ContinuousUniverse(-1.0, 1.0, leftClosed=True, rightClosed=True)

    properties = DeriveProperties(membershipFunction, universe)

    assert properties.core.isEmpty, "No finite coordinate can enter the logistic core."
    assert properties.height == pytest.approx(membershipFunction.mju(1.0), abs=1e-12, rel=0.0)
    assert properties.height < 1.0, "A bounded logistic set must remain non-normal."


def test_UniverseOutsideTriangleProducesTheEmptyFuzzySet():
    membershipFunction = MFunction("triangle", a=0.0, b=2.0, c=1.0)
    universe = ContinuousUniverse(3.0, 4.0, leftClosed=True, rightClosed=True)

    properties = DeriveProperties(membershipFunction, universe)

    assert properties.positiveSupport.isEmpty, "A disjoint universe must have empty positive support."
    assert properties.supportClosure.isEmpty, "The relative support closure must also be empty."
    assert properties.core.isEmpty, "The empty fuzzy set has an empty core."
    assert properties.boundary.isEmpty, "The empty fuzzy set has no transition region."
    assert properties.height == 0.0, "The empty fuzzy set has height zero."


def test_RelativeSupportClosureDoesNotImportAnExternalLimitPoint():
    membershipFunction = MFunction("triangle", a=0.0, b=2.0, c=1.0)
    universe = ContinuousUniverse(2.0, 3.0, leftClosed=True, rightClosed=True)

    properties = DeriveProperties(membershipFunction, universe)

    assert properties.positiveSupport.isEmpty
    assert properties.supportClosure.isEmpty, (
        "closure_X(S intersect X) must stay empty when X contains no positive-support points."
    )


def test_OpenUniverseClipsRegionsWithoutLosingSupremum():
    membershipFunction = MFunction("triangle", a=0.0, b=2.0, c=1.0)
    universe = ContinuousUniverse(0.0, 1.0, leftClosed=False, rightClosed=False)

    properties = DeriveProperties(membershipFunction, universe)

    assert properties.core.isEmpty, "The excluded apex must not belong to the relative core."
    assert properties.height == 1.0, "Height is a supremum and need not be attained in the universe."
    assert not properties.positiveSupport.Contains(0.0), "The open universe must exclude its left endpoint."
    assert not properties.positiveSupport.Contains(1.0), "The open universe must exclude its right endpoint."


def test_DiscreteUniversePropertiesAreExactAtEveryDeclaredCoordinate():
    membershipFunction = MFunction("triangle", a=0.0, b=2.0, c=1.0)
    universe = DiscreteUniverse((0.0, 0.5, 1.0, 1.5, 2.0, 3.0))

    properties = DeriveProperties(membershipFunction, universe)

    assert properties.isExact, "A finite declared universe is evaluated exhaustively."
    assert properties.positiveSupport.points == (0.5, 1.0, 1.5)
    assert properties.supportClosure == properties.positiveSupport, (
        "Every subset is closed in the declared discrete topology."
    )
    assert properties.core.points == (1.0,)
    assert properties.boundary.points == (0.5, 1.5)
    assert properties.height == 1.0


def test_SampledContinuousQueryCarriesApproximationProvenance():
    membershipFunction = MFunction("gaussian", a=0.0, b=1.0)
    analysisDomain = IntegrationDomain(-2.0, 2.0)

    properties = SampleProperties(membershipFunction, analysisDomain, sampleCount=5)

    assert not properties.isExact, "A finite grid must never claim exact continuous geometry."
    assert properties.method == "uniform-grid"
    assert properties.analysisDomain is analysisDomain
    assert properties.sampleCount == 5
    assert properties.coordinates == (-2.0, -1.0, 0.0, 1.0, 2.0)
    assert properties.heightEstimate == 1.0
    assert properties.positiveSupportSamples.points == properties.coordinates


@pytest.mark.parametrize("sampleCount", [True, 1.5, "5"])
def test_SampledContinuousQueryRejectsNonIntegerCounts(sampleCount):
    with pytest.raises(TypeError, match="sampleCount"):
        SampleProperties(
            MFunction("gaussian", a=0.0, b=1.0),
            IntegrationDomain(-1.0, 1.0),
            sampleCount=sampleCount,
        )


def test_SampledContinuousQueryRequiresAtLeastTwoPoints():
    with pytest.raises(ValueError, match="at least two"):
        SampleProperties(
            MFunction("gaussian", a=0.0, b=1.0),
            IntegrationDomain(-1.0, 1.0),
            sampleCount=1,
        )


def test_AllAnalyticalFamiliesReturnValidDerivedPartitions():
    cases = (
        MFunction("hyperbolic", a=2.0, b=2.0, c=0.0),
        MFunction("bell", a=0.0, b=0.25, c=0.5),
        MFunction("parabolic", a=0.0, b=1.0),
        MFunction("triangle", a=0.0, b=1.0, c=0.5),
        MFunction("trapezium", a=0.0, b=1.0, c=0.25, d=0.75),
        MFunction("exponential", a=0.0, b=1.0),
        MFunction("sigmoidal", a=-2.0, b=0.0),
        MFunction("desirability"),
    )

    for membershipFunction in cases:
        properties = DeriveProperties(membershipFunction, ContinuousUniverse())

        assert 0.0 <= properties.height <= 1.0, (
            f"{membershipFunction.name} height must remain within the membership codomain."
        )
        assert properties.isExact, (
            f"{membershipFunction.name} must use declared geometry instead of a sample scan."
        )


def test_ContinuousIntervalsRejectEmptyOrInvalidComponents():
    with pytest.raises(ValueError, match="singleton"):
        ContinuousInterval(1.0, 1.0)

    with pytest.raises(ValueError, match="left <= right"):
        ContinuousInterval(2.0, 1.0, True, True)

    with pytest.raises(ValueError, match="cannot be closed"):
        ContinuousInterval(None, 1.0, True, True)


def test_DerivationRejectsUnknownUniverseObjects():
    with pytest.raises(TypeError, match="universe"):
        DeriveProperties(MFunction("gaussian", a=0.0, b=1.0), object())


def test_DerivationDoesNotTreatNaNAsAValidMembershipGrade():
    membershipFunction = MFunction("gaussian", a=0.0, b=1.0)
    membershipFunction.mju = lambda coordinate: math.nan

    with pytest.raises(ValueError, match="finite real number"):
        DeriveProperties(membershipFunction, DiscreteUniverse((0.0, 1.0)))
