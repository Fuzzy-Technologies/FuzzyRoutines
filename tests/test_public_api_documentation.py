# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Public source-documentation contracts for modern and compatibility APIs."""

import inspect
from fractions import Fraction

import pytest

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
LEGACYNUMERICFUNCTIONS = (
    (legacyApi.FuzzyNOT, (Fraction(1, 2),)),
    (legacyApi.FuzzyNOTParabolic, (Fraction(1, 2),)),
    (legacyApi.FuzzyAND, (Fraction(1, 2), 0.5)),
    (legacyApi.FuzzyOR, (Fraction(1, 2), 0.5)),
    (legacyApi.TNorm, (Fraction(1, 2), 0.5)),
    (legacyApi.TNormCompose, (Fraction(1, 2), 0.5)),
    (legacyApi.SCoNorm, (Fraction(1, 2), 0.5)),
    (legacyApi.SCoNormCompose, (Fraction(1, 2), 0.5)),
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


def test_HistoricalDirectFormulaDocsExposeExtremeOverflowBoundary():
    """Keep retained intermediate overflow visible in public contracts."""

    overflowCases = (
        (legacyApi.MFunction("hyperbolic", a=1.0, b=2.0, c=0.0).Hyperbolic, 1e308),
        (legacyApi.MFunction("bell", a=-1e308, b=0.0, c=1e308).Bell, 1.5e308),
        (legacyApi.MFunction("parabolic", a=-1e308, b=1e308).Parabolic, 0.0),
    )

    for evaluator, coordinate in overflowCases:
        with pytest.raises(OverflowError):
            evaluator(coordinate)

        assert "OverflowError" in inspect.getdoc(evaluator)


def test_LegacyValidationDiagnosticsMatchTheirDocumentedBoundary(capsys):
    """Distinguish silent numeric rejection from non-numeric diagnostics."""

    assert legacyApi.IsCorrectFuzzyNumberValue(2.0) is False
    assert capsys.readouterr().out == ""

    assert legacyApi.IsCorrectFuzzyNumberValue("invalid") is False
    assert capsys.readouterr().out

    assert legacyApi.IsCorrectFuzzyNumberValue(Fraction(1, 2)) is False
    assert capsys.readouterr().out

    documentation = inspect.getdoc(legacyApi.IsCorrectFuzzyNumberValue).lower()
    assert "unsupported numeric type" in documentation
    assert "silently" in documentation


def test_LegacyNumericDocsMatchBuiltInNumberBoundary():
    """Document that historical evaluators reject other real-number types."""

    for evaluator, arguments in LEGACYNUMERICFUNCTIONS:
        with pytest.raises(ValueError):
            evaluator(*arguments)

        documentation = inspect.getdoc(evaluator).lower()
        assert "built-in `int` or `float`" in documentation

    membershipFunctions = (
        legacyApi.MFunction("hyperbolic", a=1, b=2, c=0),
        legacyApi.MFunction("bell", a=0, b=1, c=2),
        legacyApi.MFunction("parabolic", a=0, b=1),
        legacyApi.MFunction("triangle", a=0, b=1, c=0.5),
        legacyApi.MFunction("trapezium", a=0, b=1, c=0.25, d=0.75),
        legacyApi.MFunction("exponential", a=0, b=1),
        legacyApi.MFunction("sigmoidal", a=1, b=0),
        legacyApi.MFunction("desirability"),
    )

    for membershipFunction in membershipFunctions:
        with pytest.raises(ValueError):
            membershipFunction.mju(Fraction(1, 2))

        documentation = inspect.getdoc(membershipFunction.mju).lower()
        assert "built-in `int` or `float`" in documentation

    with pytest.raises(ValueError):
        legacyApi.MFunction("exponential", a=Fraction(0), b=1)

    with pytest.raises(ValueError):
        legacyApi.FuzzyScale().Fuzzy(Fraction(1, 2))

    assert "built-in `int` or `float`" in inspect.getdoc(legacyApi.MFunction)
    assert "built-in `int` or `float`" in inspect.getdoc(legacyApi.FuzzyScale.Fuzzy)


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
