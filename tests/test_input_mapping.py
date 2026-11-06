# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic numerical and input-boundary checks for the affine experiment."""

import sys
from dataclasses import FrozenInstanceError
from math import copysign, inf, nan, nextafter

import pytest

from fuzzyroutines._input_mapping import _AffineInputMapping, _MissingObservationError
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)


@pytest.mark.parametrize(
    ("bounds", "sourceUnit", "targetUnit", "observation", "expected"),
    [
        ((10, 50, 0, 1), "°C", "1", 30, 0.5),
        ((0, 80, -1, 1), "kN", "1", 60, 0.5),
        ((200, 1000, 0, 1), "points", "1", 400, 0.25),
    ],
)
def test_AnalyticalAffineExamples(bounds, sourceUnit, targetUnit, observation, expected):
    """Reproduce exact temperature, load and risk examples from ADR-0033."""

    mapping = _AffineInputMapping(*bounds, sourceUnit, targetUnit)
    assert mapping.Forward(observation, unit=sourceUnit) == expected
    assert mapping.Inverse(expected, unit=targetUnit) == observation


def test_EndpointsPreserveTheDeclaredSignedZero():
    """Anchor the closed endpoints directly, including the sign of stored zero."""

    mapping = _AffineInputMapping(-0.0, 1, -1, -0.0, "points", "1")
    assert mapping.Forward(0, unit="points") == -1
    assert copysign(1, mapping.Forward(1, unit="points")) == -1
    assert copysign(1, mapping.Inverse(-1, unit="1")) == -1
    assert mapping.Inverse(0, unit="1") == 1


def test_ExtremeSpansRemainFiniteInBothDirections():
    """Use exact ratios when a finite interval's span overflows binary64."""

    largest = sys.float_info.max
    mapping = _AffineInputMapping(-largest, largest, -largest, largest, "points", "1")
    assert mapping.Forward(largest / 2, unit="points") == largest / 2
    assert mapping.Inverse(-largest / 2, unit="1") == -largest / 2


def test_TiesRoundToEvenAndAdjacentObservationsStayOrdered():
    """Quantize a narrow target once and keep the rounded map nondecreasing."""

    upper = nextafter(1.0, inf)
    mapping = _AffineInputMapping(0, 1, 1, upper, "points", "1")
    samples = (0.0, nextafter(0.5, -inf), 0.5, nextafter(0.5, inf), 1.0)
    outputs = [mapping.Forward(sample, unit="points") for sample in samples]
    assert outputs == [1.0, 1.0, 1.0, upper, upper]
    assert mapping.Inverse(outputs[2], unit="1") == 0.0


@pytest.mark.parametrize("direction", ["Forward", "Inverse"])
@pytest.mark.parametrize("observation", [nextafter(0.0, -inf), nextafter(1.0, inf)])
def test_AdjacentOutOfRangeCoordinatesAreRejected(direction, observation):
    """Keep observations one representable step outside either bound distinct."""

    mapping = _AffineInputMapping(0, 1, 0, 1, "1", "1")

    with pytest.raises(InvalidDomainError, match="outside the closed input interval"):
        getattr(mapping, direction)(observation, unit="1")


@pytest.mark.parametrize(
    ("observation", "error", "reason"),
    [
        (None, _MissingObservationError, "missing"),
        (True, InvalidParameterTypeError, "built-in float or integer"),
        ("0.5", InvalidParameterTypeError, "built-in float or integer"),
        (nan, InvalidParameterError, "finite"),
        (inf, InvalidParameterError, "finite"),
        (2**53 + 1, InvalidParameterError, "exactly representable"),
        (10**400, InvalidParameterError, "exactly representable"),
    ],
)
def test_MissingAndInvalidObservationsHaveDistinctDiagnostics(observation, error, reason):
    """Report missing, unsupported, nonfinite and lossy inputs at evaluation."""

    mapping = _AffineInputMapping(0, 1, 0, 1, "1", "1")

    with pytest.raises(error, match=reason) as observed:
        mapping.Forward(observation, unit="1")

    assert type(observed.value) is error


def test_ExactlyRepresentableLargeIntegersAreAdmitted():
    """Accept integers with a lossless binary64 representation above 2**53."""

    start = 2**53
    mapping = _AffineInputMapping(start, start + 4, 0, 1, "points", "1")
    assert mapping.Forward(start + 2, unit="points") == 0.5
    assert mapping.Inverse(0.5, unit="1") == start + 2


def test_UnitIdentityAndImmutability():
    """Check exact unit labels in both directions and freeze the mapping."""

    mapping = _AffineInputMapping(0, 10, 0, 1, "kN", "1")

    with pytest.raises(InvalidParameterError, match="must match 'kN'"):
        mapping.Forward(5, unit="kn")

    with pytest.raises(InvalidParameterError, match="must match '1'"):
        mapping.Inverse(0.5, unit="kN")

    with pytest.raises(InvalidParameterError, match="must be nonblank"):
        _AffineInputMapping(0, 10, 0, 1, "kN", " ")

    with pytest.raises(FrozenInstanceError):
        mapping.sourceUnit = "N"


@pytest.mark.parametrize("bounds", [(1, 1, 0, 1), (1, 0, 0, 1), (0, 1, 1, 0)])
def test_BothIntervalsRequireStrictlyIncreasingBounds(bounds):
    """Reject equal or reversed bounds before evaluating any observation."""

    with pytest.raises(InvalidDomainError, match="strictly increasing"):
        _AffineInputMapping(*bounds, "1", "1")
