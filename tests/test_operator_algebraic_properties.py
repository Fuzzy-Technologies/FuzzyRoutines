# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic property tests for the supported fuzzy operator families.

The finite grid is deliberate: it keeps the suite dependency-free and
reproducible while exercising the algebraic laws required by ADR-0004.
"""

import pytest

from fuzzyroutines.FuzzyRoutines import SCoNorm, TNorm


GRIDVALUES = (0.0, 0.25, 0.5, 0.75, 1.0)
NORMTYPES = ("logic", "algebraic", "boundary", "drastic")


@pytest.mark.parametrize("normType", NORMTYPES)
def test_OperatorCommutativity(normType):
    for leftValue in GRIDVALUES:
        for rightValue in GRIDVALUES:
            assert TNorm(leftValue, rightValue, normType=normType) == TNorm(
                rightValue,
                leftValue,
                normType=normType,
            ), f"TNorm {normType!r} must be commutative."
            assert SCoNorm(leftValue, rightValue, normType=normType) == SCoNorm(
                rightValue,
                leftValue,
                normType=normType,
            ), f"SCoNorm {normType!r} must be commutative."


@pytest.mark.parametrize("normType", NORMTYPES)
def test_OperatorAssociativity(normType):
    for firstValue in GRIDVALUES:
        for secondValue in GRIDVALUES:
            for thirdValue in GRIDVALUES:
                leftTNorm = TNorm(
                    TNorm(firstValue, secondValue, normType=normType),
                    thirdValue,
                    normType=normType,
                )
                rightTNorm = TNorm(
                    firstValue,
                    TNorm(secondValue, thirdValue, normType=normType),
                    normType=normType,
                )
                leftSCoNorm = SCoNorm(
                    SCoNorm(firstValue, secondValue, normType=normType),
                    thirdValue,
                    normType=normType,
                )
                rightSCoNorm = SCoNorm(
                    firstValue,
                    SCoNorm(secondValue, thirdValue, normType=normType),
                    normType=normType,
                )

                assert leftTNorm == pytest.approx(rightTNorm, abs=1e-12, rel=0.0), (
                    f"TNorm {normType!r} must be associative."
                )
                assert leftSCoNorm == pytest.approx(rightSCoNorm, abs=1e-12, rel=0.0), (
                    f"SCoNorm {normType!r} must be associative."
                )


@pytest.mark.parametrize("normType", NORMTYPES)
def test_OperatorBoundaryIdentities(normType):
    for value in GRIDVALUES:
        assert TNorm(value, 1.0, normType=normType) == value, (
            f"TNorm {normType!r} must use one as identity."
        )
        assert TNorm(value, 0.0, normType=normType) == 0.0, (
            f"TNorm {normType!r} must use zero as annihilator."
        )
        assert SCoNorm(value, 0.0, normType=normType) == value, (
            f"SCoNorm {normType!r} must use zero as identity."
        )
        assert SCoNorm(value, 1.0, normType=normType) == 1.0, (
            f"SCoNorm {normType!r} must use one as annihilator."
        )


@pytest.mark.parametrize("normType", NORMTYPES)
def test_OperatorMonotonicity(normType):
    for lowerValue in GRIDVALUES:
        for higherValue in GRIDVALUES:
            if lowerValue > higherValue:
                continue

            for fixedValue in GRIDVALUES:
                assert TNorm(lowerValue, fixedValue, normType=normType) <= TNorm(
                    higherValue,
                    fixedValue,
                    normType=normType,
                ), f"TNorm {normType!r} must be monotone."
                assert SCoNorm(lowerValue, fixedValue, normType=normType) <= SCoNorm(
                    higherValue,
                    fixedValue,
                    normType=normType,
                ), f"SCoNorm {normType!r} must be monotone."


@pytest.mark.parametrize("normType", NORMTYPES)
def test_DeMorganDualityWithStandardComplement(normType):
    for leftValue in GRIDVALUES:
        for rightValue in GRIDVALUES:
            dualTNorm = 1.0 - SCoNorm(
                1.0 - leftValue,
                1.0 - rightValue,
                normType=normType,
            )
            dualSCoNorm = 1.0 - TNorm(
                1.0 - leftValue,
                1.0 - rightValue,
                normType=normType,
            )

            assert TNorm(leftValue, rightValue, normType=normType) == pytest.approx(
                dualTNorm,
                abs=1e-12,
                rel=0.0,
            ), f"TNorm {normType!r} must satisfy De Morgan duality."
            assert SCoNorm(leftValue, rightValue, normType=normType) == pytest.approx(
                dualSCoNorm,
                abs=1e-12,
                rel=0.0,
            ), f"SCoNorm {normType!r} must satisfy De Morgan duality."
