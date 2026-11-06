# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private scalar experiment for explicit physical input normalization."""

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite

from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)


class _MissingObservationError(InvalidParameterError):
    """A scalar mapping observation was absent."""


def _RequireBinary64(value: object, field: str) -> float:
    """Validate a finite built-in float or an integer exactly representable as one."""

    if type(value) is float:
        if not isfinite(value):
            raise InvalidParameterError(f"{field} must be finite")

        return value

    if type(value) is int:
        try:
            coordinate = float(value)

        except OverflowError as error:
            raise InvalidParameterError(f"{field} must be exactly representable as binary64") from error

        if coordinate == value:
            return coordinate

        raise InvalidParameterError(f"{field} must be exactly representable as binary64")

    raise InvalidParameterTypeError(f"{field} must be a built-in float or integer")


def _RequireUnit(unit: str, field: str) -> None:
    """Validate a case-sensitive, nonblank unit label."""

    if type(unit) is not str:
        raise InvalidParameterTypeError(f"{field} must be a string")

    if not unit.strip():
        raise InvalidParameterError(f"{field} must be nonblank")


def _Map(
    observation: object,
    unit: str,
    expectedUnit: str,
    sourceLeft: float,
    sourceRight: float,
    targetLeft: float,
    targetRight: float,
) -> float:
    """Map a validated coordinate through exact ratios with one final rounding."""

    if observation is None:
        raise _MissingObservationError("observation is missing")

    _RequireUnit(unit, "observation unit")

    if unit != expectedUnit:
        raise InvalidParameterError(f"observation unit must match {expectedUnit!r}")

    coordinate = _RequireBinary64(observation, "observation")

    if not sourceLeft <= coordinate <= sourceRight:
        raise InvalidDomainError("observation is outside the closed input interval")

    if coordinate == sourceLeft:
        return targetLeft

    if coordinate == sourceRight:
        return targetRight

    start = Fraction(sourceLeft)
    end = Fraction(targetLeft)
    position = (Fraction(coordinate) - start) / (Fraction(sourceRight) - start)

    return float(end + (Fraction(targetRight) - end) * position)


@dataclass(frozen=True, slots=True)
class _AffineInputMapping:
    """Immutable affine map between finite closed intervals with explicit units.

    Attributes:
        sourceLeft: Lower physical bound.
        sourceRight: Upper physical bound, strictly greater than sourceLeft.
        targetLeft: Lower scale-coordinate bound.
        targetRight: Upper scale-coordinate bound, strictly greater than targetLeft.
        sourceUnit: Exact unit label for physical observations.
        targetUnit: Exact unit label for scale coordinates.
    """

    sourceLeft: float
    sourceRight: float
    targetLeft: float
    targetRight: float
    sourceUnit: str
    targetUnit: str

    def __post_init__(self) -> None:
        """Validate units and freeze the four bounds in binary64."""

        _RequireUnit(self.sourceUnit, "sourceUnit")
        _RequireUnit(self.targetUnit, "targetUnit")

        for field in ("sourceLeft", "sourceRight", "targetLeft", "targetRight"):
            object.__setattr__(self, field, _RequireBinary64(getattr(self, field), field))

        if self.sourceLeft >= self.sourceRight or self.targetLeft >= self.targetRight:
            raise InvalidDomainError("source and target bounds must each be strictly increasing")

    def Forward(self, observation: object, *, unit: str) -> float:
        """Map a physical observation to a rounded scale coordinate.

        Args:
            observation: A finite binary64 value or exactly representable integer
                in the closed physical interval. `None` reports missing input.
            unit: The exact physical unit label declared by this mapping.

        Returns:
            A coordinate in the closed scale interval, with exact endpoint anchors.

        Raises:
            _MissingObservationError: The observation is missing.
            InvalidParameterTypeError: The observation or unit has the wrong type.
            InvalidParameterError: The observation or unit has an invalid value.
            InvalidDomainError: The observation is outside the closed interval.
        """

        return _Map(observation, unit, self.sourceUnit, self.sourceLeft, self.sourceRight, self.targetLeft, self.targetRight)

    def Inverse(self, observation: object, *, unit: str) -> float:
        """Map a scale coordinate back to a rounded physical observation.

        Args:
            observation: A finite binary64 value or exactly representable integer
                in the closed scale interval. `None` reports missing input.
            unit: The exact scale unit label declared by this mapping.

        Returns:
            An observation in the closed physical interval. Interior forward
            and inverse results can each round to binary64.

        Raises:
            _MissingObservationError: The observation is missing.
            InvalidParameterTypeError: The observation or unit has the wrong type.
            InvalidParameterError: The observation or unit has an invalid value.
            InvalidDomainError: The observation is outside the closed interval.
        """

        return _Map(observation, unit, self.targetUnit, self.targetLeft, self.targetRight, self.sourceLeft, self.sourceRight)
