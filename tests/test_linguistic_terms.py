# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Contracts for immutable typed linguistic terms and ordered scales."""

from dataclasses import FrozenInstanceError

import pytest

from fuzzyroutines import (
    ContinuousUniverse,
    FuzzificationPolicy,
    FuzzificationResult,
    LinguisticScale,
    LinguisticTerm,
    ScalarFuzzySet,
    TermMembership,
)
from fuzzyroutines.FuzzyRoutines import FuzzyScale, FuzzySet, MFunction


def _BuildSet(offset=0.0):
    """Build a bounded modern fuzzy set for representation tests."""

    universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
    return ScalarFuzzySet(universe, lambda coordinate: min(1.0, coordinate + offset))


def _BuildMembershipSet(membershipFunction):
    """Build a bounded modern fuzzy set from an explicit test callable."""

    universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
    return ScalarFuzzySet(universe, membershipFunction)


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


def test_LinguisticScaleIsImmutableAndContainsNoLegacyFuzzyMethod():
    scale = LinguisticScale((LinguisticTerm("Low", _BuildSet()),))

    with pytest.raises(FrozenInstanceError):
        scale.terms = ()

    assert not hasattr(scale, "Fuzzy"), "Task 82 must not preempt the deferred fuzzification policy."


@pytest.mark.parametrize("tiePolicy", ["first", "last", "all"])
def test_FuzzificationPolicyAcceptsEveryDocumentedTieMode(tiePolicy):
    policy = FuzzificationPolicy(tiePolicy=tiePolicy)

    assert policy.tiePolicy == tiePolicy
    assert policy.minimumConfidence == 0.0
    assert policy.tieTolerance == 0.0


@pytest.mark.parametrize("invalidPolicy", ["earliest", "latest", "", None])
def test_FuzzificationPolicyRejectsUnknownTieModes(invalidPolicy):
    with pytest.raises(ValueError, match="unknown tie policy"):
        FuzzificationPolicy(tiePolicy=invalidPolicy)


@pytest.mark.parametrize(
    ("fieldName", "fieldValue", "expectedError"),
    [
        ("minimumConfidence", -0.1, ValueError),
        ("minimumConfidence", 1.1, ValueError),
        ("minimumConfidence", None, TypeError),
        ("tieTolerance", -0.1, ValueError),
        ("tieTolerance", 1.1, ValueError),
        ("tieTolerance", True, TypeError),
    ],
)
def test_FuzzificationPolicyRequiresMembershipGradeThresholds(
    fieldName,
    fieldValue,
    expectedError,
):
    with pytest.raises(expectedError):
        FuzzificationPolicy(**{fieldName: fieldValue})


@pytest.mark.parametrize(
    ("tiePolicy", "selectedName"),
    [("first", "Low"), ("last", "High")],
)
def test_LinguisticScaleFuzzifyAppliesOrderedSingleWinnerTiePolicies(
    tiePolicy,
    selectedName,
):
    low = LinguisticTerm("Low", _BuildMembershipSet(lambda coordinate: 0.5))
    high = LinguisticTerm("High", _BuildMembershipSet(lambda coordinate: 0.5))
    scale = LinguisticScale((low, high))

    result = scale.Fuzzify(0.5, FuzzificationPolicy(tiePolicy=tiePolicy))

    assert result.isMatch
    assert result.isTie
    assert result.confidence == 0.5
    assert result.tiedTerms == (low, high)
    assert tuple(term.name for term in result.selectedTerms) == (selectedName,)


def test_LinguisticScaleFuzzifyCanReturnEveryTiedTerm():
    low = LinguisticTerm("Low", _BuildMembershipSet(lambda coordinate: 0.5))
    medium = LinguisticTerm("Medium", _BuildMembershipSet(lambda coordinate: 0.2))
    high = LinguisticTerm("High", _BuildMembershipSet(lambda coordinate: 0.5))
    scale = LinguisticScale((low, medium, high))

    result = scale.Fuzzify(0.5, FuzzificationPolicy(tiePolicy="all"))

    assert result.tiedTerms == (low, high)
    assert result.selectedTerms == (low, high)
    assert result.memberships == (
        TermMembership(low, 0.5),
        TermMembership(medium, 0.2),
        TermMembership(high, 0.5),
    )


def test_LinguisticScaleFuzzifyUsesAbsoluteTieTolerance():
    first = LinguisticTerm("First", _BuildMembershipSet(lambda coordinate: 0.7))
    second = LinguisticTerm("Second", _BuildMembershipSet(lambda coordinate: 0.75))
    scale = LinguisticScale((first, second))

    exactResult = scale.Fuzzify(0.5, FuzzificationPolicy(tiePolicy="all"))
    tolerantResult = scale.Fuzzify(
        0.5,
        FuzzificationPolicy(tiePolicy="all", tieTolerance=0.05),
    )

    assert exactResult.tiedTerms == (second,)
    assert tolerantResult.tiedTerms == (first, second)


@pytest.mark.parametrize(("grade", "threshold"), [(0.0, 0.0), (0.01, 0.01)])
def test_LinguisticScaleFuzzifyReturnsNoMatchAtOrBelowMinimumConfidence(
    grade,
    threshold,
):
    term = LinguisticTerm("Sparse", _BuildMembershipSet(lambda coordinate: grade))
    scale = LinguisticScale((term,))

    result = scale.Fuzzify(0.5, FuzzificationPolicy(minimumConfidence=threshold))

    assert not result.isMatch
    assert not result.isTie
    assert result.confidence == grade
    assert result.tiedTerms == ()
    assert result.selectedTerms == ()
    assert result.memberships == (TermMembership(term, grade),)


def test_LinguisticScaleFuzzifyEvaluatesEveryMembershipExactlyOnce():
    callCounts = [0, 0, 0]

    def Membership(index, grade):
        """Return a counting membership callable for one declared term."""

        def Evaluate(coordinate):
            """Count and return one deterministic membership grade."""

            callCounts[index] += 1
            return grade

        return Evaluate

    terms = tuple(
        LinguisticTerm(
            f"Term {index}",
            _BuildMembershipSet(Membership(index, grade)),
        )
        for index, grade in enumerate((0.2, 0.8, 0.3))
    )

    result = LinguisticScale(terms).Fuzzify(0.5)

    assert callCounts == [1, 1, 1]
    assert result.confidence == 0.8
    assert result.selectedTerms == (terms[1],)


def test_LinguisticScaleFuzzifyRejectsInvalidPolicyAndIncompleteUniverseCoverage():
    bounded = LinguisticTerm("Bounded", _BuildMembershipSet(lambda coordinate: 1.0))
    scale = LinguisticScale((bounded,))

    with pytest.raises(TypeError, match="policy must be a FuzzificationPolicy"):
        scale.Fuzzify(0.5, policy="first")

    with pytest.raises(ValueError, match="every term universe"):
        scale.Fuzzify(2.0)


def test_ModernLinguisticTypesAreExportedFromPackageRoot():
    import fuzzyroutines

    assert fuzzyroutines.LinguisticTerm is LinguisticTerm, (
        "The modern package root must export LinguisticTerm."
    )
    assert fuzzyroutines.LinguisticScale is LinguisticScale, (
        "The modern package root must export LinguisticScale."
    )
    assert {
        "FuzzificationPolicy",
        "FuzzificationResult",
        "LinguisticTerm",
        "LinguisticScale",
        "TermMembership",
    } <= set(fuzzyroutines.__all__), (
        "The explicit modern export list must contain every linguistic contract type."
    )
    assert fuzzyroutines.FuzzificationPolicy is FuzzificationPolicy
    assert fuzzyroutines.FuzzificationResult is FuzzificationResult
    assert fuzzyroutines.TermMembership is TermMembership


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
