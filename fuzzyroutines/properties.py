# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Derived support, core, boundary, and height contracts for scalar fuzzy sets.

Continuous analytical results are obtained from the declared geometry of the
membership family.  They are never inferred by scanning floating-point values.
Discrete universes are evaluated exactly at their declared coordinates, while
continuous sampling returns a separate result type that records its numerical
provenance and cannot be mistaken for exact mathematical support.
"""

from dataclasses import dataclass
from itertools import pairwise
from numbers import Real

from fuzzyroutines.domain import (
    ContinuousUniverse,
    DiscreteUniverse,
    IntegrationDomain,
    _RequireFiniteReal,
)
from fuzzyroutines.FuzzyRoutines import MFunction


@dataclass(frozen=True, slots=True)
class ContinuousInterval:
    """One non-empty interval component of a continuous derived region.

    Attributes:
        left: Finite left endpoint, or `None` for negative infinity.
        right: Finite right endpoint, or `None` for positive infinity.
        leftClosed: Whether a finite left endpoint is included.
        rightClosed: Whether a finite right endpoint is included.
    """

    left: Real | None = None
    right: Real | None = None
    leftClosed: bool = False
    rightClosed: bool = False

    def __post_init__(self):
        """Validate finite or unbounded endpoints and singleton semantics."""

        if not isinstance(self.leftClosed, bool) or not isinstance(self.rightClosed, bool):
            raise TypeError("interval closure flags must be boolean values")

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

        if self.left is not None and self.right is not None:
            if self.left > self.right:
                raise ValueError("continuous interval endpoints must satisfy left <= right")

            if self.left == self.right and not (self.leftClosed and self.rightClosed):
                raise ValueError("a singleton interval must be closed at both endpoints")

    @property
    def isSingleton(self):
        """Return whether this component represents exactly one coordinate."""

        return self.left is not None and self.left == self.right

    def Contains(self, coordinate):
        """Return whether a finite coordinate belongs to this interval.

        Args:
            coordinate: Finite real coordinate to test.

        Returns:
            `True` exactly when the endpoint rules admit the coordinate.

        Raises:
            TypeError: If the coordinate is not a real scalar.
            ValueError: If the coordinate is not finite.
        """

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
class ContinuousRegion:
    """Ordered union of disjoint intervals in a continuous scalar universe.

    Attributes:
        intervals: Ordered tuple of non-overlapping interval components.
    """

    intervals: tuple[ContinuousInterval, ...] = ()

    def __post_init__(self):
        """Require an explicit ordered tuple of non-overlapping components."""

        if not isinstance(self.intervals, tuple):
            raise TypeError("continuous region intervals must be an explicit tuple")

        for interval in self.intervals:
            if not isinstance(interval, ContinuousInterval):
                raise TypeError("continuous region components must be ContinuousInterval values")

        for leftInterval, rightInterval in zip(self.intervals, self.intervals[1:]):
            if leftInterval.right is None or rightInterval.left is None:
                raise ValueError("continuous region intervals must be strictly ordered")

            if leftInterval.right > rightInterval.left:
                raise ValueError("continuous region intervals must not overlap")

            if (
                leftInterval.right == rightInterval.left
                and leftInterval.rightClosed
                and rightInterval.leftClosed
            ):
                raise ValueError("continuous region intervals must not share a coordinate")

    @property
    def isEmpty(self):
        """Return whether the region contains no coordinates."""

        return not self.intervals

    def Contains(self, coordinate):
        """Return whether a finite coordinate belongs to any component.

        Args:
            coordinate: Finite real coordinate to test.

        Returns:
            `True` when at least one component contains the coordinate.

        Raises:
            TypeError: If the region is non-empty and the coordinate is not a
                real scalar.
            ValueError: If the region is non-empty and the coordinate is not
                finite.
        """

        return any(interval.Contains(coordinate) for interval in self.intervals)


@dataclass(frozen=True, slots=True)
class DiscreteRegion:
    """Ordered subset of a declared discrete universe.

    Attributes:
        points: Strictly increasing tuple of finite coordinates.
    """

    points: tuple[Real, ...] = ()

    def __post_init__(self):
        """Require finite, strictly increasing, distinct coordinates."""

        if not isinstance(self.points, tuple):
            raise TypeError("discrete region points must be an explicit tuple")

        validatedPoints = tuple(
            _RequireFiniteReal(point, f"points[{pointIndex}]")
            for pointIndex, point in enumerate(self.points)
        )

        if any(leftPoint >= rightPoint for leftPoint, rightPoint in pairwise(validatedPoints)):
            raise ValueError("discrete region points must be strictly increasing and distinct")

        object.__setattr__(self, "points", validatedPoints)

    @property
    def isEmpty(self):
        """Return whether the region contains no declared coordinates."""

        return not self.points

    def Contains(self, coordinate):
        """Return whether a finite coordinate belongs to this discrete region.

        Args:
            coordinate: Finite real coordinate to test.

        Returns:
            `True` when `coordinate` is one of `points`.

        Raises:
            TypeError: If the coordinate is not a real scalar.
            ValueError: If the coordinate is not finite.
        """

        coordinate = _RequireFiniteReal(coordinate, "coordinate")
        return coordinate in self.points


@dataclass(frozen=True, slots=True)
class ContinuousFuzzyProperties:
    """Exact analytical derived properties on a continuous universe.

    Attributes:
        universe: Continuous universe on which all regions are restricted.
        positiveSupport: Coordinates whose membership is strictly positive.
        supportClosure: Closure of `positiveSupport` within the universe.
        core: Coordinates whose membership equals one.
        boundary: Coordinates whose membership lies strictly between zero and
            one under the analytical family contract.
        height: Exact supremum of membership grades on the universe.
    """

    universe: ContinuousUniverse
    positiveSupport: ContinuousRegion
    supportClosure: ContinuousRegion
    core: ContinuousRegion
    boundary: ContinuousRegion
    height: Real

    def __post_init__(self):
        """Require internally consistent regions and a valid membership height."""

        if not isinstance(self.universe, ContinuousUniverse):
            raise TypeError("universe must be a ContinuousUniverse")

        for fieldName in ("positiveSupport", "supportClosure", "core", "boundary"):
            region = getattr(self, fieldName)

            if not isinstance(region, ContinuousRegion):
                raise TypeError(f"{fieldName} must be a ContinuousRegion")

            if _IntersectRegion(region, self.universe) != region:
                raise ValueError(f"{fieldName} must lie within the declared universe")

        height = _RequireFiniteReal(self.height, "height")

        if not 0 <= height <= 1:
            raise ValueError("height must lie in [0, 1]")

        object.__setattr__(self, "height", height)

    @property
    def isExact(self):
        """State that interval geometry came from an analytical family contract."""

        return True


@dataclass(frozen=True, slots=True)
class DiscreteFuzzyProperties:
    """Exact derived properties on an explicitly discrete universe.

    Attributes:
        universe: Exhaustively evaluated discrete universe.
        positiveSupport: Declared points with positive membership.
        supportClosure: Equal to `positiveSupport` in the discrete topology.
        core: Declared points with membership one.
        boundary: Declared points with membership strictly between zero and one.
        height: Maximum membership across all declared points.
    """

    universe: DiscreteUniverse
    positiveSupport: DiscreteRegion
    supportClosure: DiscreteRegion
    core: DiscreteRegion
    boundary: DiscreteRegion
    height: Real

    def __post_init__(self):
        """Require derived point sets to be subsets of the declared universe."""

        if not isinstance(self.universe, DiscreteUniverse):
            raise TypeError("universe must be a DiscreteUniverse")

        universePoints = set(self.universe.points)

        for fieldName in ("positiveSupport", "supportClosure", "core", "boundary"):
            region = getattr(self, fieldName)

            if not isinstance(region, DiscreteRegion):
                raise TypeError(f"{fieldName} must be a DiscreteRegion")

            if not set(region.points) <= universePoints:
                raise ValueError(f"{fieldName} must lie within the declared universe")

        height = _RequireFiniteReal(self.height, "height")

        if not 0 <= height <= 1:
            raise ValueError("height must lie in [0, 1]")

        object.__setattr__(self, "height", height)

    @property
    def isExact(self):
        """State that every coordinate in the declared universe was evaluated."""

        return True


@dataclass(frozen=True, slots=True)
class SampledFuzzyProperties:
    """Approximate observations from finite coordinates over a continuous domain.

    `SampleProperties` produces a uniform grid and derives every recorded
    region from the corresponding grades. Direct construction validates the
    table shape, endpoint coverage, region subsets, and height, but it does not
    revalidate equal spacing or recompute the three recorded regions.

    Attributes:
        analysisDomain: Closed interval covered by the grid.
        sampleCount: Number of coordinates, including both endpoints.
        coordinates: Strictly increasing coordinates spanning
            `analysisDomain`.
        grades: Validated grades corresponding to `coordinates`.
        positiveSupportSamples: Recorded subset of sampled coordinates;
            `SampleProperties` selects grades greater than zero.
        coreSamples: Recorded subset of sampled coordinates;
            `SampleProperties` selects grades equal to one.
        boundarySamples: Recorded subset of sampled coordinates;
            `SampleProperties` selects grades strictly between zero and one.
        heightEstimate: Maximum observed grade, not an exact supremum proof.
        method: Non-empty sampling provenance label. `SampleProperties` uses
            `"uniform-grid"`.
    """

    analysisDomain: IntegrationDomain
    sampleCount: int
    coordinates: tuple[Real, ...]
    grades: tuple[Real, ...]
    positiveSupportSamples: DiscreteRegion
    coreSamples: DiscreteRegion
    boundarySamples: DiscreteRegion
    heightEstimate: Real
    method: str = "uniform-grid"

    def __post_init__(self):
        """Validate the complete provenance and observation table."""

        if not isinstance(self.analysisDomain, IntegrationDomain):
            raise TypeError("analysisDomain must be an IntegrationDomain")

        if isinstance(self.sampleCount, bool) or not isinstance(self.sampleCount, int):
            raise TypeError("sampleCount must be an integer")

        if self.sampleCount < 2:
            raise ValueError("sampleCount must be at least two")

        if not isinstance(self.coordinates, tuple) or not isinstance(self.grades, tuple):
            raise TypeError("sample coordinates and grades must be explicit tuples")

        if len(self.coordinates) != self.sampleCount or len(self.grades) != self.sampleCount:
            raise ValueError("sampleCount must match coordinate and grade counts")

        coordinates = tuple(
            _RequireFiniteReal(coordinate, f"coordinates[{coordinateIndex}]")
            for coordinateIndex, coordinate in enumerate(self.coordinates)
        )

        if any(leftCoordinate >= rightCoordinate for leftCoordinate, rightCoordinate in pairwise(coordinates)):
            raise ValueError("sample coordinates must be strictly increasing and distinct")

        if coordinates[0] != self.analysisDomain.left or coordinates[-1] != self.analysisDomain.right:
            raise ValueError("sample coordinates must include both analysis-domain endpoints")

        grades = tuple(
            _ValidateMembershipGrade(grade, coordinate)
            for coordinate, grade in zip(coordinates, self.grades)
        )
        samplePoints = set(coordinates)

        for fieldName in ("positiveSupportSamples", "coreSamples", "boundarySamples"):
            region = getattr(self, fieldName)

            if not isinstance(region, DiscreteRegion):
                raise TypeError(f"{fieldName} must be a DiscreteRegion")

            if not set(region.points) <= samplePoints:
                raise ValueError(f"{fieldName} must contain only sampled coordinates")

        heightEstimate = _RequireFiniteReal(self.heightEstimate, "heightEstimate")

        if heightEstimate != max(grades):
            raise ValueError("heightEstimate must equal the maximum sampled grade")

        if not isinstance(self.method, str) or not self.method:
            raise TypeError("method must be a non-empty string")

        object.__setattr__(self, "coordinates", coordinates)
        object.__setattr__(self, "grades", grades)
        object.__setattr__(self, "heightEstimate", heightEstimate)

    @property
    def isExact(self):
        """Prevent sampled observations from being presented as exact geometry."""

        return False


def _IntersectIntervals(leftInterval, rightInterval):
    """Return the exact intersection of two interval components or `None`."""

    if leftInterval.left is None:
        left = rightInterval.left
        leftClosed = rightInterval.leftClosed

    elif rightInterval.left is None or leftInterval.left > rightInterval.left:
        left = leftInterval.left
        leftClosed = leftInterval.leftClosed

    elif rightInterval.left > leftInterval.left:
        left = rightInterval.left
        leftClosed = rightInterval.leftClosed

    else:
        left = leftInterval.left
        leftClosed = leftInterval.leftClosed and rightInterval.leftClosed

    if leftInterval.right is None:
        right = rightInterval.right
        rightClosed = rightInterval.rightClosed

    elif rightInterval.right is None or leftInterval.right < rightInterval.right:
        right = leftInterval.right
        rightClosed = leftInterval.rightClosed

    elif rightInterval.right < leftInterval.right:
        right = rightInterval.right
        rightClosed = rightInterval.rightClosed

    else:
        right = leftInterval.right
        rightClosed = leftInterval.rightClosed and rightInterval.rightClosed

    if left is not None and right is not None and (
        left > right or (left == right and not (leftClosed and rightClosed))
    ):
        return None

    return ContinuousInterval(left, right, leftClosed, rightClosed)


def _IntersectRegion(region, universe):
    """Clip an analytical region to a declared continuous universe."""

    universeInterval = ContinuousInterval(
        universe.left,
        universe.right,
        universe.leftClosed,
        universe.rightClosed,
    )
    clippedIntervals = tuple(
        clippedInterval
        for interval in region.intervals
        if (clippedInterval := _IntersectIntervals(interval, universeInterval)) is not None
    )
    return ContinuousRegion(clippedIntervals)


def _ClosureWithin(region, universe):
    """Return the closure of a clipped region in the universe's topology."""

    closedIntervals = tuple(
        ContinuousInterval(
            interval.left,
            interval.right,
            interval.left is not None and universe.Contains(interval.left),
            interval.right is not None and universe.Contains(interval.right),
        )
        for interval in region.intervals
    )
    return ContinuousRegion(closedIntervals)


def _Region(*intervals):
    """Build a continuous region from already ordered interval components."""

    return ContinuousRegion(tuple(intervals))


def _Point(coordinate):
    """Build a closed singleton interval."""

    return ContinuousInterval(coordinate, coordinate, True, True)


def _AnalyticalRegions(membershipFunction):
    """Return exact real-line regions and asymptotic membership limits."""

    functionName = membershipFunction.name
    parameters = membershipFunction.parameters
    realLine = _Region(ContinuousInterval())

    if functionName == "Hyperbolic":
        cutoff = parameters["c"]
        return (
            realLine,
            _Region(ContinuousInterval(None, cutoff, False, True)),
            _Region(ContinuousInterval(cutoff, None, False, False)),
            1.0,
            0.0,
        )

    if functionName == "Bell":
        leftFoot = parameters["a"]
        plateauStart = parameters["b"]
        plateauEnd = parameters["c"]
        rightFoot = plateauEnd + plateauStart - leftFoot
        return (
            _Region(ContinuousInterval(leftFoot, rightFoot)),
            _Region(ContinuousInterval(plateauStart, plateauEnd, True, True)),
            _Region(
                ContinuousInterval(leftFoot, plateauStart),
                ContinuousInterval(plateauEnd, rightFoot),
            ),
            0.0,
            0.0,
        )

    if functionName == "Parabolic":
        leftFoot = parameters["a"]
        coreStart = parameters["b"]
        return (
            _Region(ContinuousInterval(leftFoot, None)),
            _Region(ContinuousInterval(coreStart, None, True, False)),
            _Region(ContinuousInterval(leftFoot, coreStart)),
            0.0,
            1.0,
        )

    if functionName == "Triangle":
        leftFoot = parameters["a"]
        rightFoot = parameters["b"]
        apex = parameters["c"]
        rightClosed = apex == rightFoot
        boundaryIntervals = [ContinuousInterval(leftFoot, apex)]

        if apex < rightFoot:
            boundaryIntervals.append(ContinuousInterval(apex, rightFoot))

        return (
            _Region(ContinuousInterval(leftFoot, rightFoot, False, rightClosed)),
            _Region(_Point(apex)),
            _Region(*boundaryIntervals),
            0.0,
            0.0,
        )

    if functionName == "Trapezium":
        leftFoot = parameters["a"]
        rightFoot = parameters["b"]
        plateauStart = parameters["c"]
        plateauEnd = parameters["d"]
        return (
            _Region(ContinuousInterval(leftFoot, rightFoot)),
            _Region(ContinuousInterval(plateauStart, plateauEnd, True, True)),
            _Region(
                ContinuousInterval(leftFoot, plateauStart),
                ContinuousInterval(plateauEnd, rightFoot),
            ),
            0.0,
            0.0,
        )

    if functionName == "Exponential":
        centre = parameters["a"]
        return (
            realLine,
            _Region(_Point(centre)),
            _Region(
                ContinuousInterval(None, centre),
                ContinuousInterval(centre, None),
            ),
            0.0,
            0.0,
        )

    if functionName == "Sigmoidal":
        if parameters["a"] > 0:
            leftLimit, rightLimit = 0.0, 1.0

        else:
            leftLimit, rightLimit = 1.0, 0.0

        return realLine, _Region(), realLine, leftLimit, rightLimit

    if functionName == "Desirability":
        return realLine, _Region(), realLine, 0.0, 1.0

    raise ValueError(f"unsupported analytical membership family: {functionName!r}")


def _ContinuousHeight(membershipFunction, core, boundary, leftLimit, rightLimit):
    """Derive the exact supremum structure without scanning a numerical grid."""

    if not core.isEmpty:
        return 1.0

    if boundary.isEmpty:
        return 0.0

    candidates = []

    for interval in boundary.intervals:
        if interval.left is None:
            candidates.append(leftLimit)

        else:
            candidates.append(membershipFunction.mju(interval.left))

        if interval.right is None:
            candidates.append(rightLimit)

        else:
            candidates.append(membershipFunction.mju(interval.right))

    return max(candidates)


def _ValidateMembershipGrade(grade, coordinate):
    """Return a finite membership grade in the closed unit interval."""

    grade = _RequireFiniteReal(grade, f"membership grade at {coordinate!r}")

    if not 0 <= grade <= 1:
        raise ValueError(f"membership grade at {coordinate!r} must lie in [0, 1]")

    return grade


def _EvaluateCoordinates(membershipFunction, coordinates):
    """Evaluate and validate a membership function at explicit coordinates."""

    return tuple(
        _ValidateMembershipGrade(membershipFunction.mju(coordinate), coordinate)
        for coordinate in coordinates
    )


def DeriveProperties(membershipFunction, universe):
    """Derive exact fuzzy-set properties for a supported scalar universe.

    Continuous results require one of the analytical
    [MFunction][fuzzyroutines.FuzzyRoutines.MFunction] families.
    A discrete universe is exact because every declared coordinate is evaluated.
    Use [SampleProperties][fuzzyroutines.properties.SampleProperties] for an
    explicitly approximate continuous query.

    Args:
        membershipFunction: Supported historical analytical family.
        universe: Continuous or discrete scalar universe to analyze.

    Returns:
        Exact continuous analytical properties or exhaustive discrete
        properties, matching the universe type.

    Raises:
        TypeError: If either argument has an unsupported contract type.
        ValueError: If the analytical family is unsupported or evaluation
            produces an invalid membership grade.
    """

    if not isinstance(membershipFunction, MFunction):
        raise TypeError("membershipFunction must be an MFunction instance")

    if isinstance(universe, ContinuousUniverse):
        (
            globalPositiveSupport,
            globalCore,
            globalBoundary,
            leftLimit,
            rightLimit,
        ) = _AnalyticalRegions(membershipFunction)
        positiveSupport = _IntersectRegion(globalPositiveSupport, universe)
        supportClosure = _ClosureWithin(positiveSupport, universe)
        core = _IntersectRegion(globalCore, universe)
        boundary = _IntersectRegion(globalBoundary, universe)
        height = _ContinuousHeight(
            membershipFunction,
            core,
            boundary,
            leftLimit,
            rightLimit,
        )
        return ContinuousFuzzyProperties(
            universe,
            positiveSupport,
            supportClosure,
            core,
            boundary,
            height,
        )

    if isinstance(universe, DiscreteUniverse):
        grades = _EvaluateCoordinates(membershipFunction, universe.points)
        positivePoints = tuple(point for point, grade in zip(universe.points, grades) if grade > 0)
        corePoints = tuple(point for point, grade in zip(universe.points, grades) if grade == 1)
        boundaryPoints = tuple(
            point for point, grade in zip(universe.points, grades) if 0 < grade < 1
        )
        positiveSupport = DiscreteRegion(positivePoints)
        return DiscreteFuzzyProperties(
            universe,
            positiveSupport,
            positiveSupport,
            DiscreteRegion(corePoints),
            DiscreteRegion(boundaryPoints),
            max(grades),
        )

    raise TypeError("universe must be a ContinuousUniverse or DiscreteUniverse")


def SampleProperties(membershipFunction, analysisDomain, sampleCount=101):
    """Return explicitly approximate observations on a uniform finite grid.

    Args:
        membershipFunction: Supported historical analytical family to sample.
        analysisDomain: Closed finite interval covered by the grid.
        sampleCount: Number of uniform-grid coordinates, including endpoints.

    Returns:
        Provenance-rich sampled fuzzy-property observations.

    Raises:
        TypeError: If an argument has the wrong contract type.
        ValueError: If `sampleCount` is less than two or a sampled grade is
            outside $[0, 1]$.
    """

    if not isinstance(membershipFunction, MFunction):
        raise TypeError("membershipFunction must be an MFunction instance")

    if not isinstance(analysisDomain, IntegrationDomain):
        raise TypeError("analysisDomain must be an IntegrationDomain")

    if isinstance(sampleCount, bool) or not isinstance(sampleCount, int):
        raise TypeError("sampleCount must be an integer")

    if sampleCount < 2:
        raise ValueError("sampleCount must be at least two")

    step = (analysisDomain.right - analysisDomain.left) / (sampleCount - 1)
    coordinates = tuple(
        analysisDomain.right if sampleIndex == sampleCount - 1 else analysisDomain.left + sampleIndex * step
        for sampleIndex in range(sampleCount)
    )
    grades = _EvaluateCoordinates(membershipFunction, coordinates)
    positivePoints = tuple(point for point, grade in zip(coordinates, grades) if grade > 0)
    corePoints = tuple(point for point, grade in zip(coordinates, grades) if grade == 1)
    boundaryPoints = tuple(point for point, grade in zip(coordinates, grades) if 0 < grade < 1)
    return SampledFuzzyProperties(
        analysisDomain,
        sampleCount,
        coordinates,
        grades,
        DiscreteRegion(positivePoints),
        DiscreteRegion(corePoints),
        DiscreteRegion(boundaryPoints),
        max(grades),
    )
