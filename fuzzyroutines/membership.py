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
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import wraps
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


def _ValidateFamilyParameters(familyName: str, parameters: dict[str, MembershipScalar]) -> dict[str, float]:
    """Validate canonical analytical geometry without coercion or mutation."""

    requiredParameters = {
        'Hyperbolic': ('a', 'b', 'c'),
        'Bell': ('a', 'b', 'c'),
        'Parabolic': ('a', 'b'),
        'Triangle': ('a', 'b', 'c'),
        'Trapezium': ('a', 'b', 'c', 'd'),
        'Exponential': ('a', 'b'),
        'Sigmoidal': ('a', 'b'),
        'Desirability': (),
    }[familyName]

    if not isinstance(parameters, dict) or set(parameters) != set(requiredParameters):
        raise ValueError(
            "{} membership function requires exactly these parameters: {}".format(
                familyName,
                ', '.join(requiredParameters) if requiredParameters else 'none',
            )
        )

    arithmeticParameters = cast(dict[str, float], parameters)

    for parameterName in requiredParameters:
        parameterValue = parameters[parameterName]

        if (isinstance(parameterValue, bool) or not isinstance(parameterValue, Real)) or not math.isfinite(parameterValue):
            raise ValueError(
                f"{familyName} parameter {parameterName!r} must be a finite real number"
            )

    if familyName == 'Hyperbolic':
        if arithmeticParameters['a'] <= 0 or arithmeticParameters['b'] <= 0:
            raise ValueError("Hyperbolic parameters must satisfy a > 0 and b > 0")

    elif familyName == 'Bell':
        if not arithmeticParameters['a'] < arithmeticParameters['b'] <= arithmeticParameters['c']:
            raise ValueError("Bell parameters must satisfy a < b <= c")

    elif familyName == 'Parabolic':
        if not arithmeticParameters['a'] < arithmeticParameters['b']:
            raise ValueError("Parabolic parameters must satisfy a < b")

    elif familyName == 'Triangle':
        if not arithmeticParameters['a'] < arithmeticParameters['c'] <= arithmeticParameters['b']:
            raise ValueError("Triangle parameters must satisfy a < c <= b")

    elif familyName == 'Trapezium':
        if not arithmeticParameters['a'] < arithmeticParameters['c'] <= arithmeticParameters['d'] < arithmeticParameters['b']:
            raise ValueError("Trapezium parameters must satisfy a < c <= d < b")

    elif familyName == 'Exponential':
        if arithmeticParameters['b'] <= 0:
            raise ValueError("Exponential parameter b must satisfy b > 0")

    elif familyName == 'Sigmoidal' and arithmeticParameters['a'] == 0:
        raise ValueError("Sigmoidal parameter a must be non-zero")

    return dict(arithmeticParameters)


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

    rightBoundary = c + b - a
    rightMidpoint = (c + rightBoundary) / 2

    if x <= rightMidpoint:
        return 1 - (2 * (x - c) ** 2) / (rightBoundary - c) ** 2

    if x < rightBoundary:
        return (2 * (x - rightBoundary) ** 2) / (rightBoundary - c) ** 2

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
    numeratorLeft: float,
    numeratorRight: float,
    denominatorLeft: float,
    denominatorRight: float,
) -> float:
    """Preserve a finite ramp ratio when an endpoint difference overflows.

    Ordinary differences retain their established arithmetic. Halving all
    operands before subtraction keeps extreme binary64 endpoint differences
    representable without changing the mathematical ratio.
    """

    numerator = numeratorLeft - numeratorRight
    denominator = denominatorLeft - denominatorRight

    if abs(numerator) != math.inf and abs(denominator) != math.inf:
        return numerator / denominator

    return (numeratorLeft / 2 - numeratorRight / 2) / (
        denominatorLeft / 2 - denominatorRight / 2
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
    scaledDistance = distance / b

    if abs(distance) == math.inf:
        # Overflowing subtraction has opposite-sign operands, so distributed
        # division cannot introduce cancellation between infinite terms.
        scaledDistance = x / b - a / b

    # Binary64 underflow may produce zero far from the centre; analytical
    # support is derived from the formula, never from this sampled value.
    return math.exp(-0.5 * scaledDistance * scaledDistance)


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
    "bell": ("Bell", (("left", "a"), ('plateauStart', "b"), ('plateauEnd', "c"))),
    "s_shoulder": ("Parabolic", (("left", "a"), ("right", "b"))),
    "triangle": ("Triangle", (("left", "a"), ("peak", "c"), ("right", "b"))),
    "trapezoid": ("Trapezium", (("left", "a"), ('plateauStart', "c"), ('plateauEnd', "d"), ("right", "b"))),
    "gaussian": ("Exponential", (("center", "a"), ("scale", "b"))),
    "logistic": ("Sigmoidal", (("slope", "a"), ("midpoint", "b"))),
    "harrington_desirability": ("Desirability", ()),
}


def _NormalizePlateauAliases[Value](parameters: Mapping[str, Value]) -> dict[str, Value]:
    """Copy geometric keywords and reject conflicting pre-refactor aliases."""

    normalized = dict(parameters)

    for alias, canonical in (("plateau_start", "plateauStart"), ("plateau_end", "plateauEnd")):
        if alias not in normalized:
            continue

        if canonical in normalized:
            raise InvalidParameterError(f"{alias} and {canonical} name the same parameter")

        normalized[canonical] = normalized.pop(alias)

    return normalized


def _AcceptPlateauAliases[**Parameters, Result](
    constructor: Callable[Parameters, Result],
) -> Callable[Parameters, Result]:
    """Keep earlier development keywords callable with a canonical camelCase signature."""

    @wraps(constructor)
    def Construct(*arguments: Parameters.args, **parameters: Parameters.kwargs) -> Result:
        """Translate compatibility keywords before invoking the unchanged constructor."""

        normalized = _NormalizePlateauAliases(parameters)
        parameters.clear()
        parameters.update(normalized)

        return constructor(*arguments, **parameters)

    return Construct


@dataclass(frozen=True, slots=True)
class _AnalyticalSource:
    """Frozen validated formula source for exact regions and numerical moments."""

    name: str
    parameterItems: tuple[tuple[str, MembershipScalar], ...]

    def __post_init__(self) -> None:
        """Reject unsupported families and freeze a validated parameter copy."""

        if self.name not in _FORMULAS:
            raise ValueError(f"unsupported analytical membership family: {self.name!r}")

        parameters = _ValidateFamilyParameters(self.name, dict(self.parameterItems))
        object.__setattr__(self, 'parameterItems', tuple(sorted(parameters.items())))

    @property
    def parameters(self) -> Mapping[str, MembershipScalar]:
        """Return a read-only view of the frozen analytical parameters."""

        return MappingProxyType(dict(self.parameterItems))

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
        zero to its right. Bell's right foot is `plateauEnd + plateauStart - left`.
        Earlier development keywords `plateau_start` and `plateau_end` are
        accepted as input aliases; the parameter mapping uses camelCase keys.
        Supplying an alias and its canonical name together is invalid.
    """

    family: str
    _parameterItems: tuple[tuple[str, MembershipScalar], ...]
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

        parameters = _NormalizePlateauAliases(parameters)
        analyticalName, parameterMap = _PARAMETER_MAP[family]

        if set(parameters) != {name for name, _ in parameterMap}:
            raise InvalidParameterError(f"{family} requires exactly these parameters: {tuple(name for name, _ in parameterMap)}")

        try:
            source = _AnalyticalSource(
                analyticalName,
                tuple((key, parameters[name]) for name, key in parameterMap),
            )

        except ValueError as error:
            modernMessage = str(error)

            for name, key in parameterMap:
                # Replace only standalone analytical keys, never letters inside words.
                modernMessage = re.sub(rf"\b{key}\b", name, modernMessage)

            raise InvalidParameterError(modernMessage) from error
        object.__setattr__(self, "family", family)
        object.__setattr__(self, '_parameterItems', tuple(sorted(parameters.items())))
        object.__setattr__(self, "_source", source)

    @property
    def parameters(self) -> Mapping[str, MembershipScalar]:
        """Return the read-only modern parameter mapping."""

        return MappingProxyType(dict(self._parameterItems))

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
    evaluatorFunction = value.__func__

    if isinstance(owner, MembershipFunction) and type(owner._source) is _AnalyticalSource:
        if evaluatorFunction is MembershipFunction.Evaluate:
            return owner._source

        if evaluatorFunction is MembershipFunction.__call__ and _HasModernAnalyticalEvaluator(owner):
            return owner._source

    if type(owner) is _AnalyticalSource and evaluatorFunction is _AnalyticalSource.mju:
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
        scale: Positive multiplier of the distance beyond the cutoff.
        exponent: Positive power of the hyperbolic tail.
        cutoff: End of the grade-one left shoulder.

    Returns:
        Validated immutable analytical membership function.

    Raises:
        ValueError: Parameters are non-real, non-finite, or violate the family contract.
    """

    return MembershipFunction("hyperbolic", scale=scale, exponent=exponent, cutoff=cutoff)


@_AcceptPlateauAliases
def Bell(
    left: MembershipScalar,
    plateauStart: MembershipScalar,
    plateauEnd: MembershipScalar,
) -> MembershipFunction:
    """Return finite flat-top quadratic bell with mirrored shoulders.

    The finite real parameters must satisfy `left < plateauStart <= plateauEnd`; booleans are
    rejected. The returned callable is immutable and uses the family boundary
    conventions documented by `MembershipFunction`.

    Args:
        left: Left foot where membership is zero.
        plateauStart: Included left endpoint of the grade-one plateau.
        plateauEnd: Included right endpoint of the grade-one plateau.

    Returns:
        Validated immutable analytical membership function.

    Raises:
        ValueError: Parameters are non-real, non-finite, or violate the family contract.
    """

    return MembershipFunction("bell", left=left, plateauStart=plateauStart, plateauEnd=plateauEnd)


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


@_AcceptPlateauAliases
def Trapezoid(
    left: MembershipScalar,
    plateauStart: MembershipScalar,
    plateauEnd: MembershipScalar,
    right: MembershipScalar,
) -> MembershipFunction:
    """Return piecewise linear trapezoid with conventional left-to-right order.

    The finite real parameters must satisfy `left < plateauStart <= plateauEnd < right`; booleans are
    rejected. The returned callable is immutable and uses the family boundary
    conventions documented by `MembershipFunction`.

    Args:
        left: Left foot where membership is zero.
        plateauStart: Included left endpoint of the grade-one plateau.
        plateauEnd: Included right endpoint of the grade-one plateau.
        right: Right boundary of the shape.

    Returns:
        Validated immutable analytical membership function.

    Raises:
        ValueError: Parameters are non-real, non-finite, or violate the family contract.
    """

    return MembershipFunction("trapezoid", left=left, plateauStart=plateauStart, plateauEnd=plateauEnd, right=right)


def Gaussian(center: MembershipScalar, scale: MembershipScalar) -> MembershipFunction:
    """Return gaussian membership exp(-0.5 * ((x - center) / scale)^2).

    The finite real parameters must satisfy `scale > 0`; booleans are
    rejected. The returned callable is immutable and uses the family boundary
    conventions documented by `MembershipFunction`.

    Args:
        center: Coordinate of the grade-one Gaussian maximum.
        scale: Positive Gaussian standard deviation in coordinate units.

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
    """Return Harrington desirability membership exp(-exp(-x)).

    This constructor takes no parameters. The immutable returned callable
    accepts finite real coordinates excluding booleans. Its fixed coordinate
    scale must be given meaning by the application's preprocessing model.

    Returns:
        Validated immutable analytical membership function.

    """

    return MembershipFunction("harrington_desirability")
