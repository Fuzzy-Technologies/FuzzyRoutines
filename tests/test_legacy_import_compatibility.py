# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Regression coverage for historical FuzzyRoutines import surfaces.

These tests protect module paths and symbol availability only.  Mathematical
results deliberately belong to the family-specific reference suites, so a
correctness fix is not blocked by an old numeric observation.
"""

import importlib


LEGACY_MODULE_PATHS = (
    "fuzzyroutines",
    "fuzzyroutines.FuzzyRoutines",
)

LEGACY_PUBLIC_SYMBOLS = (
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
    "MFunction",
    "FuzzySet",
    "FuzzyScale",
    "UniversalFuzzyScale",
)


def test_HistoricalModulePathsRemainImportable():
    imported = {path: importlib.import_module(path) for path in LEGACY_MODULE_PATHS}

    assert imported["fuzzyroutines"].__name__ == "fuzzyroutines"
    assert imported["fuzzyroutines.FuzzyRoutines"].__name__ == "fuzzyroutines.FuzzyRoutines"


def test_NamedLegacyImportsResolveToModuleSymbols():
    from fuzzyroutines.FuzzyRoutines import (
        DiapasonParser,
        FuzzyAND,
        FuzzyNOT,
        FuzzyNOTParabolic,
        FuzzyOR,
        FuzzyScale,
        FuzzySet,
        IsCorrectFuzzyNumberValue,
        IsNumber,
        MFunction,
        SCoNorm,
        SCoNormCompose,
        TNorm,
        TNormCompose,
        UniversalFuzzyScale,
    )

    module = importlib.import_module("fuzzyroutines.FuzzyRoutines")
    imported = {
        "DiapasonParser": DiapasonParser,
        "IsNumber": IsNumber,
        "IsCorrectFuzzyNumberValue": IsCorrectFuzzyNumberValue,
        "FuzzyNOT": FuzzyNOT,
        "FuzzyNOTParabolic": FuzzyNOTParabolic,
        "FuzzyAND": FuzzyAND,
        "FuzzyOR": FuzzyOR,
        "TNorm": TNorm,
        "TNormCompose": TNormCompose,
        "SCoNorm": SCoNorm,
        "SCoNormCompose": SCoNormCompose,
        "MFunction": MFunction,
        "FuzzySet": FuzzySet,
        "FuzzyScale": FuzzyScale,
        "UniversalFuzzyScale": UniversalFuzzyScale,
    }

    assert tuple(imported) == LEGACY_PUBLIC_SYMBOLS
    for name, value in imported.items():
        assert value is getattr(module, name)


def test_HistoricalWildcardImportExportsProtectedSymbols():
    namespace = {}
    exec("from fuzzyroutines.FuzzyRoutines import *", namespace)

    assert set(LEGACY_PUBLIC_SYMBOLS) <= set(namespace)
