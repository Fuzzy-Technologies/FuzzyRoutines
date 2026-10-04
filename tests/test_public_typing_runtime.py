# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Protect rational runtime arithmetic across the static numeric boundary."""

from fractions import Fraction

from fuzzyroutines import (
    Centroid,
    ContinuousUniverse,
    DeriveProperties,
    IntegrationDomain,
    MembershipScalar,
    SampleProperties,
    ScalarFuzzySet,
    SNormPolicy,
    Triangle,
)


def RationalGrade(coordinate: MembershipScalar) -> MembershipScalar:
    """Return an exact rational grade independent of the coordinate."""

    return Fraction(1, 2)


def test_AnnotatedFactoriesRetainRationalParametersAndGrades():
    """Keep analytical data and arithmetic uncoerced by checker views."""

    left = Fraction(0)
    peak = Fraction(1)
    right = Fraction(2)
    membership = Triangle(left, peak, right)
    universe = ContinuousUniverse(left, right, True, True)
    fuzzy_set = ScalarFuzzySet(universe, membership)
    grade = fuzzy_set.Membership(Fraction(1, 2))

    assert membership.parameters["left"] is left, "Factory annotations must not coerce rational parameters"
    assert universe.left is left, "Universe annotation changes must preserve endpoint identity"
    assert isinstance(grade, Fraction) and grade == Fraction(1, 2), (
        "The private static arithmetic view must preserve exact rational grades"
    )
    combined = SNormPolicy("algebraic").Evaluate(grade, grade)
    assert isinstance(combined, Fraction) and combined == Fraction(3, 4), (
        "Operator typing must preserve rational arithmetic instead of coercing to float"
    )


def test_AnnotatedAnalysisPreservesRationalCoordinatesAndCentroid():
    """Retain exact rational paths through sampling and adaptive moments."""

    universe = ContinuousUniverse(Fraction(0), Fraction(1), True, True)
    domain = IntegrationDomain(Fraction(0), Fraction(1))
    membership = Triangle(Fraction(0), Fraction(1, 2), Fraction(1))
    sampled = SampleProperties(membership, domain, 3)
    derived = DeriveProperties(membership, universe)
    centroid = Centroid(ScalarFuzzySet(universe, RationalGrade), domain)

    assert all(isinstance(coordinate, Fraction) for coordinate in sampled.coordinates), (
        "Sample typing must keep rational grid coordinates when arithmetic is exact"
    )
    assert derived.core.Contains(Fraction(1, 2)), "Typed analytical evidence must retain the rational apex"
    assert isinstance(centroid, Fraction) and centroid == Fraction(1, 2), (
        "Centroid return annotations must allow an exact rational result"
    )
