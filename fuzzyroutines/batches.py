# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Explicit optional NumPy batches for built-in scalar membership and scales.

Importing this module does not import NumPy. Calling a batch operation opts in
to binary64 array evaluation; ordinary scalar APIs never dispatch here. The
analytical snapshots and branch definitions come from ``membership``. This
module lowers those branches to masked array operations, with scalar-reference
parity tests guarding the translation. See ADR-0018 for the bounded contract.
"""

from __future__ import annotations

import importlib
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, cast

from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.linguistic import FuzzificationPolicy, LinguisticScale
from fuzzyroutines.membership import (
    MembershipFunction,
    _AnalyticalSource,
    _GetAnalyticalSource,
)

if TYPE_CHECKING:
    import numpy as np
    from numpy import float64 as Float64
    from numpy.typing import NDArray

__all__ = ["EvaluateMembershipBatch", "FuzzifyBatch", "ScaleBatchResult"]


def _Numpy(backend: str = "numpy") -> Any:
    """Load the only supported backend after an explicit batch request."""

    if backend != "numpy":
        raise InvalidParameterError("backend must be 'numpy'; automatic dispatch is not supported")

    try:
        return importlib.import_module("numpy")

    except ModuleNotFoundError as error:
        if error.name != "numpy":
            raise

        raise ImportError(
            "NumPy batches require the optional dependency: pip install 'fuzzyroutines[numpy]'"
        ) from error


def _RejectBooleanSequence(np: Any, values: object) -> None:
    """Prevent mixed Python sequences from silently coercing booleans to numbers."""

    if isinstance(values, np.ndarray) and values.dtype.kind == "b":
        raise InvalidParameterTypeError("batch coordinates must not contain Boolean arrays")

    if isinstance(values, (list, tuple)):
        for value in values:
            if isinstance(value, (bool, np.bool_)):
                raise InvalidParameterTypeError("batch coordinates must not contain booleans")

            if isinstance(value, (list, tuple, np.ndarray)):
                _RejectBooleanSequence(np, value)


def _Coordinates(np: Any, values: object) -> Any:
    """Make a private binary64 snapshot of a real array with positive rank."""

    _RejectBooleanSequence(np, values)
    source = np.asarray(values)

    if source.ndim == 0 or source.dtype.kind not in "iuf":
        raise InvalidParameterTypeError("values must be a real numeric array of rank at least one")

    with np.errstate(over="ignore", invalid="ignore", under="ignore"):
        coordinates = source.astype(np.float64, copy=True, order="C")

    if not np.all(np.isfinite(coordinates)):
        raise InvalidParameterError("values must remain finite after binary64 conversion")

    return coordinates


def _Source(function: MembershipFunction) -> _AnalyticalSource:
    """Require trusted built-in evaluation and preserve its parameter snapshot."""

    if not isinstance(function, MembershipFunction):
        raise InvalidParameterTypeError("batch evaluation requires a built-in MembershipFunction")

    source = _GetAnalyticalSource(function)

    if source is None:
        raise InvalidParameterTypeError("overridden membership evaluators are not batch eligible")

    for _, value in source.parameterItems:
        if not isinstance(value, (int, float)) or float(value) != value:
            raise InvalidParameterTypeError("batch parameters must be exactly representable binary64 int/float values")

    # Exact binary64 representability does not make int arithmetic identical to
    # float arithmetic: integer endpoint sums must retain their scalar order.
    return _AnalyticalSource(source.name, source.parameterItems)


def _SquaredWidth(left: float, right: float) -> float:
    """Retain the scalar quadratic family's overflow and zero-width failures."""

    width = (right - left) ** 2

    if width == 0:
        raise ZeroDivisionError("membership squared width underflows to zero")

    return width


def _Ratio(np: Any, left: Any, right: Any, denominatorLeft: float, denominatorRight: float) -> Any:
    """Lower scalar _DifferenceRatio, including overflowing endpoint differences."""

    with np.errstate(over="ignore", invalid="ignore"):
        numerator = left - right
        denominator = denominatorLeft - denominatorRight
        extreme = np.isinf(numerator) | (abs(denominator) == math.inf)
        result = np.empty_like(numerator)

        if np.any(~extreme):
            result[~extreme] = numerator[~extreme] / denominator

        if np.any(extreme):
            safe = (left / 2 - right / 2) / (denominatorLeft / 2 - denominatorRight / 2)
            result[extreme] = safe[extreme]

    return result


def _Shoulder(np: Any, coordinates: Any, left: float, right: float) -> Any:
    """Lower only active branches of the canonical quadratic shoulder."""

    result = np.zeros_like(coordinates)
    midpoint = (left + right) / 2
    rising = (coordinates > left) & (coordinates <= midpoint)
    falling = (coordinates > left) & (coordinates > midpoint) & (coordinates < right)

    if np.any(rising) or np.any(falling):
        width = _SquaredWidth(left, right)
        result[rising] = 2 * (coordinates[rising] - left) ** 2 / width
        result[falling] = 1 - 2 * (coordinates[falling] - right) ** 2 / width

    result[coordinates >= right] = 1

    return result


def _Kernel(np: Any, source: _AnalyticalSource, coordinates: Any) -> Any:
    """Evaluate masks in the same order as membership._FORMULAS branches."""

    parameters = dict(source.parameterItems)
    name = source.name

    if name == "Desirability":
        result = np.zeros_like(coordinates)
        active = coordinates >= -math.log(float.fromhex("0x1.fffffffffffffp+1023"))
        result[active] = np.exp(-np.exp(-coordinates[active]))

        return result

    a, b = cast(float, parameters["a"]), cast(float, parameters["b"])

    if name in ("Exponential", "Sigmoidal"):
        # These two scalar families deliberately saturate overflowing products.
        with np.errstate(over="ignore", invalid="ignore"):
            distance = coordinates - (a if name == "Exponential" else b)
            extreme = np.isinf(distance)

            if name == "Exponential":
                scaled = distance / b

                if np.any(extreme):
                    scaled[extreme] = coordinates[extreme] / b - a / b

                return np.exp(-0.5 * scaled * scaled)

            exponent = a * distance

            if np.any(extreme):
                exponent[extreme] = a * coordinates[extreme] - a * b

        result = np.empty_like(coordinates)
        positive = exponent >= 0
        result[positive] = 1 / (1 + np.exp(-exponent[positive]))
        exponential = np.exp(exponent[~positive])
        result[~positive] = exponential / (1 + exponential)

        return result

    if name == "Parabolic":
        return _Shoulder(np, coordinates, a, b)

    c = cast(float, parameters["c"])

    if name == "Hyperbolic":
        result = np.ones_like(coordinates)
        active = coordinates > c
        # Python's multiplication may become infinity before exponentiation;
        # a finite base whose power overflows still raises in both paths.
        with np.errstate(over="ignore"):
            base = a * (coordinates[active] - c)

        result[active] = 1 / (1 + base ** b)

        return result

    if name == "Bell":
        result = np.zeros_like(coordinates)
        rising = coordinates < b
        result[rising] = _Shoulder(np, coordinates[rising], a, b)
        result[(coordinates >= b) & (coordinates <= c)] = 1

        if not np.any(coordinates > c):
            return result

        right = c + b - a
        midpoint = (c + right) / 2
        first = (coordinates > c) & (coordinates <= midpoint)
        second = (coordinates > c) & (coordinates > midpoint) & (coordinates < right)

        if np.any(first) or np.any(second):
            width = _SquaredWidth(c, right)
            result[first] = 1 - 2 * (coordinates[first] - c) ** 2 / width
            result[second] = 2 * (coordinates[second] - right) ** 2 / width

        return result

    result = np.zeros_like(coordinates)

    if name == "Triangle":
        rising = (coordinates > a) & (coordinates <= c)
        falling = (coordinates > c) & (coordinates < b)
        result[rising] = _Ratio(np, coordinates[rising], a, c, a)

        if np.any(falling):
            result[falling] = _Ratio(np, b, coordinates[falling], b, c)

        return result

    d = cast(float, parameters["d"])
    rising = (coordinates > a) & (coordinates < c)
    falling = (coordinates > d) & (coordinates <= b)
    result[rising] = _Ratio(np, coordinates[rising], a, c, a)
    result[(coordinates >= c) & (coordinates <= d)] = 1
    result[falling] = _Ratio(np, b, coordinates[falling], b, d)

    return result


def _Evaluate(np: Any, source: _AnalyticalSource, coordinates: Any) -> Any:
    """Isolate NumPy error state and reject invalid grades atomically."""

    try:
        with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
            result = _Kernel(np, source, coordinates)

    except FloatingPointError as error:
        raise OverflowError("membership intermediate is not representable in binary64") from error

    if not np.all(np.isfinite(result)) or np.any(result < 0) or np.any(result > 1):
        raise InvalidParameterError("membership results must be finite and lie in [0, 1]")

    return result


def EvaluateMembershipBatch(
    function: MembershipFunction,
    values: object,
    *,
    backend: Literal["numpy"] = "numpy",
) -> NDArray[np.float64]:
    """Evaluate one built-in membership function on a fresh binary64 array.

    Args:
        function: Unmodified built-in family with binary64 int/float parameters.
        values: Numeric array or rectangular sequence of rank at least one.
            Empty and noncontiguous arrays are allowed. Coordinates are copied
            and converted to float64; booleans, complex/object/string arrays and
            nonfinite converted coordinates are rejected.
        backend: Explicit optional backend; only ``"numpy"`` is supported.

    Returns:
        New writable float64 array with exactly the input shape. No input
        buffer is mutated or retained. Grades are never normalized.

    Raises:
        ImportError: NumPy is absent; the message includes the installation extra.
        TypeError: Input dtype, evaluator or parameter representation is unsupported.
        ValueError: Backend, coordinates or computed grades violate the contract.
        OverflowError: A selected arithmetic branch has an invalid/overflowing intermediate.
        ZeroDivisionError: An active quadratic branch has an underflowed squared width.

    Notes:
        Parity is with the scalar function at float64-converted coordinates,
        with absolute tolerance 1e-12 and zero relative tolerance. The operation
        fails as a whole; it does not return partial results or fall back to a
        scalar loop. Existing scalar signatures and arithmetic remain unchanged.
    """

    source = _Source(function)
    np = _Numpy(backend)

    return cast("NDArray[Float64]", _Evaluate(np, source, _Coordinates(np, values)))


def _Selection(np: Any, memberships: Any, policy: FuzzificationPolicy) -> tuple[Any, Any, Any]:
    """Lower the modern binary64 confidence, tolerance, and tie rules."""

    confidence = np.max(memberships, axis=-1)
    difference = confidence[..., None] - memberships
    tolerance = float(policy.tieTolerance)
    tied = difference <= tolerance

    if tolerance > 0 and isinstance(policy.tieTolerance, float):
        with np.errstate(under="ignore"):
            tied |= np.abs(difference - tolerance) <= 1e-12 * np.maximum(np.abs(difference), tolerance)

    tied &= confidence[..., None] > float(policy.minimumConfidence)

    if policy.tiePolicy == "all":
        selected = tied.copy()

    elif policy.tiePolicy == "first":
        selected = tied & (np.cumsum(tied, axis=-1) == 1)

    else:
        selected = tied & (np.cumsum(tied[..., ::-1], axis=-1)[..., ::-1] == 1)

    return confidence, tied, selected


@dataclass(frozen=True, slots=True)
class ScaleBatchResult:
    """Owned read-only arrays describing every coordinate and ordered term.

    Attributes:
        termNames: Declared scale term names in their original order.
        memberships: Float64 grades with shape ``input_shape + (term_count,)``.
        confidence: Float64 maximum grades with shape ``input_shape``.
        tied: Boolean mask of policy-equivalent maxima, with membership shape.
        selected: Boolean mask after first/last/all selection; false for no match.
        policy: The unchanged scalar classification policy used for selection.

    Notes:
        Arrays are copied and made read-only at construction. Call ``copy()``
        for a writable buffer. Memberships are independent grades, not a
        probability distribution; no row normalization is applied.
    """

    termNames: tuple[str, ...]
    memberships: NDArray[np.float64]
    confidence: NDArray[np.float64]
    tied: NDArray[np.bool_]
    selected: NDArray[np.bool_]
    policy: FuzzificationPolicy

    def __post_init__(self) -> None:
        """Validate complete classification evidence and detach all supplied buffers."""

        np = _Numpy()

        if not isinstance(self.termNames, tuple) or not self.termNames:
            raise InvalidParameterTypeError("termNames must be a non-empty tuple")

        if any(not isinstance(name, str) or not name.strip() for name in self.termNames):
            raise InvalidParameterTypeError("termNames must contain non-empty strings")

        if len({name.casefold() for name in self.termNames}) != len(self.termNames):
            raise InvalidParameterError("termNames must be unique ignoring case")

        if not isinstance(self.policy, FuzzificationPolicy):
            raise InvalidParameterTypeError("policy must be a FuzzificationPolicy")

        if any(not isinstance(value, (int, float)) for value in (self.policy.tieTolerance, self.policy.minimumConfidence)):
            raise InvalidParameterTypeError("batch policy thresholds require binary64 int/float values")

        grades = self.memberships

        if not isinstance(grades, np.ndarray) or grades.dtype != np.float64 or grades.ndim < 2:
            raise InvalidParameterTypeError("memberships must be a float64 array of rank at least two")

        if grades.shape[-1] != len(self.termNames):
            raise InvalidParameterError("membership last axis must match termNames")

        if not np.all(np.isfinite(grades)) or np.any(grades < 0) or np.any(grades > 1):
            raise InvalidParameterError("memberships must be finite grades in [0, 1]")

        expected = _Selection(np, grades, self.policy)

        for name, reference in zip(("confidence", "tied", "selected"), expected, strict=True):
            actual = getattr(self, name)

            if not isinstance(actual, np.ndarray) or actual.dtype != reference.dtype:
                raise InvalidParameterTypeError(f"{name} has an invalid array dtype")

            if actual.shape != reference.shape or not np.array_equal(actual, reference):
                raise InvalidParameterError(f"{name} contradicts memberships and policy")

        for name in ("memberships", "confidence", "tied", "selected"):
            owned = getattr(self, name).copy(order="C")
            owned.setflags(write=False)
            object.__setattr__(self, name, owned)


def _ValidateUniverse(np: Any, universe: ContinuousUniverse | DiscreteUniverse, coordinates: Any) -> None:
    """Apply scalar universe membership without coercing exact domain endpoints."""

    if type(universe) not in (ContinuousUniverse, DiscreteUniverse):
        raise InvalidParameterTypeError("batch evaluation requires a standard continuous or discrete universe")

    if isinstance(universe, DiscreteUniverse):
        endpoints = universe.points

    else:
        endpoints = tuple(value for value in (universe.left, universe.right) if value is not None)

    if any(not isinstance(value, (int, float)) or float(value) != value for value in endpoints):
        raise InvalidParameterTypeError("batch universe endpoints must be exactly representable binary64 int/float values")

    if isinstance(universe, DiscreteUniverse):
        valid = np.isin(coordinates, universe.points)

    else:
        valid = np.ones_like(coordinates, dtype=np.bool_)

        if universe.left is not None:
            valid &= coordinates >= universe.left if universe.leftClosed else coordinates > universe.left

        if universe.right is not None:
            valid &= coordinates <= universe.right if universe.rightClosed else coordinates < universe.right

    if not np.all(valid):
        raise InvalidDomainError("every coordinate must belong to every term universe")


def FuzzifyBatch(
    scale: LinguisticScale,
    values: object,
    policy: FuzzificationPolicy | None = None,
    *,
    backend: Literal["numpy"] = "numpy",
) -> ScaleBatchResult:
    """Classify an array with built-in scale terms and explicit scalar policies.

    Args:
        scale: Modern scale whose term functions are eligible built-in families.
            Continuous and discrete universes require binary64 int/float bounds.
        values: Coordinates accepted by ``EvaluateMembershipBatch`` and belonging
            to every term universe. A violation rejects the entire batch.
        policy: Existing first/last/all tie policy; default selects the first
            exact maximum and rejects zero coverage. Thresholds must be binary64
            int/float values; arbitrary rational policies remain scalar-only.
        backend: Explicit optional backend, currently only ``"numpy"``.

    Returns:
        Ordered grades, confidence, all ties, and selected-term boolean masks.
        Each output array is independently owned and read-only. Empty batches
        preserve their shape, including the trailing term axis.

    Raises:
        ImportError: Optional NumPy is absent.
        TypeError: A scale, policy, evaluator, dtype or numeric representation
            is unsupported. Generic, normalized or composed callables remain scalar.
        ValueError: Backend, coordinates, universes or computed grades are invalid.
        ArithmeticError: A selected membership branch cannot be evaluated.

    Notes:
        Coordinate normalization, grade normalization, probability conversion,
        inference and defuzzification are not performed. The scalar policy's
        explicit near-tie accommodation is preserved for float tolerances.
    """

    if not isinstance(scale, LinguisticScale):
        raise InvalidParameterTypeError("scale must be a LinguisticScale")

    if (
        type(scale).Fuzzify is not LinguisticScale.Fuzzify
        or getattr(scale.Fuzzify, "__func__", None) is not LinguisticScale.Fuzzify
        or getattr(scale.Fuzzify, "__self__", None) is not scale
    ):
        raise InvalidParameterTypeError("overridden scale evaluators are not batch eligible")

    if policy is None:
        policy = FuzzificationPolicy()

    if not isinstance(policy, FuzzificationPolicy):
        raise InvalidParameterTypeError("policy must be a FuzzificationPolicy")

    if any(not isinstance(value, (int, float)) for value in (policy.tieTolerance, policy.minimumConfidence)):
        raise InvalidParameterTypeError("batch policy thresholds require binary64 int/float values")

    for term in scale.terms:
        if (
            type(term.fuzzySet).Membership is not ScalarFuzzySet.Membership
            or getattr(term.fuzzySet.Membership, "__func__", None) is not ScalarFuzzySet.Membership
            or getattr(term.fuzzySet.Membership, "__self__", None) is not term.fuzzySet
        ):
            raise InvalidParameterTypeError("overridden fuzzy-set evaluators are not batch eligible")

    sources = tuple(_Source(cast(MembershipFunction, term.fuzzySet.membershipFunction)) for term in scale.terms)
    np = _Numpy(backend)
    coordinates = _Coordinates(np, values)

    for term in scale.terms:
        _ValidateUniverse(np, term.fuzzySet.universe, coordinates)

    grades = np.stack([_Evaluate(np, source, coordinates) for source in sources], axis=-1)
    confidence, tied, selected = _Selection(np, grades, policy)

    return ScaleBatchResult(tuple(term.name for term in scale.terms), grades, confidence, tied, selected, policy)
