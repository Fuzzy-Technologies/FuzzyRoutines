"""Validation tests for n-ary fuzzy operator composition."""

import pytest

from fuzzyroutines.FuzzyRoutines import SCoNormCompose, TNormCompose

COMPOSITIONS = (TNormCompose, SCoNormCompose)


@pytest.mark.parametrize("composition", COMPOSITIONS)
@pytest.mark.parametrize("invalidValue", [-0.1, 1.1, True, False, float("nan"), float("inf")])
def test_CompositionRejectsInvalidSingleOperand(composition, invalidValue):
    with pytest.raises(ValueError, match="finite real number|closed interval"):
        composition(invalidValue)


@pytest.mark.parametrize("composition", COMPOSITIONS)
@pytest.mark.parametrize("invalidValue", [-0.1, 1.1, "0.5", None])
def test_CompositionRejectsInvalidLaterOperand(composition, invalidValue):
    with pytest.raises(ValueError, match="finite real number|closed interval"):
        composition(0.5, invalidValue)


@pytest.mark.parametrize("composition", COMPOSITIONS)
def test_CompositionRejectsUnknownOperatorForSingleOperand(composition):
    with pytest.raises(ValueError, match="unknown .*norm family"):
        composition(0.5, normType="unknown")
