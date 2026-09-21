# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Contracts for exact and tolerance-based fuzzy-set relations."""

import math

import pytest

from fuzzyroutines import (
    ComparisonDomain,
    ComparisonPolicy,
    ContinuousUniverse,
    DiscreteUniverse,
    EqualOnDomain,
    IncludedOnDomain,
    ScalarFuzzySet,
)


def BuildDiscreteSet(points, grades):
    """Build a discrete fuzzy set from an explicit coordinate-to-grade map."""

    gradeByPoint = dict(zip(points, grades, strict=True))
    return ScalarFuzzySet(DiscreteUniverse(points), gradeByPoint.__getitem__)


def BuildContinuousSet(membershipFunction):
    """Build a continuous set over the canonical closed unit universe."""

    return ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True),
        membershipFunction,
    )


def test_ExactDiscreteEqualityIsExhaustiveAcrossNonIdenticalRepresentations():
    leftSet = BuildDiscreteSet((0.0, 0.5, 1.0), (0.0, 0.5, 1.0))
    rightSet = ScalarFuzzySet(leftSet.universe, lambda coordinate: coordinate)

    assert EqualOnDomain(leftSet, rightSet, ComparisonPolicy("exact")), (
        "Equivalent memberships must compare equal independently of callable identity."
    )


def test_PythonObjectEqualityDoesNotMasqueradeAsMathematicalSetEquality():
    universe = DiscreteUniverse((0.0, 1.0))
    membershipFunction = lambda coordinate: coordinate
    leftSet = ScalarFuzzySet(universe, membershipFunction)
    rightSet = ScalarFuzzySet(universe, membershipFunction)

    assert leftSet is not rightSet
    assert leftSet != rightSet, (
        "ScalarFuzzySet object equality must remain identity-based; callers must select relation semantics."
    )
    assert EqualOnDomain(leftSet, rightSet, ComparisonPolicy("exact"))


def test_ExactDiscreteEqualityRejectsOneDifferentGrade():
    leftSet = BuildDiscreteSet((0.0, 0.5, 1.0), (0.0, 0.5, 1.0))
    rightSet = BuildDiscreteSet((0.0, 0.5, 1.0), (0.0, 0.4, 1.0))

    assert not EqualOnDomain(leftSet, rightSet, ComparisonPolicy("exact")), (
        "Exact equality must reject any unequal membership grade."
    )


def test_ExactDiscreteInclusionUsesThePointwiseFuzzyRelation():
    subset = BuildDiscreteSet((0.0, 0.5, 1.0), (0.0, 0.25, 0.75))
    superset = BuildDiscreteSet((0.0, 0.5, 1.0), (0.0, 0.5, 1.0))
    policy = ComparisonPolicy("exact")

    assert IncludedOnDomain(subset, superset, policy)
    assert not IncludedOnDomain(superset, subset, policy)


def test_ExactDiscreteRelationsSatisfyReflexivityAndAntisymmetry():
    firstSet = BuildDiscreteSet((0.0, 0.5, 1.0), (0.0, 0.4, 1.0))
    equivalentSet = BuildDiscreteSet((0.0, 0.5, 1.0), (0.0, 0.4, 1.0))
    policy = ComparisonPolicy("exact")

    assert EqualOnDomain(firstSet, firstSet, policy)
    assert IncludedOnDomain(firstSet, firstSet, policy)
    assert IncludedOnDomain(firstSet, equivalentSet, policy)
    assert IncludedOnDomain(equivalentSet, firstSet, policy)
    assert EqualOnDomain(firstSet, equivalentSet, policy), (
        "Mutual exact inclusion must imply equality on the evaluated domain."
    )


def test_ToleranceEqualityAcceptsOnlyDifferencesInsideTheExplicitPolicy():
    leftSet = BuildDiscreteSet((0.0, 1.0), (0.25, 0.75))
    closeSet = BuildDiscreteSet((0.0, 1.0), (0.2500001, 0.7499999))
    distantSet = BuildDiscreteSet((0.0, 1.0), (0.251, 0.749))
    policy = ComparisonPolicy("tolerance", absoluteTolerance=1e-6, relativeTolerance=0.0)

    assert EqualOnDomain(leftSet, closeSet, policy)
    assert not EqualOnDomain(leftSet, distantSet, policy)


def test_RelativeToleranceIsAppliedWhenExplicitlyConfigured():
    leftSet = BuildDiscreteSet((0.0, 1.0), (0.5, 1.0))
    closeSet = BuildDiscreteSet((0.0, 1.0), (0.5004, 0.9996))
    distantSet = BuildDiscreteSet((0.0, 1.0), (0.501, 0.999))
    policy = ComparisonPolicy("tolerance", absoluteTolerance=0.0, relativeTolerance=1e-3)

    assert EqualOnDomain(leftSet, closeSet, policy)
    assert not EqualOnDomain(leftSet, distantSet, policy)


def test_ToleranceInclusionAllowsOnlyNumericallyCloseViolations():
    nominalSet = BuildDiscreteSet((0.0, 1.0), (0.25, 0.75))
    closeHigherSet = BuildDiscreteSet((0.0, 1.0), (0.2500001, 0.7500001))
    distantHigherSet = BuildDiscreteSet((0.0, 1.0), (0.251, 0.751))
    policy = ComparisonPolicy("tolerance", absoluteTolerance=1e-6, relativeTolerance=0.0)

    assert IncludedOnDomain(closeHigherSet, nominalSet, policy)
    assert not IncludedOnDomain(distantHigherSet, nominalSet, policy)


def test_ContinuousRelationsRequireAnExplicitComparisonDomain():
    leftSet = BuildContinuousSet(lambda coordinate: coordinate)
    rightSet = BuildContinuousSet(lambda coordinate: coordinate)

    with pytest.raises(ValueError, match="explicit ComparisonDomain"):
        EqualOnDomain(leftSet, rightSet, ComparisonPolicy("exact"))

    with pytest.raises(ValueError, match="explicit ComparisonDomain"):
        IncludedOnDomain(leftSet, rightSet, ComparisonPolicy("exact"))


def test_ContinuousEqualityComparesEquivalentBehaviorOnlyOnDeclaredPoints():
    leftSet = BuildContinuousSet(lambda coordinate: coordinate * coordinate)
    rightSet = BuildContinuousSet(lambda coordinate: coordinate**2)
    comparisonDomain = ComparisonDomain((0.0, 0.25, 0.5, 0.75, 1.0))

    assert EqualOnDomain(
        leftSet,
        rightSet,
        ComparisonPolicy("exact"),
        comparisonDomain,
    ), "Different callable representations may be equivalent on the declared sample points."


def test_ContinuousInclusionEvaluatesEveryDeclaredPoint():
    subset = BuildContinuousSet(lambda coordinate: coordinate / 2)
    superset = BuildContinuousSet(lambda coordinate: coordinate)
    comparisonDomain = ComparisonDomain((0.0, 0.25, 0.5, 0.75, 1.0))

    assert IncludedOnDomain(
        subset,
        superset,
        ComparisonPolicy("exact"),
        comparisonDomain,
    )
    assert not IncludedOnDomain(
        superset,
        subset,
        ComparisonPolicy("exact"),
        comparisonDomain,
    )


@pytest.mark.parametrize(
    "points",
    [
        (),
        (0.0, 0.0),
        (1.0, 0.0),
        (0.0, math.nan),
        (0.0, math.inf),
    ],
)
def test_ComparisonDomainRejectsEmptyUnorderedDuplicateOrNonFinitePoints(points):
    with pytest.raises((TypeError, ValueError)):
        ComparisonDomain(points)


def test_ComparisonDomainRequiresAnExplicitTuple():
    with pytest.raises(TypeError, match="tuple"):
        ComparisonDomain([0.0, 1.0])


def test_ComparisonDomainMustLieInsideTheContinuousUniverse():
    leftSet = BuildContinuousSet(lambda coordinate: coordinate)
    rightSet = BuildContinuousSet(lambda coordinate: coordinate)

    with pytest.raises(ValueError, match="belong"):
        EqualOnDomain(
            leftSet,
            rightSet,
            ComparisonPolicy("exact"),
            ComparisonDomain((-0.1, 0.5, 1.0)),
        )


def test_DiscreteRelationsRejectPartialComparisonDomains():
    leftSet = BuildDiscreteSet((0.0, 0.5, 1.0), (0.0, 0.5, 1.0))
    rightSet = BuildDiscreteSet((0.0, 0.5, 1.0), (0.0, 0.5, 1.0))

    with pytest.raises(ValueError, match="complete universe"):
        EqualOnDomain(
            leftSet,
            rightSet,
            ComparisonPolicy("exact"),
            ComparisonDomain((0.0, 1.0)),
        )


def test_RelationsFailClosedForDifferentUniverses():
    leftSet = BuildDiscreteSet((0.0, 1.0), (0.0, 1.0))
    rightSet = BuildDiscreteSet((0.0, 0.5, 1.0), (0.0, 0.5, 1.0))

    with pytest.raises(ValueError, match="equal universes"):
        EqualOnDomain(leftSet, rightSet, ComparisonPolicy("exact"))

    with pytest.raises(ValueError, match="equal universes"):
        IncludedOnDomain(leftSet, rightSet, ComparisonPolicy("exact"))


@pytest.mark.parametrize(
    ("mode", "absoluteTolerance", "relativeTolerance", "errorType"),
    [
        ("unknown", None, None, ValueError),
        ("exact", 0.0, None, ValueError),
        ("exact", None, 0.0, ValueError),
        ("tolerance", None, 0.0, TypeError),
        ("tolerance", 0.0, None, TypeError),
        ("tolerance", -1e-6, 0.0, ValueError),
        ("tolerance", 0.0, -1e-6, ValueError),
        ("tolerance", 0.0, 0.0, ValueError),
        ("tolerance", math.inf, 0.0, ValueError),
        ("tolerance", 0.0, True, TypeError),
    ],
)
def test_ComparisonPolicyRejectsAmbiguousOrInvalidConfiguration(
    mode,
    absoluteTolerance,
    relativeTolerance,
    errorType,
):
    with pytest.raises(errorType):
        ComparisonPolicy(mode, absoluteTolerance, relativeTolerance)


def test_RelationsRequireAnExplicitComparisonPolicyObject():
    leftSet = BuildDiscreteSet((0.0, 1.0), (0.0, 1.0))
    rightSet = BuildDiscreteSet((0.0, 1.0), (0.0, 1.0))

    with pytest.raises(TypeError, match="ComparisonPolicy"):
        EqualOnDomain(leftSet, rightSet, None)

    with pytest.raises(TypeError, match="ComparisonPolicy"):
        IncludedOnDomain(leftSet, rightSet, None)


@pytest.mark.parametrize("invalidGrade", [-0.1, 1.1, math.nan, math.inf, True])
def test_ComparisonPolicyRejectsInvalidDirectGradeEvaluation(invalidGrade):
    policy = ComparisonPolicy("exact")

    with pytest.raises((TypeError, ValueError)):
        policy.Equal(invalidGrade, 0.5)

    with pytest.raises((TypeError, ValueError)):
        policy.Included(0.5, invalidGrade)
