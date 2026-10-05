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
from dataclasses import dataclass
from typing import cast

from fuzzyroutines.domain import (
    ContinuousUniverse,
    DiscreteUniverse,
)
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
    UndefinedResultError,
)
from fuzzyroutines.membership import (
    MembershipCallable,
    MembershipScalar,
    _AnalyticalSource,
    _GetAnalyticalSource,
)
from fuzzyroutines.numeric import _RequireFiniteReal, _RequireGrade
from fuzzyroutines.operators import (
    OPERATOR_FAMILIES,
    NegationPolicy,
    SNormPolicy,
    TNormPolicy,
)

OPERATORFAMILIES = OPERATOR_FAMILIES


@dataclass(frozen=True, slots=True, eq=False)
class ScalarFuzzySet:
    """Immutable scalar fuzzy-set definition over one explicit universe.

    Attributes:
        universe: Continuous or discrete scalar coordinate contract.
        membershipFunction: Callable evaluated after universe membership is
            validated; its result must be a finite degree in $[0, 1]$.
            [MembershipCallable][fuzzyroutines.membership.MembershipCallable]
            describes the structural contract without requiring inheritance.
            Construction checks callability only, not signatures or results.
    """

    universe: ContinuousUniverse | DiscreteUniverse
    membershipFunction: MembershipCallable

    def __post_init__(self) -> None:
        """Require a supported universe and an evaluable membership function."""

        if not isinstance(self.universe, (ContinuousUniverse, DiscreteUniverse)):
            raise InvalidParameterTypeError("universe must be a ContinuousUniverse or DiscreteUniverse")

        if not callable(self.membershipFunction):
            raise InvalidParameterTypeError("membershipFunction must be callable")

    def Membership(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Return the validated membership grade for a universe coordinate.

        Args:
            coordinate: Finite scalar coordinate belonging to `universe`.

        Returns:
            Membership degree in $[0, 1]$.

        Raises:
            TypeError: If the coordinate or returned grade is not a real
                scalar.
            ValueError: If the coordinate is outside the universe or the
                callable returns a non-finite or out-of-range grade.
        """

        if not self.universe.Contains(coordinate):
            raise InvalidDomainError("coordinate must belong to the fuzzy set universe")

        return _RequireGrade(self.membershipFunction(coordinate), "membership grade")


@dataclass(frozen=True, slots=True)
class _NormalizedDiscreteMembership:
    """Immutable exhaustive grade snapshot for a normalized discrete set."""

    universe: DiscreteUniverse
    grades: tuple[MembershipScalar, ...]

    def __call__(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Return the normalized grade at one already validated coordinate."""

        return self.grades[self.universe.points.index(coordinate)]


@dataclass(frozen=True, slots=True)
class _NormalizedContinuousMembership:
    """Immutable continuous normalization evaluator with exact height evidence."""

    universe: ContinuousUniverse
    familyIdentifier: str
    parameters: tuple[tuple[str, MembershipScalar], ...]
    sourceHeight: MembershipScalar

    def __call__(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Evaluate the frozen analytical definition and scale its grade."""

        membershipFunction = _AnalyticalSource(self.familyIdentifier.title(), self.parameters)
        return membershipFunction.mju(coordinate) / cast(float, self.sourceHeight)


def _ContinuousAnalyticalSource(fuzzySet: ScalarFuzzySet) -> _AnalyticalSource | None:
    """Return trusted analytical evidence from a callable or supported bound evaluator."""

    return _GetAnalyticalSource(fuzzySet.membershipFunction)


def _RequireContinuousAnalyticalSource(fuzzySet: ScalarFuzzySet) -> _AnalyticalSource:
    """Return a supported exact source or reject an unproved supremum."""

    analyticalSource = _ContinuousAnalyticalSource(fuzzySet)

    if analyticalSource is None:
        raise InvalidParameterError(
            "exact continuous height is unavailable for a generic membership callable"
        )

    return analyticalSource


def _DiscreteGrades(fuzzySet: ScalarFuzzySet) -> tuple[float, ...]:
    """Evaluate every coordinate of a declared discrete universe exactly once."""

    universe = cast(DiscreteUniverse, fuzzySet.universe)

    return tuple(_RequireGrade(fuzzySet.Membership(coordinate), "membership grade") for coordinate in universe.points)


def _NormalizedContinuousHeight(
    membershipFunction: _NormalizedContinuousMembership,
    universe: ContinuousUniverse,
) -> MembershipScalar:
    """Return exact height after restricting normalized evidence to a universe."""

    from fuzzyroutines.properties import DeriveProperties

    frozenSource = _AnalyticalSource(
        membershipFunction.familyIdentifier.title(),
        membershipFunction.parameters,
    )
    sourceHeight = DeriveProperties(frozenSource, universe).height
    return _RequireGrade(
        sourceHeight / cast(float, membershipFunction.sourceHeight),
        "normalized height",
    )


def Height(fuzzySet: ScalarFuzzySet) -> MembershipScalar:
    """Return the exact supremum of membership grades when it is provable.

    A discrete universe is evaluated exhaustively.  A continuous universe
    requires internally preserved exact evidence, a modern analytical
    [MembershipFunction][fuzzyroutines.membership.MembershipFunction], or a
    registered historical [MFunction][fuzzyroutines.FuzzyRoutines.MFunction]
    evaluator supported by
    [DeriveProperties][fuzzyroutines.properties.DeriveProperties].
    The function never promotes a finite sample maximum to an exact height.

    Args:
        fuzzySet: Scalar fuzzy set whose exact height is requested.

    Returns:
        Exact supremum of the membership grades.

    Raises:
        TypeError: If `fuzzySet` is not a scalar fuzzy set.
        ValueError: If an exact continuous height is unavailable.
    """

    if not isinstance(fuzzySet, ScalarFuzzySet):
        raise InvalidParameterTypeError("fuzzySet must be a ScalarFuzzySet")

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


def IsNormal(fuzzySet: ScalarFuzzySet, tolerance: MembershipScalar = 1e-12) -> bool:
    """Return whether the exact fuzzy-set height equals one within tolerance.

    Args:
        fuzzySet: Scalar fuzzy set with a provable exact height.
        tolerance: Non-negative absolute comparison tolerance.

    Returns:
        Whether the exact height is within `tolerance` of one.

    Raises:
        TypeError: If `fuzzySet` is not a scalar fuzzy set or `tolerance` is
            not a real scalar.
        ValueError: If `tolerance` is negative or exact height is unavailable.
    """

    tolerance = _RequireFiniteReal(tolerance, "tolerance")

    if tolerance < 0:
        raise InvalidParameterError("tolerance must be non-negative")

    return math.isclose(Height(fuzzySet), 1.0, rel_tol=0.0, abs_tol=tolerance)


def Normalize(fuzzySet: ScalarFuzzySet) -> ScalarFuzzySet:
    r"""Return a new height-one fuzzy set without mutating the source set.

    Normalization is the pointwise quotient
    $\mu_A(x) / \operatorname{height}(A)$. It is
    undefined for height zero and unavailable when an exact continuous height
    cannot be proved under the current analytical contracts.

    Args:
        fuzzySet: Scalar fuzzy set with a provable nonzero exact height.

    Returns:
        A new scalar fuzzy set whose exact height is one.

    Raises:
        TypeError: If `fuzzySet` is not a scalar fuzzy set.
        ValueError: If exact height is unavailable or equals zero.
    """

    if not isinstance(fuzzySet, ScalarFuzzySet):
        raise InvalidParameterTypeError("fuzzySet must be a ScalarFuzzySet")

    height: MembershipScalar
    normalizedMembership: MembershipCallable

    if isinstance(fuzzySet.universe, DiscreteUniverse):
        sourceGrades = _DiscreteGrades(fuzzySet)
        height = max(sourceGrades)

        if height == 0:
            raise UndefinedResultError("cannot normalize a zero-height fuzzy set")

        normalizedGrades = tuple(grade / height for grade in sourceGrades)
        # max(grades / height) is exactly one at the coordinate that attained
        # the finite discrete maximum; no sampled supremum claim is involved.
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

            from fuzzyroutines.properties import DeriveProperties

            frozenSource = _AnalyticalSource(familyIdentifier.title(), parameters)
            height = DeriveProperties(frozenSource, fuzzySet.universe).height
            _RequireGrade(
                height / cast(float, fuzzySet.membershipFunction.sourceHeight),
                "normalized height",
            )

            if height == 0:
                raise UndefinedResultError("cannot normalize a zero-height fuzzy set")

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

        from fuzzyroutines.properties import DeriveProperties

        frozenSource = _AnalyticalSource(familyIdentifier.title(), parameters)
        height = DeriveProperties(frozenSource, fuzzySet.universe).height

        if height == 0:
            raise UndefinedResultError("cannot normalize a zero-height fuzzy set")

        normalizedMembership = _NormalizedContinuousMembership(
            fuzzySet.universe,
            familyIdentifier,
            parameters,
            height,
        )

    return ScalarFuzzySet(fuzzySet.universe, normalizedMembership)


def Complement(fuzzySet: ScalarFuzzySet, negationPolicy: NegationPolicy) -> ScalarFuzzySet:
    """Return a new fuzzy set using one explicit approved negation policy.

    Args:
        fuzzySet: Source scalar fuzzy set.
        negationPolicy: Explicit complement semantics.

    Returns:
        A lazy immutable set over the unchanged universe.

    Raises:
        TypeError: If either argument has the wrong contract type.
    """

    if not isinstance(fuzzySet, ScalarFuzzySet):
        raise InvalidParameterTypeError("fuzzySet must be a ScalarFuzzySet")

    if not isinstance(negationPolicy, NegationPolicy):
        raise InvalidParameterTypeError("negationPolicy must be a NegationPolicy")

    def ComplementMembership(coordinate: MembershipScalar) -> MembershipScalar:
        """Evaluate the source set before applying the configured negation."""

        return negationPolicy.Evaluate(fuzzySet.Membership(coordinate))

    return ScalarFuzzySet(fuzzySet.universe, ComplementMembership)


def _RequireCompatibleSets(
    leftSet: ScalarFuzzySet,
    rightSet: ScalarFuzzySet,
) -> tuple[ScalarFuzzySet, ScalarFuzzySet]:
    """Return two fuzzy sets after proving exact universe compatibility."""

    if not isinstance(leftSet, ScalarFuzzySet) or not isinstance(rightSet, ScalarFuzzySet):
        raise InvalidParameterTypeError("both operands must be ScalarFuzzySet instances")

    if leftSet.universe != rightSet.universe:
        raise InvalidDomainError("fuzzy-set operations require exactly equal universes")

    return leftSet, rightSet


def Intersection(
    leftSet: ScalarFuzzySet,
    rightSet: ScalarFuzzySet,
    tNormPolicy: TNormPolicy,
) -> ScalarFuzzySet:
    """Return a fuzzy-set intersection under one explicit t-norm family.

    Args:
        leftSet: Left scalar fuzzy set.
        rightSet: Right scalar fuzzy set over exactly the same universe.
        tNormPolicy: Explicit conjunction semantics.

    Returns:
        A lazy immutable intersection over the shared universe.

    Raises:
        TypeError: If an argument has the wrong contract type.
        ValueError: If the operand universes differ.
    """

    leftSet, rightSet = _RequireCompatibleSets(leftSet, rightSet)

    if not isinstance(tNormPolicy, TNormPolicy):
        raise InvalidParameterTypeError("tNormPolicy must be a TNormPolicy")

    def IntersectionMembership(coordinate: MembershipScalar) -> MembershipScalar:
        """Evaluate both operands before applying the configured t-norm."""

        return tNormPolicy.Evaluate(
            leftSet.Membership(coordinate),
            rightSet.Membership(coordinate),
        )

    return ScalarFuzzySet(leftSet.universe, IntersectionMembership)


def Union(leftSet: ScalarFuzzySet, rightSet: ScalarFuzzySet, sNormPolicy: SNormPolicy) -> ScalarFuzzySet:
    """Return a fuzzy-set union under one explicit s-norm family.

    Args:
        leftSet: Left scalar fuzzy set.
        rightSet: Right scalar fuzzy set over exactly the same universe.
        sNormPolicy: Explicit disjunction semantics.

    Returns:
        A lazy immutable union over the shared universe.

    Raises:
        TypeError: If an argument has the wrong contract type.
        ValueError: If the operand universes differ.
    """

    leftSet, rightSet = _RequireCompatibleSets(leftSet, rightSet)

    if not isinstance(sNormPolicy, SNormPolicy):
        raise InvalidParameterTypeError("sNormPolicy must be an SNormPolicy")

    def UnionMembership(coordinate: MembershipScalar) -> MembershipScalar:
        """Evaluate both operands before applying the configured s-norm."""

        return sNormPolicy.Evaluate(
            leftSet.Membership(coordinate),
            rightSet.Membership(coordinate),
        )

    return ScalarFuzzySet(leftSet.universe, UnionMembership)


def Difference(
    leftSet: ScalarFuzzySet,
    rightSet: ScalarFuzzySet,
    tNormPolicy: TNormPolicy,
    negationPolicy: NegationPolicy,
) -> ScalarFuzzySet:
    r"""Return the directed fuzzy-set difference under explicit policies.

    The membership definition is $T(\mu_A(x), N(\mu_B(x)))$.

    Args:
        leftSet: Minuend scalar fuzzy set $A$.
        rightSet: Subtrahend scalar fuzzy set $B$ over the same universe.
        tNormPolicy: Explicit conjunction semantics $T$.
        negationPolicy: Explicit complement semantics $N$.

    Returns:
        A lazy immutable directed difference over the shared universe.

    Raises:
        TypeError: If an argument has the wrong contract type.
        ValueError: If the operand universes differ.
    """

    leftSet, rightSet = _RequireCompatibleSets(leftSet, rightSet)

    if not isinstance(tNormPolicy, TNormPolicy):
        raise InvalidParameterTypeError("tNormPolicy must be a TNormPolicy")

    if not isinstance(negationPolicy, NegationPolicy):
        raise InvalidParameterTypeError("negationPolicy must be a NegationPolicy")

    def DifferenceMembership(coordinate: MembershipScalar) -> MembershipScalar:
        r"""Evaluate $T(\mu_A(x), N(\mu_B(x)))$ without an implicit policy."""

        return tNormPolicy.Evaluate(
            leftSet.Membership(coordinate),
            negationPolicy.Evaluate(rightSet.Membership(coordinate)),
        )

    return ScalarFuzzySet(leftSet.universe, DifferenceMembership)
