# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Reference and property tests for legacy membership-function contracts.

Expected values are derived from the formulas documented in ADR-0003 and the
membership-function contract table.  The tests intentionally use valid,
non-degenerate configurations only; strict rejection of invalid configurations
belongs to Task #51.
"""

import math

import pytest

from fuzzyroutines.FuzzyRoutines import MFunction

REFERENCECASES = (
    pytest.param("hyperbolic", {"a": 2.0, "b": 2.0, "c": 0.0}, -1.0, 1.0, id="hyperbolic-left-shoulder"),
    pytest.param("hyperbolic", {"a": 2.0, "b": 2.0, "c": 0.0}, 0.5, 0.5, id="hyperbolic-reference"),
    pytest.param("bell", {"a": 0.0, "b": 0.25, "c": 0.5}, 0.125, 0.5, id="bell-rising-shoulder"),
    pytest.param("bell", {"a": 0.0, "b": 0.25, "c": 0.5}, 0.5, 1.0, id="bell-plateau"),
    pytest.param("bell", {"a": 0.0, "b": 0.25, "c": 0.5}, 0.625, 0.5, id="bell-falling-shoulder"),
    pytest.param("parabolic", {"a": 0.2, "b": 0.8}, 0.35, 0.125, id="parabolic-first-half"),
    pytest.param("parabolic", {"a": 0.2, "b": 0.8}, 0.65, 0.875, id="parabolic-second-half"),
    pytest.param("triangle", {"a": 0.1, "b": 0.9, "c": 0.4}, 0.25, 0.5, id="triangle-rising"),
    pytest.param("triangle", {"a": 0.1, "b": 0.9, "c": 0.4}, 0.65, 0.5, id="triangle-falling"),
    pytest.param("trapezium", {"a": 0.1, "b": 0.9, "c": 0.3, "d": 0.7}, 0.2, 0.5, id="trapezium-rising"),
    pytest.param("trapezium", {"a": 0.1, "b": 0.9, "c": 0.3, "d": 0.7}, 0.8, 0.5, id="trapezium-falling"),
    pytest.param("exponential", {"a": 0.5, "b": 0.25}, 0.75, math.exp(-0.5), id="gaussian-reference"),
    pytest.param("sigmoidal", {"a": 2.0, "b": 0.5}, 0.5, 0.5, id="sigmoidal-midpoint"),
    pytest.param("desirability", {}, 0.0, math.exp(-1.0), id="harrington-reference"),
)

RANGECASES = (
    ("hyperbolic", {"a": 2.0, "b": 2.0, "c": 0.0}),
    ("bell", {"a": 0.0, "b": 0.25, "c": 0.5}),
    ("parabolic", {"a": 0.2, "b": 0.8}),
    ("triangle", {"a": 0.1, "b": 0.9, "c": 0.4}),
    ("trapezium", {"a": 0.1, "b": 0.9, "c": 0.3, "d": 0.7}),
    ("exponential", {"a": 0.5, "b": 0.25}),
    ("sigmoidal", {"a": 2.0, "b": 0.5}),
    ("desirability", {}),
)

GRIDVALUES = tuple(index / 20.0 for index in range(-20, 61))


@pytest.mark.parametrize(("identifier", "parameters", "inputValue", "expectedValue"), REFERENCECASES)
def test_MembershipFunctionReferenceValues(identifier, parameters, inputValue, expectedValue):
    membershipFunction = MFunction(identifier, **parameters)

    actualValue = membershipFunction.mju(inputValue)

    assert actualValue == pytest.approx(expectedValue, abs=1e-12, rel=0.0), (
        f"{identifier!r} violated its declared formula at {inputValue!r}."
    )


@pytest.mark.parametrize(("identifier", "parameters"), RANGECASES)
def test_MembershipFunctionValuesRemainWithinUnitInterval(identifier, parameters):
    membershipFunction = MFunction(identifier, **parameters)

    for inputValue in GRIDVALUES:
        actualValue = membershipFunction.mju(inputValue)

        assert 0.0 <= actualValue <= 1.0, (
            f"{identifier!r} returned {actualValue!r} outside [0, 1] for {inputValue!r}."
        )


def test_HyperbolicMembershipIsNonIncreasingAfterItsCutoff():
    membershipFunction = MFunction("hyperbolic", a=2.0, b=2.0, c=0.0)

    values = [membershipFunction.mju(inputValue) for inputValue in GRIDVALUES if inputValue >= 0.0]

    assert values == sorted(values, reverse=True), (
        "The hyperbolic right shoulder must be non-increasing after its cutoff."
    )


def test_ParabolicMembershipIsNonDecreasing():
    membershipFunction = MFunction("parabolic", a=0.2, b=0.8)

    values = [membershipFunction.mju(inputValue) for inputValue in GRIDVALUES]

    assert values == sorted(values), "The parabolic S-shoulder must be non-decreasing."


def test_TriangleWithApexAtRightFootIncludesItsApex():
    membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=1.0)

    assert membershipFunction.mju(1.0) == 1.0, (
        "The accepted c=b triangle boundary must retain membership one at x=b=c."
    )
    assert membershipFunction.mju(1.000001) == 0.0, (
        "The accepted c=b triangle boundary must be zero strictly after its apex."
    )


def test_SymmetricMembershipFamiliesAreMirrorSymmetric():
    bellFunction = MFunction("bell", a=0.0, b=0.25, c=0.5)
    exponentialFunction = MFunction("exponential", a=0.5, b=0.25)
    triangleFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)

    for offset in (0.05, 0.1, 0.2):
        assert bellFunction.mju(0.375 - offset) == pytest.approx(
            bellFunction.mju(0.375 + offset),
            abs=1e-12,
            rel=0.0,
        ), "The symmetric bell contract must have mirrored shoulders."
        assert exponentialFunction.mju(0.5 - offset) == pytest.approx(
            exponentialFunction.mju(0.5 + offset),
            abs=1e-12,
            rel=0.0,
        ), "The Gaussian contract must be symmetric about its centre."
        assert triangleFunction.mju(0.5 - offset) == pytest.approx(
            triangleFunction.mju(0.5 + offset),
            abs=1e-12,
            rel=0.0,
        ), "The symmetric triangular contract must be symmetric about its apex."


def test_SigmoidalAndDesirabilityMembershipsIncreaseForTheirDeclaredParameters():
    sigmoidalFunction = MFunction("sigmoidal", a=2.0, b=0.5)
    desirabilityFunction = MFunction("desirability")

    sigmoidalValues = [sigmoidalFunction.mju(inputValue) for inputValue in GRIDVALUES]
    desirabilityValues = [desirabilityFunction.mju(inputValue) for inputValue in GRIDVALUES]

    assert sigmoidalValues == sorted(sigmoidalValues), (
        "A positive-slope logistic membership must be non-decreasing."
    )
    assert desirabilityValues == sorted(desirabilityValues), (
        "The Harrington desirability transform must be non-decreasing."
    )
