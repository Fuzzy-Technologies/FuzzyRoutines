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
    Gaussian,
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


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    (
        (7.8, 8.0, 7.87473229552023741947),
        (8.0, 8.1, 8.04336518790245358447),
        (8.3, 8.4, 8.34312345024340282606),
        (20.0, 21.0, 20.04975306733971157807),
    ),
)
@pytest.mark.parametrize("direction", (-1, 1))
def test_GaussianTailCentroidMatchesIndependentDecimalReferences(
    left,
    right,
    expected,
    direction,
):
    """Protect same-sided tails against cancellation and incorrect coordinates.

    References use 60-digit Decimal exp and composite Simpson sums, with 4096
    and 8192 panels agreeing within 6e-13 (within 6e-17 for the 7.8--8.4 cases).
    The 1e-12 absolute bound follows ADR-0005's scalar formula-check policy.
    """

    bounds = (left, right) if direction == 1 else (-right, -left)
    domain = IntegrationDomain(*bounds)
    fuzzySet = ScalarFuzzySet(ContinuousUniverse(), Gaussian(0.0, 1.0))

    actual = Centroid(fuzzySet, domain)

    assert domain.Contains(actual), "Positive Gaussian weights must keep the centroid inside the domain"
    assert actual == pytest.approx(direction * expected, abs=1e-12, rel=0.0)


@pytest.mark.parametrize("direction", (-1, 1))
def test_GaussianTailCentroidPreservesTranslationAndScale(direction):
    """Check affine covariance against the independent standard-normal reference."""

    centre = 10.0
    scale = 2.0
    standardizedBounds = (8.0, 8.1) if direction == 1 else (-8.1, -8.0)
    domain = IntegrationDomain(
        centre + scale * standardizedBounds[0],
        centre + scale * standardizedBounds[1],
    )
    fuzzySet = ScalarFuzzySet(ContinuousUniverse(), Gaussian(centre, scale))
    expected = centre + scale * direction * 8.04336518790245358447

    actual = Centroid(fuzzySet, domain)

    assert domain.Contains(actual), "Affine Gaussian moments must retain the integration domain"
    assert actual == pytest.approx(expected, abs=1e-12, rel=0.0)


def test_LegacyGaussianTailUsesTheCorrectedSharedCentroid():
    """Keep the historical evaluator adapter on the same tail-safe strategy."""

    membershipFunction = MFunction("gaussian", a=0.0, b=1.0)
    fuzzySet = FuzzySet(membershipFunction, supportSet=(8.3, 8.4))

    actual = fuzzySet.Defuz()

    assert 8.3 <= actual <= 8.4, "Legacy defuzzification must not retain the out-of-domain Gaussian result"
    assert actual == pytest.approx(8.34312345024340282606, abs=1e-12, rel=0.0)


def test_GaussianNarrowTailUsesExistingAdaptivePolicy(monkeypatch):
    """Avoid unresolved erfc subtraction while preserving the caller's work policy."""

    from fuzzyroutines import defuzzification

    originalAdaptive = defuzzification._AdaptiveMoments
    policies = []

    def RecordAdaptivePolicy(fuzzySet, domain, policy):
        """Observe the numerical fallback without replacing its mathematical work."""

        policies.append(policy)

        return originalAdaptive(fuzzySet, domain, policy)

    monkeypatch.setattr(defuzzification, "_AdaptiveMoments", RecordAdaptivePolicy)
    policy = CentroidPolicy(maximumDepth=0)
    domain = IntegrationDomain(8.0, 8.000001)
    fuzzySet = ScalarFuzzySet(ContinuousUniverse(), Gaussian(0.0, 1.0))

    actual = Centroid(fuzzySet, domain, policy)

    assert policies == [policy], "Fallback must use the exact caller policy without a hidden replacement"
    assert domain.Contains(actual), "A narrow positive tail must not produce a clamped endpoint"
    # 60-digit Decimal Simpson references at 4096 and 8192 panels agree to 3e-38.
    assert actual == pytest.approx(8.00000049999933333329, abs=1e-12, rel=0.0)


def test_GaussianFallbackPreservesConfiguredNonConvergence():
    """A strict unresolved Gaussian path must not bypass the adaptive work limit."""

    fuzzySet = ScalarFuzzySet(ContinuousUniverse(), Gaussian(0.0, 1.0))
    policy = CentroidPolicy(
        absoluteTolerance=1e-20,
        relativeTolerance=1e-16,
        maximumDepth=0,
    )

    with pytest.raises(CentroidConvergenceError, match="maximumDepth=0"):
        Centroid(fuzzySet, IntegrationDomain(0.0, 1.0), policy)


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
