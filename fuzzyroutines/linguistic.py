# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Typed immutable linguistic terms and exact-name scale lookup.

Name lookup is either case-sensitive or Unicode case-insensitive. Membership
comparison, tie-breaking, and fuzzification policies remain separate contracts.
"""

from dataclasses import dataclass

from fuzzyroutines.fuzzysets import ScalarFuzzySet


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
