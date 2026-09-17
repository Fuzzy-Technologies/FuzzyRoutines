"""Contracts that prevent stale cross-call evaluation results."""

from fuzzyroutines import DeriveProperties, DiscreteUniverse, ScalarFuzzySet
from fuzzyroutines.FuzzyRoutines import MFunction


def test_ScalarFuzzySetMembershipObservesCallableStateChanges():
    state = {"grade": 0.25}
    fuzzySet = ScalarFuzzySet(
        DiscreteUniverse((0.0,)),
        lambda coordinate: state["grade"],
    )

    assert fuzzySet.Membership(0.0) == 0.25

    state["grade"] = 0.75

    assert fuzzySet.Membership(0.0) == 0.75, (
        "A frozen wrapper must not cache a result from caller-owned mutable callable state."
    )


def test_DerivePropertiesObservesMembershipParameterChanges():
    membershipFunction = MFunction("triangle", a=0.0, b=2.0, c=1.0)
    universe = DiscreteUniverse((0.0, 0.5, 1.0))

    assert DeriveProperties(membershipFunction, universe).height == 1.0

    membershipFunction.parameters = {"a": 0.0, "b": 4.0, "c": 2.0}

    assert DeriveProperties(membershipFunction, universe).height == 0.5, (
        "Derived properties must be recalculated after a legacy parameter mutation."
    )
