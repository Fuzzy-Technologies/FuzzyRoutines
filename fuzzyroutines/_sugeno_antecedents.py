# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private compilation and NumPy evaluation of ordered Sugeno antecedents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, cast

from fuzzyroutines.batches import _Numpy
from fuzzyroutines.exceptions import InvalidParameterTypeError
from fuzzyroutines.inference import (
    AllOf,
    Antecedent,
    AnyOf,
    InferencePolicy,
    NotCondition,
    TermCondition,
)
from fuzzyroutines.operators import NegationPolicy, SNormPolicy, TNormPolicy

if TYPE_CHECKING:
    from numpy import float64 as Float64
    from numpy.typing import NDArray

type _Instruction = tuple[Literal["term", "not", "all", "any"], int]


@dataclass(frozen=True, slots=True)
class _PreparedAntecedents:
    """Ordered rule programs and validated built-in operator settings."""

    programs: tuple[tuple[_Instruction, ...], ...]
    conjunction: str
    disjunction: str
    negation: str
    alpha: float | None


def _Lower(
    expression: Antecedent,
    columns: dict[tuple[str, str], int],
    program: list[_Instruction],
) -> None:
    """Emit a left fold while rejecting expression subclasses before field access."""

    if type(expression) is TermCondition:
        if type(expression.variable) is not str or type(expression.term) is not str:
            raise InvalidParameterTypeError("batch antecedent references must use built-in strings")

        program.append(("term", columns[expression.variable, expression.term]))

    elif type(expression) is NotCondition:
        _Lower(expression.operand, columns, program)
        program.append(("not", 0))

    elif type(expression) is AllOf or type(expression) is AnyOf:
        operation: Literal["all", "any"] = "all" if type(expression) is AllOf else "any"
        _Lower(expression.operands[0], columns, program)

        for child in expression.operands[1:]:
            _Lower(child, columns, program)
            program.append((operation, 0))

    else:
        raise InvalidParameterTypeError("batch antecedents require built-in condition types")


def _PrepareAntecedents(
    expressions: tuple[Antecedent, ...],
    columns: dict[tuple[str, str], int],
    policy: InferencePolicy,
) -> _PreparedAntecedents:
    """Bind validated rule expressions to pre-evaluated grade column indices.

    The column map comes from model metadata and contains only built-in
    name pairs. The prepared plan retains no executable user objects.
    """

    if type(policy) is not InferencePolicy or (
        type(policy.conjunction) is not TNormPolicy
        or type(policy.disjunction) is not SNormPolicy
        or type(policy.negation) is not NegationPolicy
    ):
        raise InvalidParameterTypeError("batch antecedents require built-in inference policies")

    conjunction = policy.conjunction.family
    disjunction = policy.disjunction.family
    negation = policy.negation.family
    alpha = policy.negation.alpha

    if any(type(family) is not str for family in (conjunction, disjunction, negation)) or (
        alpha is not None and type(alpha) is not float
    ):
        raise InvalidParameterTypeError("batch antecedent policies require built-in parameters")

    programs = []

    for expression in expressions:
        program: list[_Instruction] = []
        _Lower(expression, columns, program)
        programs.append(tuple(program))

    return _PreparedAntecedents(tuple(programs), conjunction, disjunction, negation, alpha)


def _Combine(
    np: Any,
    family: str,
    conjunction: bool,
    left: NDArray[Float64],
    right: NDArray[Float64],
) -> NDArray[Float64]:
    """Apply the scalar binary64 norm branches to one pair of grade vectors."""

    if family == "logic":
        takeRight = right < left if conjunction else right > left

        return cast("NDArray[Float64]", np.where(takeRight, right, left))

    if family == "algebraic":
        return left * right if conjunction else left + right - left * right

    if family == "boundary":
        return cast("NDArray[Float64]", np.maximum(left + right - 1, 0) if conjunction else np.minimum(left + right, 1))

    if conjunction:
        return cast("NDArray[Float64]", np.where(left == 1, right, np.where(right == 1, left, 0.0)))

    return cast("NDArray[Float64]", np.where(left == 0, right, np.where(right == 0, left, 1.0)))


def _Negate(np: Any, family: str, alpha: float | None, grades: NDArray[Float64]) -> NDArray[Float64]:
    """Apply only the active binary64 negation branch to each grade."""

    if family == "standard":
        return 1 - grades

    fixedPoint = cast(float, alpha)

    if family == "parametric":
        lower = grades <= fixedPoint
        result = np.empty_like(grades)
        result[lower] = grades[lower] * (fixedPoint - 1) / fixedPoint + 1
        result[~lower] = (grades[~lower] - 1) * fixedPoint / (fixedPoint - 1)

        return cast("NDArray[Float64]", result)

    if fixedPoint <= 0.5:
        discriminant = (4 * fixedPoint - 1) ** 2 + 8 * (1 - 2 * fixedPoint) * grades

    else:
        discriminant = (4 * fixedPoint - 3) ** 2 + 8 * (2 * fixedPoint - 1) * (1 - grades)

    result = grades + 4 * (fixedPoint - grades) / (1 + np.sqrt(discriminant))

    return cast("NDArray[Float64]", np.where(grades == 0, 1.0, np.where(grades == 1, 0.0, result)))


def _EvaluateAntecedents(plan: _PreparedAntecedents, termGrades: NDArray[Float64]) -> NDArray[Float64]:
    """Return a fresh rule-grade matrix for a prepared binary64 term chunk.

    Every term column has already passed membership validation. A nonfinite
    or out-of-range intermediate grade is marked NaN at that rule so the
    firing stage can classify the row as a numerical failure.
    """

    np = _Numpy()
    output: NDArray[Float64] = np.empty((termGrades.shape[0], len(plan.programs)), dtype=np.float64)

    with np.errstate(under="ignore", invalid="ignore", over="ignore", divide="ignore"):
        for ruleIndex, program in enumerate(plan.programs):
            stack: list[NDArray[Float64]] = []
            valid = np.ones(termGrades.shape[0], dtype=np.bool_)

            for operation, index in program:
                if operation == "term":
                    stack.append(termGrades[:, index])
                    continue

                right = stack.pop()

                if operation == "not":
                    value = _Negate(np, plan.negation, plan.alpha, right)

                else:
                    conjunction = operation == "all"
                    family = plan.conjunction if conjunction else plan.disjunction
                    value = _Combine(np, family, conjunction, stack.pop(), right)

                valid &= (value >= 0.0) & (value <= 1.0)
                stack.append(value)

            output[:, ruleIndex] = np.where(valid, stack.pop(), np.nan)

    return output
