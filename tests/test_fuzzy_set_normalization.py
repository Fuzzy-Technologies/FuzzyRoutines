"""Executable contracts for exact height queries and normalization."""

from dataclasses import FrozenInstanceError

import pytest

from fuzzyroutines import (
    ContinuousUniverse,
    DiscreteUniverse,
    Height,
    IsNormal,
    Normalize,
    ScalarFuzzySet,
)
from fuzzyroutines.FuzzyRoutines import MFunction


def test_DiscreteHeightEvaluatesEveryDeclaredCoordinateExactlyOnce():
    universe = DiscreteUniverse((-1.0, 0.0, 1.0, 2.0))
    evaluations = []

    def MembershipFunction(coordinate):
        """Record exhaustive evaluation without relying on sample inference."""

        evaluations.append(coordinate)
        return {-1.0: 0.0, 0.0: 0.25, 1.0: 0.75, 2.0: 0.5}[coordinate]

    fuzzySet = ScalarFuzzySet(universe, MembershipFunction)

    assert Height(fuzzySet) == 0.75
    assert evaluations == list(universe.points), (
        "Discrete height must inspect every coordinate exactly once in universe order."
    )


def test_DiscreteNormalizationProducesExactHeightOneWithoutMutatingSource():
    universe = DiscreteUniverse((0.0, 1.0, 2.0))
    fuzzySet = ScalarFuzzySet(universe, lambda coordinate: (0.2, 0.4, 0.1)[int(coordinate)])
    originalGrades = tuple(fuzzySet.Membership(point) for point in universe.points)

    normalizedSet = Normalize(fuzzySet)

    assert normalizedSet is not fuzzySet, "Normalization must construct a distinct immutable value."
    assert normalizedSet.universe is universe
    assert tuple(fuzzySet.Membership(point) for point in universe.points) == originalGrades, (
        "Normalization must not alter source membership grades."
    )
    assert tuple(normalizedSet.Membership(point) for point in universe.points) == pytest.approx(
        (0.5, 1.0, 0.25),
        abs=1e-12,
        rel=0.0,
    )
    assert Height(normalizedSet) == 1.0
    assert IsNormal(normalizedSet), "The normalized set must carry exact height-one evidence."

    with pytest.raises(FrozenInstanceError):
        normalizedSet.universe = DiscreteUniverse((0.0,))


def test_DiscreteNormalizationSnapshotsEveryGradeExactlyOnce():
    universe = DiscreteUniverse((0.0, 1.0, 2.0))
    evaluationCount = 0

    def MembershipFunction(coordinate):
        """Count source evaluations used to build the normalized snapshot."""

        nonlocal evaluationCount
        evaluationCount += 1
        return (0.25, 0.5, 0.125)[int(coordinate)]

    normalizedSet = Normalize(ScalarFuzzySet(universe, MembershipFunction))

    assert evaluationCount == len(universe.points), (
        "Discrete normalization must inspect every declared grade exactly once."
    )
    assert normalizedSet.Membership(0.0) == 0.5
    assert normalizedSet.Membership(1.0) == 1.0
    assert evaluationCount == len(universe.points), (
        "The normalized discrete set must use its stable exhaustive snapshot."
    )


def test_NormalizationRejectsZeroHeightExplicitly():
    fuzzySet = ScalarFuzzySet(DiscreteUniverse((0.0, 1.0)), lambda coordinate: 0.0)

    with pytest.raises(ValueError, match="zero-height"):
        Normalize(fuzzySet)


def test_ContinuousNormalizationRejectsAnalyticallyProvedZeroHeight():
    membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
    fuzzySet = ScalarFuzzySet(
        ContinuousUniverse(2.0, 3.0, leftClosed=True, rightClosed=True),
        membershipFunction.mju,
    )

    assert Height(fuzzySet) == 0.0

    with pytest.raises(ValueError, match="zero-height"):
        Normalize(fuzzySet)


def test_ContinuousAnalyticalHeightReusesDerivedPropertyContract():
    membershipFunction = MFunction("logistic", a=2.0, b=0.0)
    universe = ContinuousUniverse(-1.0, 1.0, leftClosed=True, rightClosed=True)
    fuzzySet = ScalarFuzzySet(universe, membershipFunction.mju)

    assert Height(fuzzySet) == pytest.approx(
        membershipFunction.mju(1.0),
        abs=1e-12,
        rel=0.0,
    )
    assert not IsNormal(fuzzySet)

    normalizedSet = Normalize(fuzzySet)

    assert normalizedSet.Membership(1.0) == pytest.approx(1.0, abs=1e-12, rel=0.0)
    assert Height(normalizedSet) == 1.0
    assert IsNormal(normalizedSet)


def test_ContinuousNormalizationSnapshotsMutableAnalyticalParameters():
    membershipFunction = MFunction("logistic", a=2.0, b=0.0)
    universe = ContinuousUniverse(-1.0, 1.0, leftClosed=True, rightClosed=True)
    fuzzySet = ScalarFuzzySet(universe, membershipFunction.mju)
    normalizedSet = Normalize(fuzzySet)
    normalizedGrades = tuple(normalizedSet.Membership(point) for point in (-1.0, 0.0, 1.0))

    membershipFunction.parameters = {"a": -4.0, "b": 0.5}

    assert tuple(normalizedSet.Membership(point) for point in (-1.0, 0.0, 1.0)) == pytest.approx(
        normalizedGrades,
        abs=1e-12,
        rel=0.0,
    ), "A normalized continuous set must not retain the mutable analytical source."
    assert Height(normalizedSet) == 1.0
    assert IsNormal(normalizedSet)


def test_ContinuousSupremumNeedNotBeAttainedForNormality():
    membershipFunction = MFunction("triangle", a=0.0, b=2.0, c=1.0)
    universe = ContinuousUniverse(0.0, 1.0, leftClosed=False, rightClosed=False)
    fuzzySet = ScalarFuzzySet(universe, membershipFunction.mju)

    assert Height(fuzzySet) == 1.0
    assert IsNormal(fuzzySet), (
        "Normality is defined by the supremum and must not require an attained core point."
    )


def test_GenericContinuousCallableFailsClosedWithoutExactHeightEvidence():
    fuzzySet = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True),
        lambda coordinate: 0.5 + coordinate / 4,
    )

    for operation in (Height, IsNormal, Normalize):
        with pytest.raises(ValueError, match="exact continuous height"):
            operation(fuzzySet)


@pytest.mark.parametrize("tolerance", [-1.0, float("nan"), float("inf"), True])
def test_NormalityRejectsInvalidTolerance(tolerance):
    fuzzySet = ScalarFuzzySet(DiscreteUniverse((0.0,)), lambda coordinate: 1.0)

    with pytest.raises((TypeError, ValueError), match="tolerance"):
        IsNormal(fuzzySet, tolerance=tolerance)


def test_NormalityToleranceIsAbsoluteAndExplicit():
    fuzzySet = ScalarFuzzySet(DiscreteUniverse((0.0,)), lambda coordinate: 1.0 - 5e-13)

    assert IsNormal(fuzzySet)
    assert not IsNormal(fuzzySet, tolerance=1e-13)


@pytest.mark.parametrize("operation", [Height, IsNormal, Normalize])
def test_HeightAwareHelpersRequireScalarFuzzySets(operation):
    with pytest.raises(TypeError, match="ScalarFuzzySet"):
        operation(object())
