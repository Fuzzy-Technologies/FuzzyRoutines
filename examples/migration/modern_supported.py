# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Run the implemented modern API without claiming roadmap APIs.

Execution writes one deterministic JSON object to stdout, creates no files,
and demonstrates explicit domains, immutable membership functions, and
operator policies through the focused modern implementation.
"""

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
from fuzzyroutines.membership import Triangle


def Main():
    """Print observations from the supported focused modern API."""

    universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
    integrationDomain = IntegrationDomain(0.0, 1.0).ValidateWithin(universe)

    membershipFunction = Triangle(left=0.0, peak=0.5, right=1.0)
    fuzzySet = ScalarFuzzySet(universe, membershipFunction)
    complement = Complement(fuzzySet, NegationPolicy("standard"))
    overlap = Intersection(fuzzySet, complement, TNormPolicy("logic"))

    result = {
        "fuzzySet": fuzzySet.Membership(0.25),
        "integrationDomain": [integrationDomain.left, integrationDomain.right],
        "membership": membershipFunction(0.5),
        "operator": TNormPolicy("algebraic").Evaluate(0.4, 0.7),
        "overlap": overlap.Membership(0.25),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    Main()
