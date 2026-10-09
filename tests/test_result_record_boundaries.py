# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Reject contradictory reconstructed evidence at public mathematical boundaries."""

from dataclasses import replace
from math import isclose, pi, sqrt

import pytest

from fuzzyroutines import (
    Centroid,
    CentroidPolicy,
    ComparisonDomain,
    ComparisonPolicy,
    Complement,
    ContinuousInterval,
    ContinuousRegion,
    ContinuousUniverse,
    DeriveProperties,
    DiscreteRegion,
    DiscreteUniverse,
    EqualOnDomain,
    FuzzificationPolicy,
    Gaussian,
    Height,
    IntegrationDomain,
    Intersection,
    LinguisticScale,
    LinguisticTerm,
    MembershipFunction,
    NegationPolicy,
    Normalize,
    SampleAlphaCut,
    SampleProperties,
    ScalarFuzzySet,
    ScaleDiagnosticsPolicy,
    TermMembership,
    TNormPolicy,
    Triangle,
)
from fuzzyroutines.exceptions import UndefinedResultError
from fuzzyroutines.FuzzyRoutines import FuzzyScale, FuzzySet, MFunction


@pytest.fixture(name="records")
def ResultRecords():
    """Construct consistent evidence from one independently understood unit triangle."""

    model = Triangle(0, 1, 2)
    universe = ContinuousUniverse(0, 2, leftClosed=True, rightClosed=True)
    domain = IntegrationDomain(0, 2)
    fuzzySet = ScalarFuzzySet(universe, model)
    term = LinguisticTerm("Peak", fuzzySet)
    scale = LinguisticScale((term,))
    diagnostics = scale.Diagnose(domain, ScaleDiagnosticsPolicy(sampleCount=3))
    return {
        "continuous": DeriveProperties(model, universe),
        "discrete": DeriveProperties(model, DiscreteUniverse((0, 1, 2))),
        "sampled": SampleProperties(model, domain, sampleCount=3),
        "cut": SampleAlphaCut(fuzzySet, 0.5, domain, sampleCount=3),
        "classification": scale.Fuzzify(1),
        "point": diagnostics.points[1],
        "diagnostics": diagnostics,
    }


@pytest.mark.parametrize(("recordKey", "changes", "error"), (
    ("continuous", {"universe": object()}, TypeError),
    ("continuous", {"core": object()}, TypeError),
    ("continuous", {"core": ContinuousRegion((ContinuousInterval(3, 4),))}, ValueError),
    ("continuous", {"height": 1.1}, ValueError),
    ("discrete", {"universe": object()}, TypeError),
    ("discrete", {"boundary": object()}, TypeError),
    ("discrete", {"core": DiscreteRegion((3,))}, ValueError),
    ("discrete", {"height": -0.1}, ValueError),
    ("sampled", {"analysisDomain": object()}, TypeError),
    ("sampled", {"sampleCount": True}, TypeError),
    ("sampled", {"sampleCount": 1}, ValueError),
    ("sampled", {"coordinates": [0, 1, 2]}, TypeError),
    ("sampled", {"grades": (0, 1)}, ValueError),
    ("sampled", {"coordinates": (0, 0, 2)}, ValueError),
    ("sampled", {"coordinates": (0.5, 1, 2)}, ValueError),
    ("sampled", {"coreSamples": object()}, TypeError),
    ("sampled", {"coreSamples": DiscreteRegion((0.5,))}, ValueError),
    ("sampled", {"heightEstimate": 0.5}, ValueError),
    ("sampled", {"method": ""}, TypeError),
    ("cut", {"analysisDomain": object()}, TypeError),
    ("cut", {"grades": [0, 1, 0]}, TypeError),
    ("cut", {"grades": (0, 1)}, ValueError),
    ("cut", {"coordinates": (0, 0, 2)}, ValueError),
    ("cut", {"coordinates": (0, 1, 1.5)}, ValueError),
    ("cut", {"cutSamples": object()}, TypeError),
    ("cut", {"cutSamples": DiscreteRegion((0, 1))}, ValueError),
    ("cut", {"method": "arbitrary"}, ValueError),
    ("classification", {"memberships": ()}, TypeError),
    ("classification", {"memberships": (object(),)}, TypeError),
    ("classification", {"policy": object()}, TypeError),
    ("classification", {"confidence": 0.5}, ValueError),
    ("classification", {"selectedTerms": ()}, ValueError),
    ("point", {"coordinate": True}, TypeError),
    ("point", {"coordinate": float("inf")}, ValueError),
    ("point", {"memberships": []}, TypeError),
    ("point", {"memberships": (object(),)}, TypeError),
    ("diagnostics", {"analysisDomain": object()}, TypeError),
    ("diagnostics", {"policy": object()}, TypeError),
    ("diagnostics", {"points": []}, TypeError),
    ("diagnostics", {"points": ()}, ValueError),
    ("diagnostics", {"points": (object(),) * 3}, TypeError),
))
def test_ReconstructedRecordsRejectInconsistentTypesGeometryAndEvidence(records, recordKey, changes, error):
    """Public constructors cannot accept contradictory metadata or fabricated cut points."""

    with pytest.raises(error):
        replace(records[recordKey], **changes)


@pytest.mark.parametrize("problem", ("start", "end", "order", "threshold", "terms"))
def test_DiagnosticsPreserveGridEndpointsOrderThresholdAndTermIdentity(records, problem):
    """Reconstructed diagnostics must preserve the same domain and measurement contract."""

    result = records["diagnostics"]
    first, middle, last = result.points
    alternatives = {
        "start": (replace(first, coordinate=0.25), middle, last),
        "end": (first, middle, replace(last, coordinate=1.75)),
        "order": (first, replace(middle, coordinate=-1), last),
        "threshold": (first, replace(middle, membershipThreshold=0.5), last),
        "terms": (first, replace(middle, memberships=(TermMembership(LinguisticTerm("Other", middle.memberships[0].term.fuzzySet), 1),)), last),
    }

    with pytest.raises(ValueError):
        replace(result, points=alternatives[problem])


@pytest.mark.parametrize("case", (
    lambda: ContinuousInterval(0, 1, leftClosed=1),
    lambda: ContinuousInterval(0, None, rightClosed=True),
    lambda: ContinuousRegion([]),
    lambda: ContinuousRegion((object(),)),
    lambda: ContinuousRegion((ContinuousInterval(0, None), ContinuousInterval(1, 2))),
    lambda: ContinuousRegion((ContinuousInterval(0, 2), ContinuousInterval(1, 3))),
    lambda: ContinuousRegion((ContinuousInterval(0, 1, rightClosed=True), ContinuousInterval(1, 2, leftClosed=True))),
    lambda: DiscreteRegion([0, 1]),
    lambda: DiscreteRegion((1, 1)),
    lambda: ContinuousUniverse(0, 1, leftClosed=1),
    lambda: FuzzificationPolicy(tieTolerance=True),
    lambda: ScaleDiagnosticsPolicy(membershipThreshold=True),
    lambda: TermMembership(object(), 0.5),
    lambda: MembershipFunction("unknown"),
    lambda: CentroidPolicy(relativeTolerance=0),
))
def test_InvalidRegionsAndPoliciesFailAtConstruction(case):
    """Invalid topology, ambiguous Booleans and unsupported families fail explicitly."""

    with pytest.raises((TypeError, ValueError)):
        case()


@pytest.mark.parametrize("sigma", (1.0, 1e-100))
def test_GaussianHalfLineLimitHasAnIndependentClosedFormCentroid(sigma):
    """An extreme finite half-window approaches the exact half-normal first moment."""

    fuzzySet = ScalarFuzzySet(ContinuousUniverse(), Gaussian(0, sigma))
    result = Centroid(fuzzySet, IntegrationDomain(-1e300, 0))
    assert isclose(result, -sigma * sqrt(2 / pi), rel_tol=2e-15)


def test_UnrepresentablySmallGaussianMassFailsInsteadOfInventingACentroid():
    """Remote positive mathematical support can have zero representable integration mass."""

    fuzzySet = ScalarFuzzySet(ContinuousUniverse(), Gaussian(0, 1))

    with pytest.raises(UndefinedResultError):
        Centroid(fuzzySet, IntegrationDomain(500, 501))


@pytest.mark.parametrize("operation", (
    lambda fuzzySet: Centroid(object(), IntegrationDomain(0, 2)),
    lambda fuzzySet: Centroid(fuzzySet, object()),
    lambda fuzzySet: Centroid(fuzzySet, IntegrationDomain(0, 2), object()),
    lambda fuzzySet: ScalarFuzzySet(object(), Triangle(0, 1, 2)),
    lambda fuzzySet: ScalarFuzzySet(fuzzySet.universe, object()),
    lambda fuzzySet: Complement(object(), NegationPolicy("standard")),
    lambda fuzzySet: Intersection(fuzzySet, object(), TNormPolicy("logic")),
    lambda fuzzySet: SampleAlphaCut(fuzzySet, 0.5, object()),
    lambda fuzzySet: SampleProperties(object(), IntegrationDomain(0, 2)),
    lambda fuzzySet: SampleProperties(Triangle(0, 1, 2), object()),
    lambda fuzzySet: DeriveProperties(object(), fuzzySet.universe),
    lambda fuzzySet: ComparisonDomain((0, 1)).ValidateWithin(DiscreteUniverse((0, 1))),
    lambda fuzzySet: EqualOnDomain(fuzzySet, fuzzySet, ComparisonPolicy("exact"), object()),
))
def test_PublicOperationsRejectObjectsWithoutTheirDeclaredContracts(operation):
    """Wrong object types must fail at the boundary before mathematical evaluation."""

    fuzzySet = ScalarFuzzySet(ContinuousUniverse(0, 2), Triangle(0, 1, 2))

    with pytest.raises(TypeError):
        operation(fuzzySet)


def test_ContinuousRenormalizationPreservesGradesAndRejectsAnEmptyRestriction():
    """Height-one evidence is reusable only on its original universe."""

    normalized = Normalize(ScalarFuzzySet(ContinuousUniverse(0, 2), Triangle(0, 1, 2)))
    repeated = Normalize(normalized)
    assert [repeated.Membership(point) for point in (0.25, 1, 1.75)] == [0.25, 1, 0.25]

    restricted = ScalarFuzzySet(ContinuousUniverse(3, 4), normalized.membershipFunction)
    with pytest.raises(UndefinedResultError, match="zero-height"):
        Normalize(restricted)


def test_ContinuousNormalizedModelUsesExhaustiveHeightOnADiscreteUniverse():
    """Changing the universe must replace continuous maximum evidence with enumeration."""

    normalized = Normalize(ScalarFuzzySet(ContinuousUniverse(0, 2), Triangle(0, 1, 2)))
    discreteSet = ScalarFuzzySet(DiscreteUniverse((0.25, 1.5)), normalized.membershipFunction)
    assert Height(discreteSet) == 0.5


def test_HistoricalRepresentationsRetainNamesParametersAndEveryLevel():
    """Readable compatibility representations include every declared scale level."""

    assert str(MFunction("desirability")) == "Desirability(y)"
    scale = FuzzyScale()
    text = str(scale)
    assert "DefaultScale = {Min, Med, High}" in text
    assert all(str(level["fSet"]) in text for level in scale.levels)
    assert '"a": 7' in text
    scale.levels = [scale.levels[0]]
    assert "{Min}" in str(scale)


@pytest.mark.parametrize("problem", ("scaleName", "emptyLevels", "levelName", "levelSet", "setName", "setModel", "construction"))
def test_HistoricalMutationRejectsInvalidPublicValues(problem):
    """Preserve historical errors for malformed mutable scale and set inputs."""

    scale = FuzzyScale()
    fuzzySet = scale.levels[0]["fSet"]
    operations = {
        "scaleName": lambda: setattr(scale, "name", 0),
        "emptyLevels": lambda: setattr(scale, "levels", []),
        "levelName": lambda: setattr(scale, "levels", [{"name": 1, "fSet": fuzzySet}]),
        "levelSet": lambda: setattr(scale, "levels", [{"name": "bad", "fSet": object()}]),
        "setName": lambda: setattr(fuzzySet, "name", 0),
        "setModel": lambda: setattr(fuzzySet, "mFunction", object()),
        "construction": lambda: FuzzySet(object()),
    }
    with pytest.raises(Exception, match="string value|at least one|instance|Not MFunction"):
        operations[problem]()
