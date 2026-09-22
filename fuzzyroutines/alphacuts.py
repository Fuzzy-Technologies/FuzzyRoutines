# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

r"""Exact discrete and explicitly sampled continuous alpha-cut operations.

An alpha-cut uses the weak boundary convention $\mu(x) \geq \alpha$. Exact
evaluation is possible for a `DiscreteUniverse` because every declared
coordinate is evaluated.  An arbitrary callable over a continuous universe
cannot be solved exactly by finite inspection, so continuous evaluation uses a
separate provenance-rich sampled result and never claims exact geometry.
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
from fuzzyroutines.fuzzysets import ScalarFuzzySet, _RequireGrade
from fuzzyroutines.properties import DiscreteRegion


def _RequireAlpha(alpha):
    """Return a finite alpha threshold in the closed unit interval."""

    alpha = _RequireFiniteReal(alpha, "alpha")

    if not 0 <= alpha <= 1:
        raise ValueError("alpha must lie in the closed interval [0, 1]")

    return alpha


def _RequireSampleCount(sampleCount):
    """Return a sample count that defines at least two grid endpoints."""

    if isinstance(sampleCount, bool) or not isinstance(sampleCount, int):
        raise TypeError("sampleCount must be an integer")

    if sampleCount < 2:
        raise ValueError("sampleCount must be at least two")

    return sampleCount


@dataclass(frozen=True, slots=True)
class SampledAlphaCut:
    r"""Finite observations of a continuous alpha-cut with full provenance.

    Attributes:
        alpha: Weak membership threshold in $[0, 1]$.
        analysisDomain: Closed interval covered by the grid.
        sampleCount: Number of grid coordinates, including both endpoints.
        coordinates: Strictly increasing coordinates spanning
            `analysisDomain`. `SampleAlphaCut` produces a uniform grid;
            direct construction does not revalidate equal spacing.
        grades: Validated membership grades corresponding to `coordinates`.
        cutSamples: Coordinates whose grades satisfy
            $\mathrm{grade} \geq \alpha$.
        method: Required provenance label, currently always `"uniform-grid"`.
            The label records the supported producer contract but does not by
            itself prove equal spacing for a directly constructed instance.
    """

    alpha: Real
    analysisDomain: IntegrationDomain
    sampleCount: int
    coordinates: tuple[Real, ...]
    grades: tuple[Real, ...]
    cutSamples: DiscreteRegion
    method: str = "uniform-grid"

    def __post_init__(self):
        """Require a complete, ordered, and internally consistent sample table."""

        alpha = _RequireAlpha(self.alpha)

        if not isinstance(self.analysisDomain, IntegrationDomain):
            raise TypeError("analysisDomain must be an IntegrationDomain")

        sampleCount = _RequireSampleCount(self.sampleCount)

        if not isinstance(self.coordinates, tuple) or not isinstance(self.grades, tuple):
            raise TypeError("sample coordinates and grades must be explicit tuples")

        if len(self.coordinates) != sampleCount or len(self.grades) != sampleCount:
            raise ValueError("sampleCount must match coordinate and grade counts")

        coordinates = tuple(
            _RequireFiniteReal(coordinate, f"coordinates[{coordinateIndex}]")
            for coordinateIndex, coordinate in enumerate(self.coordinates)
        )

        if any(
            leftCoordinate >= rightCoordinate
            for leftCoordinate, rightCoordinate in pairwise(coordinates)
        ):
            raise ValueError("sample coordinates must be strictly increasing and distinct")

        if (
            coordinates[0] != self.analysisDomain.left
            or coordinates[-1] != self.analysisDomain.right
        ):
            raise ValueError("sample coordinates must include both analysis-domain endpoints")

        grades = tuple(
            _RequireGrade(grade, f"grades[{gradeIndex}]")
            for gradeIndex, grade in enumerate(self.grades)
        )

        if not isinstance(self.cutSamples, DiscreteRegion):
            raise TypeError("cutSamples must be a DiscreteRegion")

        expectedCutPoints = tuple(
            coordinate
            for coordinate, grade in zip(coordinates, grades, strict=True)
            if grade >= alpha
        )

        if self.cutSamples.points != expectedCutPoints:
            raise ValueError("cutSamples must contain exactly the coordinates with grade >= alpha")

        if self.method != "uniform-grid":
            raise ValueError("sampled alpha cuts require method='uniform-grid'")

        object.__setattr__(self, "alpha", alpha)
        object.__setattr__(self, "coordinates", coordinates)
        object.__setattr__(self, "grades", grades)

    @property
    def isExact(self):
        """Prevent finite continuous samples from masquerading as exact geometry."""

        return False


def AlphaCut(fuzzySet, alpha):
    """Return the exact weak alpha-cut of a discrete scalar fuzzy set.

    The returned region contains every declared coordinate `x` satisfying
    `fuzzySet.Membership(x) >= alpha`. Continuous universes fail closed
    because an arbitrary membership callable has no analytical inverse or
    finite exhaustive representation in the current model.

    Args:
        fuzzySet: Scalar fuzzy set over a discrete universe.
        alpha: Weak membership threshold in $[0, 1]$.

    Returns:
        The ordered discrete region containing every qualifying coordinate.

    Raises:
        TypeError: If argument types do not match the discrete contract.
        ValueError: If `alpha` is not a finite value in $[0, 1]$.
    """

    if not isinstance(fuzzySet, ScalarFuzzySet):
        raise TypeError("fuzzySet must be a ScalarFuzzySet")

    alpha = _RequireAlpha(alpha)

    if not isinstance(fuzzySet.universe, DiscreteUniverse):
        raise TypeError(
            "exact alpha cuts require a DiscreteUniverse; "
            "use SampleAlphaCut for explicit continuous observations"
        )

    return DiscreteRegion(
        tuple(
            coordinate
            for coordinate in fuzzySet.universe.points
            if fuzzySet.Membership(coordinate) >= alpha
        )
    )


def SampleAlphaCut(fuzzySet, alpha, analysisDomain, sampleCount=101):
    """Observe a continuous weak alpha-cut on one explicit uniform grid.

    The result records coordinates, validated membership grades, threshold,
    domain, resolution, and method.  It is a sampled observation with
    `isExact == False` and is not a proof of the continuous alpha-cut.

    Args:
        fuzzySet: Scalar fuzzy set over a continuous universe.
        alpha: Weak membership threshold in $[0, 1]$.
        analysisDomain: Closed finite interval to sample inside the universe.
        sampleCount: Number of uniform-grid coordinates, including endpoints.

    Returns:
        A provenance-rich sampled alpha-cut observation.

    Raises:
        TypeError: If argument types do not match the continuous contract.
        ValueError: If a value is invalid or the domain lies outside the
            fuzzy-set universe.
    """

    if not isinstance(fuzzySet, ScalarFuzzySet):
        raise TypeError("fuzzySet must be a ScalarFuzzySet")

    alpha = _RequireAlpha(alpha)

    if not isinstance(fuzzySet.universe, ContinuousUniverse):
        raise TypeError("sampled alpha cuts require a ContinuousUniverse")

    if not isinstance(analysisDomain, IntegrationDomain):
        raise TypeError("analysisDomain must be an IntegrationDomain")

    analysisDomain.ValidateWithin(fuzzySet.universe)
    sampleCount = _RequireSampleCount(sampleCount)
    step = (analysisDomain.right - analysisDomain.left) / (sampleCount - 1)
    # Assign the final endpoint directly so binary64 accumulation cannot move
    # a logically closed grid endpoint outside the declared domain.
    coordinates = tuple(
        analysisDomain.right
        if sampleIndex == sampleCount - 1
        else analysisDomain.left + sampleIndex * step
        for sampleIndex in range(sampleCount)
    )
    grades = tuple(fuzzySet.Membership(coordinate) for coordinate in coordinates)
    cutSamples = DiscreteRegion(
        tuple(
            coordinate
            for coordinate, grade in zip(coordinates, grades, strict=True)
            if grade >= alpha
        )
    )
    return SampledAlphaCut(
        alpha,
        analysisDomain,
        sampleCount,
        coordinates,
        grades,
        cutSamples,
    )
