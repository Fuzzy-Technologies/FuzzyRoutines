# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Immutable scalar membership from declared points, with explicit semantics.

Discrete tables store exact lookup data. Piecewise-linear functions define
grades between knots and declare their behavior outside the knot interval.
Neither representation needs an optional dependency.
"""

import bisect
from dataclasses import dataclass, field
from fractions import Fraction
from numbers import Rational
from typing import Literal, cast

from fuzzyroutines.domain import DiscreteUniverse
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.numeric import _RequireFiniteReal, _RequireGrade

__all__ = ["DiscreteMembershipTable", "PiecewiseLinearMembership"]

type _Point = tuple[MembershipScalar, MembershipScalar]
type _Boundary = Literal["zero", "clamp", "error"]


def _ValidateScalar(value: object, label: str, *, grade: bool = False) -> float:
    """Use the shared scalar contract and report overflow as invalid input."""

    try:
        return _RequireGrade(value, label) if grade else _RequireFiniteReal(value, label)

    except OverflowError as error:
        raise InvalidParameterError(f"{label} must be a finite real number") from error


def _Snapshot(points: tuple[_Point, ...], label: str, minimum: int) -> tuple[tuple[float, float], ...]:
    """Freeze the declared order and check every coordinate and grade."""

    if not isinstance(points, tuple):
        raise InvalidParameterTypeError(f"{label} must be a tuple of (coordinate, grade) pairs")

    if len(points) < minimum:
        raise InvalidDomainError(f"{label} must contain at least {minimum} point(s)")

    result: list[tuple[float, float]] = []

    for index, point in enumerate(points):
        if not isinstance(point, tuple) or len(point) != 2:
            raise InvalidParameterTypeError(f"{label}[{index}] must be a (coordinate, grade) tuple")

        coordinate = _ValidateScalar(point[0], f"{label}[{index}] coordinate")
        grade = _ValidateScalar(point[1], f"{label}[{index}] grade", grade=True)

        if result and not result[-1][0] < coordinate:
            raise InvalidDomainError(f"{label} coordinates must be strictly increasing and distinct")

        result.append((coordinate, grade))

    return tuple(result)


def _Ratio(value: MembershipScalar) -> Fraction:
    """Read a real's exact ratio when available, otherwise use its float view."""

    if isinstance(value, Rational):
        return Fraction(int(value.numerator), int(value.denominator))

    ratio = getattr(value, "as_integer_ratio", None)

    if callable(ratio):
        numerator, denominator = ratio()
        return Fraction(numerator, denominator)

    return Fraction(float(cast(float, value)))


def _Interpolate(coordinate: float, lower: _Point, upper: _Point) -> MembershipScalar:
    """Blend grades without overflowing widths or rounding distinct rational knots together."""

    left, right = _Ratio(lower[0]), _Ratio(upper[0])
    position = _Ratio(coordinate)

    if not left <= position <= right or left == right:
        raise InvalidDomainError("coordinate or neighboring knots cannot be resolved at interpolation precision")

    weight = (position - left) / (right - left)
    grade = (1 - weight) * _Ratio(lower[1]) + weight * _Ratio(upper[1])

    if all(isinstance(value, Rational) for value in (coordinate, *lower, *upper)):
        return grade

    return float(grade)


@dataclass(frozen=True, slots=True)
class DiscreteMembershipTable:
    """An immutable grade table defined only at its declared coordinates.

    Use the table directly as a scalar callable, or pass its `universe` and
    the table itself to `ScalarFuzzySet`. Coordinates between or beyond the
    declared points have no grade.

    Attributes:
        points: Nonempty tuple of `(coordinate, grade)` pairs. Coordinates
            are finite and strictly increasing; grades are finite in $[0, 1]$.
            Booleans are invalid.
        universe: The discrete universe corresponding to the stored points.
    """

    points: tuple[_Point, ...]
    universe: DiscreteUniverse = field(init=False)

    def __post_init__(self) -> None:
        """Validate and freeze the table and its associated discrete universe."""

        points = _Snapshot(self.points, "points", 1)
        universe = DiscreteUniverse(tuple(coordinate for coordinate, _ in points))
        object.__setattr__(self, "points", points)
        object.__setattr__(self, "universe", universe)

    def __call__(self, coordinate: MembershipScalar, /) -> MembershipScalar:
        """Return the grade stored at exactly the supplied coordinate.

        Args:
            coordinate: Finite, non-boolean real coordinate to match.

        Returns:
            The stored grade without numeric conversion.

        Raises:
            InvalidParameterTypeError: If the coordinate is not a non-boolean real.
            InvalidParameterError: If the coordinate fails finite scalar validation.
            InvalidDomainError: If the coordinate is absent from the table.
        """

        position = _ValidateScalar(coordinate, "coordinate")
        coordinates = cast(tuple[float, ...], self.universe.points)
        index = bisect.bisect_left(coordinates, position)

        if index == len(coordinates) or coordinates[index] != position:
            raise InvalidDomainError("coordinate must be a declared table point")

        return self.points[index][1]


@dataclass(frozen=True, slots=True)
class PiecewiseLinearMembership:
    """Linear membership between strictly increasing knots.

    At every knot the stored grade is returned unchanged. For two adjacent
    knots $(a, g_a)$ and $(b, g_b)$ and an interior coordinate $x$, the grade
    is $(1-t)g_a+tg_b$, where $t=(x-a)/(b-a)$. All-rational interpolation
    returns a `Fraction`; other interpolated grades are returned as floats.
    Duplicate knots are invalid; interior jumps cannot be encoded. A zero
    extension produces a jump at any endpoint with a nonzero grade.

    Attributes:
        knots: Tuple of at least two `(coordinate, grade)` pairs. Coordinates
            are finite and strictly increasing; grades are finite in $[0, 1]$.
            Booleans are invalid.
        boundary: Behavior strictly outside the knots: `"zero"` returns zero,
            `"clamp"` returns the nearest endpoint grade, and `"error"`
            raises `InvalidDomainError`. Defaults to `"error"`.
    """

    knots: tuple[_Point, ...]
    boundary: _Boundary = "error"
    _coordinates: tuple[float, ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate and freeze the knots and the selected boundary policy."""

        if not isinstance(self.boundary, str):
            raise InvalidParameterTypeError("boundary must be a string")

        if self.boundary not in ("zero", "clamp", "error"):
            raise InvalidParameterError("boundary must be 'zero', 'clamp', or 'error'")

        knots = _Snapshot(self.knots, "knots", 2)
        object.__setattr__(self, "knots", knots)
        object.__setattr__(self, "_coordinates", tuple(coordinate for coordinate, _ in knots))

    def __call__(self, coordinate: MembershipScalar, /) -> MembershipScalar:
        """Return a knot, interpolated, or policy grade for one coordinate.

        Args:
            coordinate: Finite, non-boolean real coordinate to evaluate.

        Returns:
            A grade in $[0, 1]$ according to the knots and boundary policy.

        Raises:
            InvalidParameterTypeError: If the coordinate is not a non-boolean real.
            InvalidParameterError: If the coordinate fails finite scalar validation.
            InvalidDomainError: If the coordinate is outside the knot interval
                under the error policy, or the interpolation cannot resolve the
                supplied real type's coordinates.
        """

        position = _ValidateScalar(coordinate, "coordinate")
        index = bisect.bisect_left(self._coordinates, position)

        if index < len(self.knots) and self._coordinates[index] == position:
            return self.knots[index][1]

        if 0 < index < len(self.knots):
            return _Interpolate(position, self.knots[index - 1], self.knots[index])

        if self.boundary == "zero":
            return 0

        if self.boundary == "clamp":
            return self.knots[0 if index == 0 else -1][1]

        raise InvalidDomainError("coordinate lies outside the closed knot interval")
