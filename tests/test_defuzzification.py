# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Analytical, adaptive, boundary, and mutation evidence for centroids."""

import math

import pytest

from fuzzyroutines import (
    Centroid,
    CentroidConvergenceError,
    CentroidPolicy,
    ContinuousUniverse,
    DiscreteUniverse,
    IntegrationDomain,
    ScalarFuzzySet,
)
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction


@pytest.mark.parametrize(
    ("identifier", "parameters", "domain", "expected"),
    (
        ("triangle", {"a": 0.0, "b": 1.0, "c": 0.25}, (0.0, 1.0), 5 / 12),
        ("trapezium", {"a": 0.0, "b": 4.0, "c": 1.0, "d": 3.0}, (0.0, 4.0), 2.0),
        ("bell", {"a": -2.0, "b": -1.0, "c": 1.0}, (-2.0, 2.0), 0.0),
        ("parabolic", {"a": 0.0, "b": 1.0}, (0.0, 1.0), 17 / 24),
        ("gaussian", {"a": 3.0, "b": 0.5}, (1.0, 5.0), 3.0),
    ),
)
def test_AnalyticalFamiliesMatchIndependentReferences(identifier, parameters, domain, expected):
    membershipFunction = MFunction(identifier, **parameters)
    fuzzySet = ScalarFuzzySet(ContinuousUniverse(), membershipFunction.mju)

    actual = Centroid(fuzzySet, IntegrationDomain(*domain))

    assert actual == pytest.approx(expected, abs=1e-12, rel=0.0)


def test_AdaptiveCallableMatchesPolynomialReference():
    fuzzySet = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, True, True),
        lambda coordinate: coordinate**3,
    )
    policy = CentroidPolicy(absoluteTolerance=1e-13, relativeTolerance=1e-12)

    actual = Centroid(fuzzySet, IntegrationDomain(0.0, 1.0), policy)

    assert actual == pytest.approx(0.8, abs=1e-11, rel=0.0)


def test_AdaptiveLowMembershipDoesNotBecomeZeroArea():
    fuzzySet = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, True, True),
        lambda coordinate: 1e-14 * (1 + coordinate),
    )

    actual = Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))

    assert actual == pytest.approx(5 / 9, abs=1e-12, rel=0.0)


def test_NarrowAnalyticalTriangleIsNotMissedBySampling():
    left = 0.123456789
    apex = left + 4e-10
    right = left + 1e-9
    membershipFunction = MFunction("triangle", a=left, b=right, c=apex)
    fuzzySet = ScalarFuzzySet(ContinuousUniverse(), membershipFunction.mju)

    actual = Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))

    assert actual == pytest.approx((left + apex + right) / 3, abs=1e-12, rel=0.0)


def test_CentroidReadsCurrentParametersAndDomainWithoutStaleCache():
    membershipFunction = MFunction("triangle", a=0.0, b=2.0, c=1.0)
    fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 2.0))
    initial = fuzzySet.Defuz()

    membershipFunction.parameters = {"a": 1.0, "b": 3.0, "c": 2.0}
    fuzzySet.supportSet = (1.0, 3.0)
    mutated = fuzzySet.Defuz()

    assert initial == pytest.approx(1.0, abs=1e-12, rel=0.0)
    assert mutated == pytest.approx(2.0, abs=1e-12, rel=0.0)


def test_LegacyAccuracyDoesNotControlCentroidPrecision():
    membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.2)
    fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0))
    reference = fuzzySet.Defuz()

    membershipFunction.accuracy = 1

    assert fuzzySet.Defuz() == reference


def test_ZeroAreaRaisesDocumentedValueError():
    fuzzySet = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, True, True),
        lambda coordinate: 0.0,
    )

    with pytest.raises(ValueError, match="zero membership area"):
        Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))


def test_NonConvergenceRaisesSpecificErrorWithoutFixedGridFallback():
    fuzzySet = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, True, True),
        lambda coordinate: math.exp(coordinate) / math.e,
    )
    policy = CentroidPolicy(
        absoluteTolerance=1e-16,
        relativeTolerance=1e-16,
        maximumDepth=0,
    )

    with pytest.raises(CentroidConvergenceError, match="maximumDepth=0"):
        Centroid(fuzzySet, IntegrationDomain(0.0, 1.0), policy)


def test_CentroidRejectsDomainOutsideUniverse():
    fuzzySet = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, True, True),
        lambda coordinate: 1.0,
    )

    with pytest.raises(ValueError, match="entirely within"):
        Centroid(fuzzySet, IntegrationDomain(-1.0, 1.0))


def test_CentroidRejectsDiscreteUniverse():
    fuzzySet = ScalarFuzzySet(DiscreteUniverse((0.0, 1.0)), lambda coordinate: 1.0)

    with pytest.raises(TypeError, match="ContinuousUniverse"):
        Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))


@pytest.mark.parametrize(
    "arguments",
    (
        {"absoluteTolerance": 0.0},
        {"relativeTolerance": math.inf},
        {"maximumDepth": -1},
        {"maximumDepth": True},
    ),
)
def test_CentroidPolicyRejectsInvalidConfiguration(arguments):
    with pytest.raises((TypeError, ValueError)):
        CentroidPolicy(**arguments)
