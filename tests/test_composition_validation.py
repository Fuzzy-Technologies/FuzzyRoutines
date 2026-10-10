# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Validation tests for n-ary fuzzy operator composition."""

import pytest

from fuzzyroutines.FuzzyRoutines import SCoNormCompose, TNormCompose

COMPOSITIONS = (TNormCompose, SCoNormCompose)


@pytest.mark.parametrize("composition", COMPOSITIONS)
@pytest.mark.parametrize("family", ["logic", "algebraic", "boundary", "drastic"])
@pytest.mark.parametrize("grade", [0.0, 0.25, 1.0])
def test_CompositionPreservesUnaryIdentity(composition, family, grade):
    """Preserve valid unary calls for every accepted historical family."""

    assert composition(grade, normType=family) == grade, (
        "A nonempty unary fold must retain its validated degree."
    )


@pytest.mark.parametrize("composition", COMPOSITIONS)
@pytest.mark.parametrize('invalidValue', [-0.1, 1.1, True, False, float("nan"), float("inf")])
def test_CompositionRejectsInvalidSingleOperand(composition, invalidValue):
    """Validate a unary operand even when no binary fold is required."""

    with pytest.raises(ValueError, match="finite real number|closed interval"):
        composition(invalidValue)


@pytest.mark.parametrize("composition", COMPOSITIONS)
@pytest.mark.parametrize('invalidValue', [-0.1, 1.1, "0.5", None])
def test_CompositionRejectsInvalidLaterOperand(composition, invalidValue):
    """Reject invalid later operands before a fold can return a result."""

    with pytest.raises(ValueError, match="finite real number|closed interval"):
        composition(0.5, invalidValue)


@pytest.mark.parametrize("composition", COMPOSITIONS)
def test_CompositionRejectsUnknownOperatorForSingleOperand(composition):
    """Validate the selected family independently of operand count."""

    with pytest.raises(ValueError, match="unknown .*norm family"):
        composition(0.5, normType="unknown")
