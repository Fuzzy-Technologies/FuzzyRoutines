# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Construct explicit linear and interval partitions of a bounded universe."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import pairwise
from numbers import Rational

from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.linguistic import LinguisticScale, LinguisticTerm
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.numeric import _RequireFiniteReal

__all__ = ["BuildIntervalScale", "BuildLinearScale"]


def _ValidateCoordinate(value: object, label: str) -> float:
    """Validate a finite real without converting the original value."""

    try:
        return _RequireFiniteReal(value, label)

    except OverflowError as error:
        raise InvalidParameterError(f"{label} must be finite") from error


def _Ratio(value: MembershipScalar) -> Fraction:
    """Preserve the exact ratio of ordinary rational and float coordinates."""

    if isinstance(value, Rational):
        return Fraction(value.numerator, value.denominator)

    return Fraction(float(value))


@dataclass(frozen=True, slots=True)
class _LinearTerm:
    """A peak with neighboring ramps or constant boundary shoulders."""

    peak: Fraction
    previous: Fraction | None
    following: Fraction | None

    def __call__(self, coordinate: MembershipScalar, /) -> MembershipScalar:
        """Evaluate this term at a validated universe coordinate."""

        point = _Ratio(coordinate)

        if point == self.peak:
            return 1

        if point < self.peak:
            if self.previous is None:
                return 1

            if point <= self.previous:
                return 0

            return (point - self.previous) / (self.peak - self.previous)

        if self.following is None:
            return 1

        if point >= self.following:
            return 0

        return (self.following - point) / (self.following - self.peak)


@dataclass(frozen=True, slots=True)
class _IntervalTerm:
    """A crisp bin with a closed left edge and explicit right ownership."""

    left: float
    right: float
    include_right: bool

    def __call__(self, coordinate: MembershipScalar, /) -> MembershipScalar:
        """Return grade one exactly for coordinates owned by this bin."""

        point = _RequireFiniteReal(coordinate, "coordinate")

        return int(self.left <= point and (point < self.right or (self.include_right and point == self.right)))


def BuildLinearScale(
    terms: tuple[tuple[str, MembershipScalar], ...],
    lower: MembershipScalar,
    upper: MembershipScalar,
) -> LinguisticScale:
    """Build a linear partition on the closed interval from lower to upper.

    Each ordered term supplies its name and peak. Neighboring peaks share
    complementary ramps. The first and last terms extend at grade one from
    their peaks to the corresponding endpoints. A sole term has grade one
    throughout the universe. Rational and float coordinates are interpolated
    with exact ratios, while other real types use their binary64 view.
    """

    universe = ContinuousUniverse(
        _ValidateCoordinate(lower, "lower"),
        _ValidateCoordinate(upper, "upper"),
        leftClosed=True,
        rightClosed=True,
    )

    if not isinstance(terms, tuple):
        raise InvalidParameterTypeError("terms must be a tuple of (name, peak) pairs")

    if not terms:
        raise InvalidParameterError("terms must contain at least one (name, peak) pair")

    names: list[str] = []
    peaks: list[Fraction] = []

    for item in terms:
        if not isinstance(item, tuple) or len(item) != 2:
            raise InvalidParameterTypeError("each term must be a (name, peak) tuple")

        name, value = item
        coordinate = _ValidateCoordinate(value, "peak")

        if not universe.Contains(coordinate):
            raise InvalidDomainError("every peak must belong to the closed scale universe")

        names.append(name)
        peaks.append(_Ratio(coordinate))

    if any(left >= right for left, right in pairwise(peaks)):
        raise InvalidDomainError("peaks must be strictly increasing")

    return LinguisticScale(tuple(
        LinguisticTerm(name, ScalarFuzzySet(universe, _LinearTerm(
            peak,
            peaks[index - 1] if index > 0 else None,
            peaks[index + 1] if index + 1 < len(peaks) else None,
        )))
        for index, (name, peak) in enumerate(zip(names, peaks, strict=True))
    ))


def BuildIntervalScale(
    labels: tuple[str, ...],
    boundaries: tuple[MembershipScalar, ...],
) -> LinguisticScale:
    """Build a crisp partition of a closed universe from ordered boundaries.

    Every bin includes its left endpoint. Only the final bin includes its
    right endpoint. Boundaries are strictly increasing and there must be one
    more boundary than labels. Grades are exactly zero or one.
    """

    if not isinstance(labels, tuple) or not isinstance(boundaries, tuple):
        raise InvalidParameterTypeError("labels and boundaries must be tuples")

    if not labels or len(boundaries) != len(labels) + 1:
        raise InvalidParameterError("provide at least one label and exactly one more boundary than labels")

    coordinates = tuple(_ValidateCoordinate(value, "boundary") for value in boundaries)

    if any(left >= right for left, right in pairwise(coordinates)):
        raise InvalidDomainError("boundaries must be strictly increasing")

    universe = ContinuousUniverse(coordinates[0], coordinates[-1], leftClosed=True, rightClosed=True)

    return LinguisticScale(tuple(
        LinguisticTerm(name, ScalarFuzzySet(universe, _IntervalTerm(left, right, index == len(labels) - 1)))
        for index, (name, (left, right)) in enumerate(zip(labels, pairwise(coordinates), strict=True))
    ))
