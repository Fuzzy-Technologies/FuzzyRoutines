# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Explicit scalar universe and numerical integration-domain contracts.

The types in this module implement ADR-0002 without deriving mathematical
support from samples or numerical integration bounds.  They deliberately model
only one-dimensional scalar coordinates; multidimensional universes require a
separate architecture decision.
"""

import math
from dataclasses import dataclass
from itertools import pairwise
from numbers import Real


def _RequireFiniteReal(value, parameterName):
    """Return a finite real scalar unchanged or raise a deterministic error."""

    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{parameterName} must be a real number")

    if not math.isfinite(value):
        raise ValueError(f"{parameterName} must be a finite real number")

    return value


@dataclass(frozen=True, slots=True)
class ContinuousUniverse:
    """One-dimensional real interval that forms a fuzzy set's universe.

    ``None`` represents an unbounded endpoint.  Endpoint closure is explicit;
    an unbounded endpoint cannot be closed because it is not a member of the
    real line.
    """

    left: Real | None = None
    right: Real | None = None
    leftClosed: bool = False
    rightClosed: bool = False

    def __post_init__(self):
        """Validate interval endpoints without changing caller-supplied values."""

        if not isinstance(self.leftClosed, bool) or not isinstance(self.rightClosed, bool):
            raise TypeError("endpoint closure flags must be boolean values")

        if self.left is None:
            if self.leftClosed:
                raise ValueError("an unbounded left endpoint cannot be closed")

        else:
            object.__setattr__(self, "left", _RequireFiniteReal(self.left, "left"))

        if self.right is None:
            if self.rightClosed:
                raise ValueError("an unbounded right endpoint cannot be closed")

        else:
            object.__setattr__(self, "right", _RequireFiniteReal(self.right, "right"))

        if self.left is not None and self.right is not None and self.left >= self.right:
            raise ValueError("continuous universe endpoints must satisfy left < right")

    @property
    def isBounded(self):
        """Return whether both real endpoints are finite and declared."""

        return self.left is not None and self.right is not None

    def Contains(self, coordinate):
        """Return whether a finite scalar coordinate belongs to the universe."""

        coordinate = _RequireFiniteReal(coordinate, "coordinate")

        if self.left is not None and (
            coordinate < self.left or (coordinate == self.left and not self.leftClosed)
        ):
            return False

        return not (
            self.right is not None
            and (coordinate > self.right or (coordinate == self.right and not self.rightClosed))
        )


@dataclass(frozen=True, slots=True)
class DiscreteUniverse:
    """Finite ordered universe of distinct scalar coordinates."""

    points: tuple[Real, ...]

    def __post_init__(self):
        """Require an explicit, non-empty, strictly increasing coordinate tuple."""

        if not isinstance(self.points, tuple):
            raise TypeError("discrete universe points must be an explicit tuple")

        if not self.points:
            raise ValueError("discrete universe must contain at least one coordinate")

        validatedPoints = tuple(
            _RequireFiniteReal(point, f"points[{pointIndex}]")
            for pointIndex, point in enumerate(self.points)
        )

        if any(leftPoint >= rightPoint for leftPoint, rightPoint in pairwise(validatedPoints)):
            raise ValueError("discrete universe points must be strictly increasing and distinct")

        object.__setattr__(self, "points", validatedPoints)

    def Contains(self, coordinate):
        """Return whether a finite scalar coordinate is declared in the universe."""

        coordinate = _RequireFiniteReal(coordinate, "coordinate")
        return coordinate in self.points


@dataclass(frozen=True, slots=True)
class IntegrationDomain:
    """Finite closed interval used by a continuous numerical operation."""

    left: Real
    right: Real

    def __post_init__(self):
        """Require finite ordered endpoints without changing their scalar type."""

        object.__setattr__(self, "left", _RequireFiniteReal(self.left, "left"))
        object.__setattr__(self, "right", _RequireFiniteReal(self.right, "right"))

        if self.left >= self.right:
            raise ValueError("integration-domain endpoints must satisfy left < right")

    @classmethod
    def FromLegacyInterval(cls, interval):
        """Map the historical two-item ``supportSet`` tuple without reinterpretation."""

        if not isinstance(interval, tuple):
            raise TypeError("legacy integration interval must be a two-item tuple")

        if len(interval) != 2:
            raise ValueError("legacy integration interval must be a two-item tuple")

        return cls(interval[0], interval[1])

    def ToLegacyInterval(self):
        """Return the exact tuple shape required by the historical facade."""

        return (self.left, self.right)

    def Contains(self, coordinate):
        """Return whether a finite scalar coordinate lies in this closed interval."""

        coordinate = _RequireFiniteReal(coordinate, "coordinate")
        return self.left <= coordinate <= self.right

    def ValidateWithin(self, universe):
        """Return this domain after proving it is contained in a continuous universe."""

        if not isinstance(universe, ContinuousUniverse):
            raise TypeError("continuous integration requires a ContinuousUniverse")

        if not universe.Contains(self.left) or not universe.Contains(self.right):
            raise ValueError("integration domain must lie entirely within the continuous universe")

        return self
