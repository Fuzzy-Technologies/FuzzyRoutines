"""Regression tests for coherent legacy FuzzySet derived state."""

import pytest

from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction


def test_DefuzReflectsCurrentMembershipParameters():
    membershipFunction = MFunction("parabolic", a=0.0, b=1.0)
    fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0))

    for parameters in ({"a": 0.0, "b": 0.5}, {"a": 0.25, "b": 1.0}):
        membershipFunction.parameters = parameters
        expectedValue = fuzzySet._Defuz()

        assert fuzzySet.Defuz() == pytest.approx(expectedValue, abs=1e-12, rel=0.0), (
            "Defuz() must reflect every membership-parameter mutation."
        )
        assert fuzzySet.defuzValue == pytest.approx(expectedValue, abs=1e-12, rel=0.0), (
            "defuzValue must not expose stale derived state."
        )


def test_DefuzReflectsCurrentSupportSet():
    fuzzySet = FuzzySet(
        MFunction("parabolic", a=0.0, b=1.0),
        supportSet=(0.0, 1.0),
    )

    fuzzySet.supportSet = (0.0, 0.5)
    expectedValue = fuzzySet._Defuz()

    assert fuzzySet.Defuz() == pytest.approx(expectedValue, abs=1e-12, rel=0.0), (
        "Defuz() must reflect a support interval changed after construction."
    )
