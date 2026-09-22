# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Public source-documentation contracts for modern and compatibility APIs."""

import inspect

import fuzzyroutines
import fuzzyroutines.FuzzyRoutines as legacyApi
from fuzzyroutines.alphacuts import SampledAlphaCut
from fuzzyroutines.domain import IntegrationDomain
from fuzzyroutines.properties import DiscreteRegion, SampledFuzzyProperties

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


def test_FloatingPointEndpointResultsUseClosedDocumentedRanges():
    """Keep representable endpoint behavior aligned with public range claims."""

    endpointCases = (
        (legacyApi.MFunction("exponential", a=0.0, b=1.0).Exponential, 1e308, 0.0),
        (legacyApi.MFunction("sigmoidal", a=1.0, b=0.0).Sigmoidal, -1e308, 0.0),
        (legacyApi.MFunction("sigmoidal", a=1.0, b=0.0).Sigmoidal, 1e308, 1.0),
        (legacyApi.MFunction("desirability").Desirability, 1e308, 1.0),
    )

    for evaluator, coordinate, expectedEndpoint in endpointCases:
        documentation = inspect.getdoc(evaluator)
        assert evaluator(coordinate) == expectedEndpoint
        assert "$[0, 1]$" in documentation, (
            f"{evaluator.__qualname__} must document its representable closed range"
        )


def test_LegacyValidationDiagnosticsMatchTheirDocumentedBoundary(capsys):
    """Distinguish silent numeric rejection from non-numeric diagnostics."""

    assert legacyApi.IsCorrectFuzzyNumberValue(2.0) is False
    assert capsys.readouterr().out == ""

    assert legacyApi.IsCorrectFuzzyNumberValue("invalid") is False
    assert capsys.readouterr().out

    documentation = inspect.getdoc(legacyApi.IsCorrectFuzzyNumberValue).lower()
    assert "non-numeric" in documentation
    assert "silently" in documentation


def test_SampledResultDocsDescribeDirectConstructorValidationLimits():
    """Keep factory guarantees distinct from direct-constructor validation."""

    analysisDomain = IntegrationDomain(0.0, 1.0)
    coordinates = (0.0, 0.2, 1.0)
    grades = (0.0, 0.5, 1.0)
    nonUniformCut = SampledAlphaCut(
        0.5,
        analysisDomain,
        3,
        coordinates,
        grades,
        DiscreteRegion((0.2, 1.0)),
    )
    independentlyRecordedProperties = SampledFuzzyProperties(
        analysisDomain,
        3,
        coordinates,
        grades,
        DiscreteRegion(),
        DiscreteRegion(),
        DiscreteRegion(),
        1.0,
    )

    assert nonUniformCut.coordinates == coordinates
    assert independentlyRecordedProperties.positiveSupportSamples.isEmpty

    cutDocumentation = inspect.getdoc(SampledAlphaCut).lower()
    propertiesDocumentation = inspect.getdoc(SampledFuzzyProperties).lower()
    assert "direct construction" in cutDocumentation
    assert "equal spacing" in cutDocumentation
    assert "direct construction" in propertiesDocumentation
    assert "recompute" in propertiesDocumentation


def test_UniversalScaleDocsDoNotClaimDeepImmutability():
    """Document mutable compatibility objects despite the absent setter."""

    scale = legacyApi.UniversalFuzzyScale()
    documentation = inspect.getdoc(legacyApi.UniversalFuzzyScale).lower()

    assert isinstance(scale.levels, list)
    assert "without a setter" in documentation
    assert "remain mutable" in documentation
