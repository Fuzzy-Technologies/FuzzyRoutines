# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Collect scalar plot samples before conversion to renderer coordinates."""

from typing import cast

from fuzzyroutines.domain import DiscreteUniverse
from fuzzyroutines.exceptions import FuzzyRoutinesError, InvalidDomainError
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.numeric import _RequireFiniteReal


class PlotSamplingError(FuzzyRoutinesError):
    """A scalar evaluation failed while collecting data for a plot series."""


def SampleDiscretePlot(
    fuzzySet: ScalarFuzzySet,
    seriesName: str,
    *,
    window: tuple[MembershipScalar, MembershipScalar] | None = None,
) -> tuple[tuple[MembershipScalar, MembershipScalar], ...]:
    """Collect one marker sample per visible coordinate in declaration order.

    Args:
        fuzzySet: Scalar set with a discrete universe. Its own membership
            evaluator supplies and validates the grades.
        seriesName: Plot series label included in evaluation failures.
        window: Optional inclusive display limits with finite, increasing
            endpoints. Omitting it keeps the entire discrete universe.

    Returns:
        Coordinate and grade pairs in their original scalar types, including
        zero grades. An empty tuple denotes a fully clipped series. A
        singleton yields one marker without any synthetic padding sample.

    Raises:
        InvalidDomainError: If the universe is continuous or the display
            limits are unordered.
        InvalidParameterTypeError: If a display limit is not a real scalar.
        InvalidParameterError: If a display limit is not finite.
        PlotSamplingError: If scalar evaluation fails at a visible point.
            The original exception is retained as the cause.
    """

    universe = fuzzySet.universe

    if not isinstance(universe, DiscreteUniverse):
        raise InvalidDomainError("Discrete plot sampling requires a DiscreteUniverse.")

    points = universe.points

    if window is not None:
        left = _RequireFiniteReal(window[0], "left display limit")
        right = _RequireFiniteReal(window[1], "right display limit")

        if left >= right:
            raise InvalidDomainError("Plot display limits must satisfy left < right.")

        points = tuple(point for point in points if left <= cast(float, point) <= right)

    samples: list[tuple[MembershipScalar, MembershipScalar]] = []

    for point in points:
        try:
            grade = fuzzySet.Membership(point)

        except Exception as error:
            raise PlotSamplingError(f"Could not sample plot series {seriesName!r} at {point!r}.") from error

        samples.append((point, grade))

    return tuple(samples)
