# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Analytical, shape, loss and failure contracts for linguistic encodings."""

import math
from dataclasses import FrozenInstanceError
from fractions import Fraction

import pytest

from fuzzyroutines import (
    Centroid,
    CentroidConvergenceError,
    CentroidPolicy,
    ContinuousUniverse,
    CreateUniversalFuzzyScale,
    DiscreteUniverse,
    FuzzificationPolicy,
    IntegrationDomain,
    LinguisticCodec,
    LinguisticScale,
    LinguisticTerm,
    ScalarFuzzySet,
    SNormPolicy,
    Triangle,
    Union,
    UniversalFuzzyScaleDomains,
    UniversalFuzzyScalePolicy,
)
from fuzzyroutines.exceptions import UndefinedResultError


def HistoricalCodec(policy=None):
    """Use the published preset, original windows and explicit winner policy."""

    return LinguisticCodec(CreateUniversalFuzzyScale(), UniversalFuzzyScaleDomains(),
                           UniversalFuzzyScalePolicy() if policy is None else policy)


def UnequalTriangleCodec():
    """Construct disjoint triangles with exact areas one and two."""

    universe = ContinuousUniverse(0, 6, leftClosed=True, rightClosed=True)
    scale = LinguisticScale((
        LinguisticTerm("Small", ScalarFuzzySet(universe, Triangle(0, 1, 2))),
        LinguisticTerm("Large", ScalarFuzzySet(universe, Triangle(2, 4, 6))),
    ))

    return LinguisticCodec(scale, (IntegrationDomain(0, 2), IntegrationDomain(2, 6)), FuzzificationPolicy())


def test_EncodingRetainsHistoricalCentroidsOrderAndFullGrades():
    """Reuse scalar results on the per-term windows without probability normalization."""

    codec = HistoricalCodec()
    assert codec.termNames == ("Min", "Low", "Med", "High", "Max")

    for term, domain in zip(codec.scale.terms, codec.integrationDomains, strict=True):
        assert codec.EncodeLabel(term.name) == Centroid(term.fuzzySet, domain)

    assert codec.EncodeLabel("Low") == pytest.approx(0.285, abs=1e-12, rel=0)
    assert codec.EncodeLabel("Med") == pytest.approx(0.5, abs=1e-12, rel=0)
    assert codec.EncodeLabel("High") == pytest.approx(0.715, abs=1e-12, rel=0)
    grades = codec.EncodeMemberships(0.17)
    assert len(grades) == 5 and 0 < sum(grades) < 0.003
    assert codec.DecodePrediction(0.75).selectedTerms[0].name == "High"

    with pytest.raises(FrozenInstanceError):
        codec.selectionPolicy = FuzzificationPolicy()


def test_PredictionDecodingRetainsNoMatchAndAllTies():
    """Preserve explicit abstention and multi-label evidence without fallback labels."""

    cautious = HistoricalCodec(FuzzificationPolicy(minimumConfidence=0.1))
    assert cautious.DecodePrediction(0.17).selectedTerms == ()
    assert cautious.EncodeMemberships(0.17) == HistoricalCodec().EncodeMemberships(0.17)
    original = UnequalTriangleCodec()
    tiedScale = LinguisticScale((original.scale.terms[0], LinguisticTerm("Twin", original.scale.terms[0].fuzzySet)))
    codec = LinguisticCodec(tiedScale, (original.integrationDomains[0],) * 2, FuzzificationPolicy(tiePolicy="all"))
    assert tuple(term.name for term in codec.DecodePrediction(1).selectedTerms) == ("Small", "Twin")
    assert codec.DecodePrediction(2).selectedTerms == ()


def test_RepresentativeAverageDiffersFromAggregatedSetCentroid():
    """Distinguish a representative mean of 2.5 from an area-weighted centroid of 3."""

    codec = UnequalTriangleCodec()
    assert codec.EncodeLabel("Small") == 1
    assert codec.EncodeLabel("Large") == 4
    assert codec.AverageRepresentatives((1, 1)) == 2.5
    assert codec.AverageRepresentatives((0.25, 0.75)) == 3.25
    assert codec.AverageRepresentatives((0.5, 0.5)) == 2.5
    combined = Union(codec.scale.terms[0].fuzzySet, codec.scale.terms[1].fuzzySet, SNormPolicy("logic"))
    # Independent triangle moments: (area 1 * centre 1 + area 2 * centre 4) / 3.
    assert Centroid(combined, IntegrationDomain(0, 6)) == pytest.approx(3, abs=1e-10, rel=0)


@pytest.mark.parametrize("grade", (math.ulp(0.0), Fraction(1, 10**1000)))
def test_RepresentativeAveragePreservesUniformlyTinyPositiveGrades(grade):
    """Keep uniformly tiny positive grades from becoming a false zero denominator."""

    assert UnequalTriangleCodec().AverageRepresentatives((grade, grade)) == 2.5
    assert UnequalTriangleCodec().AverageRepresentatives((0.0, grade)) == 4


@pytest.mark.parametrize("grade", (math.ulp(0.0), Fraction(1, 10**400)))
def test_TinyGradeRetainsRepresentableLargeCoordinateContribution(grade):
    """Preserve tiny weighted contributions that would disappear if normalized first."""

    universe = ContinuousUniverse(-1, math.nextafter(1e100, math.inf), leftClosed=True, rightClosed=True)
    scale = LinguisticScale(tuple(
        LinguisticTerm(name, ScalarFuzzySet(universe, lambda coordinate: 1))
        for name in ("ZeroA", "ZeroB", "Large")
    ))
    domains = (IntegrationDomain(-1, 1), IntegrationDomain(-1, 1), IntegrationDomain(1e100, math.nextafter(1e100, math.inf)))
    codec = LinguisticCodec(scale, domains, FuzzificationPolicy())
    centroids = tuple(Centroid(term.fuzzySet, domain) for term, domain in zip(scale.terms, domains, strict=True))
    weights = (1.0, 1.0, grade)
    expected = float(sum((Fraction(weight) * Fraction(centre) for weight, centre in zip(weights, centroids, strict=True)), Fraction(0)) / sum(map(Fraction, weights)))
    assert expected > 0, "The oracle contribution is representable despite the tiny grade."
    assert codec.AverageRepresentatives(weights) == expected


def test_CentroidEncodingIsNotAnInverseOfLinguisticDecoding():
    """Exhibit an encoded term whose centroid belongs more strongly to another term."""

    universe = ContinuousUniverse(0, 6, leftClosed=True, rightClosed=True)
    scale = LinguisticScale((
        LinguisticTerm("Wide", ScalarFuzzySet(universe, Triangle(0, 1, 6))),
        LinguisticTerm("Narrow", ScalarFuzzySet(universe, Triangle(2, 7 / 3, 3))),
    ))
    codec = LinguisticCodec(scale, (IntegrationDomain(0, 6),) * 2, FuzzificationPolicy())
    representative = codec.EncodeLabel("Wide")
    assert representative == pytest.approx(7 / 3, abs=1e-12, rel=0)
    assert codec.DecodePrediction(representative).selectedTerms[0].name == "Narrow"


@pytest.mark.parametrize("label", ("Unknown", "med", "Med ", "M", ""))
def test_UnknownLabelsFailInsteadOfEncodingAsZero(label):
    """Require complete case-sensitive labels and reject plausible numeric fallbacks."""

    with pytest.raises(ValueError, match="unknown exact linguistic label"):
        HistoricalCodec().EncodeLabel(label)


@pytest.mark.parametrize("label", (None, 0, True))
def test_LabelEncodingRejectsWrongTypes(label):
    """Keep implicit string conversion outside the label contract."""

    with pytest.raises(TypeError):
        HistoricalCodec().EncodeLabel(label)


@pytest.mark.parametrize("prediction", (-0.1, 1.1, math.nan, math.inf))
def test_PredictionsAreNeitherClampedNorSilentlyNormalized(prediction):
    """Reject invalid numeric outputs at both scalar encoding and decoding boundaries."""

    codec = HistoricalCodec()

    with pytest.raises(ValueError):
        codec.EncodeMemberships(prediction)

    with pytest.raises(ValueError):
        codec.DecodePrediction(prediction)


@pytest.mark.parametrize("prediction", (True, "0.5", [0.5], (0.5,)))
def test_ScalarOperationsRejectImplicitBatchShapes(prediction):
    """Require one real coordinate and never infer a batch dimension."""

    with pytest.raises(TypeError):
        HistoricalCodec().DecodePrediction(prediction)


@pytest.mark.parametrize("grades", ((), (0.5,), (0.5, 0.5, 0.5), (-0.1, 0.5), (1.1, 0.5), (math.nan, 0.5), (math.inf, 0.5)))
def test_RepresentativeVectorRejectsInvalidShapeAndGrades(grades):
    """Reject incomplete, oversized, non-finite and out-of-range grade vectors."""

    with pytest.raises(ValueError):
        UnequalTriangleCodec().AverageRepresentatives(grades)


@pytest.mark.parametrize("grades", ([0.5, 0.5], (True, 0.5), ("0.5", 0.5), ((0.5,), 0.5)))
def test_RepresentativeVectorRejectsImplicitContainerConversions(grades):
    """Require an explicit tuple of real grades without implicit flattening."""

    with pytest.raises(TypeError):
        UnequalTriangleCodec().AverageRepresentatives(grades)


def test_ZeroDenominatorAndActiveZeroAreaFailExplicitly():
    """Distinguish zero total grade from an undefined active centroid."""

    original = UnequalTriangleCodec()

    with pytest.raises(UndefinedResultError, match="all-zero"):
        original.AverageRepresentatives((0, 0))

    scale = LinguisticScale((original.scale.terms[0], LinguisticTerm("Zero", ScalarFuzzySet(original.scale.terms[0].fuzzySet.universe, lambda coordinate: 0))))
    codec = LinguisticCodec(scale, original.integrationDomains, original.selectionPolicy)
    assert codec.AverageRepresentatives((1, 0)) == 1

    with pytest.raises(UndefinedResultError, match="zero membership area"):
        codec.EncodeLabel("Zero")

    with pytest.raises(UndefinedResultError, match="zero membership area"):
        codec.AverageRepresentatives((0, 1))

    with pytest.raises(UndefinedResultError, match="zero membership area"):
        codec.AverageRepresentatives((1.0, Fraction(1, 10**1000)))


def test_CodecPropagatesQuadratureLimitsWithoutHiddenFallbacks():
    """Keep caller-configured centroid convergence failures visible to encoders."""

    codec = LinguisticCodec(CreateUniversalFuzzyScale(), UniversalFuzzyScaleDomains(), UniversalFuzzyScalePolicy(), CentroidPolicy(maximumDepth=0))

    with pytest.raises(CentroidConvergenceError):
        codec.EncodeLabel("Min")


@pytest.mark.parametrize(("fieldName", "value", "exception"), (
    ("scale", None, TypeError),
    ("integrationDomains", [], TypeError),
    ("integrationDomains", (), ValueError),
    ("integrationDomains", (None,) * 5, TypeError),
    ("integrationDomains", (IntegrationDomain(-1, 1),) * 5, ValueError),
    ("selectionPolicy", None, TypeError),
    ("centroidPolicy", "adaptive", TypeError),
))
def test_ConfigurationRejectsInvalidDomainAndPolicyContracts(fieldName, value, exception):
    """Validate the complete codec configuration before any numerical operation."""

    arguments = {"scale": CreateUniversalFuzzyScale(), "integrationDomains": UniversalFuzzyScaleDomains(), "selectionPolicy": UniversalFuzzyScalePolicy()}
    arguments[fieldName] = value

    with pytest.raises(exception):
        LinguisticCodec(**arguments)


def test_ContinuousRepresentativeEncodingRejectsDiscreteTerms():
    """Avoid passing a discrete universe to the continuous centroid primitive."""

    scale = LinguisticScale((LinguisticTerm("Discrete", ScalarFuzzySet(DiscreteUniverse((0, 1)), lambda coordinate: 1)),))

    with pytest.raises(TypeError, match="continuous"):
        LinguisticCodec(scale, (IntegrationDomain(0, 1),), FuzzificationPolicy())
