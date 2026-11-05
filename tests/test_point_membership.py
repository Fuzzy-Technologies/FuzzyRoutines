# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic tests for the discrete and interpolated point contracts."""

import math
import sys
from dataclasses import FrozenInstanceError
from fractions import Fraction

import pytest

from fuzzyroutines import (
    ContinuousUniverse,
    DiscreteUniverse,
    Height,
    MembershipCallable,
    ScalarFuzzySet,
)
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.point_membership import DiscreteMembershipTable, PiecewiseLinearMembership

POINTS = ((-2, Fraction(1, 4)), (1, Fraction(3, 4)), (5, Fraction(1, 2)))


def test_DiscreteTablePreservesGradesAndRejectsUndeclaredPoints():
    """Expose a complete finite universe with no interpolation or implicit zero."""

    table = DiscreteMembershipTable(POINTS)
    evaluator: MembershipCallable = table
    fuzzySet = ScalarFuzzySet(table.universe, evaluator)

    assert table.universe == DiscreteUniverse((-2, 1, 5))
    assert table(1) is POINTS[1][1]
    assert table(1.0) == Fraction(3, 4)
    assert Height(fuzzySet) == Fraction(3, 4)
    assert DiscreteMembershipTable(((10, 0),))(10) == 0

    for coordinate in (-3, 0, 6, math.nextafter(1.0, math.inf)):
        with pytest.raises(InvalidDomainError, match="declared table point"):
            table(coordinate)


def test_LinearKnotsAndIrregularGrid():
    """Use the actual widths of adjacent segments and preserve the knot values."""

    curve = PiecewiseLinearMembership(POINTS)
    evaluator: MembershipCallable = curve
    fuzzySet = ScalarFuzzySet(ContinuousUniverse(), evaluator)

    for coordinate, grade in POINTS:
        assert curve(coordinate) is grade

    assert curve(-1) == Fraction(5, 12)
    assert curve(3) == Fraction(5, 8)
    assert fuzzySet.Membership(Fraction(-1, 2)) == Fraction(1, 2)
    assert curve(3.0) == 0.625


def test_LinearBoundaryPoliciesOnlyApplyOutsideTheClosedKnotInterval():
    """Preserve nonzero endpoint grades and make their possible jumps explicit."""

    before = math.nextafter(-2.0, -math.inf)
    after = math.nextafter(5.0, math.inf)
    zero = PiecewiseLinearMembership(POINTS, boundary="zero")
    clamp = PiecewiseLinearMembership(POINTS, boundary="clamp")
    error = PiecewiseLinearMembership(POINTS)

    assert zero(before) == zero(after) == 0
    assert zero(-2) == Fraction(1, 4) and zero(5) == Fraction(1, 2)
    assert clamp(before) is POINTS[0][1]
    assert clamp(after) is POINTS[-1][1]
    assert error(-2) is POINTS[0][1] and error(5) is POINTS[-1][1]

    for coordinate in (before, after):
        with pytest.raises(InvalidDomainError, match="outside the closed knot interval"):
            error(coordinate)


def test_PiecewiseBoundaryDoesNotOverrideFuzzySetUniverse():
    """Apply the explicit fuzzy-set universe before the evaluator's extension."""

    curve = PiecewiseLinearMembership(POINTS, boundary="clamp")
    fuzzySet = ScalarFuzzySet(ContinuousUniverse(-2, 5, leftClosed=True, rightClosed=True), curve)

    assert curve(6) == Fraction(1, 2)

    with pytest.raises(InvalidDomainError, match="fuzzy set universe"):
        fuzzySet.Membership(6)


def test_PointObjectsAreFrozenAndHaveImmutableRecords():
    """Prevent replacement of data and policy after successful validation."""

    table = DiscreteMembershipTable(POINTS)
    curve = PiecewiseLinearMembership(POINTS)

    assert type(table.points) is tuple and all(type(point) is tuple for point in table.points)
    assert type(curve.knots) is tuple and all(type(point) is tuple for point in curve.knots)

    with pytest.raises(FrozenInstanceError):
        table.points = ((0, 1),)

    with pytest.raises(FrozenInstanceError):
        curve.boundary = "clamp"


@pytest.mark.parametrize("constructor", (DiscreteMembershipTable, PiecewiseLinearMembership))
@pytest.mark.parametrize(
    ("points", "exception", "message"),
    (
        ([(0, 0), (1, 1)], InvalidParameterTypeError, "must be a tuple"),
        (((0, 0), [1, 1]), InvalidParameterTypeError, "must be a .* tuple"),
        (((0, 0), (1,)), InvalidParameterTypeError, "must be a .* tuple"),
        ((), InvalidDomainError, "must contain at least"),
        (((0, 0), (0.0, 1)), InvalidDomainError, "strictly increasing and distinct"),
        (((1, 0), (0, 1)), InvalidDomainError, "strictly increasing and distinct"),
        (((False, 0), (1, 1)), InvalidParameterTypeError, "coordinate must be a real number"),
        (((0, 0), ("1", 1)), InvalidParameterTypeError, "coordinate must be a real number"),
        (((0, 0), (math.nan, 1)), InvalidParameterError, "coordinate must be a finite real number"),
        (((0, 0), (math.inf, 1)), InvalidParameterError, "coordinate must be a finite real number"),
        (((0, 0), (10**400, 1)), InvalidParameterError, "coordinate must be a finite real number"),
        (((0, True), (1, 1)), InvalidParameterTypeError, "grade must be a real number"),
        (((0, math.inf), (1, 1)), InvalidParameterError, "grade must be a finite real number"),
        (((0, math.nan), (1, 1)), InvalidParameterError, "grade must be a finite real number"),
        (((0, -0.001), (1, 1)), InvalidParameterError, "closed interval"),
        (((0, 0), (1, Fraction(2))), InvalidParameterError, "closed interval"),
    ),
)
def test_PointConstructorsRejectInvalidData(constructor, points, exception, message):
    """Reject ambiguous or mathematically invalid geometry before evaluation."""

    with pytest.raises(exception, match=message):
        constructor(points)


@pytest.mark.parametrize(
    ("boundary", "exception"),
    ((None, InvalidParameterTypeError), ("extrapolate", InvalidParameterError)),
)
def test_LinearBoundaryMustBeADeclaredPolicy(boundary, exception):
    """Reject unknown policy strings and non-string options."""

    with pytest.raises(exception, match="boundary"):
        PiecewiseLinearMembership(POINTS, boundary=boundary)


def test_LinearCurveRequiresAtLeastOneSegment():
    """Reserve singleton inputs for discrete tables."""

    with pytest.raises(InvalidDomainError, match="at least 2"):
        PiecewiseLinearMembership(((1, 1),))


@pytest.mark.parametrize(
    "evaluator",
    (DiscreteMembershipTable(POINTS), PiecewiseLinearMembership(POINTS, boundary="zero")),
)
@pytest.mark.parametrize(
    ("coordinate", "exception"),
    ((True, InvalidParameterTypeError), (math.nan, InvalidParameterError), (-math.inf, InvalidParameterError)),
)
def test_InvalidQueryCannotBeHiddenByBoundaryPolicy(evaluator, coordinate, exception):
    """Validate direct coordinates before lookup or extension."""

    with pytest.raises(exception, match="coordinate"):
        evaluator(coordinate)


def test_InterpolationHandlesExtremeAndPreciselySeparatedCoordinates():
    """Keep widths valid across the floating range and retain exact rational spacing."""

    limit = sys.float_info.max
    tiny = math.ulp(0.0)
    offset = 2**53

    assert PiecewiseLinearMembership(((-limit, 0), (limit, 1)))(0) == 0.5
    assert PiecewiseLinearMembership(((0.0, 0), (2 * tiny, 1)))(tiny) == 0.5
    assert PiecewiseLinearMembership(((offset, 0), (offset + 2.0, 1)))(offset + 1) == 0.5
    assert PiecewiseLinearMembership(((0, 0), (3, 1)))(1) == Fraction(1, 3)
    assert PiecewiseLinearMembership(((0.0, 0), (3, 1)))(1) == 1.0 / 3
