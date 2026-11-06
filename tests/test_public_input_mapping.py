# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Public affine mapping boundaries and historical-scale integration."""

from dataclasses import FrozenInstanceError
from math import copysign, inf, nextafter

import pytest

from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
)
from fuzzyroutines.input_mapping import AffineInputMapping, MissingObservationError
from fuzzyroutines.presets import CreateUniversalFuzzyScale


def test_PhysicalTemperatureUsesTheHistoricalScaleUniverse():
    """Bind an explicit physical range to the existing historical scale."""

    scale = CreateUniversalFuzzyScale()
    universe = scale.terms[0].fuzzySet.universe
    assert isinstance(universe, ContinuousUniverse)
    mapping = AffineInputMapping(10, 50, universe, "°C", "1")
    coordinate = mapping.Forward(30, unit="°C")

    assert mapping.targetUniverse is universe
    assert universe.Contains(coordinate)
    assert coordinate == 0.5
    assert scale.Fuzzify(coordinate).selectedTerms[0].name == "Med"
    assert mapping.Inverse(coordinate, unit="1") == 30.0


def test_SourceUnitsAndEndpointRepresentationsAreExplicit():
    """Preserve signed endpoint zero and require the declared unit identity."""

    universe = ContinuousUniverse(-1, -0.0, True, True)
    mapping = AffineInputMapping(-0.0, 1, universe, "kN", "1")

    assert copysign(1, mapping.Forward(1, unit="kN")) == -1
    assert copysign(1, mapping.Inverse(-1, unit="1")) == -1

    with pytest.raises(InvalidParameterError, match="must match 'kN'"):
        mapping.Forward(0.5, unit="kn")

    with pytest.raises(FrozenInstanceError):
        mapping.sourceUnit = "N"


@pytest.mark.parametrize("direction", ["Forward", "Inverse"])
def test_PublicErrorsSeparateMissingInvalidAndOutOfRange(direction):
    """Keep missing data distinct from invalid numbers and adjacent overflow."""

    universe = ContinuousUniverse(0, 1, True, True)
    mapping = AffineInputMapping(0, 1, universe, "1", "1")
    operation = getattr(mapping, direction)

    with pytest.raises(MissingObservationError, match="missing"):
        operation(None, unit="1")

    with pytest.raises(InvalidParameterTypeError, match="float or integer"):
        operation(True, unit="1")

    with pytest.raises(InvalidParameterError, match="exactly representable"):
        operation(2**53 + 1, unit="1")

    with pytest.raises(InvalidDomainError, match="outside the closed input interval"):
        operation(nextafter(1, inf), unit="1")


@pytest.mark.parametrize(
    "universe",
    [
        ContinuousUniverse(0, 1, True, False),
        ContinuousUniverse(0, None, True, False),
    ],
)
def test_TargetUniverseMustBeFiniteAndClosed(universe):
    """Reject target universes with an open or unbounded side."""

    with pytest.raises(InvalidDomainError, match="finite and closed"):
        AffineInputMapping(0, 1, universe, "1", "1")


def test_TargetUniverseMustBeContinuousAndExactlyRepresentable():
    """Reject a discrete domain and a closed domain with a lossy integer bound."""

    with pytest.raises(InvalidParameterTypeError, match="ContinuousUniverse"):
        AffineInputMapping(0, 1, DiscreteUniverse((0, 1)), "1", "1")

    universe = ContinuousUniverse(2**53 + 1, 2**53 + 4, True, True)

    with pytest.raises(InvalidParameterError, match="targetUniverse.left.*exactly representable"):
        AffineInputMapping(0, 1, universe, "1", "1")
