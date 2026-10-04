# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Typed immutable linguistic terms, scale lookup, and fuzzification.

Name lookup is either case-sensitive or Unicode case-insensitive. Modern
fuzzification records every membership score and applies explicit tie and
minimum-confidence policies without changing the historical compatibility API.
"""

import math
from dataclasses import dataclass
from numbers import Real
from typing import cast

from fuzzyroutines.domain import ContinuousUniverse, IntegrationDomain
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.numeric import _RequireGrade

TIEPOLICIES = ("first", "last", "all")


def _RequireNonNegativeFiniteReal(value: MembershipScalar, parameterName: str) -> MembershipScalar:
    """Return a finite non-negative scalar or raise a deterministic error."""

    if isinstance(value, bool) or not isinstance(value, Real):
        raise InvalidParameterTypeError(f"{parameterName} must be a real number")

    if not math.isfinite(value):
        raise InvalidParameterError(f"{parameterName} must be a finite real number")

    if value < 0:
        raise InvalidParameterError(f"{parameterName} must be non-negative")

    return value


def _IsWithinTieTolerance(
    grade: MembershipScalar,
    confidence: MembershipScalar,
    tolerance: MembershipScalar,
) -> bool:
    """Return whether a grade is within an inclusive absolute tie tolerance."""

    difference = float(confidence) - float(grade)
    tolerance = float(tolerance)
    return difference <= tolerance or math.isclose(
        difference,
        tolerance,
        rel_tol=1e-12,
        abs_tol=0.0,
    )


@dataclass(frozen=True, slots=True)
class LinguisticTerm:
    """Named immutable association with one scalar fuzzy set.

    Attributes:
        name: Non-empty exact lookup and display name.
        fuzzySet: Modern scalar fuzzy set represented by the term.
    """

    name: str
    fuzzySet: ScalarFuzzySet

    def __post_init__(self) -> None:
        """Require a non-empty exact name and a modern scalar fuzzy set."""

        if not isinstance(self.name, str):
            raise InvalidParameterTypeError("name must be a string")

        if not self.name.strip():
            raise InvalidParameterError("name must contain at least one non-whitespace character")

        if not isinstance(self.fuzzySet, ScalarFuzzySet):
            raise InvalidParameterTypeError("fuzzySet must be a ScalarFuzzySet")


@dataclass(frozen=True, slots=True)
class FuzzificationPolicy:
    """Explicit tie and minimum-confidence classification policy.

    Attributes:
        tiePolicy: Selection rule for equal or tolerance-equivalent maximum
            memberships: `"first"`, `"last"`, or `"all"`.
        minimumConfidence: Maximum membership values less than or equal to this
            threshold produce no selected term. The default rejects only zero
            coverage.
        tieTolerance: Absolute membership difference from the maximum that is
            treated as a tie.
    """

    tiePolicy: str = "first"
    minimumConfidence: MembershipScalar = 0.0
    tieTolerance: MembershipScalar = 0.0

    def __post_init__(self) -> None:
        """Validate the complete classification policy."""

        if self.tiePolicy not in TIEPOLICIES:
            raise InvalidParameterError(f"unknown tie policy: {self.tiePolicy!r}")

        object.__setattr__(
            self,
            "minimumConfidence",
            _RequireGrade(self.minimumConfidence, "minimumConfidence"),
        )
        object.__setattr__(
            self,
            "tieTolerance",
            _RequireGrade(self.tieTolerance, "tieTolerance"),
        )


@dataclass(frozen=True, slots=True)
class TermMembership:
    """One linguistic term and its validated membership score."""

    term: LinguisticTerm
    grade: MembershipScalar

    def __post_init__(self) -> None:
        """Require a typed term and a valid membership grade."""

        if not isinstance(self.term, LinguisticTerm):
            raise InvalidParameterTypeError("term must be a LinguisticTerm")

        object.__setattr__(self, "grade", _RequireGrade(self.grade, "grade"))


@dataclass(frozen=True, slots=True)
class FuzzificationResult:
    """Complete immutable evidence for one scale classification.

    Attributes:
        memberships: One ordered score for every declared scale term.
        confidence: Greatest recorded membership grade.
        policy: Policy used to derive no-match and tie selections.
        tiedTerms: Maximum terms remaining after applying `tieTolerance`, or an
            empty tuple when confidence does not exceed the minimum.
        selectedTerms: Terms selected from `tiedTerms` by `tiePolicy`, or an
            empty tuple for no match.
    """

    memberships: tuple[TermMembership, ...]
    confidence: MembershipScalar
    policy: FuzzificationPolicy
    tiedTerms: tuple[LinguisticTerm, ...]
    selectedTerms: tuple[LinguisticTerm, ...]

    def __post_init__(self) -> None:
        """Require internally consistent classification evidence."""

        if not isinstance(self.memberships, tuple) or not self.memberships:
            raise InvalidParameterTypeError("memberships must be a non-empty tuple")

        if not all(isinstance(value, TermMembership) for value in self.memberships):
            raise InvalidParameterTypeError("memberships must contain only TermMembership values")

        if not isinstance(self.policy, FuzzificationPolicy):
            raise InvalidParameterTypeError("policy must be a FuzzificationPolicy")

        confidence = _RequireGrade(self.confidence, "confidence")
        if confidence != max(cast(float, value.grade) for value in self.memberships):
            raise InvalidParameterError("confidence must equal the maximum membership grade")

        object.__setattr__(self, "confidence", confidence)

        expectedTiedTerms: tuple[LinguisticTerm, ...] = ()
        if confidence > cast(float, self.policy.minimumConfidence):
            expectedTiedTerms = tuple(
                value.term
                for value in self.memberships
                if _IsWithinTieTolerance(
                    value.grade,
                    confidence,
                    self.policy.tieTolerance,
                )
            )

        if self.tiedTerms != expectedTiedTerms:
            raise InvalidParameterError("tiedTerms do not match memberships and policy")

        if self.policy.tiePolicy == "first":
            expectedSelectedTerms = expectedTiedTerms[:1]

        elif self.policy.tiePolicy == "last":
            expectedSelectedTerms = expectedTiedTerms[-1:]

        else:
            expectedSelectedTerms = expectedTiedTerms

        if self.selectedTerms != expectedSelectedTerms:
            raise InvalidParameterError("selectedTerms do not match tiedTerms and policy")

    @property
    def isMatch(self) -> bool:
        """Return whether the policy selected at least one term."""

        return bool(self.selectedTerms)

    @property
    def isTie(self) -> bool:
        """Return whether multiple maximum terms satisfied the tie policy."""

        return len(self.tiedTerms) > 1


@dataclass(frozen=True, slots=True)
class ScaleDiagnosticsPolicy:
    """Explicit grid and tolerance policy for sampled scale diagnostics.

    Attributes:
        sampleCount: Number of evenly spaced points including both endpoints of
            the analysis domain.
        membershipThreshold: A term is active only when its membership is
            strictly greater than this threshold. No active terms form a gap;
            two or more active terms form an overlap.
        partitionTolerance: Maximum accepted absolute difference between the
            sum of term memberships and one.
    """

    sampleCount: int = 101
    membershipThreshold: MembershipScalar = 0.0
    partitionTolerance: MembershipScalar = 1e-12

    def __post_init__(self) -> None:
        """Validate the complete sampled-diagnostics policy."""

        if isinstance(self.sampleCount, bool) or not isinstance(self.sampleCount, int):
            raise InvalidParameterTypeError("sampleCount must be an integer")

        if self.sampleCount < 2:
            raise InvalidParameterError("sampleCount must be at least two")

        object.__setattr__(
            self,
            "membershipThreshold",
            _RequireGrade(self.membershipThreshold, "membershipThreshold"),
        )
        object.__setattr__(
            self,
            "partitionTolerance",
            _RequireNonNegativeFiniteReal(
                self.partitionTolerance,
                "partitionTolerance",
            ),
        )


@dataclass(frozen=True, slots=True)
class ScaleDiagnosticPoint:
    """Immutable sampled membership evidence at one scale coordinate.

    Attributes:
        coordinate: Finite coordinate from the declared diagnostic grid.
        memberships: One ordered membership score for every scale term.
        membershipThreshold: Strict activity threshold used for gap and
            overlap classification.
    """

    coordinate: MembershipScalar
    memberships: tuple[TermMembership, ...]
    membershipThreshold: MembershipScalar

    def __post_init__(self) -> None:
        """Require one finite coordinate and a non-empty membership vector."""

        if isinstance(self.coordinate, bool) or not isinstance(self.coordinate, Real):
            raise InvalidParameterTypeError("coordinate must be a real number")

        if not math.isfinite(self.coordinate):
            raise InvalidParameterError("coordinate must be a finite real number")

        if not isinstance(self.memberships, tuple) or not self.memberships:
            raise InvalidParameterTypeError("memberships must be a non-empty tuple")

        if not all(isinstance(value, TermMembership) for value in self.memberships):
            raise InvalidParameterTypeError("memberships must contain only TermMembership values")

        object.__setattr__(
            self,
            "membershipThreshold",
            _RequireGrade(self.membershipThreshold, "membershipThreshold"),
        )

    @property
    def maximumMembership(self) -> MembershipScalar:
        """Greatest term membership sampled at this coordinate."""

        return max(cast(float, value.grade) for value in self.memberships)

    @property
    def membershipSum(self) -> float:
        """Floating-point sum of every term membership at this coordinate."""

        return math.fsum(float(value.grade) for value in self.memberships)

    @property
    def activeTerms(self) -> tuple[LinguisticTerm, ...]:
        """Terms whose memberships strictly exceed the activity threshold."""

        return tuple(
            value.term
            for value in self.memberships
            if cast(float, value.grade) > cast(float, self.membershipThreshold)
        )

    @property
    def isGap(self) -> bool:
        """Whether no term is active at this sampled coordinate."""

        return not self.activeTerms

    @property
    def isOverlap(self) -> bool:
        """Whether at least two terms are active at this sampled coordinate."""

        return len(self.activeTerms) > 1

    @property
    def partitionError(self) -> float:
        """Absolute sampled deviation of the membership sum from one."""

        return abs(self.membershipSum - 1.0)


@dataclass(frozen=True, slots=True)
class ScaleDiagnosticsResult:
    """Immutable sampled coverage, overlap, gap, and partition evidence.

    The result describes only the declared finite grid. It does not prove a
    continuous property between sampled coordinates.

    Attributes:
        analysisDomain: Finite closed interval sampled by the diagnostic.
        policy: Grid size and tolerance policy used by the diagnostic.
        points: Ordered evidence for every evenly spaced grid coordinate.
    """

    analysisDomain: IntegrationDomain
    policy: ScaleDiagnosticsPolicy
    points: tuple[ScaleDiagnosticPoint, ...]

    def __post_init__(self) -> None:
        """Require a complete ordered grid with stable term membership vectors."""

        if not isinstance(self.analysisDomain, IntegrationDomain):
            raise InvalidParameterTypeError("analysisDomain must be an IntegrationDomain")

        if not isinstance(self.policy, ScaleDiagnosticsPolicy):
            raise InvalidParameterTypeError("policy must be a ScaleDiagnosticsPolicy")

        if not isinstance(self.points, tuple):
            raise InvalidParameterTypeError("points must be an explicit tuple")

        if len(self.points) != self.policy.sampleCount:
            raise InvalidParameterError("points must contain exactly policy.sampleCount values")

        if not all(isinstance(point, ScaleDiagnosticPoint) for point in self.points):
            raise InvalidParameterTypeError("points must contain only ScaleDiagnosticPoint values")

        if self.points[0].coordinate != self.analysisDomain.left:
            raise InvalidDomainError("the diagnostic grid must start at analysisDomain.left")

        if self.points[-1].coordinate != self.analysisDomain.right:
            raise InvalidDomainError("the diagnostic grid must end at analysisDomain.right")

        if any(
            cast(float, leftPoint.coordinate) >= cast(float, rightPoint.coordinate)
            for leftPoint, rightPoint in zip(self.points, self.points[1:])
        ):
            raise InvalidDomainError("diagnostic coordinates must be strictly increasing")

        declaredTerms = tuple(value.term for value in self.points[0].memberships)
        for point in self.points:
            if point.membershipThreshold != self.policy.membershipThreshold:
                raise InvalidParameterError("point thresholds must match the diagnostics policy")

            if tuple(value.term for value in point.memberships) != declaredTerms:
                raise InvalidParameterError("every diagnostic point must preserve the same term order")

    @property
    def gapPoints(self) -> tuple[ScaleDiagnosticPoint, ...]:
        """Sampled points at which no term exceeds the activity threshold."""

        return tuple(point for point in self.points if point.isGap)

    @property
    def overlapPoints(self) -> tuple[ScaleDiagnosticPoint, ...]:
        """Sampled points at which at least two terms exceed the threshold."""

        return tuple(point for point in self.points if point.isOverlap)

    @property
    def gapFraction(self) -> float:
        """Fraction of sampled grid points classified as gaps."""

        return len(self.gapPoints) / len(self.points)

    @property
    def overlapFraction(self) -> float:
        """Fraction of sampled grid points classified as overlaps."""

        return len(self.overlapPoints) / len(self.points)

    @property
    def minimumCoverage(self) -> MembershipScalar:
        """Smallest sampled maximum membership across the analysis grid."""

        return min(point.maximumMembership for point in self.points)

    @property
    def meanCoverage(self) -> float:
        """Arithmetic mean of sampled maximum membership values."""

        return math.fsum(float(point.maximumMembership) for point in self.points) / len(
            self.points
        )

    @property
    def maximumCoverage(self) -> MembershipScalar:
        """Greatest sampled maximum membership across the analysis grid."""

        return max(point.maximumMembership for point in self.points)

    @property
    def maximumActiveTermCount(self) -> int:
        """Greatest number of simultaneously active terms on the sampled grid."""

        return max(len(point.activeTerms) for point in self.points)

    @property
    def meanPartitionError(self) -> float:
        """Mean sampled absolute deviation of membership sums from one."""

        return math.fsum(point.partitionError for point in self.points) / len(self.points)

    @property
    def maximumPartitionError(self) -> float:
        """Greatest sampled absolute deviation of a membership sum from one."""

        return max(point.partitionError for point in self.points)

    @property
    def isPartitionWithinTolerance(self) -> bool:
        """Whether every sampled membership sum satisfies the policy tolerance."""

        return self.maximumPartitionError <= cast(float, self.policy.partitionTolerance)


def _BuildDiagnosticCoordinates(
    analysisDomain: IntegrationDomain,
    sampleCount: int,
) -> tuple[MembershipScalar, ...]:
    """Return an endpoint-preserving evenly spaced diagnostic grid."""

    intervalWidth = float(analysisDomain.right) - float(analysisDomain.left)
    intervalCount = sampleCount - 1

    return tuple(
        analysisDomain.left
        if pointIndex == 0
        else analysisDomain.right
        if pointIndex == intervalCount
        else float(analysisDomain.left) + intervalWidth * pointIndex / intervalCount
        for pointIndex in range(sampleCount)
    )


@dataclass(frozen=True, slots=True)
class LinguisticScale:
    """Immutable ordered tuple of explicitly declared linguistic terms.

    Attributes:
        terms: Non-empty ordered tuple whose names are unique under Unicode
            case-insensitive comparison.
    """

    terms: tuple[LinguisticTerm, ...]

    def __post_init__(self) -> None:
        """Require typed terms whose names have unambiguous lookup keys."""

        if not isinstance(self.terms, tuple):
            raise InvalidParameterTypeError("terms must be an explicit tuple")

        if not self.terms:
            raise InvalidParameterError("linguistic scale must contain at least one term")

        for termIndex, term in enumerate(self.terms):
            if not isinstance(term, LinguisticTerm):
                raise InvalidParameterTypeError(f"terms[{termIndex}] must be a LinguisticTerm")

        termNames = tuple(term.name.casefold() for term in self.terms)

        if len(set(termNames)) != len(termNames):
            raise InvalidParameterError("linguistic term names must be unique ignoring case")

    def GetTermByName(self, termName: str, exactMatching: bool = True) -> LinguisticTerm | None:
        """Return the term whose complete name matches the query.

        Args:
            termName: Complete term name to retrieve.
            exactMatching: Preserve case when `True`; otherwise compare names
                with Unicode case folding.

        Returns:
            The declared term object, or `None` when no complete name matches.

        Raises:
            TypeError: `termName` is not a string or `exactMatching` is not a
                boolean.

        Notes:
            The operation never performs substring, prefix, approximate, or
            membership-based matching.
        """

        if not isinstance(termName, str):
            raise InvalidParameterTypeError("termName must be a string")

        if not isinstance(exactMatching, bool):
            raise InvalidParameterTypeError("exactMatching must be a boolean")

        lookupName = termName if exactMatching else termName.casefold()

        for term in self.terms:
            declaredName = term.name if exactMatching else term.name.casefold()
            if declaredName == lookupName:
                return term

        return None

    def Fuzzify(
        self,
        coordinate: MembershipScalar,
        policy: FuzzificationPolicy | None = None,
    ) -> FuzzificationResult:
        """Classify one coordinate with explicit tie and confidence semantics.

        Every term is evaluated exactly once after the coordinate is confirmed
        to belong to every term universe. The result always exposes all ordered
        membership scores and the maximum score as `confidence`.

        Args:
            coordinate: Finite scalar coordinate belonging to every term
                universe.
            policy: Explicit classification policy, or the default policy that
                selects the first exact maximum and treats zero coverage as no
                match.

        Returns:
            Immutable scores, confidence, tie evidence, and selected terms.

        Raises:
            TypeError: `policy` has the wrong type or `coordinate` is not a real
                scalar.
            ValueError: `coordinate` is non-finite or outside any term universe.
        """

        if policy is None:
            policy = FuzzificationPolicy()

        if not isinstance(policy, FuzzificationPolicy):
            raise InvalidParameterTypeError("policy must be a FuzzificationPolicy")

        for term in self.terms:
            if not term.fuzzySet.universe.Contains(coordinate):
                raise InvalidDomainError("coordinate must belong to every term universe")

        memberships = tuple(
            TermMembership(term, term.fuzzySet.Membership(coordinate))
            for term in self.terms
        )
        confidence = max(cast(float, membership.grade) for membership in memberships)

        if confidence <= cast(float, policy.minimumConfidence):
            return FuzzificationResult(memberships, confidence, policy, (), ())

        tiedTerms = tuple(
            membership.term
            for membership in memberships
            if _IsWithinTieTolerance(
                membership.grade,
                confidence,
                policy.tieTolerance,
            )
        )

        if policy.tiePolicy == "first":
            selectedTerms = tiedTerms[:1]

        elif policy.tiePolicy == "last":
            selectedTerms = tiedTerms[-1:]

        else:
            selectedTerms = tiedTerms

        return FuzzificationResult(
            memberships,
            confidence,
            policy,
            tiedTerms,
            selectedTerms,
        )

    def Diagnose(
        self,
        analysisDomain: IntegrationDomain,
        policy: ScaleDiagnosticsPolicy | None = None,
    ) -> ScaleDiagnosticsResult:
        """Sample coverage, overlaps, gaps, and partition quality on one grid.

        Every term is evaluated exactly once per evenly spaced grid coordinate.
        A term is active only when its membership is strictly greater than
        `membershipThreshold`. The operation reads membership functions but
        never changes scale terms, fuzzy sets, or analytical coefficients.

        Args:
            analysisDomain: Finite closed interval contained in every term's
                continuous universe.
            policy: Explicit sample count and tolerances, or the default
                101-point policy.

        Returns:
            Immutable sampled point evidence and aggregate quality metrics.

        Raises:
            TypeError: The domain or policy has the wrong type, or any term
                uses a non-continuous universe.
            ValueError: The domain lies outside any term universe.

        Notes:
            Finite sampling is reproducible evidence for the declared grid; it
            is not proof of coverage or partition quality between grid points.
        """

        if not isinstance(analysisDomain, IntegrationDomain):
            raise InvalidParameterTypeError("analysisDomain must be an IntegrationDomain")

        if policy is None:
            policy = ScaleDiagnosticsPolicy()

        if not isinstance(policy, ScaleDiagnosticsPolicy):
            raise InvalidParameterTypeError("policy must be a ScaleDiagnosticsPolicy")

        for term in self.terms:
            if not isinstance(term.fuzzySet.universe, ContinuousUniverse):
                raise InvalidParameterTypeError("scale diagnostics require ContinuousUniverse terms")

            analysisDomain.ValidateWithin(term.fuzzySet.universe)

        points = tuple(
            ScaleDiagnosticPoint(
                coordinate,
                tuple(
                    TermMembership(term, term.fuzzySet.Membership(coordinate))
                    for term in self.terms
                ),
                policy.membershipThreshold,
            )
            for coordinate in _BuildDiagnosticCoordinates(
                analysisDomain,
                policy.sampleCount,
            )
        )

        return ScaleDiagnosticsResult(analysisDomain, policy, points)
