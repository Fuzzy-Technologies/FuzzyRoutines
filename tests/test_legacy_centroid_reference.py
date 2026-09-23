# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Historical sampling observations and corrected-centroid compatibility.

The values below preserve Task #78 provenance for the retired 1000-point
right-endpoint calculation. Production centroids follow ADR-0005 and remain
within the declared `5e-4` compatibility bound for these valid cases.
"""

import pytest

from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

REFERENCECASES = (
    pytest.param(
        "hyperbolic",
        {"a": 7.0, "b": 4.0, "c": 0.0},
        (0.0, 1.0),
        0.10010669588790079,
        id="default-scale-minimum",
    ),
    pytest.param(
        "bell",
        {"a": 0.35, "b": 0.5, "c": 0.6},
        (0.0, 1.0),
        0.5500000000000003,
        id="default-scale-medium",
    ),
    pytest.param(
        "triangle",
        {"a": 0.7, "b": 1.0, "c": 1.0},
        (0.0, 1.0),
        0.9003333333333334,
        id="default-scale-high",
    ),
    pytest.param(
        "parabolic",
        {"a": 0.0, "b": 1.0},
        (0.0, 1.0),
        0.7086248751248754,
        id="parabolic-full-support",
    ),
)


def _LegacyCentroid(membershipFunction, supportSet):
    """Reproduce the frozen Task #78 algorithm without using production code."""

    left, right = supportSet
    step = (right - left) / 1000
    numerator = 0.0
    denominator = 0.0

    for iteration in range(1000):
        coordinate = left + (iteration + 1) * step
        grade = membershipFunction.mju(coordinate)
        numerator += coordinate * grade
        denominator += grade

    return numerator / denominator


@pytest.mark.parametrize(("identifier", "parameters", "supportSet", "expectedValue"), REFERENCECASES)
def test_LegacyCentroidReferenceValues(identifier, parameters, supportSet, expectedValue):
    membershipFunction = MFunction(identifier, **parameters)
    fuzzySet = FuzzySet(membershipFunction, supportSet=supportSet)

    assert membershipFunction.accuracy == 1000, (
        "This historical reference is valid only for the 1000-point legacy policy."
    )
    assert _LegacyCentroid(membershipFunction, supportSet) == pytest.approx(
        expectedValue,
        abs=1e-12,
        rel=0.0,
    ), f"The frozen Task #78 observation changed for {identifier!r}."
    assert fuzzySet.Defuz() == pytest.approx(expectedValue, abs=5e-4, rel=0.0), (
        f"The corrected centroid exceeded compatibility tolerance for {identifier!r}."
    )
    assert fuzzySet._Defuz() == fuzzySet.Defuz(), (
        "Both compatibility entry points must expose the current corrected calculation."
    )
