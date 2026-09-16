"""Explicit equality and inclusion relations for scalar fuzzy sets.

Arbitrary Python membership callables cannot be proven equal over a continuous
interval by finite evaluation.  This module therefore evaluates discrete
universes exhaustively and requires an explicit finite comparison domain for
continuous universes.  Exact and tolerance-based numeric semantics are always
selected by an immutable policy object.
"""

import math
from dataclasses import dataclass
from itertools import pairwise
from numbers import Real

from fuzzyroutines.domain import (
    ContinuousUniverse,
    DiscreteUniverse,
    _RequireFiniteReal,
)
from fuzzyroutines.fuzzysets import _RequireCompatibleSets, _RequireGrade


@dataclass(frozen=True, slots=True)
class ComparisonDomain:
    """Finite ordered coordinates used to compare continuous fuzzy sets."""

    points: tuple[Real, ...]

    def __post_init__(self):
        """Require a non-empty tuple of finite, strictly increasing points."""

        if not isinstance(self.points, tuple):
            raise TypeError("comparison-domain points must be an explicit tuple")

        if not self.points:
            raise ValueError("comparison domain must contain at least one coordinate")

        validatedPoints = tuple(
            _RequireFiniteReal(point, f"points[{pointIndex}]")
            for pointIndex, point in enumerate(self.points)
        )

        if any(leftPoint >= rightPoint for leftPoint, rightPoint in pairwise(validatedPoints)):
            raise ValueError("comparison-domain points must be strictly increasing and distinct")

        object.__setattr__(self, "points", validatedPoints)

    def ValidateWithin(self, universe):
        """Return this domain after proving every point belongs to the universe."""

        if not isinstance(universe, ContinuousUniverse):
            raise TypeError("comparison domains are used only with ContinuousUniverse")

        if any(not universe.Contains(point) for point in self.points):
            raise ValueError("every comparison-domain point must belong to the universe")

        return self


@dataclass(frozen=True, slots=True)
class ComparisonPolicy:
    """Explicit exact or tolerance-based membership comparison semantics."""

    mode: str
    absoluteTolerance: Real | None = None
    relativeTolerance: Real | None = None

    def __post_init__(self):
        """Reject incomplete, ambiguous, or zero-effect comparison policies."""

        if self.mode == "exact":
            if self.absoluteTolerance is not None or self.relativeTolerance is not None:
                raise ValueError("exact comparison does not accept tolerances")

            return

        if self.mode != "tolerance":
            raise ValueError(f"unknown comparison mode: {self.mode!r}")

        absoluteTolerance = _RequireFiniteReal(self.absoluteTolerance, "absoluteTolerance")
        relativeTolerance = _RequireFiniteReal(self.relativeTolerance, "relativeTolerance")

        if absoluteTolerance < 0 or relativeTolerance < 0:
            raise ValueError("comparison tolerances must be non-negative")

        if absoluteTolerance == 0 and relativeTolerance == 0:
            raise ValueError("tolerance comparison requires at least one positive tolerance")

        object.__setattr__(self, "absoluteTolerance", absoluteTolerance)
        object.__setattr__(self, "relativeTolerance", relativeTolerance)

    def Equal(self, leftGrade, rightGrade):
        """Return whether two validated membership grades are equal by this policy."""

        leftGrade = _RequireGrade(leftGrade, "leftGrade")
        rightGrade = _RequireGrade(rightGrade, "rightGrade")

        if self.mode == "exact":
            return leftGrade == rightGrade

        return math.isclose(
            leftGrade,
            rightGrade,
            abs_tol=self.absoluteTolerance,
            rel_tol=self.relativeTolerance,
        )

    def Included(self, subsetGrade, supersetGrade):
        """Return whether one grade is included in another by this policy."""

        subsetGrade = _RequireGrade(subsetGrade, "subsetGrade")
        supersetGrade = _RequireGrade(supersetGrade, "supersetGrade")

        if subsetGrade <= supersetGrade:
            return True

        if self.mode == "exact":
            return False

        return self.Equal(subsetGrade, supersetGrade)


def _ResolveComparisonPoints(universe, comparisonDomain):
    """Resolve exhaustive discrete points or validate an explicit sampled domain."""

    if isinstance(universe, DiscreteUniverse):
        if comparisonDomain is not None:
            raise ValueError("discrete fuzzy-set relations always evaluate the complete universe")

        return universe.points

    if comparisonDomain is None:
        raise ValueError("continuous fuzzy-set relations require an explicit ComparisonDomain")

    if not isinstance(comparisonDomain, ComparisonDomain):
        raise TypeError("comparisonDomain must be a ComparisonDomain")

    return comparisonDomain.ValidateWithin(universe).points


def EqualOnDomain(leftSet, rightSet, comparisonPolicy, comparisonDomain=None):
    """Compare membership equality over an exhaustive or explicit finite domain.

    For a discrete universe the complete declared point set is exhaustive and
    ``comparisonDomain`` must be omitted.  For a continuous universe the result
    describes only the explicitly supplied sample points; it is not a proof of
    global functional equality.
    """

    leftSet, rightSet = _RequireCompatibleSets(leftSet, rightSet)

    if not isinstance(comparisonPolicy, ComparisonPolicy):
        raise TypeError("comparisonPolicy must be a ComparisonPolicy")

    comparisonPoints = _ResolveComparisonPoints(leftSet.universe, comparisonDomain)

    return all(
        comparisonPolicy.Equal(leftSet.Membership(point), rightSet.Membership(point))
        for point in comparisonPoints
    )


def IncludedOnDomain(subset, superset, comparisonPolicy, comparisonDomain=None):
    """Evaluate fuzzy inclusion over an exhaustive or explicit finite domain.

    Inclusion means ``mu_subset(x) <= mu_superset(x)`` at every evaluated point.
    Tolerance mode permits only violations whose two grades are numerically
    close under the explicit comparison policy.
    """

    subset, superset = _RequireCompatibleSets(subset, superset)

    if not isinstance(comparisonPolicy, ComparisonPolicy):
        raise TypeError("comparisonPolicy must be a ComparisonPolicy")

    comparisonPoints = _ResolveComparisonPoints(subset.universe, comparisonDomain)

    return all(
        comparisonPolicy.Included(subset.Membership(point), superset.Membership(point))
        for point in comparisonPoints
    )
