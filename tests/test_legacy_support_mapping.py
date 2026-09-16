"""Executable compatibility boundary for legacy ``supportSet`` semantics."""

import pytest

from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction


def test_GaussianPositiveSupportExtendsBeyondLegacyIntegrationWindow():
    membershipFunction = MFunction("gaussian", a=0.0, b=1.0)
    fuzzySet = FuzzySet(membershipFunction, supportSet=(-1.0, 1.0))

    assert fuzzySet.supportSet == (-1.0, 1.0)
    assert membershipFunction.mju(-2.0) > 0.0
    assert membershipFunction.mju(2.0) > 0.0


def test_ShoulderCoreExtendsBeyondLegacyIntegrationWindow():
    membershipFunction = MFunction("sShoulder", a=0.0, b=1.0)
    fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0))

    assert fuzzySet.supportSet == (0.0, 1.0)
    assert membershipFunction.mju(2.0) == 1.0


def test_BoundedTriangleSupportCanDifferFromIntegrationWindow():
    membershipFunction = MFunction("triangle", a=0.0, b=2.0, c=1.0)
    fuzzySet = FuzzySet(membershipFunction, supportSet=(-1.0, 3.0))

    assert fuzzySet.supportSet == (-1.0, 3.0)
    assert membershipFunction.mju(-0.5) == 0.0
    assert membershipFunction.mju(0.5) > 0.0
    assert membershipFunction.mju(2.5) == 0.0


def test_SupportSetMutationChangesOnlyLegacyIntegrationWindow():
    membershipFunction = MFunction("sShoulder", a=0.0, b=1.0)
    fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0))
    originalMembership = membershipFunction.mju(1.5)
    originalCentroid = fuzzySet.Defuz()

    fuzzySet.supportSet = (0.0, 2.0)

    assert fuzzySet.supportSet == (0.0, 2.0)
    assert membershipFunction.mju(1.5) == originalMembership
    assert fuzzySet.Defuz() != pytest.approx(originalCentroid, abs=1e-12, rel=0.0)
