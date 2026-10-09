# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Optional NumPy membership prototype outside the installed scalar package.

This module has no public-package integration and intentionally requires NumPy
only when array evaluation is requested. Parameters retain historical MFunction
names and geometry; evaluation snapshots and validates them before calculation.
"""

from __future__ import annotations

import importlib
import math
from typing import Any

from fuzzyroutines.FuzzyRoutines import MFunction


def EvaluateMembership(identifier: str, values: Any, **parameters: float) -> Any:
    """Evaluate an experimental binary64 array with the scalar family contract.

    Args:
        identifier: Historical MFunction identifier or existing exact alias.
        values: Non-scalar real numeric array or sequence, converted to float64.
            Boolean, complex, string, and object arrays are rejected. All
            coordinates must remain finite after binary64 conversion.
        **parameters: Exact historical parameter mapping, validated by MFunction.

    Returns:
        A new float64 ndarray with the input shape, containing membership grades.
        Input arrays are neither mutated nor retained. Empty arrays are valid.

    Raises:
        ImportError: If the optional NumPy dependency is absent.
        ValueError: If identifiers, parameters, coordinates, or outputs are invalid.
        OverflowError: If a piecewise/power intermediate exceeds binary64 range.
        ZeroDivisionError: If a squared piecewise denominator underflows to zero.

    Notes:
        Parity targets the scalar evaluator at float-converted coordinates with
        absolute tolerance 1e-12. This prototype is not a general callable adapter
        and makes no all-finite-input or performance guarantee.
    """

    scalarFunction = MFunction(identifier, **parameters)

    try:
        np = importlib.import_module("numpy")

    except ModuleNotFoundError as error:
        if error.name != "numpy":
            raise

        raise ImportError(
            "The isolated array prototype requires experiments/requirements-vectorized.txt."
        ) from error

    source = np.asarray(values)

    if source.ndim == 0 or source.dtype.kind not in "iuf":
        raise ValueError("values must be a real numeric array with at least one dimension")

    with np.errstate(over="ignore", invalid="ignore"):
        coordinates = source.astype(np.float64, copy=True)

    if not np.all(np.isfinite(coordinates)):
        raise ValueError("values must contain only finite binary64 coordinates")

    try:
        with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
            result = _Evaluate(np, scalarFunction.name, coordinates, scalarFunction.parameters)

    except FloatingPointError as error:
        raise OverflowError("membership intermediate is not representable in binary64") from error

    if not np.all(np.isfinite(result)) or np.any(result < 0.0) or np.any(result > 1.0):
        raise ValueError("membership result must be finite and lie in [0, 1]")

    return result


def _SquaredWidth(left: float, right: float) -> float:
    """Return a representable squared width without changing scalar failure modes."""

    squaredWidth = (right - left) ** 2

    if squaredWidth == 0.0:
        raise ZeroDivisionError("membership squared width underflows to zero")

    return squaredWidth


def _Parabolic(np: Any, coordinates: Any, left: float, right: float) -> Any:
    """Evaluate only selected branches of the historical quadratic shoulder."""

    result = np.zeros_like(coordinates)
    rising = (coordinates > left) & (coordinates <= (left + right) / 2)
    falling = (coordinates > (left + right) / 2) & (coordinates < right)

    if np.any(rising) or np.any(falling):
        squaredWidth = _SquaredWidth(left, right)
        result[rising] = 2 * (coordinates[rising] - left) ** 2 / squaredWidth
        result[falling] = 1 - 2 * (coordinates[falling] - right) ** 2 / squaredWidth

    result[coordinates >= right] = 1.0

    return result


def _Evaluate(np: Any, name: str, coordinates: Any, parameters: dict[str, Any]) -> Any:
    """Dispatch validated family snapshots without evaluating inactive branches."""

    if name == "Desirability":
        result = np.zeros_like(coordinates)
        active = coordinates >= -math.log(float.fromhex("0x1.fffffffffffffp+1023"))
        result[active] = np.exp(-np.exp(-coordinates[active]))

        return result

    a = parameters["a"]
    b = parameters["b"]

    if name == "Exponential":
        # Scalar Gaussian intentionally accepts overflow to an infinite distance.
        with np.errstate(over="ignore"):
            scaledDistance = (coordinates - a) / b

            return np.exp(-0.5 * scaledDistance * scaledDistance)

    if name == "Sigmoidal":
        # Separate branches keep every exponential argument non-positive.
        with np.errstate(over="ignore"):
            exponent = a * (coordinates - b)

        result = np.empty_like(coordinates)
        positive = exponent >= 0
        result[positive] = 1 / (1 + np.exp(-exponent[positive]))
        exponential = np.exp(exponent[~positive])
        result[~positive] = exponential / (1 + exponential)

        return result

    if name == "Parabolic":
        return _Parabolic(np, coordinates, a, b)

    c = parameters["c"]

    if name == "Hyperbolic":
        result = np.ones_like(coordinates)
        active = coordinates > c
        result[active] = 1 / (1 + (a * (coordinates[active] - c)) ** b)

        return result

    if name == "Bell":
        result = np.zeros_like(coordinates)
        rising = coordinates < b
        result[rising] = _Parabolic(np, coordinates[rising], a, b)
        result[(coordinates >= b) & (coordinates <= c)] = 1
        rightBoundary = c + b - a
        rightMidpoint = (c + rightBoundary) / 2
        firstFall = (coordinates > c) & (coordinates <= rightMidpoint)
        secondFall = (coordinates > rightMidpoint) & (coordinates < rightBoundary)

        if np.any(firstFall) or np.any(secondFall):
            squaredWidth = _SquaredWidth(c, rightBoundary)
            result[firstFall] = 1 - 2 * (coordinates[firstFall] - c) ** 2 / squaredWidth
            result[secondFall] = 2 * (coordinates[secondFall] - rightBoundary) ** 2 / squaredWidth

        return result

    if name == "Triangle":
        result = np.zeros_like(coordinates)
        rising = (coordinates > a) & (coordinates <= c)
        falling = (coordinates > c) & (coordinates < b)
        result[rising] = (coordinates[rising] - a) / (c - a)

        # c == b is a supported high-term boundary; this branch is empty there.
        if np.any(falling):
            result[falling] = (b - coordinates[falling]) / (b - c)

        return result

    d = parameters["d"]
    result = np.zeros_like(coordinates)
    rising = (coordinates > a) & (coordinates < c)
    falling = (coordinates > d) & (coordinates <= b)
    result[rising] = (coordinates[rising] - a) / (c - a)
    result[(coordinates >= c) & (coordinates <= d)] = 1
    result[falling] = (b - coordinates[falling]) / (b - d)

    return result
