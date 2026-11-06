# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private preparation and finite evaluation of ordered Sugeno consequents."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from fuzzyroutines.batches import _Numpy
from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.exceptions import InvalidParameterTypeError, NumericalError
from fuzzyroutines.inference import AffineConsequent, ConstantConsequent, _FiniteSum

if TYPE_CHECKING:
    from numpy import float64 as Float64
    from numpy import intp as Intp
    from numpy import uint8 as UInt8
    from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class _PreparedConsequent:
    """Finite intercept and ordered feature offsets for one output rule."""

    intercept: float
    coefficients: tuple[tuple[int, float], ...] | None


@dataclass(frozen=True, slots=True)
class _PreparedConsequents:
    """Rule-order output descriptors and a built-in continuous domain snapshot."""

    rules: tuple[_PreparedConsequent, ...]
    outputUniverse: ContinuousUniverse


def _Binary64Value(value: object) -> float:
    """Preserve an exactly representable built-in numeric model value."""

    if type(value) is not int and type(value) is not float:
        raise InvalidParameterTypeError("batch parameters require built-in int or float values")

    try:
        converted = float(value)

    except OverflowError as error:
        raise InvalidParameterTypeError("batch parameters must be finite binary64 values") from error

    if not math.isfinite(converted) or converted != value:
        raise InvalidParameterTypeError("batch parameters must be exactly representable binary64 values")

    return converted


def _PrepareConsequents(
    consequents: tuple[ConstantConsequent | AffineConsequent, ...],
    columns: dict[str, int],
    outputUniverse: ContinuousUniverse,
) -> _PreparedConsequents:
    """Bind validated rule outputs to columns without invoking user hooks."""

    if type(outputUniverse) is not ContinuousUniverse:
        raise InvalidParameterTypeError("batch consequents require a built-in continuous output universe")

    domain = ContinuousUniverse(
        None if outputUniverse.left is None else _Binary64Value(outputUniverse.left),
        None if outputUniverse.right is None else _Binary64Value(outputUniverse.right),
        outputUniverse.leftClosed,
        outputUniverse.rightClosed,
    )
    rules = []

    for consequent in consequents:
        if type(consequent) is ConstantConsequent:
            rules.append(_PreparedConsequent(_Binary64Value(consequent.value), None))

        elif type(consequent) is AffineConsequent:
            if type(consequent.coefficients) is not tuple:
                raise InvalidParameterTypeError("batch coefficients require built-in tuples")

            coefficients = []

            for pair in consequent.coefficients:
                if type(pair) is not tuple or type(pair[0]) is not str:
                    raise InvalidParameterTypeError("batch coefficient bindings require built-in tuples and names")

                name, value = pair
                coefficients.append((columns[name], _Binary64Value(value)))

            rules.append(_PreparedConsequent(_Binary64Value(consequent.intercept), tuple(coefficients)))

        else:
            raise InvalidParameterTypeError("batch consequents require built-in constant or affine types")

    return _PreparedConsequents(tuple(rules), domain)


def _EvaluateConsequents(
    plan: _PreparedConsequents,
    coordinates: NDArray[Float64],
) -> tuple[NDArray[Float64], NDArray[UInt8], NDArray[Intp]]:
    """Evaluate every rule output for rows that passed the firing stage.

    Args:
        plan: Prepared ordered consequents and the shared output universe.
        coordinates: Finite binary64 coordinates in prepared feature order.

    Returns:
        Consequent values, row statuses and the first failing rule index per
        row. A successful row has status zero and index -1. A numerical
        failure has status 5, and a domain failure has status 4. Failed rows
        retain no consequent values, even if earlier rules were successful.
    """

    np = _Numpy()
    rowCount = coordinates.shape[0]
    values: NDArray[Float64] = np.full((rowCount, len(plan.rules)), np.nan, dtype=np.float64)
    status: NDArray[UInt8] = np.zeros(rowCount, dtype=np.uint8)
    failedRule: NDArray[Intp] = np.full(rowCount, -1, dtype=np.intp)

    for rowIndex, row in enumerate(coordinates):
        rowValues: list[float] = row.tolist()

        for ruleIndex, rule in enumerate(plan.rules):
            value = rule.intercept

            if rule.coefficients is not None:
                try:
                    value = _FiniteSum((value, *(
                        coefficient * rowValues[column] for column, coefficient in rule.coefficients
                    )))

                except NumericalError:
                    status[rowIndex] = 5
                    failedRule[rowIndex] = ruleIndex
                    break

            if not plan.outputUniverse.Contains(value):
                status[rowIndex] = 4
                failedRule[rowIndex] = ruleIndex
                break

            values[rowIndex, ruleIndex] = value

    values[status != 0] = np.nan

    return values, status, failedRule
