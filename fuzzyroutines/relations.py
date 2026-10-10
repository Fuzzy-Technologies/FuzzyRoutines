# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

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
from typing import cast

from fuzzyroutines.domain import (
    ContinuousUniverse,
    DiscreteUniverse,
)
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet, _RequireCompatibleSets
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.numeric import _RequireFiniteReal, _RequireGrade


@dataclass(frozen=True, slots=True)
class ComparisonDomain:
    """Finite ordered coordinates used to compare continuous fuzzy sets.

    Attributes:
        points: Non-empty, strictly increasing tuple of finite coordinates.
    """

    points: tuple[MembershipScalar, ...]

    def __post_init__(self) -> None:
        """Require a non-empty tuple of finite, strictly increasing points."""

        if not isinstance(self.points, tuple):
            raise InvalidParameterTypeError("comparison-domain points must be an explicit tuple")

        if not self.points:
            raise InvalidDomainError("comparison domain must contain at least one coordinate")

        validatedPoints = tuple(
            _RequireFiniteReal(point, f"points[{pointIndex}]")
            for pointIndex, point in enumerate(self.points)
        )

        if any(leftPoint >= rightPoint for leftPoint, rightPoint in pairwise(validatedPoints)):
            raise InvalidDomainError("comparison-domain points must be strictly increasing and distinct")

        object.__setattr__(self, "points", validatedPoints)

    def ValidateWithin(self, universe: ContinuousUniverse) -> "ComparisonDomain":
        """Return this domain after proving every point belongs to the universe.

        Args:
            universe: Continuous universe expected to contain every point.

        Returns:
            This unchanged comparison domain after successful validation.

        Raises:
            TypeError: If `universe` is not continuous.
            ValueError: If any comparison point lies outside the universe.
        """

        if not isinstance(universe, ContinuousUniverse):
            raise InvalidParameterTypeError("comparison domains are used only with ContinuousUniverse")

        if any(not universe.Contains(point) for point in self.points):
            raise InvalidDomainError("every comparison-domain point must belong to the universe")

        return self


@dataclass(frozen=True, slots=True)
class ComparisonPolicy:
    """Explicit exact or tolerance-based membership comparison semantics.

    Attributes:
        mode: Either `"exact"` or `"tolerance"`.
        absoluteTolerance: Non-negative absolute tolerance in tolerance mode.
        relativeTolerance: Non-negative relative tolerance in tolerance mode.
    """

    mode: str
    absoluteTolerance: MembershipScalar | None = None
    relativeTolerance: MembershipScalar | None = None

    def __post_init__(self) -> None:
        """Reject incomplete, ambiguous, or zero-effect comparison policies."""

        if self.mode == "exact":
            if self.absoluteTolerance is not None or self.relativeTolerance is not None:
                raise InvalidParameterError("exact comparison does not accept tolerances")

            return

        if self.mode != "tolerance":
            raise InvalidParameterError(f"unknown comparison mode: {self.mode!r}")

        absoluteTolerance = _RequireFiniteReal(self.absoluteTolerance, "absoluteTolerance")
        relativeTolerance = _RequireFiniteReal(self.relativeTolerance, "relativeTolerance")

        if absoluteTolerance < 0 or relativeTolerance < 0:
            raise InvalidParameterError("comparison tolerances must be non-negative")

        if absoluteTolerance == 0 and relativeTolerance == 0:
            raise InvalidParameterError("tolerance comparison requires at least one positive tolerance")

        object.__setattr__(self, "absoluteTolerance", absoluteTolerance)
        object.__setattr__(self, "relativeTolerance", relativeTolerance)

    def Equal(self, leftGrade: MembershipScalar, rightGrade: MembershipScalar) -> bool:
        """Return whether two membership grades are equal by this policy.

        Args:
            leftGrade: Left membership degree in $[0, 1]$.
            rightGrade: Right membership degree in $[0, 1]$.

        Returns:
            Exact equality or `math.isclose` according to `mode`.

        Raises:
            TypeError: If either grade is not a real scalar.
            ValueError: If either grade is non-finite or outside $[0, 1]$.
        """

        leftGrade = _RequireGrade(leftGrade, "leftGrade")
        rightGrade = _RequireGrade(rightGrade, "rightGrade")

        if self.mode == "exact":
            return leftGrade == rightGrade

        return math.isclose(
            leftGrade,
            rightGrade,
            abs_tol=cast(float, self.absoluteTolerance),
            rel_tol=cast(float, self.relativeTolerance),
        )

    def Included(self, subsetGrade: MembershipScalar, supersetGrade: MembershipScalar) -> bool:
        """Return whether one grade is included in another by this policy.

        Args:
            subsetGrade: Candidate subset membership degree.
            supersetGrade: Candidate superset membership degree.

        Returns:
            Whether the subset grade is no greater than the superset grade,
            allowing closeness only in tolerance mode.

        Raises:
            TypeError: If either grade is not a real scalar.
            ValueError: If either grade is non-finite or outside $[0, 1]$.
        """

        subsetGrade = _RequireGrade(subsetGrade, "subsetGrade")
        supersetGrade = _RequireGrade(supersetGrade, "supersetGrade")

        if subsetGrade <= supersetGrade:
            return True

        if self.mode == "exact":
            return False

        return self.Equal(subsetGrade, supersetGrade)


def _ResolveComparisonPoints(
    universe: ContinuousUniverse | DiscreteUniverse,
    comparisonDomain: ComparisonDomain | None,
) -> tuple[MembershipScalar, ...]:
    """Resolve exhaustive discrete points or validate an explicit sampled domain."""

    if isinstance(universe, DiscreteUniverse):
        if comparisonDomain is not None:
            raise InvalidParameterError("discrete fuzzy-set relations always evaluate the complete universe")

        return universe.points

    if comparisonDomain is None:
        raise InvalidDomainError("continuous fuzzy-set relations require an explicit ComparisonDomain")

    if not isinstance(comparisonDomain, ComparisonDomain):
        raise InvalidParameterTypeError("comparisonDomain must be a ComparisonDomain")

    return comparisonDomain.ValidateWithin(universe).points


def EqualOnDomain(
    leftSet: ScalarFuzzySet,
    rightSet: ScalarFuzzySet,
    comparisonPolicy: ComparisonPolicy,
    comparisonDomain: ComparisonDomain | None=None,
) -> bool:
    """Compare membership equality over an exhaustive or explicit finite domain.

    For a discrete universe the complete declared point set is exhaustive and
    `comparisonDomain` must be omitted. For a continuous universe the result
    describes only the explicitly supplied sample points; it is not a proof of
    global functional equality.

    Args:
        leftSet: Left scalar fuzzy set.
        rightSet: Right scalar fuzzy set over exactly the same universe.
        comparisonPolicy: Exact or tolerance-based grade policy.
        comparisonDomain: Required finite observation points for a continuous
            universe; omitted for a discrete universe.

    Returns:
        `True` when all evaluated membership pairs compare equal.

    Raises:
        TypeError: If an argument has the wrong contract type.
        ValueError: If universes differ or domain selection is invalid.
    """

    leftSet, rightSet = _RequireCompatibleSets(leftSet, rightSet)

    if not isinstance(comparisonPolicy, ComparisonPolicy):
        raise InvalidParameterTypeError("comparisonPolicy must be a ComparisonPolicy")

    comparisonPoints = _ResolveComparisonPoints(leftSet.universe, comparisonDomain)

    # all() preserves fail-fast semantics: at most one evaluation per declared
    # point and immediate termination at the first counterexample.
    return all(
        comparisonPolicy.Equal(leftSet.Membership(point), rightSet.Membership(point))
        for point in comparisonPoints
    )


def IncludedOnDomain(
    subset: ScalarFuzzySet,
    superset: ScalarFuzzySet,
    comparisonPolicy: ComparisonPolicy,
    comparisonDomain: ComparisonDomain | None=None,
) -> bool:
    r"""Evaluate fuzzy inclusion over an exhaustive or explicit finite domain.

    Inclusion means $\mu_{subset}(x) \leq \mu_{superset}(x)$ at every
    evaluated point.
    Tolerance mode permits only violations whose two grades are numerically
    close under the explicit comparison policy.

    Args:
        subset: Candidate subset fuzzy set.
        superset: Candidate superset over exactly the same universe.
        comparisonPolicy: Exact or tolerance-based grade policy.
        comparisonDomain: Required finite observation points for a continuous
            universe; omitted for a discrete universe.

    Returns:
        `True` when inclusion holds at every evaluated coordinate.

    Raises:
        TypeError: If an argument has the wrong contract type.
        ValueError: If universes differ or domain selection is invalid.
    """

    subset, superset = _RequireCompatibleSets(subset, superset)

    if not isinstance(comparisonPolicy, ComparisonPolicy):
        raise InvalidParameterTypeError("comparisonPolicy must be a ComparisonPolicy")

    comparisonPoints = _ResolveComparisonPoints(subset.universe, comparisonDomain)

    # Worst-case O(n), O(1) auxiliary space; a finite continuous domain remains
    # evidence only for its declared points, never a global proof.
    return all(
        comparisonPolicy.Included(subset.Membership(point), superset.Membership(point))
        for point in comparisonPoints
    )
