# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Typed immutable representations for ordered linguistic terms.

This module defines representation only.  Lookup, membership comparison,
tie-breaking, and fuzzification policies remain separate contracts.
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
        terms: Non-empty ordered tuple whose term names are exactly unique.
    """

    terms: tuple[LinguisticTerm, ...]

    def __post_init__(self):
        """Require a non-empty tuple of typed terms with exact unique names."""

        if not isinstance(self.terms, tuple):
            raise TypeError("terms must be an explicit tuple")

        if not self.terms:
            raise ValueError("linguistic scale must contain at least one term")

        for termIndex, term in enumerate(self.terms):
            if not isinstance(term, LinguisticTerm):
                raise TypeError(f"terms[{termIndex}] must be a LinguisticTerm")

        termNames = tuple(term.name for term in self.terms)

        if len(set(termNames)) != len(termNames):
            raise ValueError("linguistic term names must be exactly unique")
