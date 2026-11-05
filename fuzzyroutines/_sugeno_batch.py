# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private NumPy stages for prepared Sugeno rule batches."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from fuzzyroutines.batches import _Numpy

if TYPE_CHECKING:
    from numpy import float64 as Float64
    from numpy import uint8 as UInt8
    from numpy.typing import NDArray


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
