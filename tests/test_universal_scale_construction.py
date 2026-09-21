# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Construction-work tests for the historical UniversalFuzzyScale preset."""

from fuzzyroutines.FuzzyRoutines import FuzzySet, UniversalFuzzyScale


def test_UniversalScaleConstructsOnlyRetainedLevels(monkeypatch):
    constructionCount = 0
    originalInitializer = FuzzySet.__init__

    def CountedInitializer(self, *arguments, **keywordArguments):
        nonlocal constructionCount
        constructionCount += 1
        originalInitializer(self, *arguments, **keywordArguments)

    monkeypatch.setattr(FuzzySet, "__init__", CountedInitializer)

    scale = UniversalFuzzyScale()

    assert constructionCount == len(scale.levels) == 5, (
        "UniversalFuzzyScale must not construct and discard the three default levels."
    )
