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

from fuzzyroutines.fuzzysets import ScalarFuzzySet, _RequireGrade

TIEPOLICIES = ("first", "last", "all")


def _IsWithinTieTolerance(grade, confidence, tolerance):
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

    def __post_init__(self):
        """Require a non-empty exact name and a modern scalar fuzzy set."""

        if not isinstance(self.name, str):
            raise TypeError("name must be a string")

        if not self.name.strip():
            raise ValueError("name must contain at least one non-whitespace character")

        if not isinstance(self.fuzzySet, ScalarFuzzySet):
            raise TypeError("fuzzySet must be a ScalarFuzzySet")


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
    minimumConfidence: Real = 0.0
    tieTolerance: Real = 0.0

    def __post_init__(self):
        """Validate the complete classification policy."""

        if self.tiePolicy not in TIEPOLICIES:
            raise ValueError(f"unknown tie policy: {self.tiePolicy!r}")

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
    grade: Real

    def __post_init__(self):
        """Require a typed term and a valid membership grade."""

        if not isinstance(self.term, LinguisticTerm):
            raise TypeError("term must be a LinguisticTerm")

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
    confidence: Real
    policy: FuzzificationPolicy
    tiedTerms: tuple[LinguisticTerm, ...]
    selectedTerms: tuple[LinguisticTerm, ...]

    def __post_init__(self):
        """Require internally consistent classification evidence."""

        if not isinstance(self.memberships, tuple) or not self.memberships:
            raise TypeError("memberships must be a non-empty tuple")

        if not all(isinstance(value, TermMembership) for value in self.memberships):
            raise TypeError("memberships must contain only TermMembership values")

        if not isinstance(self.policy, FuzzificationPolicy):
            raise TypeError("policy must be a FuzzificationPolicy")

        confidence = _RequireGrade(self.confidence, "confidence")
        if confidence != max(value.grade for value in self.memberships):
            raise ValueError("confidence must equal the maximum membership grade")

        object.__setattr__(self, "confidence", confidence)

        expectedTiedTerms = ()
        if confidence > self.policy.minimumConfidence:
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
            raise ValueError("tiedTerms do not match memberships and policy")

        if self.policy.tiePolicy == "first":
            expectedSelectedTerms = expectedTiedTerms[:1]

        elif self.policy.tiePolicy == "last":
            expectedSelectedTerms = expectedTiedTerms[-1:]

        else:
            expectedSelectedTerms = expectedTiedTerms

        if self.selectedTerms != expectedSelectedTerms:
            raise ValueError("selectedTerms do not match tiedTerms and policy")

    @property
    def isMatch(self):
        """Return whether the policy selected at least one term."""

        return bool(self.selectedTerms)

    @property
    def isTie(self):
        """Return whether multiple maximum terms satisfied the tie policy."""

        return len(self.tiedTerms) > 1


@dataclass(frozen=True, slots=True)
class LinguisticScale:
    """Immutable ordered tuple of explicitly declared linguistic terms.

    Attributes:
        terms: Non-empty ordered tuple whose names are unique under Unicode
            case-insensitive comparison.
    """

    terms: tuple[LinguisticTerm, ...]

    def __post_init__(self):
        """Require typed terms whose names have unambiguous lookup keys."""

        if not isinstance(self.terms, tuple):
            raise TypeError("terms must be an explicit tuple")

        if not self.terms:
            raise ValueError("linguistic scale must contain at least one term")

        for termIndex, term in enumerate(self.terms):
            if not isinstance(term, LinguisticTerm):
                raise TypeError(f"terms[{termIndex}] must be a LinguisticTerm")

        termNames = tuple(term.name.casefold() for term in self.terms)

        if len(set(termNames)) != len(termNames):
            raise ValueError("linguistic term names must be unique ignoring case")

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
            raise TypeError("termName must be a string")

        if not isinstance(exactMatching, bool):
            raise TypeError("exactMatching must be a boolean")

        lookupName = termName if exactMatching else termName.casefold()

        for term in self.terms:
            declaredName = term.name if exactMatching else term.name.casefold()
            if declaredName == lookupName:
                return term

        return None

    def Fuzzify(
        self,
        coordinate: Real,
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
            raise TypeError("policy must be a FuzzificationPolicy")

        for term in self.terms:
            if not term.fuzzySet.universe.Contains(coordinate):
                raise ValueError("coordinate must belong to every term universe")

        memberships = tuple(
            TermMembership(term, term.fuzzySet.Membership(coordinate))
            for term in self.terms
        )
        confidence = max(membership.grade for membership in memberships)

        if confidence <= policy.minimumConfidence:
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
