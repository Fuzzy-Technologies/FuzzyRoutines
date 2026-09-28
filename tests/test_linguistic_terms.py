# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Contracts for immutable typed linguistic terms and ordered scales."""

from dataclasses import FrozenInstanceError

import pytest

from fuzzyroutines import (
    ContinuousUniverse,
    LinguisticScale,
    LinguisticTerm,
    ScalarFuzzySet,
)
from fuzzyroutines.FuzzyRoutines import FuzzyScale, FuzzySet, MFunction


def _BuildSet(offset=0.0):
    """Build a bounded modern fuzzy set for representation tests."""

    universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
    return ScalarFuzzySet(universe, lambda coordinate: min(1.0, coordinate + offset))


def _BuildLegacySet():
    """Build one historical fuzzy set for compatibility-boundary tests."""

    return FuzzySet(MFunction("parabolic", a=0.0, b=1.0))


def test_LinguisticTermCarriesExactNameAndScalarFuzzySet():
    fuzzySet = _BuildSet()
    term = LinguisticTerm("Medium", fuzzySet)

    assert term.name == "Medium", "Term construction must preserve the exact declared name."
    assert term.fuzzySet is fuzzySet, "Term construction must preserve fuzzy-set identity."


@pytest.mark.parametrize("invalidName", [None, 1, (), []])
def test_LinguisticTermRejectsNonStringNames(invalidName):
    with pytest.raises(TypeError, match="name must be a string"):
        LinguisticTerm(invalidName, _BuildSet())


@pytest.mark.parametrize("invalidName", ["", " ", "\t\n"])
def test_LinguisticTermRejectsEmptyNames(invalidName):
    with pytest.raises(ValueError, match="non-whitespace"):
        LinguisticTerm(invalidName, _BuildSet())


def test_LinguisticTermRejectsLegacyAndArbitraryFuzzySetValues():
    for invalidFuzzySet in (None, object(), _BuildLegacySet()):
        with pytest.raises(TypeError, match="ScalarFuzzySet"):
            LinguisticTerm("Medium", invalidFuzzySet)


def test_LinguisticTermIsImmutable():
    term = LinguisticTerm("Medium", _BuildSet())

    with pytest.raises(FrozenInstanceError):
        term.name = "Changed"

    with pytest.raises(FrozenInstanceError):
        term.fuzzySet = _BuildSet(0.1)


def test_LinguisticScalePreservesExplicitTermOrderAndIdentity():
    low = LinguisticTerm("Low", _BuildSet())
    medium = LinguisticTerm("Medium", _BuildSet(0.1))
    high = LinguisticTerm("High", _BuildSet(0.2))
    declaredTerms = (low, medium, high)
    scale = LinguisticScale(declaredTerms)

    assert scale.terms is declaredTerms, "The ordered representation must preserve tuple identity."
    assert scale.terms == (low, medium, high), "The declared term order must remain unchanged."


def test_LinguisticScaleRequiresExplicitNonEmptyTypedTuple():
    low = LinguisticTerm("Low", _BuildSet())

    with pytest.raises(TypeError, match="explicit tuple"):
        LinguisticScale([low])

    with pytest.raises(ValueError, match="at least one term"):
        LinguisticScale(())

    with pytest.raises(TypeError, match=r"terms\[1\]"):
        LinguisticScale((low, {"name": "High", "fSet": _BuildLegacySet()}))


def test_LinguisticScaleRejectsCaseInsensitiveNameCollisions():
    low = LinguisticTerm("Low", _BuildSet())
    duplicate = LinguisticTerm("Low", _BuildSet(0.1))

    with pytest.raises(ValueError, match="unique ignoring case"):
        LinguisticScale((low, duplicate))

    with pytest.raises(ValueError, match="unique ignoring case"):
        LinguisticScale((low, LinguisticTerm("LOW", _BuildSet(0.2))))


@pytest.mark.parametrize(
    ("declaredName", "queryName"),
    [("Low", "low"), ("Straße", "STRASSE"), ("ΟΣ", "ος")],
)
def test_LinguisticScaleSupportsUnicodeCaseInsensitiveCompleteNameLookup(
    declaredName,
    queryName,
):
    term = LinguisticTerm(declaredName, _BuildSet())
    scale = LinguisticScale((term,))

    assert scale.GetTermByName(queryName) is None, (
        "Exact lookup must preserve the declared name's case."
    )
    assert scale.GetTermByName(queryName, exactMatching=False) is term, (
        "Case-insensitive lookup must use Unicode case folding."
    )


def test_LinguisticScaleLookupNeverPerformsPartialOrApproximateMatching():
    low = LinguisticTerm("Low", _BuildSet())
    scale = LinguisticScale((low,))

    assert scale.GetTermByName("Low") is low, "Exact complete-name lookup must return the term."
    assert scale.GetTermByName("Lo") is None, "Exact lookup must not accept a name prefix."
    assert scale.GetTermByName("ow", exactMatching=False) is None, (
        "Case-insensitive lookup must not accept a name substring."
    )
    assert scale.GetTermByName("Lowest", exactMatching=False) is None, (
        "Case-insensitive lookup must not accept an approximate extension."
    )


@pytest.mark.parametrize("invalidName", [None, 1, (), []])
def test_LinguisticScaleLookupRejectsNonStringNames(invalidName):
    scale = LinguisticScale((LinguisticTerm("Low", _BuildSet()),))

    with pytest.raises(TypeError, match="termName must be a string"):
        scale.GetTermByName(invalidName)


@pytest.mark.parametrize("invalidMode", [None, 0, 1, "false"])
def test_LinguisticScaleLookupRequiresBooleanMatchingMode(invalidMode):
    scale = LinguisticScale((LinguisticTerm("Low", _BuildSet()),))

    with pytest.raises(TypeError, match="exactMatching must be a boolean"):
        scale.GetTermByName("Low", exactMatching=invalidMode)


def test_LinguisticScaleIsImmutableAndContainsNoFuzzificationPolicy():
    scale = LinguisticScale((LinguisticTerm("Low", _BuildSet()),))

    with pytest.raises(FrozenInstanceError):
        scale.terms = ()

    assert not hasattr(scale, "Fuzzy"), "Task 82 must not preempt the deferred fuzzification policy."


def test_ModernLinguisticTypesAreExportedFromPackageRoot():
    import fuzzyroutines

    assert fuzzyroutines.LinguisticTerm is LinguisticTerm, (
        "The modern package root must export LinguisticTerm."
    )
    assert fuzzyroutines.LinguisticScale is LinguisticScale, (
        "The modern package root must export LinguisticScale."
    )
    assert {"LinguisticTerm", "LinguisticScale"} <= set(fuzzyroutines.__all__), (
        "The explicit modern export list must contain both linguistic representation types."
    )


def test_LegacyFuzzyScaleLevelsRemainMutableDictionaries():
    scale = FuzzyScale()

    assert isinstance(scale.levels, list), "Legacy levels must remain a list."
    assert all(isinstance(level, dict) for level in scale.levels), (
        "Legacy levels must remain dictionary records."
    )
    assert all(set(level) == {"name", "fSet"} for level in scale.levels), (
        "Legacy level dictionaries must preserve their historical keys."
    )

    replacement = [{"name": "Only", "fSet": _BuildLegacySet()}]
    scale.levels = replacement

    assert scale.levels is replacement, "Legacy levels mutation must preserve historical behavior."
    assert scale.GetLevelByName("Only") is replacement[0], (
        "Legacy dictionary lookup must remain available and unchanged."
    )


@pytest.mark.parametrize(
    "invalidLevel",
    [
        {"name": "Missing fuzzy set"},
        {"fSet": None},
        {"name": "Extra", "fSet": None, "unexpected": object()},
    ],
)
def test_LegacyFuzzyScaleRequiresBothExactLevelKeys(invalidLevel):
    scale = FuzzyScale()

    with pytest.raises(Exception, match="2-dim dictionary"):
        scale.levels = [invalidLevel]


@pytest.mark.parametrize(("firstName", "secondName"), [("Low", "LOW"), ("i", "ı")])
def test_LegacyFuzzyScaleRejectsCaseInsensitiveNameCollisions(firstName, secondName):
    scale = FuzzyScale()

    with pytest.raises(ValueError, match="not unique ignoring case"):
        scale.levels = [
            {"name": firstName, "fSet": _BuildLegacySet()},
            {"name": secondName, "fSet": _BuildLegacySet()},
        ]


def test_LegacyFuzzyScaleLookupPreservesExactAndCaseInsensitiveModes():
    scale = FuzzyScale()
    level = {"name": "Medium", "fSet": _BuildLegacySet()}
    scale.levels = [level]

    assert scale.GetLevelByName("Medium") is level, "Legacy exact lookup must remain callable."
    assert scale.GetLevelByName("medium") is None, "Legacy exact lookup must preserve case."
    assert scale.GetLevelByName("medium", exactMatching=False) is level, (
        "Legacy case-insensitive lookup must remain callable."
    )
    assert scale.GetLevelByName("Med", exactMatching=False) is None, (
        "Legacy case-insensitive lookup must still require a complete name."
    )
