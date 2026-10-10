# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Contracts for immutable typed linguistic terms and ordered scales."""

import math
from dataclasses import FrozenInstanceError
from fractions import Fraction

import pytest

from fuzzyroutines import (
    ContinuousUniverse,
    DiscreteUniverse,
    FuzzificationPolicy,
    FuzzificationResult,
    IntegrationDomain,
    LinguisticScale,
    LinguisticTerm,
    ScalarFuzzySet,
    ScaleDiagnosticPoint,
    ScaleDiagnosticsPolicy,
    ScaleDiagnosticsResult,
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
    """Verify that linguistic term carries exact name and scalar fuzzy set."""

    fuzzySet = _BuildSet()
    term = LinguisticTerm("Medium", fuzzySet)

    assert term.name == "Medium", "Term construction must preserve the exact declared name."
    assert term.fuzzySet is fuzzySet, "Term construction must preserve fuzzy-set identity."


@pytest.mark.parametrize("invalidName", [None, 1, (), []])
def test_LinguisticTermRejectsNonStringNames(invalidName):
    """Verify that linguistic term rejects nonstring names."""

    with pytest.raises(TypeError, match="name must be a string"):
        LinguisticTerm(invalidName, _BuildSet())


@pytest.mark.parametrize("invalidName", ["", " ", "\t\n"])
def test_LinguisticTermRejectsEmptyNames(invalidName):
    """Verify that linguistic term rejects empty names."""

    with pytest.raises(ValueError, match="non-whitespace"):
        LinguisticTerm(invalidName, _BuildSet())


def test_LinguisticTermRejectsLegacyAndArbitraryFuzzySetValues():
    """Verify that linguistic term rejects legacy and arbitrary fuzzy set values."""

    for invalidFuzzySet in (None, object(), _BuildLegacySet()):
        with pytest.raises(TypeError, match="ScalarFuzzySet"):
            LinguisticTerm("Medium", invalidFuzzySet)


def test_LinguisticTermIsImmutable():
    """Verify that linguistic term is immutable."""

    term = LinguisticTerm("Medium", _BuildSet())

    with pytest.raises(FrozenInstanceError):
        term.name = "Changed"

    with pytest.raises(FrozenInstanceError):
        term.fuzzySet = _BuildSet(0.1)


def test_LinguisticScalePreservesExplicitTermOrderAndIdentity():
    """Verify that linguistic scale preserves explicit term order and identity."""

    low = LinguisticTerm("Low", _BuildSet())
    medium = LinguisticTerm("Medium", _BuildSet(0.1))
    high = LinguisticTerm("High", _BuildSet(0.2))
    declaredTerms = (low, medium, high)
    scale = LinguisticScale(declaredTerms)

    assert scale.terms is declaredTerms, "The ordered representation must preserve tuple identity."
    assert scale.terms == (low, medium, high), "The declared term order must remain unchanged."


def test_LinguisticScaleRequiresExplicitNonEmptyTypedTuple():
    """Verify that linguistic scale requires explicit nonempty typed tuple."""

    low = LinguisticTerm("Low", _BuildSet())

    with pytest.raises(TypeError, match="explicit tuple"):
        LinguisticScale([low])

    with pytest.raises(ValueError, match="at least one term"):
        LinguisticScale(())

    with pytest.raises(TypeError, match=r"terms\[1\]"):
        LinguisticScale((low, {"name": "High", "fSet": _BuildLegacySet()}))


def test_LinguisticScaleRejectsCaseInsensitiveNameCollisions():
    """Verify that linguistic scale rejects case insensitive name collisions."""

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
    """Verify that linguistic scale supports unicode case insensitive complete name
    lookup.
    """

    term = LinguisticTerm(declaredName, _BuildSet())
    scale = LinguisticScale((term,))

    assert scale.GetTermByName(queryName) is None, (
        "Exact lookup must preserve the declared name's case."
    )
    assert scale.GetTermByName(queryName, exactMatching=False) is term, (
        "Case-insensitive lookup must use Unicode case folding."
    )


def test_LinguisticScaleLookupNeverPerformsPartialOrApproximateMatching():
    """Verify that linguistic scale lookup never performs partial or approximate matching."""

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
    """Verify that linguistic scale lookup rejects nonstring names."""

    scale = LinguisticScale((LinguisticTerm("Low", _BuildSet()),))

    with pytest.raises(TypeError, match="termName must be a string"):
        scale.GetTermByName(invalidName)


@pytest.mark.parametrize("invalidMode", [None, 0, 1, "false"])
def test_LinguisticScaleLookupRequiresBooleanMatchingMode(invalidMode):
    """Verify that linguistic scale lookup requires boolean matching mode."""

    scale = LinguisticScale((LinguisticTerm("Low", _BuildSet()),))

    with pytest.raises(TypeError, match="exactMatching must be a boolean"):
        scale.GetTermByName("Low", exactMatching=invalidMode)


def test_LinguisticScaleIsImmutableAndContainsNoLegacyFuzzyMethod():
    """Verify that linguistic scale is immutable and contains no legacy fuzzy method."""

    scale = LinguisticScale((LinguisticTerm("Low", _BuildSet()),))

    with pytest.raises(FrozenInstanceError):
        scale.terms = ()

    assert not hasattr(scale, "Fuzzy"), "Task 82 must not preempt the deferred fuzzification policy."


@pytest.mark.parametrize("tiePolicy", ["first", "last", "all"])
def test_FuzzificationPolicyAcceptsEveryDocumentedTieMode(tiePolicy):
    """Verify that fuzzification policy accepts every documented tie mode."""

    policy = FuzzificationPolicy(tiePolicy=tiePolicy)

    assert policy.tiePolicy == tiePolicy
    assert policy.minimumConfidence == 0.0
    assert policy.tieTolerance == 0.0


@pytest.mark.parametrize("invalidPolicy", ["earliest", "latest", "", None])
def test_FuzzificationPolicyRejectsUnknownTieModes(invalidPolicy):
    """Verify that fuzzification policy rejects unknown tie modes."""

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
    """Verify that fuzzification policy requires membership grade thresholds."""

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
    """Verify that linguistic scale fuzzify applies ordered single winner tie policies."""

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
    """Verify that linguistic scale fuzzify can return every tied term."""

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
    """Verify that linguistic scale fuzzify uses absolute tie tolerance."""

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


@pytest.mark.parametrize('tiePolicy', ["first", "last", "all"])
@pytest.mark.parametrize('maximumGrade', [Fraction(1, 2), 0.5])
@pytest.mark.parametrize('maximumFirst', [False, True])
def test_LinguisticScaleFuzzifyPreservesExactRationalMaxima(
    tiePolicy,
    maximumGrade,
    maximumFirst,
):
    """Distinguish rational grades even when their float views are equal."""

    lowerGrade = Fraction(1, 2) - Fraction(1, 10**20)
    lower = LinguisticTerm("Lower", _BuildMembershipSet(lambda coordinate: lowerGrade))
    maximum = LinguisticTerm("Maximum", _BuildMembershipSet(lambda coordinate: maximumGrade))
    terms = (maximum, lower) if maximumFirst else (lower, maximum)

    result = LinguisticScale(terms).Fuzzify(0.5, FuzzificationPolicy(tiePolicy=tiePolicy))

    assert float(lowerGrade) == float(maximumGrade), "The fixture must expose float coercion loss."
    assert result.confidence is maximumGrade, "Confidence must retain the original maximum grade."
    assert result.tiedTerms == (maximum,), "Zero tolerance must exclude every unequal rational grade."
    assert result.selectedTerms == (maximum,), "Every tie policy must select the sole exact maximum."
    assert not result.isTie, "Float rounding must not create ambiguous classification evidence."


@pytest.mark.parametrize('maximumGrade', [Fraction(1, 2), 0.5])
@pytest.mark.parametrize(
    ('tieTolerance', 'includesLower'),
    [
        (Fraction(1, 10**20) - Fraction(1, 10**40), False),
        (Fraction(1, 10**20), True),
        (Fraction(1, 10**20) + Fraction(1, 10**40), True),
        (1e-21, False),
        (1e-19, True),
    ],
)
def test_LinguisticScaleFuzzifyPreservesInclusiveRationalToleranceBoundary(
    maximumGrade,
    tieTolerance,
    includesLower,
):
    """Apply exact inclusive distances to rational and mixed numeric evidence."""

    lowerGrade = Fraction(1, 2) - Fraction(1, 10**20)
    lower = LinguisticTerm("Lower", _BuildMembershipSet(lambda coordinate: lowerGrade))
    maximum = LinguisticTerm("Maximum", _BuildMembershipSet(lambda coordinate: maximumGrade))
    policy = FuzzificationPolicy(tiePolicy="all", tieTolerance=tieTolerance)

    result = LinguisticScale((lower, maximum)).Fuzzify(0.5, policy)
    expectedTerms = (lower, maximum) if includesLower else (maximum,)

    assert result.tiedTerms == expectedTerms, "Rational distance must retain the inclusive boundary."
    assert result.selectedTerms == expectedTerms, "The all policy must preserve exact tie evidence."
    assert result.policy.tieTolerance is tieTolerance, "Policy validation must not coerce tolerance."


@pytest.mark.parametrize('tiePolicy', ["first", "last", "all"])
def test_LinguisticScaleFuzzifyDistinguishesAdjacentFloatsAtZeroTolerance(tiePolicy):
    """Keep distinct adjacent floating grades distinct without caller tolerance."""

    lowerGrade = math.nextafter(0.5, 0.0)
    lower = LinguisticTerm("Lower", _BuildMembershipSet(lambda coordinate: lowerGrade))
    maximum = LinguisticTerm("Maximum", _BuildMembershipSet(lambda coordinate: 0.5))

    result = LinguisticScale((lower, maximum)).Fuzzify(
        0.5,
        FuzzificationPolicy(tiePolicy=tiePolicy),
    )

    assert result.tiedTerms == (maximum,), "Zero tolerance must preserve adjacent float differences."
    assert result.selectedTerms == (maximum,), "All selection modes must use exact zero-tolerance ties."


@pytest.mark.parametrize(
    ('lowerGrade', 'includesLower'),
    [(0.7, True), (0.7 - 1e-10, False), (0.7 + 1e-10, True)],
)
def test_LinguisticScaleFuzzifyRetainsExplicitFloatingBoundaryPolicy(
    lowerGrade,
    includesLower,
):
    """Retain rounding accommodation only at an explicitly positive float tolerance."""

    lower = LinguisticTerm("Lower", _BuildMembershipSet(lambda coordinate: lowerGrade))
    maximum = LinguisticTerm("Maximum", _BuildMembershipSet(lambda coordinate: 0.75))

    result = LinguisticScale((lower, maximum)).Fuzzify(
        0.5,
        FuzzificationPolicy(tiePolicy="all", tieTolerance=0.05),
    )
    expectedTerms = (lower, maximum) if includesLower else (maximum,)

    assert result.tiedTerms == expectedTerms, "Float rounding must not replace the caller's tolerance."


def test_FuzzificationResultRejectsRationalGradesCollapsedIntoFalseTies():
    """Reject supplied tie evidence that contradicts exact rational memberships."""

    lowerGrade = Fraction(1, 2) - Fraction(1, 10**20)
    maximumGrade = Fraction(1, 2)
    lower = LinguisticTerm("Lower", _BuildMembershipSet(lambda coordinate: lowerGrade))
    maximum = LinguisticTerm("Maximum", _BuildMembershipSet(lambda coordinate: maximumGrade))
    memberships = (TermMembership(lower, lowerGrade), TermMembership(maximum, maximumGrade))

    with pytest.raises(ValueError, match="tiedTerms do not match"):
        FuzzificationResult(
            memberships,
            maximumGrade,
            FuzzificationPolicy(),
            (lower, maximum),
            (lower,),
        )


@pytest.mark.parametrize(("grade", "threshold"), [(0.0, 0.0), (0.01, 0.01)])
def test_LinguisticScaleFuzzifyReturnsNoMatchAtOrBelowMinimumConfidence(
    grade,
    threshold,
):
    """Verify that linguistic scale fuzzify returns no match at or below minimum
    confidence.
    """

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
    """Verify that linguistic scale fuzzify evaluates every membership exactly once."""

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
    """Verify that linguistic scale fuzzify rejects invalid policy and incomplete universe
    coverage.
    """

    bounded = LinguisticTerm("Bounded", _BuildMembershipSet(lambda coordinate: 1.0))
    scale = LinguisticScale((bounded,))

    with pytest.raises(TypeError, match="policy must be a FuzzificationPolicy"):
        scale.Fuzzify(0.5, policy="first")

    with pytest.raises(ValueError, match="every term universe"):
        scale.Fuzzify(2.0)


@pytest.mark.parametrize(
    ("arguments", "expectedError"),
    [
        ({"sampleCount": True}, TypeError),
        ({"sampleCount": 2.5}, TypeError),
        ({"sampleCount": 1}, ValueError),
        ({"membershipThreshold": -0.01}, ValueError),
        ({"membershipThreshold": 1.01}, ValueError),
        ({"partitionTolerance": -1e-12}, ValueError),
        ({"partitionTolerance": float("inf")}, ValueError),
    ],
)
def test_ScaleDiagnosticsPolicyRejectsInvalidGridAndTolerances(
    arguments,
    expectedError,
):
    """Verify that scale diagnostics policy rejects invalid grid and tolerances."""

    with pytest.raises(expectedError):
        ScaleDiagnosticsPolicy(**arguments)


def test_LinguisticScaleDiagnoseReportsCoverageOverlapAndPartitionMetrics():
    """Verify that linguistic scale diagnose reports coverage overlap and partition
    metrics.
    """

    universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
    low = LinguisticTerm("Low", ScalarFuzzySet(universe, lambda coordinate: 1.0 - coordinate))
    high = LinguisticTerm("High", ScalarFuzzySet(universe, lambda coordinate: coordinate))
    scale = LinguisticScale((low, high))

    result = scale.Diagnose(
        IntegrationDomain(0.0, 1.0),
        ScaleDiagnosticsPolicy(sampleCount=5),
    )

    assert tuple(point.coordinate for point in result.points) == (0.0, 0.25, 0.5, 0.75, 1.0)
    assert tuple(point.maximumMembership for point in result.points) == (
        1.0,
        0.75,
        0.5,
        0.75,
        1.0,
    )
    assert result.gapPoints == (), "A complementary two-term partition must have no sampled gaps."
    assert tuple(point.coordinate for point in result.overlapPoints) == (0.25, 0.5, 0.75)
    assert result.gapFraction == 0.0
    assert result.overlapFraction == 0.6
    assert result.minimumCoverage == 0.5
    assert result.meanCoverage == 0.8
    assert result.maximumCoverage == 1.0
    assert result.maximumActiveTermCount == 2
    assert result.meanPartitionError == 0.0
    assert result.maximumPartitionError == 0.0
    assert result.isPartitionWithinTolerance


def test_LinguisticScaleDiagnoseUsesOneStrictThresholdForGapsAndOverlaps():
    """Verify that linguistic scale diagnose uses one strict threshold for gaps and
    overlaps.
    """

    first = LinguisticTerm("First", _BuildMembershipSet(lambda coordinate: 0.05))
    second = LinguisticTerm("Second", _BuildMembershipSet(lambda coordinate: 0.04))
    scale = LinguisticScale((first, second))
    analysisDomain = IntegrationDomain(0.0, 1.0)

    overlapResult = scale.Diagnose(
        analysisDomain,
        ScaleDiagnosticsPolicy(sampleCount=3, membershipThreshold=0.0),
    )
    gapResult = scale.Diagnose(
        analysisDomain,
        ScaleDiagnosticsPolicy(sampleCount=3, membershipThreshold=0.05),
    )

    assert all(point.isOverlap for point in overlapResult.points)
    assert all(point.isGap for point in gapResult.points)
    assert overlapResult.overlapFraction == 1.0
    assert gapResult.gapFraction == 1.0


def test_LinguisticScaleDiagnoseFindsAnExplicitSampledCoverageGap():
    """Verify that linguistic scale diagnose finds an explicit sampled coverage gap."""

    low = LinguisticTerm(
        "Low",
        _BuildMembershipSet(lambda coordinate: max(0.0, 1.0 - 2.0 * coordinate)),
    )
    high = LinguisticTerm(
        "High",
        _BuildMembershipSet(lambda coordinate: max(0.0, 2.0 * coordinate - 1.0)),
    )

    result = LinguisticScale((low, high)).Diagnose(
        IntegrationDomain(0.0, 1.0),
        ScaleDiagnosticsPolicy(sampleCount=5),
    )

    assert tuple(point.coordinate for point in result.gapPoints) == (0.5,)
    assert result.minimumCoverage == 0.0
    assert result.gapFraction == 0.2
    assert not result.isPartitionWithinTolerance


def test_LinguisticScaleDiagnoseIsReproducibleAndEvaluatesEachTermOncePerPoint():
    """Verify that linguistic scale diagnose is reproducible and evaluates each term once
    per point.
    """

    callCounts = [0, 0]

    def Membership(termIndex):
        """Return one deterministic counting membership callable."""

        def Evaluate(coordinate):
            """Record one evaluation and return a stable affine grade."""

            callCounts[termIndex] += 1
            return coordinate if termIndex else 1.0 - coordinate

        return Evaluate

    scale = LinguisticScale(
        tuple(
            LinguisticTerm(f"Term {termIndex}", _BuildMembershipSet(Membership(termIndex)))
            for termIndex in range(2)
        )
    )
    policy = ScaleDiagnosticsPolicy(sampleCount=7)
    analysisDomain = IntegrationDomain(0.0, 1.0)

    firstResult = scale.Diagnose(analysisDomain, policy)
    assert callCounts == [7, 7], "Every term must be evaluated once per declared grid point."

    callCounts[:] = [0, 0]
    secondResult = scale.Diagnose(analysisDomain, policy)

    assert callCounts == [7, 7]
    assert firstResult == secondResult, "The declared domain, grid, and tolerance must reproduce."


def test_LinguisticScaleDiagnoseRejectsUnsupportedDomainsAndUniverses():
    """Verify that linguistic scale diagnose rejects unsupported domains and universes."""

    continuousScale = LinguisticScale((LinguisticTerm("Bounded", _BuildSet()),))
    discreteTerm = LinguisticTerm(
        "Discrete",
        ScalarFuzzySet(DiscreteUniverse((0.0, 1.0)), lambda coordinate: coordinate),
    )

    with pytest.raises(TypeError, match="analysisDomain must be an IntegrationDomain"):
        continuousScale.Diagnose((0.0, 1.0))

    with pytest.raises(TypeError, match="policy must be a ScaleDiagnosticsPolicy"):
        continuousScale.Diagnose(IntegrationDomain(0.0, 1.0), policy="dense")

    with pytest.raises(ValueError, match="integration domain must lie entirely"):
        continuousScale.Diagnose(IntegrationDomain(-1.0, 1.0))

    with pytest.raises(TypeError, match="ContinuousUniverse"):
        LinguisticScale((discreteTerm,)).Diagnose(IntegrationDomain(0.0, 1.0))


def test_LinguisticScaleDiagnoseDoesNotModifyMembershipCoefficients():
    """Verify that linguistic scale diagnose does not modify membership coefficients."""

    membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
    originalParameters = dict(membershipFunction.parameters)
    universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
    term = LinguisticTerm(
        "Triangle",
        ScalarFuzzySet(universe, membershipFunction.mju),
    )

    LinguisticScale((term,)).Diagnose(
        IntegrationDomain(0.0, 1.0),
        ScaleDiagnosticsPolicy(sampleCount=11),
    )

    assert membershipFunction.parameters == originalParameters, (
        "Scale diagnostics must observe analytical coefficients without modifying them."
    )


def test_ModernLinguisticTypesAreExportedFromPackageRoot():
    """Verify that modern linguistic types are exported from package root."""

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
        "ScaleDiagnosticPoint",
        "ScaleDiagnosticsPolicy",
        "ScaleDiagnosticsResult",
        "TermMembership",
    } <= set(fuzzyroutines.__all__), (
        "The explicit modern export list must contain every linguistic contract type."
    )
    assert fuzzyroutines.FuzzificationPolicy is FuzzificationPolicy
    assert fuzzyroutines.FuzzificationResult is FuzzificationResult
    assert fuzzyroutines.ScaleDiagnosticPoint is ScaleDiagnosticPoint
    assert fuzzyroutines.ScaleDiagnosticsPolicy is ScaleDiagnosticsPolicy
    assert fuzzyroutines.ScaleDiagnosticsResult is ScaleDiagnosticsResult
    assert fuzzyroutines.TermMembership is TermMembership


def test_LegacyFuzzyScaleLevelsRemainMutableDictionaries():
    """Verify that legacy fuzzy scale levels remain mutable dictionaries."""

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
    """Verify that legacy fuzzy scale requires both exact level keys."""

    scale = FuzzyScale()

    with pytest.raises(Exception, match="2-dim dictionary"):
        scale.levels = [invalidLevel]


@pytest.mark.parametrize(("firstName", "secondName"), [("Low", "LOW"), ("i", "ı")])
def test_LegacyFuzzyScaleRejectsCaseInsensitiveNameCollisions(firstName, secondName):
    """Verify that legacy fuzzy scale rejects case insensitive name collisions."""

    scale = FuzzyScale()

    with pytest.raises(ValueError, match="not unique ignoring case"):
        scale.levels = [
            {"name": firstName, "fSet": _BuildLegacySet()},
            {"name": secondName, "fSet": _BuildLegacySet()},
        ]


def test_LegacyFuzzyScaleLookupPreservesExactAndCaseInsensitiveModes():
    """Verify that legacy fuzzy scale lookup preserves exact and case insensitive modes."""

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
