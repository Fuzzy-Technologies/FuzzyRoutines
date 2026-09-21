# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Run the currently implemented modern API without claiming roadmap APIs."""

import json

from fuzzyroutines import (
    Complement,
    ContinuousUniverse,
    IntegrationDomain,
    Intersection,
    NegationPolicy,
    ScalarFuzzySet,
    TNormPolicy,
)
from fuzzyroutines.FuzzyRoutines import MFunction


def Main():
    """Print observations from the supported modern and hybrid migration path."""

    universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
    integrationDomain = IntegrationDomain(0.0, 1.0).ValidateWithin(universe)

    # A focused membership-function factory is still roadmap work. The
    # protected factory can supply a callable to the modern set API today.
    membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
    fuzzySet = ScalarFuzzySet(universe, membershipFunction.mju)
    complement = Complement(fuzzySet, NegationPolicy("standard"))
    overlap = Intersection(fuzzySet, complement, TNormPolicy("logic"))

    result = {
        "fuzzySet": fuzzySet.Membership(0.25),
        "integrationDomain": [integrationDomain.left, integrationDomain.right],
        "membership": membershipFunction.mju(0.5),
        "operator": TNormPolicy("algebraic").Evaluate(0.4, 0.7),
        "overlap": overlap.Membership(0.25),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    Main()
