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

from collections.abc import Mapping
from dataclasses import dataclass
from itertools import pairwise
from typing import cast, overload

from fuzzyroutines.domain import (
    ContinuousUniverse,
    DiscreteUniverse,
    IntegrationDomain,
)
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.membership import (
    MembershipFunction,
    MembershipScalar,
    _AnalyticalSource,
    _GetAnalyticalSource,
    _LegacyAnalyticalAdapter,
)
from fuzzyroutines.numeric import _RequireFiniteReal, _RequireGrade


@dataclass(frozen=True, slots=True)
class ContinuousInterval:
    """One non-empty interval component of a continuous derived region.

    Attributes:
        left: Finite left endpoint, or `None` for negative infinity.
        right: Finite right endpoint, or `None` for positive infinity.
        leftClosed: Whether a finite left endpoint is included.
        rightClosed: Whether a finite right endpoint is included.
    """

    left: MembershipScalar | None = None
    right: MembershipScalar | None = None
    leftClosed: bool = False
    rightClosed: bool = False

    def __post_init__(self) -> None:
        """Validate finite or unbounded endpoints and singleton semantics."""

        if not isinstance(self.leftClosed, bool) or not isinstance(self.rightClosed, bool):
            raise InvalidParameterTypeError("interval closure flags must be boolean values")

        if self.left is None:
            if self.leftClosed:
                raise InvalidDomainError("an unbounded left endpoint cannot be closed")

        else:
            object.__setattr__(self, "left", _RequireFiniteReal(self.left, "left"))

        if self.right is None:
            if self.rightClosed:
                raise InvalidDomainError("an unbounded right endpoint cannot be closed")

        else:
            object.__setattr__(self, "right", _RequireFiniteReal(self.right, "right"))

        if self.left is not None and self.right is not None:
            if cast(float, self.left) > cast(float, self.right):
                raise InvalidDomainError("continuous interval endpoints must satisfy left <= right")

            if self.left == self.right and not (self.leftClosed and self.rightClosed):
                raise InvalidDomainError("a singleton interval must be closed at both endpoints")

    @property
    def isSingleton(self) -> bool:
        """Return whether this component represents exactly one coordinate."""

        return self.left is not None and self.left == self.right

    def Contains(self, coordinate: MembershipScalar) -> bool:
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
            coordinate < cast(float, self.left) or (coordinate == self.left and not self.leftClosed)
        ):
            return False

        return not (
            self.right is not None
            and (coordinate > cast(float, self.right) or (coordinate == self.right and not self.rightClosed))
        )


@dataclass(frozen=True, slots=True)
class ContinuousRegion:
    """Ordered union of disjoint intervals in a continuous scalar universe.

    Attributes:
        intervals: Ordered tuple of non-overlapping interval components.
    """

    intervals: tuple[ContinuousInterval, ...] = ()

    def __post_init__(self) -> None:
        """Require an explicit ordered tuple of non-overlapping components."""

        if not isinstance(self.intervals, tuple):
            raise InvalidParameterTypeError("continuous region intervals must be an explicit tuple")

        for interval in self.intervals:
            if not isinstance(interval, ContinuousInterval):
                raise InvalidParameterTypeError("continuous region components must be ContinuousInterval values")

        for leftInterval, rightInterval in zip(self.intervals, self.intervals[1:]):
            if leftInterval.right is None or rightInterval.left is None:
                raise InvalidDomainError("continuous region intervals must be strictly ordered")

            if cast(float, leftInterval.right) > cast(float, rightInterval.left):
                raise InvalidDomainError("continuous region intervals must not overlap")

            if (
                leftInterval.right == rightInterval.left
                and leftInterval.rightClosed
                and rightInterval.leftClosed
            ):
                raise InvalidDomainError("continuous region intervals must not share a coordinate")

    @property
    def isEmpty(self) -> bool:
        """Return whether the region contains no coordinates."""

        return not self.intervals

    def Contains(self, coordinate: MembershipScalar) -> bool:
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

    points: tuple[MembershipScalar, ...] = ()

    def __post_init__(self) -> None:
        """Require finite, strictly increasing, distinct coordinates."""

        if not isinstance(self.points, tuple):
            raise InvalidParameterTypeError("discrete region points must be an explicit tuple")

        validatedPoints = tuple(
            _RequireFiniteReal(point, f"points[{pointIndex}]")
            for pointIndex, point in enumerate(self.points)
        )

        if any(leftPoint >= rightPoint for leftPoint, rightPoint in pairwise(validatedPoints)):
            raise InvalidDomainError("discrete region points must be strictly increasing and distinct")

        object.__setattr__(self, "points", validatedPoints)

    @property
    def isEmpty(self) -> bool:
        """Return whether the region contains no declared coordinates."""

        return not self.points

    def Contains(self, coordinate: MembershipScalar) -> bool:
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
    height: MembershipScalar

    def __post_init__(self) -> None:
        """Require internally consistent regions and a valid membership height."""

        if not isinstance(self.universe, ContinuousUniverse):
            raise InvalidParameterTypeError("universe must be a ContinuousUniverse")

        for fieldName in ("positiveSupport", "supportClosure", "core", "boundary"):
            region = getattr(self, fieldName)

            if not isinstance(region, ContinuousRegion):
                raise InvalidParameterTypeError(f"{fieldName} must be a ContinuousRegion")

            if _IntersectRegion(region, self.universe) != region:
                raise InvalidDomainError(f"{fieldName} must lie within the declared universe")

        height = _RequireFiniteReal(self.height, "height")

        if not 0 <= height <= 1:
            raise InvalidParameterError("height must lie in [0, 1]")

        object.__setattr__(self, "height", height)

    @property
    def isExact(self) -> bool:
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
    height: MembershipScalar

    def __post_init__(self) -> None:
        """Require derived point sets to be subsets of the declared universe."""

        if not isinstance(self.universe, DiscreteUniverse):
            raise InvalidParameterTypeError("universe must be a DiscreteUniverse")

        universePoints = set(self.universe.points)

        for fieldName in ("positiveSupport", "supportClosure", "core", "boundary"):
            region = getattr(self, fieldName)

            if not isinstance(region, DiscreteRegion):
                raise InvalidParameterTypeError(f"{fieldName} must be a DiscreteRegion")

            if not set(region.points) <= universePoints:
                raise InvalidDomainError(f"{fieldName} must lie within the declared universe")

        height = _RequireFiniteReal(self.height, "height")

        if not 0 <= height <= 1:
            raise InvalidParameterError("height must lie in [0, 1]")

        object.__setattr__(self, "height", height)

    @property
    def isExact(self) -> bool:
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
    coordinates: tuple[MembershipScalar, ...]
    grades: tuple[MembershipScalar, ...]
    positiveSupportSamples: DiscreteRegion
    coreSamples: DiscreteRegion
    boundarySamples: DiscreteRegion
    heightEstimate: MembershipScalar
    method: str = "uniform-grid"

    def __post_init__(self) -> None:
        """Validate the complete provenance and observation table."""

        if not isinstance(self.analysisDomain, IntegrationDomain):
            raise InvalidParameterTypeError("analysisDomain must be an IntegrationDomain")

        if isinstance(self.sampleCount, bool) or not isinstance(self.sampleCount, int):
            raise InvalidParameterTypeError("sampleCount must be an integer")

        if self.sampleCount < 2:
            raise InvalidParameterError("sampleCount must be at least two")

        if not isinstance(self.coordinates, tuple) or not isinstance(self.grades, tuple):
            raise InvalidParameterTypeError("sample coordinates and grades must be explicit tuples")

        if len(self.coordinates) != self.sampleCount or len(self.grades) != self.sampleCount:
            raise InvalidParameterError("sampleCount must match coordinate and grade counts")

        coordinates = tuple(
            _RequireFiniteReal(coordinate, f"coordinates[{coordinateIndex}]")
            for coordinateIndex, coordinate in enumerate(self.coordinates)
        )

        if any(leftCoordinate >= rightCoordinate for leftCoordinate, rightCoordinate in pairwise(coordinates)):
            raise InvalidDomainError("sample coordinates must be strictly increasing and distinct")

        if coordinates[0] != self.analysisDomain.left or coordinates[-1] != self.analysisDomain.right:
            raise InvalidDomainError("sample coordinates must include both analysis-domain endpoints")

        grades = tuple(
            _ValidateMembershipGrade(grade, coordinate)
            for coordinate, grade in zip(coordinates, self.grades)
        )
        samplePoints = set(coordinates)

        for fieldName in ("positiveSupportSamples", "coreSamples", "boundarySamples"):
            region = getattr(self, fieldName)

            if not isinstance(region, DiscreteRegion):
                raise InvalidParameterTypeError(f"{fieldName} must be a DiscreteRegion")

            if not set(region.points) <= samplePoints:
                raise InvalidParameterError(f"{fieldName} must contain only sampled coordinates")

        heightEstimate = _RequireFiniteReal(self.heightEstimate, "heightEstimate")

        if heightEstimate != max(grades):
            raise InvalidParameterError("heightEstimate must equal the maximum sampled grade")

        if not isinstance(self.method, str) or not self.method:
            raise InvalidParameterTypeError("method must be a non-empty string")

        object.__setattr__(self, "coordinates", coordinates)
        object.__setattr__(self, "grades", grades)
        object.__setattr__(self, "heightEstimate", heightEstimate)

    @property
    def isExact(self) -> bool:
        """Prevent sampled observations from being presented as exact geometry."""

        return False


def _IntersectIntervals(
    leftInterval: ContinuousInterval,
    rightInterval: ContinuousInterval,
) -> ContinuousInterval | None:
    """Return the exact intersection of two interval components or `None`."""

    if leftInterval.left is None:
        left = rightInterval.left
        leftClosed = rightInterval.leftClosed

    elif rightInterval.left is None or cast(float, leftInterval.left) > cast(float, rightInterval.left):
        left = leftInterval.left
        leftClosed = leftInterval.leftClosed

    elif cast(float, rightInterval.left) > cast(float, leftInterval.left):
        left = rightInterval.left
        leftClosed = rightInterval.leftClosed

    else:
        left = leftInterval.left
        leftClosed = leftInterval.leftClosed and rightInterval.leftClosed

    if leftInterval.right is None:
        right = rightInterval.right
        rightClosed = rightInterval.rightClosed

    elif rightInterval.right is None or cast(float, leftInterval.right) < cast(float, rightInterval.right):
        right = leftInterval.right
        rightClosed = leftInterval.rightClosed

    elif cast(float, rightInterval.right) < cast(float, leftInterval.right):
        right = rightInterval.right
        rightClosed = rightInterval.rightClosed

    else:
        right = leftInterval.right
        rightClosed = leftInterval.rightClosed and rightInterval.rightClosed

    if left is not None and right is not None and (
        cast(float, left) > cast(float, right) or (left == right and not (leftClosed and rightClosed))
    ):
        return None

    return ContinuousInterval(left, right, leftClosed, rightClosed)


def _IntersectRegion(region: ContinuousRegion, universe: ContinuousUniverse) -> ContinuousRegion:
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


def _ClosureWithin(region: ContinuousRegion, universe: ContinuousUniverse) -> ContinuousRegion:
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


def _Region(*intervals: ContinuousInterval) -> ContinuousRegion:
    """Build a continuous region from already ordered interval components."""

    return ContinuousRegion(tuple(intervals))


def _Point(coordinate: MembershipScalar) -> ContinuousInterval:
    """Build a closed singleton interval."""

    return ContinuousInterval(coordinate, coordinate, True, True)


def _AnalyticalRegions(
    membershipFunction: _AnalyticalSource,
) -> tuple[ContinuousRegion, ContinuousRegion, ContinuousRegion, MembershipScalar, MembershipScalar]:
    """Return exact real-line regions and asymptotic membership limits."""

    # These regions are algebraic consequences of the canonical formulas in
    # docs/mathematics/membership-function-contracts.md. Never infer them from
    # floating-point samples: Gaussian tails, for example, may underflow.
    functionName = membershipFunction.name
    parameters = cast(Mapping[str, float], membershipFunction.parameters)
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

    raise InvalidParameterError(f"unsupported analytical membership family: {functionName!r}")


def _ContinuousHeight(
    membershipFunction: _AnalyticalSource,
    core: ContinuousRegion,
    boundary: ContinuousRegion,
    leftLimit: MembershipScalar,
    rightLimit: MembershipScalar,
) -> MembershipScalar:
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


def _ValidateMembershipGrade(grade: MembershipScalar, coordinate: MembershipScalar) -> float:
    """Return a finite membership grade in the closed unit interval."""

    return _RequireGrade(grade, f"membership grade at {coordinate!r}")


def _EvaluateCoordinates(
    membershipFunction: _AnalyticalSource | _LegacyAnalyticalAdapter,
    coordinates: tuple[MembershipScalar, ...],
) -> tuple[float, ...]:
    """Evaluate and validate a membership function at explicit coordinates."""

    return tuple(
        _ValidateMembershipGrade(membershipFunction.mju(coordinate), coordinate)
        for coordinate in coordinates
    )


@overload
def DeriveProperties(
    membershipFunction: MembershipFunction | _AnalyticalSource | _LegacyAnalyticalAdapter,
    universe: ContinuousUniverse,
) -> ContinuousFuzzyProperties:
    """Describe exact analytical evidence on a continuous universe."""


@overload
def DeriveProperties(
    membershipFunction: MembershipFunction | _AnalyticalSource | _LegacyAnalyticalAdapter,
    universe: DiscreteUniverse,
) -> DiscreteFuzzyProperties:
    """Describe exhaustive evidence on a discrete universe."""


def DeriveProperties(
    membershipFunction: MembershipFunction | _AnalyticalSource | _LegacyAnalyticalAdapter,
    universe: ContinuousUniverse | DiscreteUniverse,
) -> ContinuousFuzzyProperties | DiscreteFuzzyProperties:
    """Derive exact fuzzy-set properties for a supported scalar universe.

    Continuous results require a modern
    [MembershipFunction][fuzzyroutines.membership.MembershipFunction] or a
    historical [MFunction][fuzzyroutines.FuzzyRoutines.MFunction] adapter.
    Exact analytical evidence is copied from a validated formula source; an
    arbitrary callable does not prove continuous support or height.
    A discrete universe is exact because every declared coordinate is evaluated.
    Use [SampleProperties][fuzzyroutines.properties.SampleProperties] for an
    explicitly approximate continuous query.

    Args:
        membershipFunction: Modern analytical family or supported historical
            analytical adapter.
        universe: Continuous or discrete scalar universe to analyze.

    Returns:
        Exact continuous analytical properties or exhaustive discrete
        properties, matching the universe type.

    Raises:
        TypeError: If either argument has an unsupported contract type.
        ValueError: If the analytical family is unsupported or evaluation
            produces an invalid membership grade.
    """

    source: _AnalyticalSource | _LegacyAnalyticalAdapter | None

    if not (isinstance(universe, DiscreteUniverse) and isinstance(membershipFunction, _LegacyAnalyticalAdapter)):
        source = _GetAnalyticalSource(membershipFunction)

    else:
        source = membershipFunction

    if source is None:
        if isinstance(universe, ContinuousUniverse) and isinstance(membershipFunction, _LegacyAnalyticalAdapter):
            raise InvalidParameterError("exact analytical evidence requires an unchanged registered evaluator")

        raise InvalidParameterTypeError("membershipFunction must be a supported analytical membership source")

    if isinstance(universe, ContinuousUniverse):
        # Continuous inputs always pass through _GetAnalyticalSource above.
        analyticalSource = cast(_AnalyticalSource, source)
        (
            globalPositiveSupport,
            globalCore,
            globalBoundary,
            leftLimit,
            rightLimit,
        ) = _AnalyticalRegions(analyticalSource)
        positiveSupport = _IntersectRegion(globalPositiveSupport, universe)
        supportClosure = _ClosureWithin(positiveSupport, universe)
        core = _IntersectRegion(globalCore, universe)
        boundary = _IntersectRegion(globalBoundary, universe)
        height = _ContinuousHeight(
            analyticalSource,
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
        grades = _EvaluateCoordinates(source, universe.points)
        positivePoints = tuple(point for point, grade in zip(universe.points, grades) if grade > 0)
        corePoints = tuple(point for point, grade in zip(universe.points, grades) if grade == 1)
        boundaryPoints = tuple(
            point for point, grade in zip(universe.points, grades) if 0 < grade < 1
        )
        discreteSupport = DiscreteRegion(positivePoints)
        return DiscreteFuzzyProperties(
            universe,
            discreteSupport,
            discreteSupport,
            DiscreteRegion(corePoints),
            DiscreteRegion(boundaryPoints),
            max(grades),
        )

    raise InvalidParameterTypeError("universe must be a ContinuousUniverse or DiscreteUniverse")


def SampleProperties(
    membershipFunction: MembershipFunction | _AnalyticalSource | _LegacyAnalyticalAdapter,
    analysisDomain: IntegrationDomain,
    sampleCount: int = 101,
) -> SampledFuzzyProperties:
    """Return explicitly approximate observations on a uniform finite grid.

    Args:
        membershipFunction: Modern analytical family or historical analytical
            adapter whose scalar evaluations are sampled.
        analysisDomain: Closed finite interval covered by the grid.
        sampleCount: Number of uniform-grid coordinates, including endpoints.

    Returns:
        Provenance-rich sampled fuzzy-property observations.

    Raises:
        TypeError: If an argument has the wrong contract type.
        ValueError: If `sampleCount` is less than two or a sampled grade is
            outside $[0, 1]$.
    """

    source: _AnalyticalSource | _LegacyAnalyticalAdapter | None

    if not isinstance(membershipFunction, _LegacyAnalyticalAdapter):
        source = _GetAnalyticalSource(membershipFunction)

    else:
        source = membershipFunction

    if source is None:
        raise InvalidParameterTypeError("membershipFunction must be a supported analytical membership source")

    if not isinstance(analysisDomain, IntegrationDomain):
        raise InvalidParameterTypeError("analysisDomain must be an IntegrationDomain")

    if isinstance(sampleCount, bool) or not isinstance(sampleCount, int):
        raise InvalidParameterTypeError("sampleCount must be an integer")

    if sampleCount < 2:
        raise InvalidParameterError("sampleCount must be at least two")

    step = (cast(float, analysisDomain.right) - cast(float, analysisDomain.left)) / (sampleCount - 1)
    # Preserve the exact declared right endpoint instead of trusting the last
    # rounded multiply-add; see source-algorithm-invariants.md.
    coordinates = tuple(
        analysisDomain.right if sampleIndex == sampleCount - 1 else cast(float, analysisDomain.left) + sampleIndex * step
        for sampleIndex in range(sampleCount)
    )
    grades = _EvaluateCoordinates(source, coordinates)
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
