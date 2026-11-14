# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Explicit affine normalization from physical inputs to a scale universe."""

from dataclasses import dataclass, field

from fuzzyroutines._input_mapping import _AffineInputMapping, _RequireBinary64
from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)

__all__ = ["AffineInputMapping", "MissingObservationError"]


class MissingObservationError(InvalidParameterError):
    """An affine mapping was asked to evaluate an absent observation."""


def _RequireObservation(observation: object) -> object:
    """Report the facade's missing-value error before numeric validation."""

    if observation is None:
        raise MissingObservationError("observation is missing")

    return observation


@dataclass(frozen=True, slots=True)
class AffineInputMapping:
    """Immutable mapping to a finite closed continuous scale universe.

    Each operation requires the corresponding unit label exactly as declared.
    Callers convert observations in other units before applying the map.
    Endpoint results preserve the declared binary64 representation. Interior
    results round once to binary64, which can limit inverse round-trip precision.

    Attributes:
        sourceLeft: Finite lower bound of the closed physical interval.
        sourceRight: Finite upper bound, strictly greater than sourceLeft.
        targetUniverse: The finite closed continuous universe of the scale.
            Bounds must be floats or integers exactly representable as binary64.
        sourceUnit: Case-sensitive, nonblank label for physical observations.
        targetUnit: Case-sensitive, nonblank label for scale coordinates.
    """

    sourceLeft: float
    sourceRight: float
    targetUniverse: ContinuousUniverse
    sourceUnit: str
    targetUnit: str
    _mapping: _AffineInputMapping = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Bind the prototype to the full closed target universe."""

        universe = self.targetUniverse

        if type(universe) is not ContinuousUniverse:
            raise InvalidParameterTypeError("targetUniverse must be a ContinuousUniverse")

        if not (universe.isBounded and universe.leftClosed and universe.rightClosed):
            raise InvalidDomainError("targetUniverse must be finite and closed")

        mapping = _AffineInputMapping(
            self.sourceLeft,
            self.sourceRight,
            _RequireBinary64(universe.left, "targetUniverse.left"),
            _RequireBinary64(universe.right, "targetUniverse.right"),
            self.sourceUnit,
            self.targetUnit,
        )
        object.__setattr__(self, "sourceLeft", mapping.sourceLeft)
        object.__setattr__(self, "sourceRight", mapping.sourceRight)
        object.__setattr__(self, "_mapping", mapping)

    def Forward(self, observation: object, *, unit: str) -> float:
        """Map a physical observation to a coordinate in the target universe.

        Args:
            observation: A finite float or exactly representable integer in the
                closed physical interval. Use `None` to represent missing data.
            unit: The exact declared physical unit.

        Returns:
            The rounded coordinate in the closed target universe.

        Raises:
            MissingObservationError: The observation is missing.
            InvalidParameterTypeError: The observation or unit has the wrong type.
            InvalidParameterError: The observation or unit has an invalid value.
            InvalidDomainError: The observation lies outside the physical interval.
        """

        return self._mapping.Forward(_RequireObservation(observation), unit=unit)

    def Inverse(self, coordinate: object, *, unit: str) -> float:
        """Map a target coordinate to a rounded observation in physical units.

        Args:
            coordinate: A finite float or exactly representable integer in the
                closed target universe. Use `None` to represent missing data.
            unit: The exact declared scale unit.

        Returns:
            The rounded observation in the closed physical interval.

        Raises:
            MissingObservationError: The coordinate is missing.
            InvalidParameterTypeError: The coordinate or unit has the wrong type.
            InvalidParameterError: The coordinate or unit has an invalid value.
            InvalidDomainError: The coordinate lies outside the target universe.
        """

        return self._mapping.Inverse(_RequireObservation(coordinate), unit=unit)
