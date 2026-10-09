# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Regression contracts for the historical public API surface."""

import inspect

import fuzzyroutines.FuzzyRoutines as fr


EXPECTED_FUNCTION_SIGNATURES = {
    "DiapasonParser": "(diapason)",
    "IsNumber": "(value)",
    "IsCorrectFuzzyNumberValue": "(value)",
    "FuzzyNOT": "(fuzzyNumber, alpha=0.5)",
    "FuzzyNOTParabolic": "(fuzzyNumber, alpha=0.5, epsilon=0.001)",
    "FuzzyAND": "(aNumber, bNumber)",
    "FuzzyOR": "(aNumber, bNumber)",
    "TNorm": "(aFuzzyNumber, bFuzzyNumber, normType='logic')",
    "TNormCompose": "(*fuzzyNumbers, normType='logic')",
    "SCoNorm": "(aFuzzyNumber, bFuzzyNumber, normType='logic')",
    "SCoNormCompose": "(*fuzzyNumbers, normType='logic')",
}

EXPECTED_CLASS_SIGNATURES = {
    "MFunction": "(userFunc, **membershipFunctionParams)",
    "FuzzySet": "(membershipFunction, supportSet=(0.0, 1.0), linguisticName='FuzzySet')",
    "FuzzyScale": "()",
    "UniversalFuzzyScale": "()",
}

EXPECTED_PUBLIC_MEMBERS = {
    "MFunction": {
        "name",
        "parameters",
        "Hyperbolic",
        "Bell",
        "Parabolic",
        "Triangle",
        "Trapezium",
        "Exponential",
        "Sigmoidal",
        "Desirability",
    },
    "FuzzySet": {"name", "mFunction", "supportSet", "defuzValue", "Defuz"},
    "FuzzyScale": {"name", "levels", "Fuzzy", "GetLevelByName"},
    "UniversalFuzzyScale": {
        "name",
        "levels",
        "Fuzzy",
        "GetLevelByName",
        "levelsNames",
        "levelsNamesUpper",
    },
}

EXPECTED_MEMBERSHIP_IDENTIFIERS = {
    "hyperbolic",
    "bell",
    "parabolic",
    "triangle",
    "trapezium",
    "exponential",
    "sigmoidal",
    "desirability",
}


def test_LegacyTopLevelFunctionSignatures():
    """Preserve protected top-level legacy parameter names and defaults."""

    for name, expected in EXPECTED_FUNCTION_SIGNATURES.items():
        obj = getattr(fr, name)
        assert str(inspect.signature(obj)) == expected


def test_LegacyClassConstructorSignatures():
    """Preserve historical constructor parameter names and defaults."""

    for name, expected in EXPECTED_CLASS_SIGNATURES.items():
        obj = getattr(fr, name)
        assert str(inspect.signature(obj)) == expected


def test_LegacyPublicClassMembersExist():
    """Verify that legacy public class members exist."""

    for className, expectedMembers in EXPECTED_PUBLIC_MEMBERS.items():
        actualMembers = set(dir(getattr(fr, className)))
        assert expectedMembers <= actualMembers


def test_HistoricalMembershipIdentifiersAreRegistered():
    """Verify that historical membership identifiers are registered."""

    instances = [
        fr.MFunction("hyperbolic", a=1, b=1, c=0),
        fr.MFunction("bell", a=0, b=0.5, c=0.75),
        fr.MFunction("parabolic", a=0, b=1),
        fr.MFunction("triangle", a=0, b=1, c=0.5),
        fr.MFunction("trapezium", a=0, b=1, c=0.25, d=0.75),
        fr.MFunction("exponential", a=0.5, b=0.1),
        fr.MFunction("sigmoidal", a=1, b=0.5),
        fr.MFunction("desirability"),
    ]
    registered = {instance.name.lower() for instance in instances}
    assert registered == EXPECTED_MEMBERSHIP_IDENTIFIERS


def test_HistoricalWildcardImportRetainsOnlySupportedSymbols():
    """Exclude historical helper leaks while retaining all fifteen API symbols."""

    namespace = {}
    exec("from fuzzyroutines.FuzzyRoutines import *", namespace)

    protectedNames = (
        set(EXPECTED_FUNCTION_SIGNATURES)
        | set(EXPECTED_CLASS_SIGNATURES)
    )
    assert set(fr.__all__) == protectedNames, "The facade must retain all supported historical names"
    assert set(namespace) - {"__builtins__"} == protectedNames, (
        "Historical wildcard imports must expose only the curated compatibility API"
    )
