"""Reference-value contracts for the supported fuzzy operator families.

The formulas and historical family names are defined by ADR-0004.  These tests
cover valid inputs only; invalid-input and composition validation belong to the
separate policy and implementation tasks.
"""

import pytest

from fuzzyroutines.FuzzyRoutines import SCoNorm, TNorm


REFERENCECASES = (
    pytest.param("logic", 0.25, 0.75, 0.25, 0.75, id="logic-interior"),
    pytest.param("algebraic", 0.25, 0.75, 0.1875, 0.8125, id="algebraic-interior"),
    pytest.param("boundary", 0.75, 0.75, 0.5, 1.0, id="boundary-interior"),
    pytest.param("drastic", 1.0, 0.25, 0.25, 1.0, id="drastic-left-identity"),
    pytest.param("drastic", 0.25, 0.0, 0.0, 0.25, id="drastic-right-identity"),
)

NORMTYPES = ("logic", "algebraic", "boundary", "drastic")


@pytest.mark.parametrize(
    ("normType", "leftValue", "rightValue", "expectedTNorm", "expectedSCoNorm"),
    REFERENCECASES,
)
def test_OperatorReferenceValues(
    normType,
    leftValue,
    rightValue,
    expectedTNorm,
    expectedSCoNorm,
):
    actualTNorm = TNorm(leftValue, rightValue, normType=normType)
    actualSCoNorm = SCoNorm(leftValue, rightValue, normType=normType)

    assert actualTNorm == expectedTNorm, (
        f"TNorm {normType!r} violated its reference value for "
        f"({leftValue}, {rightValue})."
    )
    assert actualSCoNorm == expectedSCoNorm, (
        f"SCoNorm {normType!r} violated its reference value for "
        f"({leftValue}, {rightValue})."
    )


@pytest.mark.parametrize("normType", NORMTYPES)
def test_OperatorReferenceBoundaries(normType):
    assert TNorm(0.0, 1.0, normType=normType) == 0.0, (
        f"TNorm {normType!r} must have zero as annihilator."
    )
    assert TNorm(1.0, 1.0, normType=normType) == 1.0, (
        f"TNorm {normType!r} must preserve the all-true boundary."
    )
    assert SCoNorm(0.0, 0.0, normType=normType) == 0.0, (
        f"SCoNorm {normType!r} must preserve the all-false boundary."
    )
    assert SCoNorm(0.0, 1.0, normType=normType) == 1.0, (
        f"SCoNorm {normType!r} must have one as annihilator."
    )
