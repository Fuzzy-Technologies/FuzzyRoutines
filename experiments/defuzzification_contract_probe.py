# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Verify exact reference values for the proposed defuzzification measures."""

from fractions import Fraction


def CheckDiscreteReferences() -> None:
    """Verify atomic moments, half-mass crossings and maximum ties."""

    weighted_mass = Fraction(1, 4) + 1 + 1
    weighted_moment = 0 * Fraction(1, 4) + 2 + 10
    assert weighted_moment / weighted_mass == Fraction(16, 3), "Atomic centroid has no cell widths"
    assert Fraction(1, 4) < weighted_mass / 2 <= Fraction(5, 4), "The atom at 2 crosses half the mass"
    assert Fraction(2 + 10, 2) == 6, "Both maximum-grade coordinates have equal weight"

    tied_mass = Fraction(1 + 0 + 1)
    assert 1 == tied_mass / 2, "The atom at 0 reaches half before the gap"
    assert Fraction(0 + 10, 2) == 5, "The tied maximum mean can lie outside the declared points"


def CheckContinuousReferences() -> None:
    """Verify interval areas, first moments and plateau weighting."""

    original_area = 2 + 2
    original_moment = 2 * 1 + 2 * 5
    assert Fraction(original_moment, original_area) == 3, "Equal plateaus center at the gap midpoint"
    assert 2 == Fraction(original_area, 2), "The cumulative area first reaches half at 2"

    truncated_area = 1 + 2
    truncated_moment = Fraction(3, 2) + 2 * 5
    assert truncated_moment / truncated_area == Fraction(23, 6), "Truncation alters the centroid"
    assert 1 + (Fraction(9, 2) - 4) == Fraction(truncated_area, 2), "The truncated bisector lies on the second plateau"

    maximal_length = 1 + 2
    maximal_moment = Fraction(1, 2) + 2 * 4
    assert maximal_moment / maximal_length == Fraction(17, 6), "The isolated peak adds no plateau length"

    # For g(x) = x / 2 on [0, 2], A(x) = x² / 4 and M(x) = x³ / 6.
    rising_area = Fraction(2**2, 4)
    rising_moment = Fraction(2**3, 6)
    assert rising_moment / rising_area == Fraction(4, 3), "The continuous ramp centroid differs from its sampled atomic mean"
    assert 4 * (rising_area / 2) == 2, "The positive ramp bisector is the square root of two"


def Main() -> None:
    """Run the hand-derived witnesses without importing the package."""

    CheckDiscreteReferences()
    CheckContinuousReferences()
    print("Discrete and continuous defuzzification witnesses passed")


if __name__ == "__main__":
    Main()
