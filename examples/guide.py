# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Run nine worked scalar scenarios with independent numerical assertions.

The default executes every scenario and prints deterministic JSON. Use
``--scenario NAME`` to select one. No files, network, plotting packages, or
optional numerical dependencies are used. Install FuzzyRoutines first; the
script is also executed with isolated Python against wheel/sdist installs in CI.
"""

import argparse
import json
from itertools import pairwise
from math import fsum, isclose

from fuzzyroutines import (
    AlphaCut,
    Bell,
    Centroid,
    ComparisonPolicy,
    Complement,
    ContinuousUniverse,
    DeriveProperties,
    Difference,
    DiscreteUniverse,
    EqualOnDomain,
    FuzzificationPolicy,
    Height,
    Hyperbolic,
    IncludedOnDomain,
    IntegrationDomain,
    Intersection,
    LinguisticScale,
    LinguisticTerm,
    MembershipScalar,
    NegationPolicy,
    Normalize,
    SampleAlphaCut,
    ScalarFuzzySet,
    ScaleDiagnosticsPolicy,
    SNormPolicy,
    SShoulder,
    TNormPolicy,
    Triangle,
    Union,
)
from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale


def ClosedUniverse(left: float, right: float) -> ContinuousUniverse:
    """Declare a finite physical range including both endpoints."""

    return ContinuousUniverse(left, right, leftClosed=True, rightClosed=True)


def ComfortScale() -> LinguisticScale:
    """Build illustrative expert-defined temperature labels in degrees Celsius."""

    universe = ClosedUniverse(0, 40)
    return LinguisticScale((
        LinguisticTerm("Comfort", ScalarFuzzySet(universe, Triangle(16, 22, 28))),
        LinguisticTerm("Warm", ScalarFuzzySet(universe, SShoulder(22, 30))),
    ))


def RiskScale() -> LinguisticScale:
    """Define linguistic labels for an illustrative severity score, not probability."""

    universe = ClosedUniverse(0, 100)
    return LinguisticScale((
        LinguisticTerm("Low", ScalarFuzzySet(universe, Triangle(0, 20, 50))),
        LinguisticTerm("Moderate", ScalarFuzzySet(universe, Triangle(25, 50, 75))),
        LinguisticTerm("High", ScalarFuzzySet(universe, SShoulder(50, 90))),
    ))


def AlarmSets() -> tuple[ScalarFuzzySet, ScalarFuzzySet]:
    """Define warning and critical temperature models on the same universe."""

    universe = ClosedUniverse(40, 120)
    return (
        ScalarFuzzySet(universe, SShoulder(60, 100)),
        ScalarFuzzySet(universe, SShoulder(90, 110)),
    )


def AuditScale(gappy: bool = False) -> LinguisticScale:
    """Build intentionally overlapping or gappy models for a design audit."""

    universe = ClosedUniverse(0, 10)
    leftParameters = (0, 2, 4) if gappy else (0, 2, 6)
    rightParameters = (6, 8, 10) if gappy else (4, 8, 10)
    return LinguisticScale((
        LinguisticTerm("Low", ScalarFuzzySet(universe, Triangle(*leftParameters))),
        LinguisticTerm("High", ScalarFuzzySet(universe, Triangle(*rightParameters))),
    ))


def RisingQuality(coordinate: MembershipScalar) -> MembershipScalar:
    """Map a declared quality score in [0, 100] to a linear membership grade."""

    return coordinate / 100


def CheckClose(observed: float, expected: float, tolerance: float = 1e-9) -> None:
    """Check a numerical oracle with an explicit absolute and relative tolerance."""

    assert isclose(observed, expected, abs_tol=tolerance, rel_tol=tolerance), (
        observed, expected
    )


def TemperatureComfort() -> dict:
    """Measure 24 degrees against two labels and verify the selected term."""

    result = ComfortScale().Fuzzify(24)
    grades = {item.term.name: item.grade for item in result.memberships}
    CheckClose(grades["Comfort"], 2 / 3)
    CheckClose(grades["Warm"], 1 / 8)
    assert tuple(term.name for term in result.selectedTerms) == ("Comfort",)
    return {"temperatureC": 24, "grades": grades, "selected": "Comfort"}


def RiskAbstention() -> dict:
    """Compare default classification with an explicit abstention threshold."""

    scale = RiskScale()
    result = scale.Fuzzify(65)
    cautiousResult = scale.Fuzzify(65, FuzzificationPolicy(minimumConfidence=0.45))
    grades = {item.term.name: item.grade for item in result.memberships}
    CheckClose(grades["Moderate"], 0.4)
    CheckClose(grades["High"], 0.28125)
    assert result.selectedTerms[0].name == "Moderate"
    assert not cautiousResult.isMatch
    return {
        "severityScore": 65,
        "grades": grades,
        "defaultSelected": "Moderate",
        "minimumConfidence": 0.45,
        "cautiousIsMatch": cautiousResult.isMatch,
    }


def SensorCriteria() -> dict:
    """Combine two different physical measurements as scalar membership grades."""

    temperatureGrade = SShoulder(60, 100)(80)
    vibrationGrade = Triangle(0, 8, 16)(10)
    results = {
        "temperatureC": 80,
        "vibrationMmPerS": 10,
        "temperatureGrade": temperatureGrade,
        "vibrationGrade": vibrationGrade,
        "logicAnd": TNormPolicy("logic").Evaluate(temperatureGrade, vibrationGrade),
        "productAnd": TNormPolicy("algebraic").Evaluate(temperatureGrade, vibrationGrade),
        "logicOr": SNormPolicy("logic").Evaluate(temperatureGrade, vibrationGrade),
        "algebraicOr": SNormPolicy("algebraic").Evaluate(temperatureGrade, vibrationGrade),
    }
    for name, expected in (
        ("temperatureGrade", 0.5), ("vibrationGrade", 0.75),
        ("logicAnd", 0.5), ("productAnd", 0.375),
        ("logicOr", 0.75), ("algebraicOr", 0.875),
    ):
        CheckClose(results[name], expected)
    return results


def MaintenanceAlarm() -> dict:
    """Evaluate warning AND NOT critical without treating fuzzy difference as subtraction."""

    warning, critical = AlarmSets()
    negation = NegationPolicy("standard")
    conjunction = TNormPolicy("logic")
    difference = Difference(warning, critical, conjunction, negation)
    overlap = Intersection(warning, critical, conjunction)
    either = Union(warning, critical, SNormPolicy("logic"))
    noncritical = Complement(critical, negation)
    coordinate = 100
    results = {
        "temperatureC": coordinate,
        "warning": warning.Membership(coordinate),
        "critical": critical.Membership(coordinate),
        "warningWithoutCritical": difference.Membership(coordinate),
        "both": overlap.Membership(coordinate),
        "either": either.Membership(coordinate),
        "noncritical": noncritical.Membership(coordinate),
    }
    for name, expected in (
        ("warning", 1), ("critical", 0.5), ("warningWithoutCritical", 0.5),
        ("both", 0.5), ("either", 1), ("noncritical", 0.5),
    ):
        CheckClose(results[name], expected)
    return results


def QualityAlphaCuts() -> dict:
    """Distinguish exhaustive discrete cuts, sampled cuts, and analytical geometry."""

    membershipFunction = Triangle(10, 12, 14)
    discreteSet = ScalarFuzzySet(DiscreteUniverse((10, 11, 12, 13, 14)), membershipFunction)
    exactCut = AlphaCut(discreteSet, 0.5)
    assert exactCut.points == (11, 12, 13)
    assert AlphaCut(discreteSet, 0).points == discreteSet.universe.points
    assert AlphaCut(discreteSet, 1).points == (12,)
    universe = ClosedUniverse(10, 14)
    continuousSet = ScalarFuzzySet(universe, membershipFunction)
    sampledCut = SampleAlphaCut(continuousSet, 0.5, IntegrationDomain(10, 14), sampleCount=9)
    properties = DeriveProperties(membershipFunction, universe)
    assert sampledCut.cutSamples.points == (11, 11.5, 12, 12.5, 13)
    assert not sampledCut.isExact and properties.isExact
    assert not properties.positiveSupport.Contains(10)
    assert properties.supportClosure.Contains(10)
    assert properties.core.Contains(12)
    return {
        "alpha": 0.5,
        "discreteCut": exactCut.points,
        "sampledCut": sampledCut.cutSamples.points,
        "sampleCount": sampledCut.sampleCount,
        "sampledIsExact": sampledCut.isExact,
        "analyticalSupport": "(10, 14)",
        "supportClosure": "[10, 14]",
        "core": [12],
    }


def GridCentroid(fuzzySet: ScalarFuzzySet, coordinates: tuple[float, ...]) -> float:
    """Illustrate user-side trapezoidal moments, separately from library Centroid."""

    grades = tuple(fuzzySet.Membership(coordinate) for coordinate in coordinates)
    area = fsum(
        (right - left) * (leftGrade + rightGrade) / 2
        for (left, right), (leftGrade, rightGrade) in zip(pairwise(coordinates), pairwise(grades), strict=True)
    )
    moment = fsum(
        (right - left) * (left * leftGrade + right * rightGrade) / 2
        for (left, right), (leftGrade, rightGrade) in zip(pairwise(coordinates), pairwise(grades), strict=True)
    )
    return moment / area


def CentroidAndSampling() -> dict:
    """Check exact triangle and adaptive composite centroids against area moments."""

    triangle = ScalarFuzzySet(ClosedUniverse(0, 8), Triangle(0, 2, 8))
    centroid = Centroid(triangle, IntegrationDomain(0, 8))
    coarseCentroid = GridCentroid(triangle, (0, 8 / 3, 16 / 3, 8))
    CheckClose(centroid, 10 / 3)
    CheckClose(coarseCentroid, 32 / 9)
    universe = ClosedUniverse(0, 10)
    left = ScalarFuzzySet(universe, Triangle(0, 1, 3))
    right = ScalarFuzzySet(universe, Triangle(4, 6, 10))
    combined = Union(left, right, SNormPolicy("logic"))
    combinedCentroid = Centroid(combined, IntegrationDomain(0, 10))
    # Disjoint areas 3/2 and 3; their first moments are 2 and 20.
    CheckClose(combinedCentroid, 44 / 9)
    return {
        "triangleCentroid": centroid,
        "independentTriangleOracle": 10 / 3,
        "fourPointTrapezoidalCentroid": coarseCentroid,
        "coarseAbsoluteError": abs(coarseCentroid - centroid),
        "compositeCentroid": combinedCentroid,
        "independentCompositeOracle": 44 / 9,
    }


def ScaleAudit() -> dict:
    """Expose a tie, abstention, and sampled gaps without asserting global coverage."""

    scale = AuditScale()
    tied = scale.Fuzzify(5, FuzzificationPolicy(tiePolicy="all"))
    assert tied.isTie and len(tied.selectedTerms) == 2
    CheckClose(tied.confidence, 0.25)
    assert scale.Fuzzify(5).selectedTerms[0].name == "Low"
    assert not scale.Fuzzify(5, FuzzificationPolicy(minimumConfidence=0.3)).isMatch
    domain = IntegrationDomain(0, 10)
    policy = ScaleDiagnosticsPolicy(sampleCount=11)
    overlapping = scale.Diagnose(domain, policy)
    gappyScale = AuditScale(gappy=True)
    gappy = gappyScale.Diagnose(domain, policy)
    assert not gappyScale.Fuzzify(5).isMatch
    assert tuple(point.coordinate for point in gappy.gapPoints) == (0, 4, 5, 6, 10)
    CheckClose(gappy.gapFraction, 5 / 11)
    return {
        "tieCoordinate": 5,
        "tiedTerms": [term.name for term in tied.selectedTerms],
        "confidence": tied.confidence,
        "overlapSamples": [point.coordinate for point in overlapping.overlapPoints],
        "gapSamples": [point.coordinate for point in gappy.gapPoints],
        "gapFraction": gappy.gapFraction,
        "analysisDomain": [0, 10],
        "sampleCount": policy.sampleCount,
    }


def CustomModel() -> dict:
    """Integrate a typed callable, then normalize and compare a discrete model."""

    continuousSet = ScalarFuzzySet(ClosedUniverse(0, 100), RisingQuality)
    CheckClose(continuousSet.Membership(75), 0.75)
    centroid = Centroid(continuousSet, IntegrationDomain(0, 100))
    CheckClose(centroid, 200 / 3)
    discreteSet = ScalarFuzzySet(DiscreteUniverse((0, 25, 50)), RisingQuality)
    normalized = Normalize(discreteSet)
    grades = tuple(normalized.Membership(coordinate) for coordinate in discreteSet.universe.points)
    assert grades == (0, 0.5, 1)
    assert Height(discreteSet) == 0.5 and Height(normalized) == 1
    policy = ComparisonPolicy("exact")
    assert IncludedOnDomain(discreteSet, normalized, policy)
    assert not EqualOnDomain(discreteSet, normalized, policy)
    return {
        "continuousCentroid": centroid,
        "independentIntegralOracle": 200 / 3,
        "discreteCoordinates": discreteSet.universe.points,
        "originalGrades": [discreteSet.Membership(coordinate) for coordinate in discreteSet.universe.points],
        "normalizedGrades": grades,
        "originalHeight": Height(discreteSet),
        "normalizedHeight": Height(normalized),
        "originalIncludedInNormalized": True,
        "originalEqualsNormalized": False,
    }


def UniversalScale() -> LinguisticScale:
    """Reconstruct the historical classifier on its intended normalized range."""

    universe = ClosedUniverse(0, 1)
    models = (
        ("Min", Hyperbolic(8, 20, 0)),
        ("Low", Bell(0.17, 0.23, 0.34)),
        ("Med", Bell(0.34, 0.40, 0.60)),
        ("High", Bell(0.60, 0.66, 0.77)),
        ("Max", SShoulder(0.77, 0.95)),
    )

    return LinguisticScale(tuple(
        LinguisticTerm(name, ScalarFuzzySet(universe, model))
        for name, model in models
    ))


def UniversalReference(coordinate: float) -> tuple[float, ...]:
    """Calculate grades independently with normalized quadratic ramps."""

    def Ramp(left: float, right: float) -> float:
        """Evaluate the elementary piecewise quadratic S shape."""

        fraction = max(0.0, min(1.0, (coordinate - left) / (right - left)))

        if fraction <= 0.5:
            return 2 * fraction**2

        return 1 - 2 * (1 - fraction)**2

    return (
        1 / (1 + (8 * coordinate)**20),
        min(Ramp(0.17, 0.23), 1 - Ramp(0.34, 0.40)),
        min(Ramp(0.34, 0.40), 1 - Ramp(0.60, 0.66)),
        min(Ramp(0.60, 0.66), 1 - Ramp(0.77, 0.83)),
        Ramp(0.77, 0.95),
    )


def HistoricalUniversalScale() -> dict:
    """Verify migration grades, labels, tails and explicit confidence policy."""

    historical = UniversalFuzzyScale()
    modern = UniversalScale()
    policy = FuzzificationPolicy(tiePolicy="last")
    coordinates = tuple(index / 1000 for index in range(1001))
    error = 0.0

    for coordinate in coordinates:
        expected = UniversalReference(coordinate)
        previous = tuple(level["fSet"].mFunction.mju(coordinate) for level in historical.levels)
        result = modern.Fuzzify(coordinate, policy)
        current = tuple(item.grade for item in result.memberships)

        for grades in (previous, current):
            for observed, reference in zip(grades, expected, strict=True):
                CheckClose(observed, reference, tolerance=1e-12)
                error = max(error, abs(observed - reference))

        assert result.selectedTerms[0].name == historical.Fuzzy(coordinate)["name"]

    selected = {str(x): modern.Fuzzify(x, policy).selectedTerms[0].name for x in (0, 0.2, 0.4, 0.7, 0.9, 1)}
    assert tuple(selected.values()) == ("Min", "Low", "Med", "High", "Max", "Max")
    CheckClose(modern.Fuzzify(0.125).confidence, 0.5)
    CheckClose(modern.Fuzzify(0.17).confidence, 1 / (1 + 1.36**20))
    tail = modern.terms[0].fuzzySet.Membership(0.5)
    CheckClose(tail, 1 / (1 + 4**20), tolerance=1e-15)
    assert tail > 0, "Historical supportSet must not truncate the Min tail."
    cautious = modern.Fuzzify(0.17, FuzzificationPolicy(minimumConfidence=0.1))
    assert not cautious.isMatch, "A confidence threshold must reject the weakly covered coordinate."
    equality = modern.Fuzzify(0.125, FuzzificationPolicy(minimumConfidence=0.5))
    assert not equality.isMatch, "Equality with minimumConfidence is a no-match."

    return {
        "selected": selected,
        "gridSamples": len(coordinates),
        "maximumOracleError": error,
        "gradesAt020": UniversalReference(0.2),
        "confidenceAt017": modern.Fuzzify(0.17).confidence,
        "minTailAt050": tail,
        "cautiousIsMatch": cautious.isMatch,
        "tiePolicy": policy.tiePolicy,
    }


SCENARIOS = {
    "temperature": TemperatureComfort,
    "risk": RiskAbstention,
    "sensors": SensorCriteria,
    "alarm": MaintenanceAlarm,
    "alpha-cuts": QualityAlphaCuts,
    "centroid": CentroidAndSampling,
    "scale-audit": ScaleAudit,
    "custom": CustomModel,
    "universal-fuzzy-scale": HistoricalUniversalScale,
}


def Main(arguments=None) -> int:
    """Select scenarios, verify numerical expectations, and print JSON evidence."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("all", *SCENARIOS), default="all")
    parsedArguments = parser.parse_args(arguments)
    selected = SCENARIOS if parsedArguments.scenario == "all" else {
        parsedArguments.scenario: SCENARIOS[parsedArguments.scenario]
    }
    print(json.dumps({name: scenario() for name, scenario in selected.items()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
