"""Validation tests for n-ary fuzzy operator composition."""

import pytest

from fuzzyroutines.FuzzyRoutines import SCoNormCompose, TNormCompose

COMPOSITIONS = (TNormCompose, SCoNormCompose)


@pytest.mark.parametrize("composition", COMPOSITIONS)
@pytest.mark.parametrize("invalidValue", [-0.1, 1.1, True, False, float("nan"), float("inf")])
def test_CompositionRejectsInvalidSingleOperand(composition, invalidValue):
    assert composition(invalidValue) is None, (
        "A one-element composition must enforce the fuzzy-number domain."
    )


@pytest.mark.parametrize("composition", COMPOSITIONS)
@pytest.mark.parametrize("invalidValue", [-0.1, 1.1, "0.5", None])
def test_CompositionRejectsInvalidLaterOperand(composition, invalidValue):
    assert composition(0.5, invalidValue) is None, (
        "Every composition operand must enforce the fuzzy-number domain."
    )


@pytest.mark.parametrize("composition", COMPOSITIONS)
def test_CompositionRejectsUnknownOperatorForSingleOperand(composition):
    assert composition(0.5, normType="unknown") is None, (
        "An unknown operator name must not bypass validation in a one-element composition."
    )
