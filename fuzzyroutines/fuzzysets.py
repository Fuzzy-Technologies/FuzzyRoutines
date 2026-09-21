# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Immutable scalar fuzzy sets and explicitly configured algebraic operations.

The modern algebra has no process-wide operator settings.  Every complement,
intersection, union, and directed difference receives immutable policy values,
and binary operations require exactly equal universes before constructing a
result.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass
from numbers import Real

from fuzzyroutines.domain import (
    ContinuousUniverse,
    DiscreteUniverse,
    _RequireFiniteReal,
)

OPERATORFAMILIES = ("logic", "algebraic", "boundary", "drastic")


def _RequireGrade(value, parameterName):
    """Return a finite real membership grade in the closed unit interval."""

    value = _RequireFiniteReal(value, parameterName)

    if not 0 <= value <= 1:
        raise ValueError(f"{parameterName} must lie in the closed interval [0, 1]")

    return value


@dataclass(frozen=True, slots=True)
class NegationPolicy:
    """Explicit fuzzy-negation family and its optional fixed-point parameter."""

    family: str
    alpha: Real | None = None

    def __post_init__(self):
        """Validate the complete negation configuration before evaluation."""

        if self.family == "standard":
            if self.alpha is not None:
                raise ValueError("standard negation does not accept alpha")

            return

        if self.family == "parametric":
            alpha = _RequireFiniteReal(self.alpha, "alpha")

            if not 0 < alpha < 1:
                raise ValueError("parametric negation alpha must lie in the open interval (0, 1)")

            object.__setattr__(self, "alpha", alpha)
            return

        if self.family == "parabolic":
            alpha = _RequireFiniteReal(self.alpha, "alpha")

            if not 0.25 <= alpha <= 0.75:
                raise ValueError("parabolic negation alpha must lie in the closed interval [1/4, 3/4]")

            object.__setattr__(self, "alpha", alpha)
            return

        raise ValueError(f"unknown negation family: {self.family!r}")

    def Evaluate(self, grade):
        """Evaluate the configured negation for one validated membership grade."""

        grade = _RequireGrade(grade, "grade")

        if self.family == "standard":
            return 1 - grade

        if self.family == "parametric":
            if grade <= self.alpha:
                return grade * (self.alpha - 1) / self.alpha + 1

            return (grade - 1) * self.alpha / (self.alpha - 1)

        if grade == 0:
            return 1.0

        if grade == 1:
            return 0.0

        if self.alpha <= 0.5:
            discriminant = (4 * self.alpha - 1) ** 2 + 8 * (1 - 2 * self.alpha) * grade

        else:
            discriminant = (4 * self.alpha - 3) ** 2 + 8 * (2 * self.alpha - 1) * (1 - grade)

        return grade + 4 * (self.alpha - grade) / (1 + math.sqrt(discriminant))


@dataclass(frozen=True, slots=True)
class TNormPolicy:
    """Explicit t-norm family used by fuzzy-set intersection."""

    family: str

    def __post_init__(self):
        """Reject every family not accepted by ADR-0004."""

        if self.family not in OPERATORFAMILIES:
            raise ValueError(f"unknown t-norm family: {self.family!r}")

    def Evaluate(self, leftGrade, rightGrade):
        """Evaluate the configured t-norm for two membership grades."""

        leftGrade = _RequireGrade(leftGrade, "leftGrade")
        rightGrade = _RequireGrade(rightGrade, "rightGrade")

        if self.family == "logic":
            return min(leftGrade, rightGrade)

        if self.family == "algebraic":
            return leftGrade * rightGrade

        if self.family == "boundary":
            return max(leftGrade + rightGrade - 1, 0)

        if leftGrade == 1:
            return rightGrade

        if rightGrade == 1:
            return leftGrade

        return 0


@dataclass(frozen=True, slots=True)
class SNormPolicy:
    """Explicit s-norm family used by fuzzy-set union."""

    family: str

    def __post_init__(self):
        """Reject every family not accepted by ADR-0004."""

        if self.family not in OPERATORFAMILIES:
            raise ValueError(f"unknown s-norm family: {self.family!r}")

    def Evaluate(self, leftGrade, rightGrade):
        """Evaluate the configured s-norm for two membership grades."""

        leftGrade = _RequireGrade(leftGrade, "leftGrade")
        rightGrade = _RequireGrade(rightGrade, "rightGrade")

        if self.family == "logic":
            return max(leftGrade, rightGrade)

        if self.family == "algebraic":
            return leftGrade + rightGrade - leftGrade * rightGrade

        if self.family == "boundary":
            return min(leftGrade + rightGrade, 1)

        if leftGrade == 0:
            return rightGrade

        if rightGrade == 0:
            return leftGrade

        return 1


@dataclass(frozen=True, slots=True, eq=False)
class ScalarFuzzySet:
    """Immutable scalar fuzzy-set definition over one explicit universe."""

    universe: ContinuousUniverse | DiscreteUniverse
    membershipFunction: Callable[[Real], Real]

    def __post_init__(self):
        """Require a supported universe and an evaluable membership function."""

        if not isinstance(self.universe, (ContinuousUniverse, DiscreteUniverse)):
            raise TypeError("universe must be a ContinuousUniverse or DiscreteUniverse")

        if not callable(self.membershipFunction):
            raise TypeError("membershipFunction must be callable")

    def Membership(self, coordinate):
        """Return the validated membership grade for a coordinate in the universe."""

        if not self.universe.Contains(coordinate):
            raise ValueError("coordinate must belong to the fuzzy set universe")

        return _RequireGrade(self.membershipFunction(coordinate), "membership grade")


@dataclass(frozen=True, slots=True)
class _NormalizedDiscreteMembership:
    """Immutable exhaustive grade snapshot for a normalized discrete set."""

    universe: DiscreteUniverse
    grades: tuple[Real, ...]

    def __call__(self, coordinate):
        """Return the normalized grade at one already validated coordinate."""

        return self.grades[self.universe.points.index(coordinate)]


@dataclass(frozen=True, slots=True)
class _NormalizedContinuousMembership:
    """Immutable continuous normalization evaluator with exact height evidence."""

    universe: ContinuousUniverse
    familyIdentifier: str
    parameters: tuple[tuple[str, Real], ...]
    sourceHeight: Real

    def __call__(self, coordinate):
        """Evaluate the frozen analytical definition and scale its grade."""

        from fuzzyroutines.FuzzyRoutines import MFunction

        membershipFunction = MFunction(self.familyIdentifier, **dict(self.parameters))
        return membershipFunction.mju(coordinate) / self.sourceHeight


def _ContinuousAnalyticalSource(fuzzySet):
    """Return the exact analytical source behind a bound ``MFunction`` method."""

    from fuzzyroutines.FuzzyRoutines import MFunction

    source = getattr(fuzzySet.membershipFunction, "__self__", None)

    if isinstance(source, MFunction) and fuzzySet.membershipFunction == source.mju:
        return source

    return None


def _RequireContinuousAnalyticalSource(fuzzySet):
    """Return a supported exact source or reject an unproved supremum."""

    analyticalSource = _ContinuousAnalyticalSource(fuzzySet)

    if analyticalSource is None:
        raise ValueError(
            "exact continuous height is unavailable for a generic membership callable"
        )

    return analyticalSource


def _DiscreteGrades(fuzzySet):
    """Evaluate every coordinate of a declared discrete universe exactly once."""

    return tuple(fuzzySet.Membership(coordinate) for coordinate in fuzzySet.universe.points)


def _NormalizedContinuousHeight(membershipFunction, universe):
    """Return exact height after restricting normalized evidence to a universe."""

    from fuzzyroutines.FuzzyRoutines import MFunction
    from fuzzyroutines.properties import DeriveProperties

    frozenSource = MFunction(
        membershipFunction.familyIdentifier,
        **dict(membershipFunction.parameters),
    )
    sourceHeight = DeriveProperties(frozenSource, universe).height
    return _RequireGrade(
        sourceHeight / membershipFunction.sourceHeight,
        "normalized height",
    )


def Height(fuzzySet):
    """Return the exact supremum of membership grades when it is provable.

    A discrete universe is evaluated exhaustively.  A continuous universe
    requires either internally preserved exact evidence or a bound analytical
    ``MFunction`` supported by :func:`fuzzyroutines.properties.DeriveProperties`.
    The function never promotes a finite sample maximum to an exact height.
    """

    if not isinstance(fuzzySet, ScalarFuzzySet):
        raise TypeError("fuzzySet must be a ScalarFuzzySet")

    membershipFunction = fuzzySet.membershipFunction

    if isinstance(membershipFunction, _NormalizedDiscreteMembership):
        if fuzzySet.universe == membershipFunction.universe:
            return 1.0

    elif isinstance(membershipFunction, _NormalizedContinuousMembership):
        if fuzzySet.universe == membershipFunction.universe:
            return 1.0

        if isinstance(fuzzySet.universe, ContinuousUniverse):
            return _NormalizedContinuousHeight(membershipFunction, fuzzySet.universe)

    if isinstance(fuzzySet.universe, DiscreteUniverse):
        return max(_DiscreteGrades(fuzzySet))

    analyticalSource = _RequireContinuousAnalyticalSource(fuzzySet)

    from fuzzyroutines.properties import DeriveProperties

    return DeriveProperties(analyticalSource, fuzzySet.universe).height


def IsNormal(fuzzySet, tolerance=1e-12):
    """Return whether the exact fuzzy-set height equals one within tolerance."""

    tolerance = _RequireFiniteReal(tolerance, "tolerance")

    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    return math.isclose(Height(fuzzySet), 1.0, rel_tol=0.0, abs_tol=tolerance)


def Normalize(fuzzySet):
    """Return a new height-one fuzzy set without mutating the source set.

    Normalization is the pointwise quotient ``mu_A(x) / height(A)``.  It is
    undefined for height zero and unavailable when an exact continuous height
    cannot be proved under the current analytical contracts.
    """

    if not isinstance(fuzzySet, ScalarFuzzySet):
        raise TypeError("fuzzySet must be a ScalarFuzzySet")

    if isinstance(fuzzySet.universe, DiscreteUniverse):
        sourceGrades = _DiscreteGrades(fuzzySet)
        height = max(sourceGrades)

        if height == 0:
            raise ValueError("cannot normalize a zero-height fuzzy set")

        normalizedGrades = tuple(grade / height for grade in sourceGrades)
        normalizedMembership = _NormalizedDiscreteMembership(
            fuzzySet.universe,
            normalizedGrades,
        )

    else:
        if isinstance(fuzzySet.membershipFunction, _NormalizedContinuousMembership):
            if fuzzySet.universe == fuzzySet.membershipFunction.universe:
                return ScalarFuzzySet(fuzzySet.universe, fuzzySet.membershipFunction)

            familyIdentifier = fuzzySet.membershipFunction.familyIdentifier
            parameters = fuzzySet.membershipFunction.parameters

            from fuzzyroutines.FuzzyRoutines import MFunction
            from fuzzyroutines.properties import DeriveProperties

            frozenSource = MFunction(familyIdentifier, **dict(parameters))
            height = DeriveProperties(frozenSource, fuzzySet.universe).height
            _RequireGrade(
                height / fuzzySet.membershipFunction.sourceHeight,
                "normalized height",
            )

            if height == 0:
                raise ValueError("cannot normalize a zero-height fuzzy set")

            normalizedMembership = _NormalizedContinuousMembership(
                fuzzySet.universe,
                familyIdentifier,
                parameters,
                height,
            )
            return ScalarFuzzySet(fuzzySet.universe, normalizedMembership)

        analyticalSource = _RequireContinuousAnalyticalSource(fuzzySet)

        familyIdentifier = analyticalSource.name.lower()
        parameters = tuple(sorted(analyticalSource.parameters.items()))

        from fuzzyroutines.FuzzyRoutines import MFunction
        from fuzzyroutines.properties import DeriveProperties

        frozenSource = MFunction(familyIdentifier, **dict(parameters))
        height = DeriveProperties(frozenSource, fuzzySet.universe).height

        if height == 0:
            raise ValueError("cannot normalize a zero-height fuzzy set")

        normalizedMembership = _NormalizedContinuousMembership(
            fuzzySet.universe,
            familyIdentifier,
            parameters,
            height,
        )

    return ScalarFuzzySet(fuzzySet.universe, normalizedMembership)


def Complement(fuzzySet, negationPolicy):
    """Return a new fuzzy set using one explicit approved negation policy."""

    if not isinstance(fuzzySet, ScalarFuzzySet):
        raise TypeError("fuzzySet must be a ScalarFuzzySet")

    if not isinstance(negationPolicy, NegationPolicy):
        raise TypeError("negationPolicy must be a NegationPolicy")

    def ComplementMembership(coordinate):
        """Evaluate the source set before applying the configured negation."""

        return negationPolicy.Evaluate(fuzzySet.Membership(coordinate))

    return ScalarFuzzySet(fuzzySet.universe, ComplementMembership)


def _RequireCompatibleSets(leftSet, rightSet):
    """Return two fuzzy sets after proving exact universe compatibility."""

    if not isinstance(leftSet, ScalarFuzzySet) or not isinstance(rightSet, ScalarFuzzySet):
        raise TypeError("both operands must be ScalarFuzzySet instances")

    if leftSet.universe != rightSet.universe:
        raise ValueError("fuzzy-set operations require exactly equal universes")

    return leftSet, rightSet


def Intersection(leftSet, rightSet, tNormPolicy):
    """Return a fuzzy-set intersection under one explicit t-norm family."""

    leftSet, rightSet = _RequireCompatibleSets(leftSet, rightSet)

    if not isinstance(tNormPolicy, TNormPolicy):
        raise TypeError("tNormPolicy must be a TNormPolicy")

    def IntersectionMembership(coordinate):
        """Evaluate both operands before applying the configured t-norm."""

        return tNormPolicy.Evaluate(
            leftSet.Membership(coordinate),
            rightSet.Membership(coordinate),
        )

    return ScalarFuzzySet(leftSet.universe, IntersectionMembership)


def Union(leftSet, rightSet, sNormPolicy):
    """Return a fuzzy-set union under one explicit s-norm family."""

    leftSet, rightSet = _RequireCompatibleSets(leftSet, rightSet)

    if not isinstance(sNormPolicy, SNormPolicy):
        raise TypeError("sNormPolicy must be an SNormPolicy")

    def UnionMembership(coordinate):
        """Evaluate both operands before applying the configured s-norm."""

        return sNormPolicy.Evaluate(
            leftSet.Membership(coordinate),
            rightSet.Membership(coordinate),
        )

    return ScalarFuzzySet(leftSet.universe, UnionMembership)


def Difference(leftSet, rightSet, tNormPolicy, negationPolicy):
    """Return the directed fuzzy-set difference under explicit policies."""

    leftSet, rightSet = _RequireCompatibleSets(leftSet, rightSet)

    if not isinstance(tNormPolicy, TNormPolicy):
        raise TypeError("tNormPolicy must be a TNormPolicy")

    if not isinstance(negationPolicy, NegationPolicy):
        raise TypeError("negationPolicy must be a NegationPolicy")

    def DifferenceMembership(coordinate):
        """Evaluate T(mu_A(x), N(mu_B(x))) without an implicit policy."""

        return tNormPolicy.Evaluate(
            leftSet.Membership(coordinate),
            negationPolicy.Evaluate(rightSet.Membership(coordinate)),
        )

    return ScalarFuzzySet(leftSet.universe, DifferenceMembership)
