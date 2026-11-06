# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Optional headless export of scalar membership sets, callables and scales."""

from math import isfinite
from os import PathLike
from pathlib import Path
from typing import cast

from fuzzyroutines._plot_export import WritePlotExport, _PlotFormat
from fuzzyroutines._plot_render import PlotSeries, RenderPlot
from fuzzyroutines._plot_sampling import (
    PlotSamplingError,
    SampleDiscretePlot,
    SampleSegmentedPlot,
    _CheckPlotSampleCount,
)
from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse
from fuzzyroutines.exceptions import InvalidDomainError, InvalidParameterTypeError
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.linguistic import LinguisticScale, LinguisticTerm
from fuzzyroutines.membership import (
    MembershipCallable,
    MembershipScalar,
    _GetAnalyticalSource,
)
from fuzzyroutines.numeric import _RequireFiniteReal

__all__ = ["ExportMembershipPlot", "PlotSamplingError"]

type _Window = tuple[MembershipScalar, MembershipScalar]
type _Sample = tuple[MembershipScalar, MembershipScalar]

_KNOT_KEYS = {
    "Hyperbolic": ("c",),
    "Bell": ("a", "b", "c"),
    "Parabolic": ("a", "b"),
    "Triangle": ("a", "b", "c"),
    "Trapezium": ("a", "b", "c", "d"),
    "Exponential": ("a",),
    "Sigmoidal": ("b",),
}


def ExportMembershipPlot(
    source: ScalarFuzzySet | LinguisticScale | MembershipCallable,
    destination: str | PathLike[str],
    *,
    universe: ContinuousUniverse | DiscreteUniverse | None = None,
    displayWindow: _Window | None = None,
    sampleCount: int = 401,
    title: str = "Membership functions",
    coordinateLabel: str = "Coordinate",
    formatName: str | None = None,
    background: str | None = None,
    transparent: bool = False,
    overwrite: bool = False,
    svgTextAsPaths: bool = False,
) -> Path:
    """Export the scalar membership data as a headless scientific figure.

    Discrete universes and unrecognized callables use unconnected markers.
    Supported built-in formulas use paths split at known discontinuities.
    All grades come from the scalar set evaluator, and overlays retain the
    term order and common coordinate units declared by the caller.

    Args:
        source: Scalar fuzzy set, ordered scale or standalone membership callable.
        destination: Explicit output path ending in `.png`, `.jpg`, `.jpeg` or `.svg`.
        universe: Required universe for a standalone callable only.
        displayWindow: Inclusive finite increasing limits. The default spans
            the bounded term universes, with axis padding for a singleton.
        sampleCount: Base sample count per visible continuous segment, at least two.
        title: Literal figure title and SVG metadata title.
        coordinateLabel: Literal coordinate label, including any known units.
        formatName: Optional format, which must agree with the filename suffix.
        background: Explicit opaque `#RRGGBB` color required for JPEG.
        transparent: Whether the PNG or SVG canvas and axes are transparent.
        overwrite: Allow atomic replacement of the destination.
        svgTextAsPaths: Export SVG labels as glyph outlines.

    Returns:
        The absolute path of the published figure.

    Raises:
        InvalidParameterTypeError: If the source, universe or coordinate types are unsuitable.
        InvalidParameterError: If the sample count, labels or format options are invalid.
        InvalidDomainError: If the display window or grid is invalid or has no samples.
        PlotSamplingError: If the scalar source fails at a visible coordinate.
        ImportError: If the optional Matplotlib backend is unavailable.
        OSError: If the destination cannot be published, including a collision.
    """

    terms = _PlotTerms(source, universe)
    window = _PlotWindow(terms, displayWindow)
    _CheckPlotSampleCount(sampleCount)

    def Encode(outputFormat: _PlotFormat) -> bytes:
        """Sample only after format and destination validation, then render to memory."""

        series = tuple(_PreparePlotSeries(term, window, sampleCount) for term in terms)

        return RenderPlot(
            series, window, outputFormat, title=title, coordinateLabel=coordinateLabel,
            background=background, transparent=transparent, svgTextAsPaths=svgTextAsPaths,
        )

    return WritePlotExport(
        Path(destination), Encode, formatName=formatName, background=background,
        transparent=transparent, overwrite=overwrite,
    )


def _PlotTerms(
    source: ScalarFuzzySet | LinguisticScale | MembershipCallable,
    universe: ContinuousUniverse | DiscreteUniverse | None,
) -> tuple[LinguisticTerm, ...]:
    """Normalize plot sources to declared terms without evaluating them."""

    if isinstance(source, (LinguisticScale, ScalarFuzzySet)):
        if universe is not None:
            raise InvalidDomainError("Supply a universe only for a standalone membership callable.")

        return source.terms if isinstance(source, LinguisticScale) else (LinguisticTerm("Membership", source),)

    if universe is None:
        raise InvalidDomainError("A standalone membership callable requires an explicit universe.")

    return (LinguisticTerm("Membership", ScalarFuzzySet(universe, source)),)


def _PlotWindow(terms: tuple[LinguisticTerm, ...], displayWindow: _Window | None) -> _Window:
    """Select finite display limits from the declared universes or caller bounds."""

    if displayWindow is None:
        bounds = []

        for term in terms:
            universe = term.fuzzySet.universe

            if isinstance(universe, DiscreteUniverse):
                bounds.append((universe.points[0], universe.points[-1]))

            elif universe.left is None or universe.right is None:
                raise InvalidDomainError("An unbounded plot universe requires an explicit display window.")

            else:
                bounds.append((universe.left, universe.right))

        left = min(cast(float, lower) for lower, _ in bounds)
        right = max(cast(float, upper) for _, upper in bounds)

        if left == right:
            point = float(left)
            padding = max(abs(point) * 0.05, 0.5)
            lower, upper = point - padding, point + padding
            left, right = lower if isfinite(lower) else point, upper if isfinite(upper) else point

    else:
        if not isinstance(displayWindow, tuple) or len(displayWindow) != 2:
            raise InvalidParameterTypeError("Plot display window must be a tuple of two real coordinates.")

        left = _RequireFiniteReal(displayWindow[0], "left display limit")
        right = _RequireFiniteReal(displayWindow[1], "right display limit")

    if left >= right or float(left) >= float(right):
        raise InvalidDomainError("Plot display window must have distinct increasing display limits.")

    return left, right


def _PreparePlotSeries(term: LinguisticTerm, window: _Window, sampleCount: int) -> PlotSeries:
    """Assign artists only where scalar or declared analytic geometry supports them."""

    fuzzySet = term.fuzzySet
    universe = fuzzySet.universe

    if isinstance(universe, DiscreteUniverse):
        return PlotSeries(term.name, markers=SampleDiscretePlot(fuzzySet, term.name, window=window))

    source = _GetAnalyticalSource(fuzzySet.membershipFunction) if type(fuzzySet).Membership is ScalarFuzzySet.Membership else None
    parameters = source.parameters if source is not None else {}
    knots = tuple(parameters[key] for key in _KNOT_KEYS.get(source.name, ())) if source is not None else ()
    triangle = (parameters["a"], parameters["c"], parameters["b"]) if source is not None and source.name == "Triangle" else None
    breaks = (triangle[1],) if triangle is not None and triangle[1] == triangle[2] else ()
    sampled = SampleSegmentedPlot(
        fuzzySet, term.name, window, breakCoordinates=breaks,
        samplesPerSegment=sampleCount, extraCoordinates=knots,
    )

    if source is None:
        return PlotSeries(term.name, markers=tuple(sample for segment in sampled.segments for sample in segment.samples))

    paths = tuple(segment.samples for segment in sampled.segments)
    limits = _TriangleLimits(universe, window, triangle) if triangle is not None else ()

    return PlotSeries(term.name, paths, sampled.breakMarkers, limits)


def _TriangleLimits(
    universe: ContinuousUniverse, window: _Window, triangle: tuple[MembershipScalar, MembershipScalar, MembershipScalar],
) -> tuple[_Sample, ...]:
    """Use formula limits at the triangle's declared knots without endpoint evaluation."""

    start, peak, end = cast(tuple[float, float, float], triangle)
    left, right = cast(tuple[float, float], window)
    limits: list[_Sample] = []

    if universe.left == start and not universe.leftClosed and left <= start < right:
        limits.append((start, 0))

    if universe.right == end and not universe.rightClosed and left < end <= right:
        limits.append((end, 1 if peak == end else 0))

    if peak == end and left <= peak < right and (universe.left is None or cast(float, universe.left) <= peak) and (
        universe.right is None or peak < cast(float, universe.right)
    ):
        limits.append((peak, 0))

    return tuple(limits)
