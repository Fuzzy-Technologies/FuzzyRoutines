# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Custom structural membership integration and runtime validation boundaries."""

from fractions import Fraction

import pytest

from fuzzyroutines.defuzzification import Centroid
from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse, IntegrationDomain
from fuzzyroutines.fuzzysets import Height, ScalarFuzzySet
from fuzzyroutines.membership import MembershipCallable, MembershipScalar, Triangle


class CountingGrade:
    """User-owned callable with mutable bookkeeping and stable linear grades."""

    def __init__(self):
        """Track evaluated coordinates without changing the membership formula."""

        self.coordinates = []

    def __call__(self, value: MembershipScalar, /) -> MembershipScalar:
        """Record a valid coordinate and return the same linear grade each time."""

        self.coordinates.append(value)

        return value

    def Evaluate(self, value: MembershipScalar) -> MembershipScalar:
        """Provide a bound-method alternative with the same scalar contract."""

        return self(value)


def RisingGrade(coordinate: MembershipScalar) -> MembershipScalar:
    """Return a linear grade on the caller-declared closed unit interval."""

    return coordinate


def ClosedUnitUniverse() -> ContinuousUniverse:
    """Return the universe where the test's linear grade remains in range."""

    return ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)


@pytest.mark.parametrize("evaluator_kind", ["function", "lambda", "object", "bound_method"])
def test_CustomFormsRequireNoInheritance(evaluator_kind):
    """Functions and user-owned objects participate in numerical centroid."""

    custom_object = CountingGrade()
    evaluators = {
        "function": RisingGrade,
        "lambda": lambda value: value,
        "object": custom_object,
        "bound_method": custom_object.Evaluate,
    }
    membership_function: MembershipCallable = evaluators[evaluator_kind]
    fuzzy_set = ScalarFuzzySet(ClosedUnitUniverse(), membership_function)
    assert fuzzy_set.Membership(Fraction(1, 4)) == Fraction(1, 4)
    assert Centroid(fuzzy_set, IntegrationDomain(0.0, 1.0)) == pytest.approx(2 / 3)

    if evaluator_kind in {"object", "bound_method"}:
        assert custom_object.coordinates, "Custom callable was bypassed during evaluation"
        assert all(0 <= value <= 1 for value in custom_object.coordinates)


def test_ConstructionDoesNotExecuteCustomFunction():
    """Construction preserves user state and defers grade validation to use."""

    custom_object = CountingGrade()
    fuzzy_set = ScalarFuzzySet(ClosedUnitUniverse(), custom_object)
    assert custom_object.coordinates == []
    assert fuzzy_set.membershipFunction is custom_object


@pytest.mark.parametrize("coordinate", [True, False, "0.5", 0.5j, None])
def test_InvalidCoordinateTypeRejectedBeforeInvocation(coordinate):
    """Only non-boolean real scalar coordinates may reach custom code."""

    custom_object = CountingGrade()
    fuzzy_set = ScalarFuzzySet(ClosedUnitUniverse(), custom_object)

    with pytest.raises(TypeError, match="coordinate must be a real number"):
        fuzzy_set.Membership(coordinate)

    assert custom_object.coordinates == []


@pytest.mark.parametrize("coordinate", [float("nan"), float("inf"), -float("inf"), -0.1, 1.1])
def test_InvalidCoordinateValueRejectedBeforeInvocation(coordinate):
    """Nonfinite and outside-universe inputs fail without user side effects."""

    custom_object = CountingGrade()
    fuzzy_set = ScalarFuzzySet(ClosedUnitUniverse(), custom_object)

    with pytest.raises(ValueError):
        fuzzy_set.Membership(coordinate)

    assert custom_object.coordinates == []


@pytest.mark.parametrize(
    ("grade", "error_type"),
    [
        (True, TypeError),
        (False, TypeError),
        ("0.5", TypeError),
        (0.5j, TypeError),
        (None, TypeError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (-float("inf"), ValueError),
        (-0.1, ValueError),
        (1.1, ValueError),
    ],
)
@pytest.mark.parametrize("consumer", ["membership", "centroid", "discrete_height"])
def test_InvalidCustomGradesRejected(grade, error_type, consumer):
    """Every sampled consumer validates grades instead of coercing or clamping."""

    universe = (
        DiscreteUniverse((0.0, 0.5, 1.0))
        if consumer == "discrete_height"
        else ClosedUnitUniverse()
    )
    fuzzy_set = ScalarFuzzySet(universe, lambda value: grade)

    with pytest.raises(error_type, match="membership grade"):
        if consumer == "membership":
            fuzzy_set.Membership(0.5)

        elif consumer == "centroid":
            Centroid(fuzzy_set, IntegrationDomain(0.0, 1.0))

        else:
            Height(fuzzy_set)


def test_CallabilityDoesNotValidateSignature():
    """A malformed callable fails on invocation rather than gaining a valid grade."""

    fuzzy_set = ScalarFuzzySet(ClosedUnitUniverse(), lambda: 0.5)

    with pytest.raises(TypeError):
        fuzzy_set.Membership(0.5)


def test_CustomExceptionsPropagateUnchanged():
    """Caller failures are not hidden behind a fabricated membership value."""

    sentinel = RuntimeError("custom evaluator failed")

    def FailingGrade(coordinate: MembershipScalar) -> MembershipScalar:
        """Raise the original user error for every coordinate."""

        raise sentinel

    fuzzy_set = ScalarFuzzySet(ClosedUnitUniverse(), FailingGrade)

    with pytest.raises(RuntimeError) as error:
        Centroid(fuzzy_set, IntegrationDomain(0.0, 1.0))

    assert error.value is sentinel


def test_LookalikeMetadataProvidesNoAnalyticalEvidence(monkeypatch):
    """Untrusted shape attributes cannot bypass numeric custom evaluation."""

    custom_object = CountingGrade()
    custom_object.name = "Triangle"
    custom_object.parameters = {"a": 0, "b": 1, "c": 0.5}
    fuzzy_set = ScalarFuzzySet(ClosedUnitUniverse(), custom_object)

    def RejectAnalyticalBypass(*args):
        """Fail if arbitrary callable metadata is promoted to exact evidence."""

        pytest.fail("Custom metadata must not enable analytical moments")

    monkeypatch.setattr(
        "fuzzyroutines.defuzzification._PolynomialFamilyMoments",
        RejectAnalyticalBypass,
    )
    assert Centroid(fuzzy_set, IntegrationDomain(0.0, 1.0)) == pytest.approx(2 / 3)
    assert len(custom_object.coordinates) >= 5

    with pytest.raises(ValueError, match="generic membership callable"):
        Height(fuzzy_set)


def test_ModernAnalyticalEvidenceRemainsAvailable(monkeypatch):
    """The structural interface preserves trusted built-in analytical paths."""

    membership_function: MembershipCallable = Triangle(0.0, 0.25, 1.0)
    fuzzy_set = ScalarFuzzySet(ClosedUnitUniverse(), membership_function)

    def RejectNumericFallback(*args):
        """Fail when an analytical built-in unexpectedly enters quadrature."""

        pytest.fail("Trusted triangle must retain analytical centroid moments")

    monkeypatch.setattr("fuzzyroutines.defuzzification._AdaptiveMoments", RejectNumericFallback)
    assert Centroid(fuzzy_set, IntegrationDomain(0.0, 1.0)) == pytest.approx(5 / 12)
    assert Height(fuzzy_set) == 1


def test_CustomCentroidRequiresFiniteContainedDomain():
    """Integration bounds remain a separate validated contract for custom code."""

    custom_object = CountingGrade()
    fuzzy_set = ScalarFuzzySet(ClosedUnitUniverse(), custom_object)

    with pytest.raises(ValueError, match="entirely within"):
        Centroid(fuzzy_set, IntegrationDomain(-1.0, 1.0))

    assert custom_object.coordinates == []

    with pytest.raises(ValueError, match="finite"):
        IntegrationDomain(0.0, float("inf"))
