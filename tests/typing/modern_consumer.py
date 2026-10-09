# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Static consumer contracts for every focused modern API family.

Exact type assertions reject accidental `Any` return values. Precisely scoped
negative probes require their stated diagnostic, and strict unused-ignore
checking fails if an API is weakened enough to accept the invalid use.
This module is checker input and is never executed as a runtime example.
"""

from fractions import Fraction
from typing import assert_type as assertType

from fuzzyroutines import (
    AlphaCut,
    Bell,
    Centroid,
    CentroidPolicy,
    ComparisonDomain,
    ComparisonPolicy,
    Complement,
    ContinuousFuzzyProperties,
    ContinuousInterval,
    ContinuousRegion,
    ContinuousUniverse,
    DeriveProperties,
    Difference,
    DiscreteFuzzyProperties,
    DiscreteRegion,
    DiscreteUniverse,
    EqualOnDomain,
    FuzzificationPolicy,
    FuzzificationResult,
    Gaussian,
    HarringtonDesirability,
    Height,
    Hyperbolic,
    IncludedOnDomain,
    IntegrationDomain,
    Intersection,
    IsNormal,
    LinguisticScale,
    LinguisticTerm,
    Logistic,
    MembershipCallable,
    MembershipFunction,
    MembershipScalar,
    NegationPolicy,
    Normalize,
    SNormPolicy,
    SShoulder,
    SampleAlphaCut,
    SampleProperties,
    SampledAlphaCut,
    SampledFuzzyProperties,
    ScalarFuzzySet,
    ScaleDiagnosticsPolicy,
    ScaleDiagnosticsResult,
    TNormPolicy,
    Trapezoid,
    Triangle,
    Union,
)
from fuzzyroutines.exceptions import InvalidParameterError
from fuzzyroutines.membership import Triangle as CanonicalTriangle


def CustomGrade(coordinate: MembershipScalar) -> MembershipScalar:
    """Return a rational grade while accepting every supported scalar."""

    return Fraction(1, 2)


def CheckModernConsumers() -> None:
    """Check numeric inputs, immutable values, operations, and result evidence."""

    membership = Triangle(0, 0.5, 1)
    assertType(membership, MembershipFunction)
    assertType(CanonicalTriangle(0, Fraction(1, 2), 1), MembershipFunction)
    assertType(membership.Evaluate(0.5), MembershipScalar)
    assertType(membership(1), MembershipScalar)
    assertType(Bell(0, 0.5, 1), MembershipFunction)
    assertType(SShoulder(0, 1), MembershipFunction)
    assertType(Trapezoid(0, 0.25, 0.75, 1), MembershipFunction)
    assertType(Gaussian(0.5, 0.1), MembershipFunction)
    assertType(Logistic(2, 0.5), MembershipFunction)
    assertType(Hyperbolic(1, 2, 3), MembershipFunction)
    assertType(HarringtonDesirability(), MembershipFunction)

    evaluator: MembershipCallable = CustomGrade
    bounded = ContinuousUniverse(0, 1, True, True)
    discrete = DiscreteUniverse((0, 0.5, 1))
    domain = IntegrationDomain(0, 1)
    continuousSet = ScalarFuzzySet(bounded, membership)
    discreteSet = ScalarFuzzySet(discrete, evaluator)
    assertType(bounded.Contains(0.5), bool)
    assertType(discrete.Contains(1), bool)
    assertType(domain.ValidateWithin(bounded), IntegrationDomain)
    assertType(continuousSet.Membership(0.5), MembershipScalar)

    negation = NegationPolicy("standard")
    tNorm = TNormPolicy("logic")
    sNorm = SNormPolicy("algebraic")
    assertType(negation.Evaluate(0.5), MembershipScalar)
    assertType(tNorm.Evaluate(0, 1), MembershipScalar)
    assertType(sNorm.Evaluate(Fraction(1, 2), 0.5), MembershipScalar)
    assertType(Complement(continuousSet, negation), ScalarFuzzySet)
    assertType(Intersection(continuousSet, continuousSet, tNorm), ScalarFuzzySet)
    assertType(Union(continuousSet, continuousSet, sNorm), ScalarFuzzySet)
    assertType(Difference(continuousSet, continuousSet, tNorm, negation), ScalarFuzzySet)
    assertType(Normalize(discreteSet), ScalarFuzzySet)
    assertType(Height(discreteSet), MembershipScalar)
    assertType(IsNormal(discreteSet), bool)
    assertType(Centroid(continuousSet, domain, CentroidPolicy()), MembershipScalar)

    interval = ContinuousInterval(0, 1, True, True)
    assertType(ContinuousRegion((interval,)).Contains(0.5), bool)
    assertType(DiscreteRegion((0, 1)).Contains(1), bool)
    assertType(DeriveProperties(membership, bounded), ContinuousFuzzyProperties)
    assertType(DeriveProperties(membership, discrete), DiscreteFuzzyProperties)
    assertType(SampleProperties(membership, domain, 11), SampledFuzzyProperties)
    assertType(AlphaCut(discreteSet, 0.5), DiscreteRegion)
    assertType(SampleAlphaCut(continuousSet, Fraction(1, 2), domain, 11), SampledAlphaCut)

    comparison = ComparisonPolicy("exact")
    comparisonDomain = ComparisonDomain((0, 0.5, 1))
    assertType(comparison.Equal(0.5, 0.5), bool)
    assertType(comparison.Included(0, 1), bool)
    assertType(EqualOnDomain(discreteSet, discreteSet, comparison), bool)
    assertType(IncludedOnDomain(continuousSet, continuousSet, comparison, comparisonDomain), bool)

    term = LinguisticTerm("middle", continuousSet)
    scale = LinguisticScale((term,))
    assertType(scale.GetTermByName("middle"), LinguisticTerm | None)
    found = scale.GetTermByName("middle", exactMatching=False)
    if found is not None:
        assertType(found.fuzzySet, ScalarFuzzySet)

    fuzzification = scale.Fuzzify(0.5, FuzzificationPolicy("all"))
    assertType(fuzzification, FuzzificationResult)
    assertType(fuzzification.selectedTerms, tuple[LinguisticTerm, ...])
    assertType(fuzzification.isTie, bool)
    diagnostics = scale.Diagnose(domain, ScaleDiagnosticsPolicy(sampleCount=11))
    assertType(diagnostics, ScaleDiagnosticsResult)
    assertType(diagnostics.gapFraction, float)
    assertType(diagnostics.isPartitionWithinTolerance, bool)
    error: ValueError = InvalidParameterError("invalid scalar")
    assertType(error, ValueError)

    # Each diagnostic protects a distinct public boundary against accepting Any.
    Triangle("left", 0.5, 1)  # type: ignore[arg-type]
    ContinuousUniverse("left", 1)  # type: ignore[arg-type]
    DiscreteUniverse((0, "middle", 1))  # type: ignore[arg-type]
    ScalarFuzzySet(bounded, "membership")  # type: ignore[arg-type]
    continuousSet.Membership("coordinate")  # type: ignore[arg-type]
    Complement(continuousSet, tNorm)  # type: ignore[arg-type]
    Intersection(continuousSet, continuousSet, sNorm)  # type: ignore[arg-type]
    Centroid(continuousSet, bounded)  # type: ignore[arg-type]
    AlphaCut(discreteSet, "alpha")  # type: ignore[arg-type]
    SampleAlphaCut(continuousSet, 0.5, domain, "count")  # type: ignore[arg-type]
    DeriveProperties(evaluator, discrete)  # type: ignore[call-overload]
    SampleProperties(evaluator, domain)  # type: ignore[arg-type]
    EqualOnDomain(discreteSet, discreteSet, negation)  # type: ignore[arg-type]
    scale.Fuzzify(0.5, comparison)  # type: ignore[arg-type]
    scale.Diagnose(domain, FuzzificationPolicy())  # type: ignore[arg-type]
    LinguisticScale(("middle",))  # type: ignore[arg-type]
    requiredTerm: LinguisticTerm = scale.GetTermByName("missing")  # type: ignore[assignment]
    scalarText: str = continuousSet.Membership(0.5)  # type: ignore[assignment]
    centroidText: str = Centroid(continuousSet, domain)  # type: ignore[assignment]
    assertType((requiredTerm, scalarText, centroidText), tuple[LinguisticTerm, str, str])
    membership.parameters["a"] = 0.5  # type: ignore[index]
    term.name = "changed"  # type: ignore[misc]
