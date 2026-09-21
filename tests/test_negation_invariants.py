# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Mathematical invariants for supported fuzzy negations."""

import pytest

from fuzzyroutines.FuzzyRoutines import FuzzyNOT, FuzzyNOTParabolic


@pytest.mark.parametrize("fuzzyNumber", [0.0, 0.125, 0.25, 0.5, 0.875, 1.0])
def test_FuzzyNOTStandardNegationInvolution(fuzzyNumber):
    assert FuzzyNOT(FuzzyNOT(fuzzyNumber)) == pytest.approx(fuzzyNumber)


@pytest.mark.parametrize("fuzzyNumber", [0.0, 1.0])
def test_FuzzyNOTStandardNegationSwapsEndpoints(fuzzyNumber):
    assert FuzzyNOT(fuzzyNumber) == 1.0 - fuzzyNumber


def test_FuzzyNOTStandardNegationFixedPoint():
    assert FuzzyNOT(0.5) == pytest.approx(0.5)


@pytest.mark.parametrize("fuzzyNumber", [0.0, 1.0])
def test_FuzzyNOTParabolicSwapsEndpoints(fuzzyNumber):
    assert FuzzyNOTParabolic(fuzzyNumber, alpha=0.5) == 1.0 - fuzzyNumber


@pytest.mark.parametrize("fuzzyNumber", [0.125, 0.25, 0.5, 0.75, 0.875])
def test_FuzzyNOTParabolicHasDocumentedInvolution(fuzzyNumber):
    value = FuzzyNOTParabolic(fuzzyNumber, alpha=0.5)
    assert FuzzyNOTParabolic(value, alpha=0.5) == pytest.approx(fuzzyNumber, abs=1e-12)


@pytest.mark.parametrize(
    "alpha",
    [
        0.0,
        1.0,
        -0.25,
        1.25,
        True,
        False,
        pytest.param(float("nan"), id="nan"),
        float("inf"),
    ],
)
def test_FuzzyNOTRejectsInvalidAlpha(alpha):
    with pytest.raises(ValueError, match="open interval"):
        FuzzyNOT(0.5, alpha=alpha)


@pytest.mark.parametrize(
    "alpha",
    [
        0.0,
        0.2,
        0.8,
        1.0,
        True,
        False,
        pytest.param(float("nan"), id="nan"),
        float("inf"),
    ],
)
def test_FuzzyNOTParabolicRejectsAlphaOutsideProvedInterval(alpha):
    with pytest.raises(ValueError, match="closed interval"):
        FuzzyNOTParabolic(0.5, alpha=alpha)


PARABOLICALPHAS = (0.25, 0.3, 0.5, 0.7, 0.75)
PARABOLICGRID = tuple(index / 100.0 for index in range(101))


@pytest.mark.parametrize("alpha", PARABOLICALPHAS)
def test_FuzzyNOTParabolicSatisfiesDefiningEquation(alpha):
    for fuzzyNumber in PARABOLICGRID:
        result = FuzzyNOTParabolic(fuzzyNumber, alpha=alpha)
        residual = (
            2 * alpha
            - fuzzyNumber
            - result
            - (2 * alpha - 1) * (result - fuzzyNumber) ** 2
        )

        assert residual == pytest.approx(0.0, abs=2e-15, rel=0.0)


@pytest.mark.parametrize("alpha", PARABOLICALPHAS)
def test_FuzzyNOTParabolicIsStrongNegation(alpha):
    values = [FuzzyNOTParabolic(fuzzyNumber, alpha=alpha) for fuzzyNumber in PARABOLICGRID]

    assert values[0] == 1.0
    assert values[-1] == 0.0
    assert FuzzyNOTParabolic(alpha, alpha=alpha) == alpha
    assert all(0.0 <= value <= 1.0 for value in values)
    assert values == sorted(values, reverse=True)

    for fuzzyNumber, value in zip(PARABOLICGRID, values):
        assert FuzzyNOTParabolic(value, alpha=alpha) == pytest.approx(
            fuzzyNumber,
            abs=1e-12,
            rel=0.0,
        )


@pytest.mark.parametrize("epsilon", [0.0, 1e-12, 0.001, 1.0, -1.0])
def test_FuzzyNOTParabolicRetainsButIgnoresLegacyEpsilon(epsilon):
    assert FuzzyNOTParabolic(0.2, alpha=0.3, epsilon=epsilon) == pytest.approx(
        FuzzyNOTParabolic(0.2, alpha=0.3),
        abs=0.0,
        rel=0.0,
    )
