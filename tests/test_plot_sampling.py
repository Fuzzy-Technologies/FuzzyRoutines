# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic scalar evidence for discrete scientific plot samples."""

from fractions import Fraction

import pytest

from fuzzyroutines._plot_sampling import PlotSamplingError, SampleDiscretePlot
from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.membership import MembershipScalar


def test_PreserveDeclaredPointsAndGradesExactly():
    """Match the ADR marker fixture, including zero and the exact rational point."""

    points = (0, Fraction(2, 5), 1)
    grades = {0: 0, Fraction(2, 5): Fraction(7, 10), 1: Fraction(1, 2)}
    evaluated = []

    def Evaluate(coordinate: MembershipScalar) -> MembershipScalar:
        """Record the coordinate passed to the scalar callback."""

        evaluated.append(coordinate)

        return grades[coordinate]

    fuzzySet = ScalarFuzzySet(DiscreteUniverse(points), Evaluate)
    samples = SampleDiscretePlot(fuzzySet, "measured")

    assert samples == ((0, 0), (Fraction(2, 5), Fraction(7, 10)), (1, Fraction(1, 2)))
    assert evaluated == list(points), "Plot markers must use each declared coordinate exactly once."
    assert samples[1][0] is points[1], "Rational coordinates must reach the marker without coercion."
    assert isinstance(samples[1][1], Fraction), "Rational grades must be preserved before rendering."


def test_ClipByExactInclusiveWindow():
    """Preserve adjacent large integers and include both limits without resampling."""

    left = 2**53
    right = left + 1

    def Evaluate(coordinate: MembershipScalar) -> MembershipScalar:
        """Return distinct reference grades for the two visible coordinates."""

        if coordinate == left:
            return 0

        assert coordinate == right, "Clipped coordinates must never be evaluated."

        return 1

    fuzzySet = ScalarFuzzySet(DiscreteUniverse((left - 1, left, right, right + 1)), Evaluate)

    assert SampleDiscretePlot(fuzzySet, "integer grid", window=(left, right)) == ((left, 0), (right, 1))
    assert SampleDiscretePlot(fuzzySet, "integer grid", window=(0, 1)) == ()


def test_SampleSingletonWithoutInventingCoordinates():
    """Allow a singleton marker without turning display padding into data."""

    def Evaluate(coordinate: MembershipScalar) -> MembershipScalar:
        """Return the grade only for the declared singleton."""

        assert coordinate == 4, "Singleton sampling must not synthesize another coordinate."

        return Fraction(3, 4)

    fuzzySet = ScalarFuzzySet(DiscreteUniverse((4,)), Evaluate)

    assert SampleDiscretePlot(fuzzySet, "singleton") == ((4, Fraction(3, 4)),)


@pytest.mark.parametrize(
    ("window", "exceptionType"),
    [
        ((2, 1), InvalidDomainError),
        ((1, 1), InvalidDomainError),
        ((0, float("inf")), InvalidParameterError),
        ((float("nan"), 1), InvalidParameterError),
        ((False, 1), InvalidParameterTypeError),
    ],
)
def test_RejectInvalidDisplayWindowBeforeSampling(window, exceptionType):
    """Reject invalid limits before evaluating any point."""

    def UnexpectedEvaluation(coordinate: MembershipScalar) -> MembershipScalar:
        """Fail if validation evaluates a point."""

        pytest.fail(f"Unexpected scalar evaluation at {coordinate!r}.")

    fuzzySet = ScalarFuzzySet(DiscreteUniverse((0, 1)), UnexpectedEvaluation)

    with pytest.raises(exceptionType):
        SampleDiscretePlot(fuzzySet, "invalid window", window=window)


def test_RejectContinuousUniverse():
    """Keep continuous input outside the discrete marker path."""

    def UnexpectedEvaluation(coordinate: MembershipScalar) -> MembershipScalar:
        """Fail if the discrete sampler attempts continuous evaluation."""

        pytest.fail(f"Unexpected scalar evaluation at {coordinate!r}.")

    fuzzySet = ScalarFuzzySet(ContinuousUniverse(0, 1), UnexpectedEvaluation)

    with pytest.raises(InvalidDomainError, match="DiscreteUniverse"):
        SampleDiscretePlot(fuzzySet, "continuous")


def test_InvalidScalarGradeReportsPointAndStopsSampling():
    """Report the series and failing coordinate while preserving scalar validation."""

    evaluated = []

    def Evaluate(coordinate: MembershipScalar) -> MembershipScalar:
        """Return one invalid grade and record all attempted evaluations."""

        evaluated.append(coordinate)

        return 2 if coordinate == 1 else 0

    fuzzySet = ScalarFuzzySet(DiscreteUniverse((0, 1, 2)), Evaluate)

    with pytest.raises(PlotSamplingError, match="'invalid grades' at 1") as failure:
        SampleDiscretePlot(fuzzySet, "invalid grades")

    assert isinstance(failure.value.__cause__, InvalidParameterError)
    assert evaluated == [0, 1], "A failed grade must stop the series rather than become zero."
