# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic scalar evidence for discrete scientific plot samples."""

import sys
from fractions import Fraction
from math import nextafter

import pytest

from fuzzyroutines._plot_sampling import (
    PlotSamplingError,
    SampleClosedPlotSegment,
    SampleDiscretePlot,
)
from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.membership import MembershipScalar, Triangle


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


def test_SampleClosedTriangleAtOffGridKnotAndInput():
    """Check independent analytical grades and separate grid from added samples."""

    universe = ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True)
    fuzzySet = ScalarFuzzySet(universe, Triangle(0, 0.37, 1))
    result = SampleClosedPlotSegment(fuzzySet, "triangle", (0, 1), sampleCount=4, extraCoordinates=(0.41, 0.37, 0.37))

    assert result.baseSampleCount == 4
    assert result.addedCoordinates == (0.37, 0.41)
    assert tuple(point for point, _ in result.samples) == (0, 1 / 3, 0.37, 0.41, 2 / 3, 1)
    grades = dict(result.samples)
    assert grades[0.37] == 1
    assert grades[0.41] == pytest.approx(0.59 / 0.63, rel=0, abs=1e-14)


def test_UseExactCoordinatesInsideAnOpenUniverse():
    """Evaluate a closed interior window while preserving supplied scalar types."""

    left = Fraction(1, 4)
    knot = Fraction(1, 2)
    right = Fraction(3, 4)
    evaluated = []

    def Evaluate(coordinate: MembershipScalar) -> MembershipScalar:
        """Record the original coordinates delivered to the scalar source."""

        evaluated.append(coordinate)

        return Fraction(1, 3)

    fuzzySet = ScalarFuzzySet(ContinuousUniverse(0, 1), Evaluate)
    result = SampleClosedPlotSegment(
        fuzzySet, "interior", (left, right), sampleCount=3, extraCoordinates=(0, knot, 1),
    )

    assert result.window == (left, right)
    assert result.addedCoordinates == ()
    assert len(evaluated) == 3, "The declared knot must replace its equal base coordinate."
    assert all(actual is declared for actual, declared in zip(evaluated, (left, knot, right), strict=True))
    assert all(isinstance(grade, Fraction) for _, grade in result.samples)


def test_GridHandlesOppositeExtremeEndpoints():
    """Resolve the finite midpoint without overflowing the interval width."""

    limit = sys.float_info.max

    def Evaluate(coordinate: MembershipScalar) -> MembershipScalar:
        """Use a unit grade only at the expected midpoint."""

        return int(coordinate == 0)

    universe = ContinuousUniverse(-limit, limit, leftClosed=True, rightClosed=True)
    result = SampleClosedPlotSegment(ScalarFuzzySet(universe, Evaluate), "wide", (-limit, limit), sampleCount=3)

    assert result.samples == ((-limit, 0), (0, 1), (limit, 0))


@pytest.mark.parametrize(
    ("window", "sampleCount", "exceptionType"),
    [
        ((0, 1), 3, InvalidDomainError),
        ((0.5, nextafter(0.5, 1)), 3, InvalidDomainError),
        ((Fraction(1, 10), nextafter(0.1, 1)), 3, InvalidDomainError),
        ((0.25, 0.75), 1, InvalidParameterError),
        ((0.25, 0.75), True, InvalidParameterTypeError),
    ],
)
def test_RejectUnusableClosedGridBeforeEvaluation(window, sampleCount, exceptionType):
    """Reject open edges, duplicate floating grid samples and invalid counts."""

    def UnexpectedEvaluation(coordinate: MembershipScalar) -> MembershipScalar:
        """Fail if validation attempts membership evaluation."""

        pytest.fail(f"Unexpected scalar evaluation at {coordinate!r}.")

    fuzzySet = ScalarFuzzySet(ContinuousUniverse(0, 1), UnexpectedEvaluation)

    with pytest.raises(exceptionType):
        SampleClosedPlotSegment(fuzzySet, "invalid", window, sampleCount=sampleCount)
