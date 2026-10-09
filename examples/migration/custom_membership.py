# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Use a custom scalar membership evaluator without inheritance or registration."""

from fuzzyroutines.defuzzification import Centroid
from fuzzyroutines.domain import ContinuousUniverse, IntegrationDomain
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.membership import MembershipCallable, MembershipScalar


def RisingGrade(coordinate: MembershipScalar) -> MembershipScalar:
    """Return a linear grade on the closed unit interval enforced by the set."""

    return coordinate


def Main() -> None:
    """Evaluate custom membership and its numerical centroid on a finite domain."""

    membershipFunction: MembershipCallable = RisingGrade
    fuzzySet = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True),
        membershipFunction,
    )
    centroid = Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))
    print(f"Membership at 0.25: {fuzzySet.Membership(0.25)}")
    print(f"Centroid: {centroid:.12f}")


if __name__ == "__main__":
    Main()
