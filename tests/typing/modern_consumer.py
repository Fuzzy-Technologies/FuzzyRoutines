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
from typing import assert_type

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
    assert_type(membership, MembershipFunction)
    assert_type(CanonicalTriangle(0, Fraction(1, 2), 1), MembershipFunction)
    assert_type(membership.Evaluate(0.5), MembershipScalar)
    assert_type(membership(1), MembershipScalar)
    assert_type(Bell(0, 0.5, 1), MembershipFunction)
    assert_type(SShoulder(0, 1), MembershipFunction)
    assert_type(Trapezoid(0, 0.25, 0.75, 1), MembershipFunction)
    assert_type(Gaussian(0.5, 0.1), MembershipFunction)
    assert_type(Logistic(2, 0.5), MembershipFunction)
    assert_type(Hyperbolic(1, 2, 3), MembershipFunction)
    assert_type(HarringtonDesirability(), MembershipFunction)

    evaluator: MembershipCallable = CustomGrade
    bounded = ContinuousUniverse(0, 1, True, True)
    discrete = DiscreteUniverse((0, 0.5, 1))
    domain = IntegrationDomain(0, 1)
    continuous_set = ScalarFuzzySet(bounded, membership)
    discrete_set = ScalarFuzzySet(discrete, evaluator)
    assert_type(bounded.Contains(0.5), bool)
    assert_type(discrete.Contains(1), bool)
    assert_type(domain.ValidateWithin(bounded), IntegrationDomain)
    assert_type(continuous_set.Membership(0.5), MembershipScalar)

    negation = NegationPolicy("standard")
    t_norm = TNormPolicy("logic")
    s_norm = SNormPolicy("algebraic")
    assert_type(negation.Evaluate(0.5), MembershipScalar)
    assert_type(t_norm.Evaluate(0, 1), MembershipScalar)
    assert_type(s_norm.Evaluate(Fraction(1, 2), 0.5), MembershipScalar)
    assert_type(Complement(continuous_set, negation), ScalarFuzzySet)
    assert_type(Intersection(continuous_set, continuous_set, t_norm), ScalarFuzzySet)
    assert_type(Union(continuous_set, continuous_set, s_norm), ScalarFuzzySet)
    assert_type(Difference(continuous_set, continuous_set, t_norm, negation), ScalarFuzzySet)
    assert_type(Normalize(discrete_set), ScalarFuzzySet)
    assert_type(Height(discrete_set), MembershipScalar)
    assert_type(IsNormal(discrete_set), bool)
    assert_type(Centroid(continuous_set, domain, CentroidPolicy()), MembershipScalar)

    interval = ContinuousInterval(0, 1, True, True)
    assert_type(ContinuousRegion((interval,)).Contains(0.5), bool)
    assert_type(DiscreteRegion((0, 1)).Contains(1), bool)
    assert_type(DeriveProperties(membership, bounded), ContinuousFuzzyProperties)
    assert_type(DeriveProperties(membership, discrete), DiscreteFuzzyProperties)
    assert_type(SampleProperties(membership, domain, 11), SampledFuzzyProperties)
    assert_type(AlphaCut(discrete_set, 0.5), DiscreteRegion)
    assert_type(SampleAlphaCut(continuous_set, Fraction(1, 2), domain, 11), SampledAlphaCut)

    comparison = ComparisonPolicy("exact")
    comparison_domain = ComparisonDomain((0, 0.5, 1))
    assert_type(comparison.Equal(0.5, 0.5), bool)
    assert_type(comparison.Included(0, 1), bool)
    assert_type(EqualOnDomain(discrete_set, discrete_set, comparison), bool)
    assert_type(IncludedOnDomain(continuous_set, continuous_set, comparison, comparison_domain), bool)

    term = LinguisticTerm("middle", continuous_set)
    scale = LinguisticScale((term,))
    assert_type(scale.GetTermByName("middle"), LinguisticTerm | None)
    found = scale.GetTermByName("middle", exactMatching=False)
    if found is not None:
        assert_type(found.fuzzySet, ScalarFuzzySet)

    fuzzification = scale.Fuzzify(0.5, FuzzificationPolicy("all"))
    assert_type(fuzzification, FuzzificationResult)
    assert_type(fuzzification.selectedTerms, tuple[LinguisticTerm, ...])
    assert_type(fuzzification.isTie, bool)
    diagnostics = scale.Diagnose(domain, ScaleDiagnosticsPolicy(sampleCount=11))
    assert_type(diagnostics, ScaleDiagnosticsResult)
    assert_type(diagnostics.gapFraction, float)
    assert_type(diagnostics.isPartitionWithinTolerance, bool)
    error: ValueError = InvalidParameterError("invalid scalar")
    assert_type(error, ValueError)

    # Each diagnostic protects a distinct public boundary against accepting Any.
    Triangle("left", 0.5, 1)  # type: ignore[arg-type]
    ContinuousUniverse("left", 1)  # type: ignore[arg-type]
    DiscreteUniverse((0, "middle", 1))  # type: ignore[arg-type]
    ScalarFuzzySet(bounded, "membership")  # type: ignore[arg-type]
    continuous_set.Membership("coordinate")  # type: ignore[arg-type]
    Complement(continuous_set, t_norm)  # type: ignore[arg-type]
    Intersection(continuous_set, continuous_set, s_norm)  # type: ignore[arg-type]
    Centroid(continuous_set, bounded)  # type: ignore[arg-type]
    AlphaCut(discrete_set, "alpha")  # type: ignore[arg-type]
    SampleAlphaCut(continuous_set, 0.5, domain, "count")  # type: ignore[arg-type]
    DeriveProperties(evaluator, discrete)  # type: ignore[call-overload]
    SampleProperties(evaluator, domain)  # type: ignore[arg-type]
    EqualOnDomain(discrete_set, discrete_set, negation)  # type: ignore[arg-type]
    scale.Fuzzify(0.5, comparison)  # type: ignore[arg-type]
    scale.Diagnose(domain, FuzzificationPolicy())  # type: ignore[arg-type]
    LinguisticScale(("middle",))  # type: ignore[arg-type]
    required_term: LinguisticTerm = scale.GetTermByName("missing")  # type: ignore[assignment]
    scalar_text: str = continuous_set.Membership(0.5)  # type: ignore[assignment]
    centroid_text: str = Centroid(continuous_set, domain)  # type: ignore[assignment]
    assert_type((required_term, scalar_text, centroid_text), tuple[LinguisticTerm, str, str])
    membership.parameters["a"] = 0.5  # type: ignore[index]
    term.name = "changed"  # type: ignore[misc]
