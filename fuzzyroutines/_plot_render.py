# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private optional headless rendering of prepared scalar plot data."""

import importlib
from dataclasses import dataclass
from io import BytesIO
from threading import RLock
from typing import Any

from fuzzyroutines._plot_export import _PlotFormat
from fuzzyroutines.exceptions import InvalidDomainError, InvalidParameterError
from fuzzyroutines.membership import MembershipScalar

_PALETTE = ("#a99aff", "#4dd8d0", "#ffd166", "#ff8c9d", "#8cdb91")
_LINE_STYLES = ("solid", "dashed", "dashdot", "dotted")
_POINT_STYLES = ("o", "s", "D", "^")
_CANVAS_COLOR = "#121829"
_TEXT_COLOR = "#edf0f8"
_TICK_COLOR = "#c6cede"
_GRID_COLOR = "#8490ab"
_RENDER_LOCK = RLock()

type _Sample = tuple[MembershipScalar, MembershipScalar]


@dataclass(frozen=True, slots=True)
class PlotSeries:
    """Prepared membership data in declaration order.

    Attributes:
        label: Legend text, retained even for a clipped series.
        paths: Separate ordered paths with established continuity.
        markers: Discrete samples and isolated actual grades.
    """

    label: str
    paths: tuple[tuple[_Sample, ...], ...] = ()
    markers: tuple[_Sample, ...] = ()


def RenderPlot(
    series: tuple[PlotSeries, ...],
    window: tuple[MembershipScalar, MembershipScalar],
    outputFormat: _PlotFormat,
    *,
    title: str,
    coordinateLabel: str = "Coordinate",
    transparent: bool = False,
    svgTextAsPaths: bool = False,
) -> bytes:
    """Encode a single-panel scientific figure using the optional backend.

    Args:
        series: Prepared data in palette and legend order. The caller must
            separate discontinuous paths and supply no paths for discrete data.
        window: Finite increasing display bounds, already validated.
        outputFormat: PNG or SVG for this rendering stage.
        title: Literal figure title and SVG metadata title.
        coordinateLabel: Literal coordinate label including any declared units.
        transparent: Whether the canvas and axes backgrounds are clear.
        svgTextAsPaths: Whether SVG text becomes outlines.

    Returns:
        Complete PNG or UTF-8 SVG bytes with deterministic metadata and IDs.

    Raises:
        InvalidParameterError: If the format is unsupported or DejaVu Sans
            cannot represent the supplied labels.
        InvalidDomainError: If there are no renderable samples in any series.
        ImportError: If the optional Matplotlib backend is unavailable.
    """

    if outputFormat not in ("png", "svg"):
        raise InvalidParameterError("This renderer supports PNG and SVG.")

    if not any(item.markers or any(item.paths) for item in series):
        raise InvalidDomainError("The display window contains no renderable samples.")

    try:
        matplotlib = importlib.import_module("matplotlib")

    except ModuleNotFoundError as error:
        if error.name == "matplotlib":
            raise ImportError("Scientific plot rendering requires Matplotlib.") from error

        raise

    with _RENDER_LOCK:
        style = {key: matplotlib.rcParamsDefault[key] for key in matplotlib.rcParamsDefault if key != "backend"}
        style.update({
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "figure.facecolor": "none" if transparent else _CANVAS_COLOR,
            "axes.facecolor": "none" if transparent else _CANVAS_COLOR,
            "axes.edgecolor": _GRID_COLOR,
            "axes.formatter.use_locale": False,
            "axes.labelcolor": _TEXT_COLOR,
            "grid.alpha": 0.2,
            "grid.color": _GRID_COLOR,
            "legend.labelcolor": _TEXT_COLOR,
            "text.color": _TEXT_COLOR,
            "text.parse_math": False,
            "svg.fonttype": "path" if svgTextAsPaths else "none",
            "svg.hashsalt": "fuzzyroutines-scientific-plot-v1",
            "xtick.color": _TICK_COLOR,
            "ytick.color": _TICK_COLOR,
        })

        with matplotlib.rc_context(style):
            _CheckPlotGlyphs((title, coordinateLabel, *(item.label for item in series)))
            figure = importlib.import_module("matplotlib.figure").Figure(figsize=(10.8, 5.3), dpi=160)

            try:
                _DrawPlot(figure, series, window, title, coordinateLabel)
                return _EncodePlot(figure, outputFormat, title)

            finally:
                figure.clear()


def _CheckPlotGlyphs(labels: tuple[str, ...]) -> None:
    """Reject unsupported literal text before the renderer attempts font fallback."""

    fontManager = importlib.import_module("matplotlib.font_manager")
    fontPath = fontManager.findfont("DejaVu Sans", fallback_to_default=False)
    font = importlib.import_module("matplotlib.ft2font").FT2Font(fontPath)
    codePoints = font.get_charmap()

    for label in labels:
        for character in label:
            if character != "\n" and ord(character) not in codePoints:
                raise InvalidParameterError(f"DejaVu Sans lacks plot label glyph U+{ord(character):04X}.")


def _DrawPlot(
    figure: Any,
    series: tuple[PlotSeries, ...],
    window: tuple[MembershipScalar, MembershipScalar],
    title: str,
    coordinateLabel: str,
) -> None:
    """Draw each supplied path independently and every marker without a line."""

    axis = figure.add_subplot()
    figure.subplots_adjust(left=0.09, right=0.97, bottom=0.16, top=0.77)
    figure.suptitle(title, fontsize=18, fontweight="bold", y=0.95)
    axis.set_xlim(float(window[0]), float(window[1]))
    axis.set_ylim(0, 1)
    axis.set_yticks((0, 0.25, 0.5, 0.75, 1))
    axis.set_xlabel(coordinateLabel)
    axis.set_ylabel("Membership grade")
    axis.set_axisbelow(True)
    axis.grid(True)
    lineClass = importlib.import_module("matplotlib.lines").Line2D
    handles = []

    for seriesIndex, item in enumerate(series):
        color = _PALETTE[seriesIndex % len(_PALETTE)]
        cycle = seriesIndex // len(_PALETTE)
        lineStyle = _LINE_STYLES[cycle % len(_LINE_STYLES)]
        markerStyle = _POINT_STYLES[cycle % len(_POINT_STYLES)]
        markers = list(item.markers)
        hasPath = False

        for pathIndex, path in enumerate(item.paths):
            if len(path) < 2:
                markers.extend(path)
                continue

            hasPath = True
            coordinates, grades = _PlotValues(path)
            axis.plot(coordinates, grades, color=color, linestyle=lineStyle, gid=f"series-{seriesIndex}-path-{pathIndex}")

        if markers:
            coordinates, grades = _PlotValues(tuple(markers))
            axis.scatter(coordinates, grades, color=color, marker=markerStyle, clip_on=False, gid=f"series-{seriesIndex}-markers")

        handles.append(lineClass(
            [], [], color=color, label=item.label, linestyle=lineStyle if hasPath else "None",
            marker=markerStyle if markers or not hasPath else "None",
        ))

    axis.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncols=min(5, len(handles)), frameon=False)


def _PlotValues(samples: tuple[_Sample, ...]) -> tuple[list[float], list[float]]:
    """Convert exact samples to binary64 only at the artist boundary."""

    return [float(point) for point, _ in samples], [float(grade) for _, grade in samples]


def _EncodePlot(figure: Any, outputFormat: _PlotFormat, title: str) -> bytes:
    """Encode with an explicit local canvas and omit volatile metadata."""

    with BytesIO() as output:
        if outputFormat == "png":
            canvas = importlib.import_module("matplotlib.backends.backend_agg").FigureCanvasAgg(figure)
            canvas.print_png(output, metadata={"Software": "FuzzyRoutines"})

        else:
            canvas = importlib.import_module("matplotlib.backends.backend_svg").FigureCanvasSVG(figure)
            canvas.print_svg(output, metadata={
                "Creator": "FuzzyRoutines",
                "Description": "Scientific membership plot from scalar samples.",
                "Title": title,
                "Date": None,
            })

        return output.getvalue()
