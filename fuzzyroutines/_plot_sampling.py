# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Collect scalar plot samples before conversion to renderer coordinates."""

from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction
from itertools import groupby, pairwise
from math import inf, nextafter
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
class ContinuousPlotSamples:
    """Scalar samples and provenance for a single continuous display segment.

    Attributes:
        window: Exact clipped geometric bounds before excluding open edges.
        baseSampleCount: Grid size before merging supplied coordinates.
        addedCoordinates: Visible coordinates that fell outside the base grid.
        samples: Ordered scalar coordinate and grade pairs.
    """

    window: tuple[MembershipScalar, MembershipScalar]
    baseSampleCount: int
    addedCoordinates: tuple[MembershipScalar, ...]
    samples: tuple[tuple[MembershipScalar, MembershipScalar], ...]


@dataclass(frozen=True, slots=True)
class SegmentedPlotSamples:
    """Independent paths and isolated scalar markers at declared breaks.

    Attributes:
        segments: Ordered sample collections for separate artists.
        breakMarkers: Exact coordinate and grade at each included break.
    """

    segments: tuple[ContinuousPlotSamples, ...]
    breakMarkers: tuple[tuple[MembershipScalar, MembershipScalar], ...]


@dataclass(frozen=True, slots=True)
class _PlotInterval:
    """Finite geometric bounds with explicit endpoint inclusion."""

    left: float
    right: float
    leftClosed: bool
    rightClosed: bool

    def Includes(self, point: float) -> bool:
        """Check membership without changing the scalar representation."""

        return (self.left < point or (self.leftClosed and self.left == point)) and (
            point < self.right or (self.rightClosed and point == self.right)
        )


def SampleClosedPlotSegment(
    fuzzySet: ScalarFuzzySet,
    seriesName: str,
    window: tuple[MembershipScalar, MembershipScalar],
    *,
    sampleCount: int = 401,
    extraCoordinates: tuple[MembershipScalar, ...] = (),
) -> ContinuousPlotSamples:
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

    _CheckPlotSampleCount(sampleCount)

    left = _RequireFiniteReal(window[0], "left display limit")
    right = _RequireFiniteReal(window[1], "right display limit")

    if left >= right or not universe.Contains(left) or not universe.Contains(right):
        raise InvalidDomainError("The closed plot segment must have increasing endpoints inside the universe.")

    interval = _PlotInterval(left, right, True, True)
    return _SamplePlotInterval(fuzzySet, seriesName, interval, sampleCount, extraCoordinates)


def SampleClippedPlotSegment(
    fuzzySet: ScalarFuzzySet,
    seriesName: str,
    window: tuple[MembershipScalar, MembershipScalar],
    *,
    sampleCount: int = 401,
    extraCoordinates: tuple[MembershipScalar, ...] = (),
) -> ContinuousPlotSamples | None:
    """Sample the intersection of a continuous universe and a display window.

    Args:
        fuzzySet: Scalar set whose continuous universe clips the window.
        seriesName: Plot series label included in evaluation failures.
        window: Finite, increasing, inclusive display bounds.
        sampleCount: Number of base grid points for a nondegenerate segment.
        extraCoordinates: Declared coordinates to preserve in the
            intersection, including values between an open edge and the
            first representable binary64 grid point.

    Returns:
        Samples and the true clipped bounds, or `None` for an empty
        intersection. A shared included boundary produces one sample.
        Open bounds stay in the geometry while the grid starts or ends
        inside them. The result supplies no continuity or artist topology.

    Raises:
        InvalidParameterTypeError: If the universe, count or coordinate type
            is unsuitable.
        InvalidParameterError: If the count is below two or a coordinate
            is not finite.
        InvalidDomainError: If the display window is unordered or there
            are too few distinct display coordinates for the base grid.
        PlotSamplingError: If scalar membership fails at a visible point.
    """

    universe = fuzzySet.universe

    if not isinstance(universe, ContinuousUniverse):
        raise InvalidParameterTypeError("Clipped plot sampling requires a ContinuousUniverse.")

    _CheckPlotSampleCount(sampleCount)
    interval = _ClipPlotWindow(universe, window)

    if interval is None:
        return None

    return _SamplePlotInterval(fuzzySet, seriesName, interval, sampleCount, extraCoordinates)


def SampleSegmentedPlot(
    fuzzySet: ScalarFuzzySet,
    seriesName: str,
    window: tuple[MembershipScalar, MembershipScalar],
    *,
    breakCoordinates: tuple[MembershipScalar, ...],
    samplesPerSegment: int,
    extraCoordinates: tuple[MembershipScalar, ...] = (),
) -> SegmentedPlotSamples:
    """Split a visible scalar series into independent paths at declared breaks.

    Args:
        fuzzySet: Scalar set with a continuous universe.
        seriesName: Plot series label included in evaluation failures.
        window: Inclusive finite display bounds, clipped to the universe.
        breakCoordinates: Declared discontinuity or separation coordinates.
            Breaks outside the visible set are ignored.
        samplesPerSegment: Base grid count for each nondegenerate path.
        extraCoordinates: Declared knots or inputs to merge into the paths.

    Returns:
        Independent paths that exclude every declared break and one
        isolated marker at each included break. The marker represents
        the actual scalar value. The caller must establish continuity within
        each path before drawing lines. No one-sided limit is inferred.

    Raises:
        InvalidParameterTypeError: If the universe or scalar types are unsuitable.
        InvalidParameterError: If the count is below two or a coordinate is not finite.
        InvalidDomainError: If the window is unordered or the grids cannot fit.
        PlotSamplingError: If scalar membership fails at a visible point.
    """

    universe = fuzzySet.universe

    if not isinstance(universe, ContinuousUniverse):
        raise InvalidParameterTypeError("Segmented plot sampling requires a ContinuousUniverse.")

    _CheckPlotSampleCount(samplesPerSegment)
    interval = _ClipPlotWindow(universe, window)

    if interval is None:
        return SegmentedPlotSamples((), ())

    declared = sorted(_RequireFiniteReal(point, "plot break coordinate") for point in breakCoordinates)
    visibleBreaks = tuple(point for point, _ in groupby(declared) if interval.Includes(point))

    if not visibleBreaks:
        segment = _SamplePlotInterval(fuzzySet, seriesName, interval, samplesPerSegment, extraCoordinates)
        return SegmentedPlotSamples((segment,), ())

    interiorBreaks = (point for point in visibleBreaks if interval.left < point < interval.right)
    edges = (interval.left, *interiorBreaks, interval.right)
    leftClosed = interval.leftClosed and interval.left != visibleBreaks[0]
    rightClosed = interval.rightClosed and interval.right != visibleBreaks[-1]
    segments = tuple(
        _SamplePlotInterval(
            fuzzySet, seriesName,
            _PlotInterval(left, right, left == interval.left and leftClosed, right == interval.right and rightClosed),
            samplesPerSegment, extraCoordinates,
        )
        for left, right in pairwise(edges)
        if left < right
    )
    return SegmentedPlotSamples(segments, _SamplePoints(fuzzySet, seriesName, visibleBreaks))


def _ClipPlotWindow(
    universe: ContinuousUniverse, window: tuple[MembershipScalar, MembershipScalar],
) -> _PlotInterval | None:
    """Intersect a finite display window with the continuous universe."""

    left = _RequireFiniteReal(window[0], "left display limit")
    right = _RequireFiniteReal(window[1], "right display limit")

    if left >= right:
        raise InvalidDomainError("Plot display limits must satisfy left < right.")

    if universe.left is not None:
        left = max(left, cast(float, universe.left))

    if universe.right is not None:
        right = min(right, cast(float, universe.right))

    if left > right or (left == right and not universe.Contains(left)):
        return None

    return _PlotInterval(left, right, universe.Contains(left), universe.Contains(right))


def _SamplePlotInterval(
    fuzzySet: ScalarFuzzySet,
    seriesName: str,
    interval: _PlotInterval,
    sampleCount: int,
    extraCoordinates: tuple[MembershipScalar, ...],
) -> ContinuousPlotSamples:
    """Sample a clipped interval with its own endpoint inclusion rules."""

    left, right = interval.left, interval.right

    if left == right:
        return _SampleContinuousGrid(fuzzySet, seriesName, interval, (left,), extraCoordinates)

    first = left if interval.leftClosed else _InteriorFloat(left, inf)
    last = right if interval.rightClosed else _InteriorFloat(right, -inf)

    if first >= last:
        raise InvalidDomainError("Plot segment cannot supply the requested distinct grid coordinates.")

    grid = _ClosedPlotGrid(first, last, sampleCount)
    return _SampleContinuousGrid(fuzzySet, seriesName, interval, grid, extraCoordinates)


def _CheckPlotSampleCount(sampleCount: int) -> None:
    """Require an integer count for a nondegenerate plot grid."""

    if isinstance(sampleCount, bool) or not isinstance(sampleCount, int):
        raise InvalidParameterTypeError("Plot sample count must be an integer.")

    if sampleCount < 2:
        raise InvalidParameterError("Plot sample count must be at least two.")


def _InteriorFloat(edge: float, direction: float) -> float:
    """Find the closest binary64 value strictly toward the interval interior."""

    rounded = float(edge)
    inside = rounded > edge if direction > 0 else rounded < edge
    return rounded if inside else nextafter(rounded, direction)


def _SampleContinuousGrid(
    fuzzySet: ScalarFuzzySet,
    seriesName: str,
    interval: _PlotInterval,
    grid: tuple[float, ...],
    extraCoordinates: tuple[MembershipScalar, ...],
) -> ContinuousPlotSamples:
    """Merge exact declared coordinates and evaluate the visible grid in order."""

    left, right = interval.left, interval.right
    tagged = [(point, True) for point in (grid[0], grid[-1]) if point == left or point == right]

    for value in extraCoordinates:
        point = _RequireFiniteReal(value, "extra plot coordinate")

        if interval.Includes(point):
            tagged.append((point, False))

    tagged.extend((point, True) for point in grid)
    tagged.sort(key=lambda entry: entry[0])
    coordinates = []
    added = []

    for point, entries in groupby(tagged, key=lambda entry: entry[0]):
        coordinates.append(point)

        if not any(onGrid for _, onGrid in entries):
            added.append(point)

    return ContinuousPlotSamples((left, right), len(grid), tuple(added), _SamplePoints(fuzzySet, seriesName, coordinates))


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
