"""Historical centroid observations for the legacy sampling implementation.

The values below freeze the current 1000-point, right-endpoint Riemann policy.
They are provenance evidence for Task #78, not the modern centroid
specification defined by ADR-0005.
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


@pytest.mark.parametrize(("identifier", "parameters", "supportSet", "expectedValue"), REFERENCECASES)
def test_LegacyCentroidReferenceValues(identifier, parameters, supportSet, expectedValue):
    membershipFunction = MFunction(identifier, **parameters)
    fuzzySet = FuzzySet(membershipFunction, supportSet=supportSet)

    assert membershipFunction.accuracy == 1000, (
        "This historical reference is valid only for the 1000-point legacy policy."
    )
    assert fuzzySet.Defuz() == pytest.approx(expectedValue, abs=1e-12, rel=0.0), (
        f"The frozen legacy centroid changed for {identifier!r} on {supportSet!r}."
    )
    assert fuzzySet._Defuz() == pytest.approx(expectedValue, abs=1e-12, rel=0.0), (
        "The construction-time cache must initially match its historical calculation."
    )
