"""Regression specification for the stale legacy defuzzification cache.

Task #66 must make Defuz() reflect the current membership function and support
state.  This strict expected failure documents the defect without declaring it
a compatibility requirement.
"""

import pytest

from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction


@pytest.mark.xfail(
    strict=True,
    reason="Task #66: legacy Defuz() returns a construction-time cached value.",
)
def test_DefuzReflectsCurrentMembershipParameters():
    membershipFunction = MFunction("parabolic", a=0.0, b=1.0)
    fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0))

    membershipFunction.parameters = {"a": 0.0, "b": 0.5}
    expectedValue = fuzzySet._Defuz()

    assert fuzzySet.Defuz() == pytest.approx(expectedValue, abs=1e-12, rel=0.0), (
        "Defuz() must reflect membership parameters changed after FuzzySet construction."
    )
