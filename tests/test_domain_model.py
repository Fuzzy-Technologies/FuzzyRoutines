# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Contracts for explicit scalar universes and numerical integration domains."""

import math
from dataclasses import FrozenInstanceError
from fractions import Fraction

import pytest

from fuzzyroutines import ContinuousUniverse, DiscreteUniverse, IntegrationDomain
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction


def test_ContinuousUniverseRepresentsTheRealLineExplicitly():
    universe = ContinuousUniverse()

    assert universe.isBounded is False, "The real line must remain explicitly unbounded."
    assert universe.Contains(-1.0e100), "Every finite negative coordinate belongs to the real line."
    assert universe.Contains(1.0e100), "Every finite positive coordinate belongs to the real line."


@pytest.mark.parametrize(
    ("leftClosed", "rightClosed", "expectedAtLeft", "expectedAtRight"),
    [
        (False, False, False, False),
        (True, False, True, False),
        (False, True, False, True),
        (True, True, True, True),
    ],
)
def test_ContinuousUniversePreservesEndpointClosure(
    leftClosed,
    rightClosed,
    expectedAtLeft,
    expectedAtRight,
):
    universe = ContinuousUniverse(0.0, 1.0, leftClosed, rightClosed)

    assert universe.Contains(0.0) is expectedAtLeft, "Left-endpoint membership must follow leftClosed."
    assert universe.Contains(1.0) is expectedAtRight, "Right-endpoint membership must follow rightClosed."
    assert universe.Contains(0.5), "Every interior coordinate must belong to the interval."


@pytest.mark.parametrize(
    "constructorArguments",
    [
        (1.0, 1.0),
        (2.0, 1.0),
        (math.nan, 1.0),
        (0.0, math.inf),
        (True, 1.0),
    ],
)
def test_ContinuousUniverseRejectsInvalidBounds(constructorArguments):
    with pytest.raises((TypeError, ValueError)):
        ContinuousUniverse(*constructorArguments)


def test_ContinuousUniverseRejectsClosedUnboundedEndpoints():
    with pytest.raises(ValueError, match="unbounded left endpoint"):
        ContinuousUniverse(left=None, right=1.0, leftClosed=True)

    with pytest.raises(ValueError, match="unbounded right endpoint"):
        ContinuousUniverse(left=0.0, right=None, rightClosed=True)


def test_DiscreteUniverseRequiresExplicitOrderedDistinctFinitePoints():
    universe = DiscreteUniverse((-1, 0.5, 2))

    assert universe.points == (-1, 0.5, 2), "Discrete coordinates must preserve declared values."
    assert isinstance(universe.points[0], int), "Domain construction must not rewrite scalar representation."
    assert universe.Contains(0.5), "Declared coordinates must belong to the discrete universe."
    assert not universe.Contains(0.0), "Undeclared coordinates must remain outside the discrete universe."

    for invalidPoints in ([], (), (0.0, 0.0), (1.0, 0.0), (0.0, math.inf)):
        with pytest.raises((TypeError, ValueError)):
            DiscreteUniverse(invalidPoints)


def test_IntegrationDomainIsFiniteClosedAndOrdered():
    domain = IntegrationDomain(-2, 3)

    assert domain.Contains(-2.0), "A numerical integration domain includes its left endpoint."
    assert domain.Contains(3.0), "A numerical integration domain includes its right endpoint."
    assert not domain.Contains(3.1), "Coordinates beyond the interval must be excluded."

    for invalidBounds in ((0.0, 0.0), (1.0, 0.0), (math.nan, 1.0), (0.0, math.inf)):
        with pytest.raises(ValueError):
            IntegrationDomain(*invalidBounds)


def test_DomainTypesAcceptAndPreserveStandardRealScalars():
    left = Fraction(1, 10)
    right = Fraction(9, 10)
    domain = IntegrationDomain(left, right)

    assert domain.ToLegacyInterval() == (left, right), "Real scalar values must not be coerced or rounded."
    assert domain.Contains(Fraction(1, 2)), "Exact rational coordinates must retain exact comparison semantics."


def test_IntegrationDomainValidatesContainmentInContinuousUniverse():
    universe = ContinuousUniverse(0.0, 10.0, leftClosed=True, rightClosed=True)
    domain = IntegrationDomain(1.0, 9.0)

    assert domain.ValidateWithin(universe) is domain, "Successful validation must preserve object identity."

    with pytest.raises(ValueError, match="entirely within"):
        IntegrationDomain(-1.0, 9.0).ValidateWithin(universe)

    with pytest.raises(ValueError, match="entirely within"):
        IntegrationDomain(0.0, 9.0).ValidateWithin(
            ContinuousUniverse(0.0, 10.0, leftClosed=False, rightClosed=True)
        )

    with pytest.raises(TypeError, match="ContinuousUniverse"):
        domain.ValidateWithin(DiscreteUniverse((1.0, 9.0)))


def test_DomainTypesAreImmutableValueObjects():
    universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)

    with pytest.raises(FrozenInstanceError):
        universe.left = -1.0


def test_LegacyIntervalAdapterPreservesTupleShapeAndValues():
    domain = IntegrationDomain.FromLegacyInterval((-1, 2))

    assert domain.ToLegacyInterval() == (-1, 2), "Legacy mapping must preserve both interval endpoints."
    assert all(isinstance(endpoint, int) for endpoint in domain.ToLegacyInterval()), (
        "Legacy mapping must not silently rewrite serialized scalar representation."
    )

    for invalidInterval in ([-1.0, 2.0], (-1.0,), (-1.0, 2.0, 3.0)):
        with pytest.raises((TypeError, ValueError), match="two-item tuple"):
            IntegrationDomain.FromLegacyInterval(invalidInterval)


def test_LegacyFuzzySetDelegatesSupportSetToIntegrationDomain():
    fuzzySet = FuzzySet(MFunction("gaussian", a=0.0, b=1.0), supportSet=(-2, 2))

    assert isinstance(fuzzySet._integrationDomain, IntegrationDomain), (
        "The compatibility facade must store the approved integration-domain value object."
    )
    assert fuzzySet.supportSet == (-2, 2), "The historical getter must retain its exact tuple contract."

    fuzzySet.supportSet = (-3, 3)

    assert fuzzySet._integrationDomain == IntegrationDomain(-3, 3), (
        "The historical setter must replace the internal domain atomically."
    )
    assert fuzzySet.supportSet == (-3, 3), "The updated tuple must remain visible to legacy callers."


def test_LegacySupportSetRejectsInvalidMutationWithoutChangingState():
    fuzzySet = FuzzySet(MFunction("gaussian", a=0.0, b=1.0), supportSet=(-2.0, 2.0))

    with pytest.raises(ValueError):
        fuzzySet.supportSet = (2.0, -2.0)

    assert fuzzySet.supportSet == (-2.0, 2.0), "Rejected mutation must leave the previous domain unchanged."
