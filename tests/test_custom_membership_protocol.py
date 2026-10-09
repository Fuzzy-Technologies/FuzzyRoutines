# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Custom structural membership integration and runtime validation boundaries."""

from fractions import Fraction

import pytest

from fuzzyroutines.defuzzification import Centroid
from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse, IntegrationDomain
from fuzzyroutines.FuzzyRoutines import MFunction
from fuzzyroutines.fuzzysets import Height, ScalarFuzzySet
from fuzzyroutines.membership import (
    MembershipCallable,
    MembershipFunction,
    MembershipScalar,
    Triangle,
)


class InheritedMembership(MembershipFunction):
    """Retain the built-in evaluator while extending the public family type."""


class CallOverrideMembership(MembershipFunction):
    """Replace callable evaluation while retaining the stored triangle geometry."""

    def __call__(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Return a constant grade independently of the inherited triangle."""

        return 0.25


class EvaluateOverrideMembership(MembershipFunction):
    """Replace delegated evaluation while retaining the stored triangle geometry."""

    def Evaluate(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Return a constant grade independently of the inherited triangle."""

        return 0.25


class LegacyTriangleOverride(MFunction):
    """Replace a registered historical family method with custom evaluation."""

    def Triangle(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Return a constant grade instead of the declared triangle shape."""

        return 0.25


class InheritedLegacyMembership(MFunction):
    """Retain the canonical historical evaluator in a subclass."""


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


@pytest.mark.parametrize('evaluatorKind', ["function", "lambda", "object", "bound_method"])
def test_CustomFormsRequireNoInheritance(evaluatorKind):
    """Functions and user-owned objects participate in numerical centroid."""

    customObject = CountingGrade()
    evaluators = {
        "function": RisingGrade,
        "lambda": lambda value: value,
        "object": customObject,
        "bound_method": customObject.Evaluate,
    }
    membershipFunction: MembershipCallable = evaluators[evaluatorKind]
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), membershipFunction)
    assert fuzzySet.Membership(Fraction(1, 4)) == Fraction(1, 4)
    assert Centroid(fuzzySet, IntegrationDomain(0.0, 1.0)) == pytest.approx(2 / 3)

    if evaluatorKind in {"object", "bound_method"}:
        assert customObject.coordinates, "Custom callable was bypassed during evaluation"
        assert all(0 <= value <= 1 for value in customObject.coordinates)


def test_ConstructionDoesNotExecuteCustomFunction():
    """Construction preserves user state and defers grade validation to use."""

    customObject = CountingGrade()
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), customObject)
    assert customObject.coordinates == []
    assert fuzzySet.membershipFunction is customObject


@pytest.mark.parametrize("coordinate", [True, False, "0.5", 0.5j, None])
def test_InvalidCoordinateTypeRejectedBeforeInvocation(coordinate):
    """Only non-boolean real scalar coordinates may reach custom code."""

    customObject = CountingGrade()
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), customObject)

    with pytest.raises(TypeError, match="coordinate must be a real number"):
        fuzzySet.Membership(coordinate)

    assert customObject.coordinates == []


@pytest.mark.parametrize("coordinate", [float("nan"), float("inf"), -float("inf"), -0.1, 1.1])
def test_InvalidCoordinateValueRejectedBeforeInvocation(coordinate):
    """Nonfinite and outside-universe inputs fail without user side effects."""

    customObject = CountingGrade()
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), customObject)

    with pytest.raises(ValueError):
        fuzzySet.Membership(coordinate)

    assert customObject.coordinates == []


@pytest.mark.parametrize(
    ("grade", 'errorType'),
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
def test_InvalidCustomGradesRejected(grade, errorType, consumer):
    """Every sampled consumer validates grades instead of coercing or clamping."""

    universe = (
        DiscreteUniverse((0.0, 0.5, 1.0))
        if consumer == "discrete_height"
        else ClosedUnitUniverse()
    )
    fuzzySet = ScalarFuzzySet(universe, lambda value: grade)

    with pytest.raises(errorType, match="membership grade"):
        if consumer == "membership":
            fuzzySet.Membership(0.5)

        elif consumer == "centroid":
            Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))

        else:
            Height(fuzzySet)


def test_CallabilityDoesNotValidateSignature():
    """A malformed callable fails on invocation rather than gaining a valid grade."""

    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), lambda: 0.5)

    with pytest.raises(TypeError):
        fuzzySet.Membership(0.5)


def test_CustomExceptionsPropagateUnchanged():
    """Caller failures are not hidden behind a fabricated membership value."""

    sentinel = RuntimeError("custom evaluator failed")

    def FailingGrade(coordinate: MembershipScalar) -> MembershipScalar:
        """Raise the original user error for every coordinate."""

        raise sentinel

    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), FailingGrade)

    with pytest.raises(RuntimeError) as error:
        Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))

    assert error.value is sentinel


def test_LookalikeMetadataProvidesNoAnalyticalEvidence(monkeypatch):
    """Untrusted shape attributes cannot bypass numeric custom evaluation."""

    customObject = CountingGrade()
    customObject.name = "Triangle"
    customObject.parameters = {"a": 0, "b": 1, "c": 0.5}
    customObject.__self__ = Triangle(0.0, 0.5, 1.0)
    customObject.__func__ = MembershipFunction.Evaluate
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), customObject)

    def RejectAnalyticalBypass(*args):
        """Fail if arbitrary callable metadata is promoted to exact evidence."""

        pytest.fail("Custom metadata must not enable analytical moments")

    monkeypatch.setattr(
        "fuzzyroutines.defuzzification._PolynomialFamilyMoments",
        RejectAnalyticalBypass,
    )
    assert Centroid(fuzzySet, IntegrationDomain(0.0, 1.0)) == pytest.approx(2 / 3)
    assert len(customObject.coordinates) >= 5

    with pytest.raises(ValueError, match="generic membership callable"):
        Height(fuzzySet)


def test_ModernAnalyticalEvidenceRemainsAvailable(monkeypatch):
    """The structural interface preserves trusted built-in analytical paths."""

    membershipFunction: MembershipCallable = Triangle(0.0, 0.25, 1.0)
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), membershipFunction)

    def RejectNumericFallback(*args):
        """Fail when an analytical built-in unexpectedly enters quadrature."""

        pytest.fail("Trusted triangle must retain analytical centroid moments")

    monkeypatch.setattr("fuzzyroutines.defuzzification._AdaptiveMoments", RejectNumericFallback)
    assert Centroid(fuzzySet, IntegrationDomain(0.0, 1.0)) == pytest.approx(5 / 12)
    assert Height(fuzzySet) == 1


@pytest.mark.parametrize('membershipType', [CallOverrideMembership, EvaluateOverrideMembership])
@pytest.mark.parametrize('evaluatorKind', ["object", "bound_call"])
def test_OverriddenMembershipUsesActualCallable(membershipType, evaluatorKind, monkeypatch):
    """A stored family never overrides the grade supplied by a subclass."""

    membershipFunction = membershipType("triangle", left=0.0, peak=0.25, right=1.0)
    evaluator = membershipFunction if evaluatorKind == "object" else membershipFunction.__call__
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), evaluator)

    def RejectAnalyticalBypass(*args):
        """Fail if stored geometry bypasses the active custom callable."""

        pytest.fail("Overridden evaluation must not gain triangle analytical moments")

    monkeypatch.setattr("fuzzyroutines.defuzzification._PolynomialFamilyMoments", RejectAnalyticalBypass)
    assert fuzzySet.Membership(0.25) == 0.25
    assert Centroid(fuzzySet, IntegrationDomain(0.0, 1.0)) == pytest.approx(0.5)

    with pytest.raises(ValueError, match="generic membership callable"):
        Height(fuzzySet)


def test_OverriddenBoundEvaluateUsesActualCallable(monkeypatch):
    """An overridden bound evaluator cannot inherit its owner's certificate."""

    membershipFunction = EvaluateOverrideMembership("triangle", left=0.0, peak=0.25, right=1.0)
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), membershipFunction.Evaluate)

    def RejectAnalyticalBypass(*args):
        """Fail if the custom bound method is replaced with triangle moments."""

        pytest.fail("Overridden Evaluate must remain a generic bound evaluator")

    monkeypatch.setattr("fuzzyroutines.defuzzification._PolynomialFamilyMoments", RejectAnalyticalBypass)
    assert Centroid(fuzzySet, IntegrationDomain(0.0, 1.0)) == pytest.approx(0.5)

    with pytest.raises(ValueError, match="generic membership callable"):
        Height(fuzzySet)


@pytest.mark.parametrize('evaluatorKind', ["object", "bound_call", "bound_evaluate"])
def test_UnchangedSubclassEvaluatorsRetainEvidence(evaluatorKind, monkeypatch):
    """Inherited evaluators keep exact evidence when their function is verified."""

    membershipFunction = InheritedMembership("triangle", left=0.0, peak=0.25, right=1.0)
    evaluators = {
        "object": membershipFunction,
        "bound_call": membershipFunction.__call__,
        "bound_evaluate": membershipFunction.Evaluate,
    }
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), evaluators[evaluatorKind])

    def RejectNumericFallback(*args):
        """Fail when an unchanged evaluator unexpectedly loses its evidence."""

        pytest.fail("Unchanged subclass evaluator must retain triangle moments")

    monkeypatch.setattr("fuzzyroutines.defuzzification._AdaptiveMoments", RejectNumericFallback)
    assert Centroid(fuzzySet, IntegrationDomain(0.0, 1.0)) == pytest.approx(5 / 12)
    assert Height(fuzzySet) == 1


def test_CanonicalBoundEvaluateRetainsEvidenceWithCustomCall(monkeypatch):
    """A canonical bound Evaluate is distinct from an overridden callable."""

    membershipFunction = CallOverrideMembership("triangle", left=0.0, peak=0.25, right=1.0)
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), membershipFunction.Evaluate)

    def RejectNumericFallback(*args):
        """Fail if the independently verified canonical method loses evidence."""

        pytest.fail("Canonical Evaluate must retain its own analytical evidence")

    monkeypatch.setattr("fuzzyroutines.defuzzification._AdaptiveMoments", RejectNumericFallback)
    assert Centroid(fuzzySet, IntegrationDomain(0.0, 1.0)) == pytest.approx(5 / 12)
    assert Height(fuzzySet) == 1


def test_OverriddenHistoricalFamilyRemainsGeneric(monkeypatch):
    """A historical registry entry does not certify an overridden method."""

    membershipFunction = LegacyTriangleOverride("triangle", a=0.0, b=1.0, c=0.25)
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), membershipFunction.mju)

    def RejectAnalyticalBypass(*args):
        """Fail if a custom registry method is replaced by built-in geometry."""

        pytest.fail("Overridden historical family must remain a generic callable")

    monkeypatch.setattr("fuzzyroutines.defuzzification._PolynomialFamilyMoments", RejectAnalyticalBypass)
    assert Centroid(fuzzySet, IntegrationDomain(0.0, 1.0)) == pytest.approx(0.5)

    with pytest.raises(ValueError, match="generic membership callable"):
        Height(fuzzySet)


def test_UnchangedHistoricalSubclassRetainsEvidence(monkeypatch):
    """Historical subclasses with canonical bound methods retain exact moments."""

    membershipFunction = InheritedLegacyMembership("triangle", a=0.0, b=1.0, c=0.25)
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), membershipFunction.mju)

    def RejectNumericFallback(*args):
        """Fail if verified historical methods unnecessarily enter quadrature."""

        pytest.fail("Canonical historical subclass must retain analytical moments")

    monkeypatch.setattr("fuzzyroutines.defuzzification._AdaptiveMoments", RejectNumericFallback)
    assert Centroid(fuzzySet, IntegrationDomain(0.0, 1.0)) == pytest.approx(5 / 12)
    assert Height(fuzzySet) == 1


def test_CustomCentroidRequiresFiniteContainedDomain():
    """Integration bounds remain a separate validated contract for custom code."""

    customObject = CountingGrade()
    fuzzySet = ScalarFuzzySet(ClosedUnitUniverse(), customObject)

    with pytest.raises(ValueError, match="entirely within"):
        Centroid(fuzzySet, IntegrationDomain(-1.0, 1.0))

    assert customObject.coordinates == []

    with pytest.raises(ValueError, match="finite"):
        IntegrationDomain(0.0, float("inf"))
