# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Public source-documentation contracts for modern and compatibility APIs."""

import inspect

import fuzzyroutines
import fuzzyroutines.FuzzyRoutines as legacyApi

LEGACYFUNCTIONS = (
    "DiapasonParser",
    "IsNumber",
    "IsCorrectFuzzyNumberValue",
    "FuzzyNOT",
    "FuzzyNOTParabolic",
    "FuzzyAND",
    "FuzzyOR",
    "TNorm",
    "TNormCompose",
    "SCoNorm",
    "SCoNormCompose",
)
LEGACYCLASSES = (
    legacyApi.MFunction,
    legacyApi.FuzzySet,
    legacyApi.FuzzyScale,
    legacyApi.UniversalFuzzyScale,
)


def _AssertDocumented(publicName, publicObject):
    """Require a non-empty docstring with a canonical summary sentence."""

    documentation = inspect.getdoc(publicObject)
    assert documentation, f"{publicName} has no public docstring"
    assert documentation.splitlines()[0].endswith("."), (
        f"{publicName} docstring summary must end with a period"
    )


def test_ModernRootExportsHaveCanonicalDocstrings():
    """Require documentation for every explicitly exported modern symbol."""

    assert len(fuzzyroutines.__all__) == len(set(fuzzyroutines.__all__))

    for publicName in fuzzyroutines.__all__:
        _AssertDocumented(publicName, getattr(fuzzyroutines, publicName))


def test_LegacyFunctionsHaveCanonicalDocstrings():
    """Require documentation for every protected legacy function."""

    for publicName in LEGACYFUNCTIONS:
        _AssertDocumented(publicName, getattr(legacyApi, publicName))


def test_LegacyClassesAndPublicMembersHaveCanonicalDocstrings():
    """Require documentation for legacy classes and their authored members."""

    for legacyClass in LEGACYCLASSES:
        _AssertDocumented(legacyClass.__name__, legacyClass)

        for memberName, member in legacyClass.__dict__.items():
            if memberName.startswith("_"):
                continue

            if inspect.isfunction(member) or isinstance(member, property):
                _AssertDocumented(f"{legacyClass.__name__}.{memberName}", member)
