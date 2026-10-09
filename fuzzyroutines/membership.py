# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Immutable scalar membership functions with explicit geometric parameters.

These analytical families own their scalar formulas. Historical adapters map
legacy parameter order to this core; importing this module never imports the
mutable compatibility API. Floating-point evaluation retains the established
arithmetic and boundary behavior, including underflow in positive tails.
"""

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Real
from types import MappingProxyType, MethodType
from typing import Protocol, cast

from fuzzyroutines.exceptions import InvalidParameterError
from fuzzyroutines.numeric import _RequireFiniteReal

__all__ = [
    "Bell",
    "Gaussian",
    "HarringtonDesirability",
    "Hyperbolic",
    "Logistic",
    "MembershipCallable",
    "MembershipFunction",
    "MembershipScalar",
    "SShoulder",
    "Trapezoid",
    "Triangle",
]


type MembershipScalar = float | Real
"""Scalar typing vocabulary including built-in floats and registered real types.

Built-in integers are compatible with `float` in Python's static numeric tower.
The `Real` alternative retains the broader runtime scalar contract; finite
values and exclusion of booleans remain runtime requirements, not type checks.
"""


class MembershipCallable(Protocol):
    """Structural scalar contract for built-in or user-defined membership.

    Functions, lambdas, bound methods, and callable objects need no inheritance
    or registration. A conforming evaluator accepts one positional finite
    real coordinate excluding booleans, and returns a finite real
    grade in the closed interval $[0, 1]$, also excluding booleans.

    This protocol describes a typing contract; it does not validate a callable
    at runtime. `ScalarFuzzySet.Membership` validates the coordinate against its
    universe before calling the evaluator, then validates the returned grade.
    Direct calls to a custom evaluator retain that evaluator's own behavior.
    Exceptions raised by the custom evaluator propagate unchanged.

    Generic callables provide no analytical evidence for exact continuous
    properties. Numerical centroid integration requires a sufficiently regular
    function whose grades remain consistent during one integration. Internal
    state such as a call counter is allowed when it does not alter those grades.
    Use `MembershipScalar` for custom annotations: `numbers.Real` alone does
    not include built-in `float` and `int` in common static type checkers.
    """

    def __call__(self, coordinate: MembershipScalar, /) -> MembershipScalar:
        """Return one finite grade in $[0, 1]$ for a finite real coordinate.

        Args:
            coordinate: Positional real scalar, finite and not boolean.

        Returns:
            Finite real membership grade in $[0, 1]$, not boolean.
        """

        ...


def _ValidateFamilyParameters(family_name: str, parameters: dict[str, MembershipScalar]) -> dict[str, float]:
    """Validate canonical analytical geometry without coercion or mutation."""

    required_parameters = {
        'Hyperbolic': ('a', 'b', 'c'),
        'Bell': ('a', 'b', 'c'),
        'Parabolic': ('a', 'b'),
        'Triangle': ('a', 'b', 'c'),
        'Trapezium': ('a', 'b', 'c', 'd'),
        'Exponential': ('a', 'b'),
        'Sigmoidal': ('a', 'b'),
        'Desirability': (),
    }[family_name]

    if not isinstance(parameters, dict) or set(parameters) != set(required_parameters):
        raise ValueError(
            "{} membership function requires exactly these parameters: {}".format(
                family_name,
                ', '.join(required_parameters) if required_parameters else 'none',
            )
        )

    arithmetic_parameters = cast(dict[str, float], parameters)

    for parameter_name in required_parameters:
        parameter_value = parameters[parameter_name]

        if (isinstance(parameter_value, bool) or not isinstance(parameter_value, Real)) or not math.isfinite(parameter_value):
            raise ValueError(
                f"{family_name} parameter {parameter_name!r} must be a finite real number"
            )

    if family_name == 'Hyperbolic':
        if arithmetic_parameters['a'] <= 0 or arithmetic_parameters['b'] <= 0:
            raise ValueError("Hyperbolic parameters must satisfy a > 0 and b > 0")

    elif family_name == 'Bell':
        if not arithmetic_parameters['a'] < arithmetic_parameters['b'] <= arithmetic_parameters['c']:
            raise ValueError("Bell parameters must satisfy a < b <= c")

    elif family_name == 'Parabolic':
        if not arithmetic_parameters['a'] < arithmetic_parameters['b']:
            raise ValueError("Parabolic parameters must satisfy a < b")

    elif family_name == 'Triangle':
        if not arithmetic_parameters['a'] < arithmetic_parameters['c'] <= arithmetic_parameters['b']:
            raise ValueError("Triangle parameters must satisfy a < c <= b")

    elif family_name == 'Trapezium':
        if not arithmetic_parameters['a'] < arithmetic_parameters['c'] <= arithmetic_parameters['d'] < arithmetic_parameters['b']:
            raise ValueError("Trapezium parameters must satisfy a < c <= d < b")

    elif family_name == 'Exponential':
        if arithmetic_parameters['b'] <= 0:
            raise ValueError("Exponential parameter b must satisfy b > 0")

    elif family_name == 'Sigmoidal' and arithmetic_parameters['a'] == 0:
        raise ValueError("Sigmoidal parameter a must be non-zero")

    return dict(arithmetic_parameters)


def _Hyperbolic(parameters: Mapping[str, float], x: float) -> float:
    """Evaluate the validated hyperbolic family without changing parameters."""

    a = parameters['a']
    b = parameters['b']
    c = parameters['c']

    if x <= c:
        return 1

    return cast(float, 1 / (1 + (a * (x - c)) ** b))


def _Bell(parameters: Mapping[str, float], x: float) -> float:
    """Evaluate the validated bell family without changing parameters."""

    a = parameters['a']
    b = parameters['b']
    c = parameters['c']

    if x < b:
        return _Parabolic(parameters, x)

    if x <= c:
        return 1

    right_boundary = c + b - a
    right_midpoint = (c + right_boundary) / 2

    if x <= right_midpoint:
        return 1 - (2 * (x - c) ** 2) / (right_boundary - c) ** 2

    if x < right_boundary:
        return (2 * (x - right_boundary) ** 2) / (right_boundary - c) ** 2

    return 0


def _Parabolic(parameters: Mapping[str, float], x: float) -> float:
    """Evaluate the validated parabolic family without changing parameters."""

    a = parameters['a']
    b = parameters['b']

    if x <= a:
        return 0

    if x <= (a + b) / 2:
        return (2 * (x - a) ** 2) / (b - a) ** 2

    if x < b:
        return 1 - (2 * (x - b) ** 2) / (b - a) ** 2

    return 1


def _DifferenceRatio(
    numerator_left: float,
    numerator_right: float,
    denominator_left: float,
    denominator_right: float,
) -> float:
    """Preserve a finite ramp ratio when an endpoint difference overflows.

    Ordinary differences retain their established arithmetic. Halving all
    operands before subtraction keeps extreme binary64 endpoint differences
    representable without changing the mathematical ratio.
    """

    numerator = numerator_left - numerator_right
    denominator = denominator_left - denominator_right

    if abs(numerator) != math.inf and abs(denominator) != math.inf:
        return numerator / denominator

    return (numerator_left / 2 - numerator_right / 2) / (
        denominator_left / 2 - denominator_right / 2
    )


def _Triangle(parameters: Mapping[str, float], x: float) -> float:
    """Evaluate the validated triangle family without changing parameters."""

    a = parameters['a']
    b = parameters['b']
    c = parameters['c']

    if x <= a:
        return 0

    if x <= c:
        return _DifferenceRatio(x, a, c, a)

    if x < b:
        return _DifferenceRatio(b, x, b, c)

    return 0


def _Trapezium(parameters: Mapping[str, float], x: float) -> float:
    """Evaluate the validated trapezium family without changing parameters."""

    a = parameters['a']
    b = parameters['b']
    c = parameters['c']
    d = parameters['d']

    if x <= a:
        return 0

    if x < c:
        return _DifferenceRatio(x, a, c, a)

    if x <= d:
        return 1

    if x <= b:
        return _DifferenceRatio(b, x, b, d)

    return 0


def _Exponential(parameters: Mapping[str, float], x: float) -> float:
    """Evaluate the validated exponential family without changing parameters."""

    a = parameters['a']
    b = parameters['b']
    distance = x - a
    scaled_distance = distance / b

    if abs(distance) == math.inf:
        # Overflowing subtraction has opposite-sign operands, so distributed
        # division cannot introduce cancellation between infinite terms.
        scaled_distance = x / b - a / b

    # Binary64 underflow may produce zero far from the centre; analytical
    # support is derived from the formula, never from this sampled value.
    return math.exp(-0.5 * scaled_distance * scaled_distance)


def _Sigmoidal(parameters: Mapping[str, float], x: float) -> float:
    """Evaluate the validated sigmoidal family without changing parameters."""

    a = parameters['a']
    b = parameters['b']
    distance = x - b
    exponent = a * distance

    if abs(distance) == math.inf:
        exponent = a * x - a * b

    # Algebraically equivalent branches keep the exp argument non-positive,
    # preventing overflow for every finite exponent. See the numerical
    # derivation in docs/mathematics/source-algorithm-invariants.md.
    if exponent >= 0:
        return 1 / (1 + math.exp(-exponent))

    exponential = math.exp(exponent)
    return exponential / (1 + exponential)


def _Desirability(parameters: Mapping[str, float], y: float) -> float:
    """Evaluate the validated desirability family without changing parameters."""


    # Beyond this binary64 bound the inner exponential overflows while the
    # representable value of exp(-exp(-y)) is already exactly zero. See
    # docs/mathematics/source-algorithm-invariants.md.
    if y < -math.log(float.fromhex('0x1.fffffffffffffp+1023')):
        return 0.0

    return math.exp(-math.exp(-y))


_FORMULAS = {
    "Hyperbolic": _Hyperbolic,
    "Bell": _Bell,
    "Parabolic": _Parabolic,
    "Triangle": _Triangle,
    "Trapezium": _Trapezium,
    "Exponential": _Exponential,
    "Sigmoidal": _Sigmoidal,
    "Desirability": _Desirability,
}

# Private analytical snapshots retain the existing exact-region/moment schema.
# The public family API below uses geometric names rather than this adapter map.
_PARAMETER_MAP = {
    "hyperbolic": ("Hyperbolic", (("scale", "a"), ("exponent", "b"), ("cutoff", "c"))),
    "bell": ("Bell", (("left", "a"), ("plateau_start", "b"), ("plateau_end", "c"))),
    "s_shoulder": ("Parabolic", (("left", "a"), ("right", "b"))),
    "triangle": ("Triangle", (("left", "a"), ("peak", "c"), ("right", "b"))),
    "trapezoid": ("Trapezium", (("left", "a"), ("plateau_start", "c"), ("plateau_end", "d"), ("right", "b"))),
    "gaussian": ("Exponential", (("center", "a"), ("scale", "b"))),
    "logistic": ("Sigmoidal", (("slope", "a"), ("midpoint", "b"))),
    "harrington_desirability": ("Desirability", ()),
}


@dataclass(frozen=True, slots=True)
class _AnalyticalSource:
    """Frozen validated formula source for exact regions and numerical moments."""

    name: str
    parameter_items: tuple[tuple[str, MembershipScalar], ...]

    def __post_init__(self) -> None:
        """Reject unsupported families and freeze a validated parameter copy."""

        if self.name not in _FORMULAS:
            raise ValueError(f"unsupported analytical membership family: {self.name!r}")

        parameters = _ValidateFamilyParameters(self.name, dict(self.parameter_items))
        object.__setattr__(self, "parameter_items", tuple(sorted(parameters.items())))

    @property
    def parameters(self) -> Mapping[str, MembershipScalar]:
        """Return a read-only view of the frozen analytical parameters."""

        return MappingProxyType(dict(self.parameter_items))

    def mju(self, coordinate: MembershipScalar) -> float:
        """Evaluate the frozen scalar formula at one finite real coordinate."""

        coordinate = _RequireFiniteReal(coordinate, "coordinate")

        return _FORMULAS[self.name](cast(Mapping[str, float], self.parameters), coordinate)


@dataclass(frozen=True, slots=True, init=False)
class MembershipFunction:
    """Immutable validated analytical membership function on the real line.

    `family` selects one of `hyperbolic`, `bell`, `s_shoulder`, `triangle`,
    `trapezoid`, `gaussian`, `logistic`, or `harrington_desirability`.
    The named constructors expose their complete geometric parameter contracts.
    Evaluation accepts finite real coordinates excluding booleans. Parameters
    are copied at construction; reading `parameters` cannot mutate the source.

    Attributes:
        family: Canonical modern family identifier.
        parameters: Read-only parameter mapping with modern geometric names.

    Notes:
        Positive analytical tails may underflow to zero when evaluated.
        Triangle permits `peak == right`, with grade one at that endpoint and
        zero to its right. Bell's right foot is `plateau_end + plateau_start - left`.
    """

    family: str
    _parameter_items: tuple[tuple[str, MembershipScalar], ...]
    _source: _AnalyticalSource

    def __init__(self, family: str, **parameters: MembershipScalar) -> None:
        """Freeze a family with its exact named parameter set.

        Args:
            family: Canonical modern family identifier listed in the class contract.
            **parameters: Exact finite real parameters documented by the named
                family constructor; booleans are rejected.

        Raises:
            ValueError: The family, parameter names, finiteness, or geometric
                ordering is invalid.
        """

        if family not in _PARAMETER_MAP:
            raise InvalidParameterError(f"unknown membership-function family: {family!r}")

        analytical_name, parameter_map = _PARAMETER_MAP[family]

        if set(parameters) != {name for name, _ in parameter_map}:
            raise InvalidParameterError(f"{family} requires exactly these parameters: {tuple(name for name, _ in parameter_map)}")

        try:
            source = _AnalyticalSource(
                analytical_name,
                tuple((key, parameters[name]) for name, key in parameter_map),
            )

        except ValueError as error:
            modern_message = str(error)

            for name, key in parameter_map:
                # Replace only standalone analytical keys, never letters inside words.
                modern_message = re.sub(rf"\b{key}\b", name, modern_message)

            raise InvalidParameterError(modern_message) from error
        object.__setattr__(self, "family", family)
        object.__setattr__(self, "_parameter_items", tuple(sorted(parameters.items())))
        object.__setattr__(self, "_source", source)

    @property
    def parameters(self) -> Mapping[str, MembershipScalar]:
        """Return the read-only modern parameter mapping."""

        return MappingProxyType(dict(self._parameter_items))

    def Evaluate(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Return the scalar membership degree at a finite real coordinate.

        Args:
            coordinate: Finite real coordinate on the mathematical real line.

        Returns:
            Representable membership degree, preserving family endpoint rules.

        Raises:
            TypeError: The coordinate is not a real number or is a boolean.
            ValueError: The coordinate is not finite.
            OverflowError: A hyperbolic power or polynomial intermediate is
                unrepresentable for otherwise finite coordinates.
        """

        return self._source.mju(coordinate)

    def __call__(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Evaluate the same scalar contract as `Evaluate` for callable use."""

        return self.Evaluate(coordinate)


class _LegacyAnalyticalAdapter:
    """Explicit private marker for trusted historical analytical adapters."""

    def mju(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Describe the scalar evaluation supplied by a historical adapter."""

        raise NotImplementedError

    def _AnalyticalSnapshot(self) -> _AnalyticalSource:
        """Return an immutable validated source; implemented by the adapter."""

        raise NotImplementedError


    def _HasAnalyticalEvaluator(self) -> bool:
        """Reject adapters that have not verified their active scalar formula."""

        return False


def _HasModernAnalyticalEvaluator(value: MembershipFunction) -> bool:
    """Verify the actual callable and delegated evaluator use built-in formulas."""

    return (
        type(value).__call__ is MembershipFunction.__call__
        and getattr(value.Evaluate, "__func__", None) is MembershipFunction.Evaluate
        and getattr(value.Evaluate, "__self__", None) is value
        and type(value._source) is _AnalyticalSource
    )


def _GetAnalyticalSource(value: object) -> _AnalyticalSource | None:
    """Return evidence only for the formula used by the actual evaluator.

    Inherited unchanged evaluators retain analytical evidence. Overridden
    callables and bound methods remain generic even when their owner stores a
    built-in family definition.
    """

    if type(value) is _AnalyticalSource:
        return value

    if isinstance(value, MembershipFunction) and _HasModernAnalyticalEvaluator(value):
        return value._source

    if isinstance(value, _LegacyAnalyticalAdapter) and value._HasAnalyticalEvaluator():
        return value._AnalyticalSnapshot()

    if not isinstance(value, MethodType):
        return None

    owner = value.__self__
    evaluator_function = value.__func__

    if isinstance(owner, MembershipFunction) and type(owner._source) is _AnalyticalSource:
        if evaluator_function is MembershipFunction.Evaluate:
            return owner._source

        if evaluator_function is MembershipFunction.__call__ and _HasModernAnalyticalEvaluator(owner):
            return owner._source

    if type(owner) is _AnalyticalSource and evaluator_function is _AnalyticalSource.mju:
        return owner

    if (
        isinstance(owner, _LegacyAnalyticalAdapter)
        and owner._HasAnalyticalEvaluator()
        and value == owner.mju
    ):
        return owner._AnalyticalSnapshot()

    return None


def Hyperbolic(
    scale: MembershipScalar,
    exponent: MembershipScalar,
    cutoff: MembershipScalar,
) -> MembershipFunction:
    """Return decreasing hyperbolic tail with grade one for coordinates at or below cutoff.

    The finite real parameters must satisfy `scale > 0 and exponent > 0`; booleans are
    rejected. The returned callable is immutable and uses the family boundary
    conventions documented by `MembershipFunction`.

    Args:
        scale: Positive scale (Gaussian standard deviation or hyperbolic multiplier).
        exponent: Positive power of the hyperbolic tail.
        cutoff: End of the grade-one left shoulder.

    Returns:
        Validated immutable analytical membership function.

    Raises:
        ValueError: Parameters are non-real, non-finite, or violate the family contract.
    """

    return MembershipFunction("hyperbolic", scale=scale, exponent=exponent, cutoff=cutoff)


def Bell(
    left: MembershipScalar,
    plateau_start: MembershipScalar,
    plateau_end: MembershipScalar,
) -> MembershipFunction:
    """Return finite flat-top quadratic bell with mirrored shoulders.

    The finite real parameters must satisfy `left < plateau_start <= plateau_end`; booleans are
    rejected. The returned callable is immutable and uses the family boundary
    conventions documented by `MembershipFunction`.

    Args:
        left: Left foot where membership is zero.
        plateau_start: Included left endpoint of the grade-one plateau.
        plateau_end: Included right endpoint of the grade-one plateau.

    Returns:
        Validated immutable analytical membership function.

    Raises:
        ValueError: Parameters are non-real, non-finite, or violate the family contract.
    """

    return MembershipFunction("bell", left=left, plateau_start=plateau_start, plateau_end=plateau_end)


def SShoulder(left: MembershipScalar, right: MembershipScalar) -> MembershipFunction:
    """Return rising quadratic S-shoulder, zero at left and one from right onward.

    The finite real parameters must satisfy `left < right`; booleans are
    rejected. The returned callable is immutable and uses the family boundary
    conventions documented by `MembershipFunction`.

    Args:
        left: Left foot where membership is zero.
        right: Right boundary of the shape.

    Returns:
        Validated immutable analytical membership function.

    Raises:
        ValueError: Parameters are non-real, non-finite, or violate the family contract.
    """

    return MembershipFunction("s_shoulder", left=left, right=right)


def Triangle(left: MembershipScalar, peak: MembershipScalar, right: MembershipScalar) -> MembershipFunction:
    """Return piecewise linear triangle with conventional left, peak, right order.

    The finite real parameters must satisfy `left < peak <= right`; booleans are
    rejected. The returned callable is immutable and uses the family boundary
    conventions documented by `MembershipFunction`.

    Args:
        left: Left foot where membership is zero.
        peak: Coordinate attaining grade one, possibly equal to `right`.
        right: Right boundary of the shape.

    Returns:
        Validated immutable analytical membership function.

    Raises:
        ValueError: Parameters are non-real, non-finite, or violate the family contract.
    """

    return MembershipFunction("triangle", left=left, peak=peak, right=right)


def Trapezoid(
    left: MembershipScalar,
    plateau_start: MembershipScalar,
    plateau_end: MembershipScalar,
    right: MembershipScalar,
) -> MembershipFunction:
    """Return piecewise linear trapezoid with conventional left-to-right order.

    The finite real parameters must satisfy `left < plateau_start <= plateau_end < right`; booleans are
    rejected. The returned callable is immutable and uses the family boundary
    conventions documented by `MembershipFunction`.

    Args:
        left: Left foot where membership is zero.
        plateau_start: Included left endpoint of the grade-one plateau.
        plateau_end: Included right endpoint of the grade-one plateau.
        right: Right boundary of the shape.

    Returns:
        Validated immutable analytical membership function.

    Raises:
        ValueError: Parameters are non-real, non-finite, or violate the family contract.
    """

    return MembershipFunction("trapezoid", left=left, plateau_start=plateau_start, plateau_end=plateau_end, right=right)


def Gaussian(center: MembershipScalar, scale: MembershipScalar) -> MembershipFunction:
    """Return gaussian membership exp(-0.5 * ((x - center) / scale)^2).

    The finite real parameters must satisfy `scale > 0`; booleans are
    rejected. The returned callable is immutable and uses the family boundary
    conventions documented by `MembershipFunction`.

    Args:
        center: Coordinate of the grade-one Gaussian maximum.
        scale: Positive scale (Gaussian standard deviation or hyperbolic multiplier).

    Returns:
        Validated immutable analytical membership function.

    Raises:
        ValueError: Parameters are non-real, non-finite, or violate the family contract.
    """

    return MembershipFunction("gaussian", center=center, scale=scale)


def Logistic(slope: MembershipScalar, midpoint: MembershipScalar) -> MembershipFunction:
    """Return stable logistic membership with grade one-half at midpoint.

    The finite real parameters must satisfy `slope != 0`; booleans are
    rejected. The returned callable is immutable and uses the family boundary
    conventions documented by `MembershipFunction`.

    Args:
        slope: Nonzero signed slope; its sign sets monotonic direction.
        midpoint: Coordinate with membership one-half.

    Returns:
        Validated immutable analytical membership function.

    Raises:
        ValueError: Parameters are non-real, non-finite, or violate the family contract.
    """

    return MembershipFunction("logistic", slope=slope, midpoint=midpoint)


def HarringtonDesirability() -> MembershipFunction:
    """Return harrington desirability membership exp(-exp(-x)).

    The finite real parameters must satisfy `no stored parameters`; booleans are
    rejected. The returned callable is immutable and uses the family boundary
    conventions documented by `MembershipFunction`.

    Returns:
        Validated immutable analytical membership function.

    Raises:
        ValueError: Parameters are non-real, non-finite, or violate the family contract.
    """

    return MembershipFunction("harrington_desirability")
