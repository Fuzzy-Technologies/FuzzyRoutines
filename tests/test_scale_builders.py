# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic references for scale partitions and endpoint ownership."""

from fractions import Fraction

import pytest

from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.linguistic import LinguisticScale, LinguisticTerm
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.scale_builders import BuildIntervalScale, BuildLinearScale

NAMES = ("low", "mid", "high")
PEAKS = tuple(zip(NAMES, (0, 2, 7), strict=True))


def _Grades(scale: LinguisticScale, point: MembershipScalar) -> tuple[MembershipScalar, ...]:
    """Read ordered grades through the existing fuzzification interface."""

    return tuple(item.grade for item in scale.Fuzzify(point).memberships)


def _Low(point: MembershipScalar) -> MembershipScalar:
    """Compute the first linear shoulder independently for the witness."""

    return max(0, min(1, 1 - Fraction(float(point)) / 2))


def _Mid(point: MembershipScalar) -> MembershipScalar:
    """Compute the interior triangular term independently for the witness."""

    ratio = Fraction(float(point))

    return max(0, min(ratio / 2, (7 - ratio) / 5))


def _High(point: MembershipScalar) -> MembershipScalar:
    """Compute the second linear shoulder independently for the witness."""

    return max(0, min(1, (Fraction(float(point)) - 2) / 5))


def test_LinearScaleMatchesIndependentReferenceAcrossClosedUniverse() -> None:
    """Match a manual scale at knots, between knots, and along the shoulders."""

    universe = ContinuousUniverse(-2, 9, leftClosed=True, rightClosed=True)
    reference = LinguisticScale(tuple(
        LinguisticTerm(name, ScalarFuzzySet(universe, callback))
        for name, callback in zip(NAMES, (_Low, _Mid, _High), strict=True)
    ))
    scale = BuildLinearScale(PEAKS, -2, 9)

    for index in range(-8, 37):
        point = Fraction(index, 4)
        grades = _Grades(scale, point)
        assert grades == _Grades(reference, point), "The builder must match the manual scale"
        assert sum(grades) == 1, "The complementary ramps must partition the whole universe"


def test_IntervalBoundaryOwnershipAndSingleTerm() -> None:
    """Assign inner edges to the right bin and include both global endpoints."""

    scale = BuildIntervalScale(NAMES, (-2, 0, 2, 9))

    for point, expected in ((-2, (1, 0, 0)), (0, (0, 1, 0)), (2, (0, 0, 1)), (9, (0, 0, 1))):
        assert _Grades(scale, point) == expected, "Every edge must have one declared owner"

    with pytest.raises(InvalidDomainError, match="every term universe"):
        scale.Fuzzify(10)

    for point in (-2, 0, 9):
        assert _Grades(BuildLinearScale((("all", 0),), -2, 9), point) == (1,)
        assert _Grades(BuildIntervalScale(("all",), (-2, 9)), point) == (1,)


def test_EndpointPeaksAndAdjacentRationalKnots() -> None:
    """Support zero-width shoulders and distinct rational peaks near a float."""

    edge = 2**53
    scale = BuildLinearScale((("left", edge), ("right", edge + 1)), edge, edge + 1)
    assert _Grades(scale, edge) == (1, 0)
    assert _Grades(scale, edge + 1) == (0, 1)
    assert _Grades(scale, Fraction(2 * edge + 1, 2)) == (Fraction(1, 2), Fraction(1, 2))


def test_BuildersRejectAmbiguousNamesAndCoordinates() -> None:
    """Reject empty declarations, bad labels, and equal or crossed positions."""

    for positions in ((0, 0), (1, 0)):
        with pytest.raises(InvalidDomainError, match="strictly increasing"):
            BuildLinearScale(tuple(zip(("a", "b"), positions, strict=True)), -2, 9)

    for boundaries in ((0, 0, 1), (0, 2, 1)):
        with pytest.raises(InvalidDomainError, match="strictly increasing"):
            BuildIntervalScale(("a", "b"), boundaries)

    with pytest.raises(InvalidParameterError, match="unique"):
        BuildIntervalScale(("A", "a"), (0, 1, 2))

    with pytest.raises(InvalidParameterError, match="non-whitespace"):
        BuildLinearScale(((" ", 0),), -2, 9)

    with pytest.raises(InvalidParameterError, match="at least one"):
        BuildLinearScale((), -2, 9)

    with pytest.raises(InvalidParameterError, match="at least one"):
        BuildIntervalScale((), (0,))

    with pytest.raises(InvalidParameterTypeError, match="real number"):
        BuildIntervalScale(("a",), (False, 1))

    with pytest.raises(InvalidParameterError, match="finite"):
        BuildLinearScale((("a", float("inf")),), -2, 9)
