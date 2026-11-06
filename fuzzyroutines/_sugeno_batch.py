# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private NumPy stages for prepared Sugeno rule batches."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING, cast

from fuzzyroutines.batches import _Numpy
from fuzzyroutines.exceptions import NumericalError
from fuzzyroutines.inference import _ExactRatio, _FiniteSum

if TYPE_CHECKING:
    from numpy import bool_ as Bool
    from numpy import float64 as Float64
    from numpy import uint8 as UInt8
    from numpy.typing import NDArray

_MIN_NORMAL = float.fromhex("0x1.0p-1022")


def _ComputeFirings(
    antecedents: NDArray[Float64],
    weights: NDArray[Float64],
) -> tuple[NDArray[Float64], NDArray[UInt8]]:
    """Compute weighted firings and classify failures for one prepared chunk.

    Args:
        antecedents: Binary64 matrix with one column per rule and only rows
            that have passed coordinate and universe validation.
        weights: Binary64 vector of validated grades, one per rule in
            declaration order. A prepared model has at least one rule.

    Returns:
        Fresh firing strengths and a per-row ADR-0023 status vector. Invalid
        grades or lost positive products have status 5, truly zero firings
        have status 3, and rows ready for consequent evaluation have status 0.
        Failed rows carry NaNs in the firing matrix.
    """

    np = _Numpy()

    with np.errstate(under="ignore", invalid="ignore", over="ignore"):
        validGrades = ((antecedents >= 0.0) & (antecedents <= 1.0)).all(axis=1)
        firings = antecedents * weights
        lostPositive = ((antecedents > 0.0) & (weights > 0.0) & (firings == 0.0)).any(axis=1)

    numericalFailure = ~validGrades | lostPositive
    noFire = ~numericalFailure & ~(firings > 0.0).any(axis=1)
    status = np.zeros(antecedents.shape[0], dtype=np.uint8)
    status[noFire] = 3
    status[numericalFailure] = 5
    firings[status != 0] = np.nan

    return firings, cast("NDArray[UInt8]", status)


@dataclass(frozen=True, slots=True)
class _WeightedChunkTrace:
    """Normalization evidence for the accepted rows of a prepared chunk.

    Attributes:
        normalized: Rounded normalized strengths in declared rule order.
        contributions: Weighted values computed before exact ratios are rounded.
        exactRatio: Entries whose positive normalized strength used an exact ratio.
    """

    normalized: NDArray[Float64]
    contributions: NDArray[Float64]
    exactRatio: NDArray[Bool]


def _CombineConsequents(
    strengths: tuple[float, ...],
    consequences: tuple[float, ...],
    products: tuple[float, ...],
    exactDenominator: Fraction | None,
) -> float:
    """Return a finite sum or recompute the ratio when roundoff escapes the hull."""

    try:
        value = _FiniteSum(products)

    except NumericalError:
        value = float("inf")

    if min(consequences) <= value <= max(consequences):
        return value

    exactStrengths = tuple(_ExactRatio(strength) for strength in strengths)
    denominator = exactDenominator if exactDenominator is not None else sum(exactStrengths, Fraction(0))
    numerator = sum((
        strength * _ExactRatio(consequence)
        for strength, consequence in zip(exactStrengths, consequences, strict=True)
    ), Fraction(0))

    return float(numerator / denominator)


def _ReduceConsequents(
    firings: NDArray[Float64],
    consequents: NDArray[Float64],
    *,
    fullTrace: bool,
) -> tuple[NDArray[Float64], _WeightedChunkTrace | None]:
    """Reduce validated firing and consequent matrices in declared rule order.

    Args:
        firings: Binary64 chunk matrix with at least one positive strength per
            row and no failed rows.
        consequents: Matching finite matrix already checked against the output
            universe, including each inactive rule's consequent.
        fullTrace: Retain per-rule normalization and contribution evidence.

    Returns:
        Fresh scalar values for the accepted chunk rows and, when requested,
        fresh trace arrays. The caller applies final output domain validation.

    Notes:
        Row-local compensated summation and exact-ratio arithmetic follow the
        scalar contract. No rule evaluation or scalar model dispatch occurs here.
    """

    np = _Numpy()
    values: NDArray[Float64] = np.empty(firings.shape[0], dtype=np.float64)
    trace = None

    if fullTrace:
        trace = _WeightedChunkTrace(np.empty_like(firings), np.empty_like(firings), np.zeros(firings.shape, dtype=np.bool_))

    for rowIndex, (firingRow, consequentRow) in enumerate(zip(firings, consequents, strict=True)):
        strengths = tuple(float(strength) for strength in firingRow)
        consequences = tuple(float(consequence) for consequence in consequentRow)
        maximum = max(strengths)
        scaled = tuple(strength / maximum for strength in strengths)
        denominator = _FiniteSum(scaled)
        exactDenominator = None
        products = []

        for ruleIndex, (strength, scaledStrength, consequence) in enumerate(zip(strengths, scaled, consequences, strict=True)):
            normalized = scaledStrength / denominator
            useExact = strength > 0 and normalized < _MIN_NORMAL

            if useExact:
                if exactDenominator is None:
                    exactDenominator = sum((_ExactRatio(item) for item in strengths), Fraction(0))

                exact = _ExactRatio(strength) / exactDenominator
                product = float(exact * _ExactRatio(consequence))
                normalized = float(exact)

            else:
                product = normalized * consequence

            products.append(product)

            if trace is not None:
                trace.normalized[rowIndex, ruleIndex] = normalized
                trace.contributions[rowIndex, ruleIndex] = product
                trace.exactRatio[rowIndex, ruleIndex] = useExact

        values[rowIndex] = _CombineConsequents(strengths, consequences, tuple(products), exactDenominator)

    return values, trace
