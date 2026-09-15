"""Strict parameter-domain tests for the historical membership families."""

import math

import pytest

from fuzzyroutines.FuzzyRoutines import MFunction

VALIDCASES = (
    ("hyperbolic", {"a": 2.0, "b": 3.0, "c": -1.0}),
    ("bell", {"a": 0.0, "b": 0.25, "c": 0.25}),
    ("parabolic", {"a": 0.0, "b": 1.0}),
    ("triangle", {"a": 0.0, "b": 1.0, "c": 1.0}),
    ("trapezium", {"a": 0.0, "b": 1.0, "c": 0.5, "d": 0.5}),
    ("exponential", {"a": 0.0, "b": 1.0}),
    ("sigmoidal", {"a": -1.0, "b": 0.0}),
    ("desirability", {}),
)

INVALIDCASES = (
    ("hyperbolic", {"a": 0.0, "b": 2.0, "c": 0.0}, "a > 0"),
    ("hyperbolic", {"a": 2.0, "b": 0.0, "c": 0.0}, "b > 0"),
    ("bell", {"a": 0.0, "b": 0.0, "c": 1.0}, "a < b <= c"),
    ("bell", {"a": 0.0, "b": 0.75, "c": 0.5}, "a < b <= c"),
    ("parabolic", {"a": 0.5, "b": 0.5}, "a < b"),
    ("triangle", {"a": 0.5, "b": 1.0, "c": 0.5}, "a < c <= b"),
    ("triangle", {"a": 0.0, "b": 0.5, "c": 0.75}, "a < c <= b"),
    ("trapezium", {"a": 0.0, "b": 1.0, "c": 0.0, "d": 0.5}, "a < c <= d < b"),
    ("trapezium", {"a": 0.0, "b": 1.0, "c": 0.75, "d": 0.5}, "a < c <= d < b"),
    ("trapezium", {"a": 0.0, "b": 1.0, "c": 0.5, "d": 1.0}, "a < c <= d < b"),
    ("exponential", {"a": 0.0, "b": 0.0}, "b > 0"),
    ("exponential", {"a": 0.0, "b": -1.0}, "b > 0"),
    ("sigmoidal", {"a": 0.0, "b": 0.0}, "non-zero"),
)


@pytest.mark.parametrize(("identifier", "parameters"), VALIDCASES)
def test_MembershipFunctionAcceptsValidatedParameters(identifier, parameters):
    membershipFunction = MFunction(identifier, **parameters)

    assert membershipFunction.parameters == parameters


@pytest.mark.parametrize(("identifier", "parameters", "message"), INVALIDCASES)
def test_MembershipFunctionRejectsInvalidParameterGeometry(identifier, parameters, message):
    with pytest.raises(ValueError, match=message):
        MFunction(identifier, **parameters)


@pytest.mark.parametrize("invalidValue", [True, False, math.nan, math.inf, -math.inf])
def test_MembershipFunctionRejectsNonFiniteAndBooleanParameters(invalidValue):
    with pytest.raises(ValueError, match="finite real number"):
        MFunction("parabolic", a=0.0, b=invalidValue)


@pytest.mark.parametrize(
    ("identifier", "parameters"),
    [
        ("triangle", {"a": 0.0, "b": 1.0}),
        ("triangle", {"a": 0.0, "b": 1.0, "c": 0.5, "d": 0.75}),
        ("desirability", {"a": 0.0}),
    ],
)
def test_MembershipFunctionRequiresExactParameterSet(identifier, parameters):
    with pytest.raises(ValueError, match="requires exactly"):
        MFunction(identifier, **parameters)


def test_MembershipFunctionRejectsUnknownIdentifier():
    with pytest.raises(ValueError, match="unknown membership-function identifier"):
        MFunction("unknown", a=0.0)


def test_MembershipFunctionParameterSetterIsTransactional():
    membershipFunction = MFunction("parabolic", a=0.0, b=1.0)

    with pytest.raises(ValueError, match="a < b"):
        membershipFunction.parameters = {"a": 0.5, "b": 0.5}

    assert membershipFunction.parameters == {"a": 0.0, "b": 1.0}
