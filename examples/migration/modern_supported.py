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
    integration_domain = IntegrationDomain(0.0, 1.0).ValidateWithin(universe)

    membership_function = Triangle(left=0.0, peak=0.5, right=1.0)
    fuzzy_set = ScalarFuzzySet(universe, membership_function)
    complement = Complement(fuzzy_set, NegationPolicy("standard"))
    overlap = Intersection(fuzzy_set, complement, TNormPolicy("logic"))

    result = {
        "fuzzySet": fuzzy_set.Membership(0.25),
        "integrationDomain": [integration_domain.left, integration_domain.right],
        "membership": membership_function(0.5),
        "operator": TNormPolicy("algebraic").Evaluate(0.4, 0.7),
        "overlap": overlap.Membership(0.25),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    Main()
