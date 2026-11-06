# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Collect scalar plot samples before conversion to renderer coordinates."""

from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction
from itertools import groupby, pairwise
from numbers import Rational
from typing import cast

from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse
from fuzzyroutines.exceptions import (
    FuzzyRoutinesError,
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.numeric import _RequireFiniteReal


class PlotSamplingError(FuzzyRoutinesError):
    """A scalar evaluation failed while collecting data for a plot series."""


def SampleDiscretePlot(
    fuzzySet: ScalarFuzzySet,
    seriesName: str,
    *,
    window: tuple[MembershipScalar, MembershipScalar] | None = None,
) -> tuple[tuple[MembershipScalar, MembershipScalar], ...]:
    """Collect one marker sample per visible coordinate in declaration order.

    Args:
        fuzzySet: Scalar set with a discrete universe. Its own membership
            evaluator supplies and validates the grades.
        seriesName: Plot series label included in evaluation failures.
        window: Optional inclusive display limits with finite, increasing
            endpoints. Omitting it keeps the entire discrete universe.

    Returns:
        Coordinate and grade pairs in their original scalar types, including
        zero grades. An empty tuple denotes a fully clipped series. A
        singleton yields one marker without any synthetic padding sample.

    Raises:
        InvalidDomainError: If the universe is continuous or the display
            limits are unordered.
        InvalidParameterTypeError: If a display limit is not a real scalar.
        InvalidParameterError: If a display limit is not finite.
        PlotSamplingError: If scalar evaluation fails at a visible point.
            The original exception is retained as the cause.
    """

    universe = fuzzySet.universe

    if not isinstance(universe, DiscreteUniverse):
        raise InvalidDomainError("Discrete plot sampling requires a DiscreteUniverse.")

    points = universe.points

    if window is not None:
        left = _RequireFiniteReal(window[0], "left display limit")
        right = _RequireFiniteReal(window[1], "right display limit")

        if left >= right:
            raise InvalidDomainError("Plot display limits must satisfy left < right.")

        points = tuple(point for point in points if left <= cast(float, point) <= right)

    return _SamplePoints(fuzzySet, seriesName, points)


@dataclass(frozen=True, slots=True)
class ClosedPlotSamples:
    """Scalar samples and provenance for a single closed display segment.

    Attributes:
        window: Exact endpoints supplied for the sampled segment.
        baseSampleCount: Grid size before merging supplied coordinates.
        addedCoordinates: Visible coordinates that fell outside the base grid.
        samples: Ordered scalar coordinate and grade pairs.
    """

    window: tuple[MembershipScalar, MembershipScalar]
    baseSampleCount: int
    addedCoordinates: tuple[MembershipScalar, ...]
    samples: tuple[tuple[MembershipScalar, MembershipScalar], ...]


def SampleClosedPlotSegment(
    fuzzySet: ScalarFuzzySet,
    seriesName: str,
    window: tuple[MembershipScalar, MembershipScalar],
    *,
    sampleCount: int = 401,
    extraCoordinates: tuple[MembershipScalar, ...] = (),
) -> ClosedPlotSamples:
    """Sample one closed segment, preserving its endpoints and supplied coordinates.

    Args:
        fuzzySet: Scalar set with a continuous universe containing both
            endpoints. Its membership evaluator supplies the grades.
        seriesName: Plot series label included in evaluation failures.
        window: Finite, increasing bounds of the selected closed segment.
        sampleCount: Number of base grid samples, including both endpoints.
        extraCoordinates: Declared knots or input coordinates. Finite values
            inside the segment are merged into the grid without rounding.

    Returns:
        The ordered samples and their grid provenance. This data describes
        scalar evaluations only. It does not authorize connecting markers
        across a jump or infer that an arbitrary callable is continuous.

    Raises:
        InvalidParameterTypeError: If the universe, count or coordinate type
            is unsuitable.
        InvalidParameterError: If the count is below two or a coordinate
            is not finite.
        InvalidDomainError: If the segment falls outside the universe or
            the requested grid cannot be represented by distinct coordinates.
        PlotSamplingError: If scalar membership fails at a visible point.
    """

    universe = fuzzySet.universe

    if not isinstance(universe, ContinuousUniverse):
        raise InvalidParameterTypeError("Closed plot sampling requires a ContinuousUniverse.")

    if isinstance(sampleCount, bool) or not isinstance(sampleCount, int):
        raise InvalidParameterTypeError("Plot sample count must be an integer.")

    if sampleCount < 2:
        raise InvalidParameterError("Plot sample count must be at least two.")

    left = _RequireFiniteReal(window[0], "left display limit")
    right = _RequireFiniteReal(window[1], "right display limit")

    if left >= right or not universe.Contains(left) or not universe.Contains(right):
        raise InvalidDomainError("The closed plot segment must have increasing endpoints inside the universe.")

    grid = _ClosedPlotGrid(left, right, sampleCount)
    tagged = [(left, True), (right, True)]

    for value in extraCoordinates:
        point = _RequireFiniteReal(value, "extra plot coordinate")

        if left <= point <= right:
            tagged.append((point, False))

    tagged.extend((point, True) for point in grid[1:-1])
    tagged.sort(key=lambda entry: entry[0])
    coordinates = []
    added = []

    for point, entries in groupby(tagged, key=lambda entry: entry[0]):
        coordinates.append(point)

        if not any(onGrid for _, onGrid in entries):
            added.append(point)

    return ClosedPlotSamples(window, sampleCount, tuple(added), _SamplePoints(fuzzySet, seriesName, coordinates))


def _ClosedPlotGrid(left: float, right: float, sampleCount: int) -> tuple[float, ...]:
    """Interpolate before binary64 conversion to avoid overflow and grid drift."""

    exactLeft = Fraction(left) if isinstance(left, Rational) else Fraction(float(left))
    exactRight = Fraction(right) if isinstance(right, Rational) else Fraction(float(right))
    step = (exactRight - exactLeft) / (sampleCount - 1)
    grid = (left, *(float(exactLeft + index * step) for index in range(1, sampleCount - 1)), right)

    if any(float(previous) >= float(following) for previous, following in pairwise(grid)):
        raise InvalidDomainError("Plot segment cannot supply the requested distinct grid coordinates.")

    return grid


def _SamplePoints(
    fuzzySet: ScalarFuzzySet, seriesName: str, points: Iterable[MembershipScalar],
) -> tuple[tuple[MembershipScalar, MembershipScalar], ...]:
    """Evaluate the scalar source in order and preserve failures with plot context."""

    samples: list[tuple[MembershipScalar, MembershipScalar]] = []

    for point in points:
        try:
            grade = fuzzySet.Membership(point)

        except Exception as error:
            raise PlotSamplingError(f"Could not sample plot series {seriesName!r} at {point!r}.") from error

        samples.append((point, grade))

    return tuple(samples)
