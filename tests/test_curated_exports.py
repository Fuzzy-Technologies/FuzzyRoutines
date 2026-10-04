# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Curated import contracts for modern callers and historical consumers."""

import importlib
import subprocess
import sys

import fuzzyroutines
import fuzzyroutines.FuzzyRoutines as legacy_api

MODERN_EXPORTS = {
    "alphacuts": {"AlphaCut", "SampleAlphaCut", "SampledAlphaCut"},
    "defuzzification": {"Centroid", "CentroidConvergenceError", "CentroidPolicy"},
    "domain": {"ContinuousUniverse", "DiscreteUniverse", "IntegrationDomain"},
    "fuzzysets": {
        "Complement", "Difference", "Height", "Intersection", "IsNormal",
        "Normalize", "ScalarFuzzySet", "Union",
    },
    "linguistic": {
        "FuzzificationPolicy", "FuzzificationResult", "LinguisticScale", "LinguisticTerm",
        "ScaleDiagnosticPoint", "ScaleDiagnosticsPolicy", "ScaleDiagnosticsResult", "TermMembership",
    },
    "membership": {
        "Bell", "Gaussian", "HarringtonDesirability", "Hyperbolic", "Logistic",
        "MembershipCallable", "MembershipFunction", "MembershipScalar", "SShoulder",
        "Trapezoid", "Triangle",
    },
    "operators": {"NegationPolicy", "SNormPolicy", "TNormPolicy"},
    "properties": {
        "ContinuousFuzzyProperties", "ContinuousInterval", "ContinuousRegion",
        "DeriveProperties", "DiscreteFuzzyProperties", "DiscreteRegion",
        "SampledFuzzyProperties", "SampleProperties",
    },
    "relations": {"ComparisonDomain", "ComparisonPolicy", "EqualOnDomain", "IncludedOnDomain"},
}
LEGACY_EXPORTS = {
    "DiapasonParser", "FuzzyAND", "FuzzyNOT", "FuzzyNOTParabolic", "FuzzyOR",
    "FuzzyScale", "FuzzySet", "IsCorrectFuzzyNumberValue", "IsNumber", "MFunction",
    "SCoNorm", "SCoNormCompose", "TNorm", "TNormCompose", "UniversalFuzzyScale",
}


def test_ModernExportsResolveToCanonicalObjects():
    """Require the complete intended root API and preserve module object identity."""

    expected = set().union(*MODERN_EXPORTS.values())
    assert set(fuzzyroutines.__all__) == expected, "The curated modern root surface drifted"
    assert fuzzyroutines.__all__ == sorted(expected), "Modern exports must be unique and deterministic"

    for module_name, names in MODERN_EXPORTS.items():
        module = importlib.import_module(f"fuzzyroutines.{module_name}")

        for name in names:
            assert getattr(fuzzyroutines, name) is getattr(module, name), (
                f"Root export {name} must retain its canonical module identity"
            )


def test_WildcardSurfacesExcludeHelpersEvenAfterLegacyImport():
    """Keep both wildcard surfaces deliberate despite package submodule attributes."""

    modern_namespace = {}
    legacy_namespace = {}
    exec("from fuzzyroutines import *", modern_namespace)  # noqa: S102 - literal wildcard-import contract
    exec("from fuzzyroutines.FuzzyRoutines import *", legacy_namespace)  # noqa: S102 - literal import contract

    assert set(modern_namespace) - {"__builtins__"} == set(fuzzyroutines.__all__), (
        "Modern wildcard import must follow its curated list even after facade imports"
    )
    assert set(legacy_namespace) - {"__builtins__"} == LEGACY_EXPORTS, (
        "Legacy wildcard import must retain exactly the fifteen supported names"
    )
    assert legacy_api.__all__ == sorted(LEGACY_EXPORTS), "Legacy exports must be unique and deterministic"
    assert not {"math", "copy", "_historical_symbol"} & set(vars(legacy_api)), (
        "Unused historical helpers and adapter setup variables must remain private"
    )


def test_ModernRootImportAvoidsLegacyAndOptionalDependencies():
    """Check a fresh process so prior imports cannot mask eager dependency loading."""

    source = '''import sys
import fuzzyroutines
assert not any(name == "fuzzyroutines.FuzzyRoutines" or name.startswith("fuzzyroutines._legacy") for name in sys.modules)
assert not {"numpy", "scipy", "matplotlib"} & sys.modules.keys()
assert fuzzyroutines.Triangle(0, 0.5, 1)(0.25) == 0.5
assert fuzzyroutines.MembershipScalar.__name__ == "MembershipScalar"
'''
    result = subprocess.run([sys.executable, "-c", source], text=True, capture_output=True, check=False)

    assert result.returncode == 0, f"Modern root import boundary failed: {result.stderr}"
