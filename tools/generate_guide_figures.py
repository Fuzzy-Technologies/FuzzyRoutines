# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Render reproducible English SVG teaching figures from the actual scalar API.

Install docs/requirements-plots.txt and FuzzyRoutines before execution. The
command has no network access. --output-directory writes only SVG files there;
--check compares existing files without writing. --preview-directory optionally
writes PNGs for visual review. Plotting is a documentation dependency only.
"""

import argparse
import io
import json
import runpy
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fuzzyroutines import (
    Bell,
    Centroid,
    Difference,
    Gaussian,
    HarringtonDesirability,
    Hyperbolic,
    IntegrationDomain,
    Logistic,
    NegationPolicy,
    SampleAlphaCut,
    ScalarFuzzySet,
    SShoulder,
    TNormPolicy,
    Trapezoid,
    Triangle,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COLORS = ("#a99aff", "#4dd8d0", "#ffd166", "#ff8c9d")


def ConfigureStyle() -> None:
    """Fix fonts, SVG identifiers, metadata, and accessible chart contrast."""

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "svg.fonttype": "none",
        "svg.hashsalt": "fuzzyroutines-english-guide-v1",
        "figure.facecolor": "#121829",
        "axes.facecolor": "#121829",
        "axes.edgecolor": "#8490ab",
        "text.color": "#edf0f8",
        "axes.labelcolor": "#edf0f8",
        "xtick.color": "#c6cede",
        "ytick.color": "#c6cede",
        "grid.color": "#8490ab",
        "grid.alpha": 0.2,
        "axes.prop_cycle": matplotlib.cycler(color=COLORS),
    })


def NewFigure(title: str, panels: int = 1):
    """Create spacious axes with a consistent grade scale and visible provenance."""

    figure, axes = plt.subplots(1, panels, figsize=(10.8, 5.3), squeeze=False)
    figure.suptitle(title, fontsize=18, fontweight="bold", x=0.06, ha="left")
    figure.subplots_adjust(left=0.08, right=0.96, top=0.80, bottom=0.22, wspace=0.28)
    figure.text(0.06, 0.055, "FuzzyRoutines  ·  scalar API  ·  illustrative model, not fitted data", fontsize=9, color="#aab6cf")
    for axis in axes[0]:
        axis.set_ylim(-0.04, 1.08)
        axis.set_yticks((0, 0.25, 0.5, 0.75, 1))
        axis.set_ylabel("Membership grade")
        axis.grid(True)
        axis.spines[["top", "right"]].set_visible(False)
    return figure, tuple(axes[0])


def DrawCurves(axis, models, left: float, right: float, xlabel: str) -> None:
    """Sample actual API callables at 401 coordinates for display only."""

    coordinates = tuple(left + (right - left) * index / 400 for index in range(401))
    for label, evaluator in models:
        axis.plot(coordinates, [evaluator(coordinate) for coordinate in coordinates], label=label, linewidth=2.5)
    axis.set_xlim(left, right)
    axis.set_xlabel(xlabel)
    axis.legend(loc="upper center", bbox_to_anchor=(0.5, 1.19), ncol=min(3, len(models)), frameon=False, fontsize=10)


def DrawScale(axis, scale, left: float, right: float, xlabel: str) -> None:
    """Draw the exact model functions underlying the executable scale example."""

    DrawCurves(axis, tuple((term.name, term.fuzzySet.Membership) for term in scale.terms), left, right, xlabel)


def BuildFigures() -> dict:
    """Run the eight scenario assertions and draw their explanatory figures."""

    guide = runpy.run_path(str(PROJECT_ROOT / "examples" / "guide.py"))
    scenarioResults = {name: scenario() for name, scenario in guide["SCENARIOS"].items()}
    figures = {}

    figure, (axis,) = NewFigure("From a temperature to linguistic labels")
    scale = guide["ComfortScale"]()
    DrawScale(axis, scale, 0, 40, "Temperature (°C)")
    axis.axvline(24, color="#edf0f8", linestyle="--", linewidth=1)
    axis.scatter((24, 24), (2 / 3, 1 / 8), c=COLORS[:2], s=65, zorder=5)
    axis.annotate("24 °C: Comfort = 0.667", (24, 2 / 3), xytext=(26, 0.70), fontsize=10)
    figures["temperature"] = figure

    figure, (axis,) = NewFigure("A winning label can still be too weak")
    DrawScale(axis, guide["RiskScale"](), 0, 100, "Illustrative severity score")
    axis.axhline(0.45, color="#edf0f8", linestyle="--", linewidth=1, label="Abstention threshold")
    axis.axvline(65, color="#edf0f8", linestyle=":", linewidth=1)
    axis.scatter((65, 65), (0.4, 0.28125), c=COLORS[1:3], s=65, zorder=5)
    axis.text(3, 0.48, "minimumConfidence = 0.45", fontsize=10)
    figures["risk"] = figure

    figure, (axis,) = NewFigure("Combine grades after measuring each physical quantity")
    labels = ("Temperature\ngrade", "Vibration\ngrade", "Minimum\nAND", "Product\nAND", "Maximum\nOR", "Algebraic\nOR")
    sensorResults = scenarioResults["sensors"]
    grades = tuple(sensorResults[name] for name in (
        "temperatureGrade", "vibrationGrade", "logicAnd", "productAnd", "logicOr", "algebraicOr",
    ))
    bars = axis.bar(labels, grades, color=(COLORS[0], COLORS[1], COLORS[2], COLORS[2], COLORS[3], COLORS[3]), width=0.6)
    axis.bar_label(bars, labels=[f"{grade:g}" for grade in grades], padding=6, color="#edf0f8")
    axis.set_xlabel("80 °C and 10 mm/s → grades → explicit scalar policies")
    figures["sensors"] = figure

    figure, (axis,) = NewFigure("Warning without critical: a directed fuzzy difference")
    warning, critical = guide["AlarmSets"]()
    difference = Difference(warning, critical, TNormPolicy("logic"), NegationPolicy("standard"))
    DrawCurves(axis, (("Warning", warning.Membership), ("Critical", critical.Membership), ("Warning AND NOT critical", difference.Membership)), 40, 120, "Temperature (°C)")
    axis.axvline(100, color="#edf0f8", linestyle="--", linewidth=1)
    figures["alarm"] = figure

    figure, (axis,) = NewFigure("An α-cut: exact discrete points versus a sampled continuous model")
    model = Triangle(10, 12, 14)
    DrawCurves(axis, (("Continuous triangle", model),), 10, 14, "Quality score")
    sampled = SampleAlphaCut(ScalarFuzzySet(guide["ClosedUniverse"](10, 14), model), 0.5, IntegrationDomain(10, 14), sampleCount=9)
    axis.axhline(0.5, color=COLORS[2], linestyle="--", linewidth=1.5)
    axis.scatter(sampled.coordinates, sampled.grades, c=COLORS[1], s=40, zorder=4)
    axis.scatter((11, 12, 13), (0.5, 1, 0.5), facecolors="none", edgecolors=COLORS[2], s=150, linewidth=2, zorder=5)
    axis.text(10.05, 0.57, "α = 0.5; circles mark the discrete cut", fontsize=10)
    figures["alpha-cuts"] = figure

    figure, (axis,) = NewFigure("Centroid accuracy depends on how moments are computed")
    fuzzySet = ScalarFuzzySet(guide["ClosedUniverse"](0, 8), Triangle(0, 2, 8))
    DrawCurves(axis, (("Triangle membership", fuzzySet.Membership),), 0, 8, "Coordinate")
    coordinates = (0, 8 / 3, 16 / 3, 8)
    axis.plot(coordinates, [fuzzySet.Membership(coordinate) for coordinate in coordinates], "o--", color=COLORS[1], linewidth=1.5)
    centroid = Centroid(fuzzySet, IntegrationDomain(0, 8))
    coarse = guide["GridCentroid"](fuzzySet, coordinates)
    axis.axvline(centroid, color=COLORS[2], linewidth=2)
    axis.axvline(coarse, color=COLORS[3], linestyle="--", linewidth=2)
    axis.text(4.1, 0.88, "Analytical moments: 3.333333\nUser-side 4-point trapezoids: 3.555556", fontsize=10)
    figures["centroid"] = figure

    figure, axes = NewFigure("Audit ties and gaps before using a linguistic scale", panels=2)
    for axis, gappy in zip(axes, (False, True), strict=True):
        DrawScale(axis, guide["AuditScale"](gappy=gappy), 0, 10, "Score (11 audit coordinates)")
        axis.set_title("Overlap and tie" if not gappy else "Uncovered coordinates", fontsize=12, pad=34)
        axis.axvline(5, color="#edf0f8", linestyle="--", linewidth=1)
        if gappy:
            axis.scatter((0, 4, 5, 6, 10), (0, 0, 0, 0, 0), color=COLORS[2], s=50, zorder=4, clip_on=False)
    figures["scale-audit"] = figure

    figure, (axis,) = NewFigure("Normalize the declared discrete universe, preserving the original")
    axis.scatter((0, 25, 50), (0, 0.25, 0.5), s=85, color=COLORS[0], label="Original: height = 0.5")
    axis.scatter((0, 25, 50), (0, 0.5, 1), s=160, facecolors="none", edgecolors=COLORS[1], linewidth=2, label="Normalized: height = 1")
    axis.set_xlim(-5, 55)
    axis.set_xlabel("Declared discrete quality scores (no interpolation)")
    axis.legend(loc="upper left", frameon=False)
    figures["custom"] = figure

    figure, axes = plt.subplots(2, 4, figsize=(13, 7))
    figure.suptitle("Eight analytical membership families", fontsize=20, fontweight="bold")
    models = (
        ("Hyperbolic(1, 2, 0)", Hyperbolic(1, 2, 0), -3, 3),
        ("Bell(-2, -1, 1)", Bell(-2, -1, 1), -3, 3),
        ("SShoulder(-2, 2)", SShoulder(-2, 2), -3, 3),
        ("Triangle(-2, 0, 2)", Triangle(-2, 0, 2), -3, 3),
        ("Trapezoid(-2, -1, 1, 2)", Trapezoid(-2, -1, 1, 2), -3, 3),
        ("Gaussian(0, 1)", Gaussian(0, 1), -3, 3),
        ("Logistic(2, 0)", Logistic(2, 0), -3, 3),
        ("HarringtonDesirability()", HarringtonDesirability(), -3, 3),
    )
    for axis, (label, evaluator, left, right) in zip(axes.flat, models, strict=True):
        coordinates = tuple(left + (right - left) * index / 400 for index in range(401))
        axis.plot(coordinates, [evaluator(coordinate) for coordinate in coordinates], linewidth=2.5)
        axis.set(title=label, xlabel="Coordinate", ylabel="Grade", ylim=(-0.04, 1.08))
        axis.grid(True)
    figure.tight_layout(rect=(0, 0.035, 1, 0.93))
    figure.text(0.025, 0.015, "401 display samples per curve · parameters are illustrative · tails extend beyond the displayed interval", fontsize=10)
    figures["membership-families"] = figure
    return figures


def RenderSvg(figure, name: str) -> bytes:
    """Remove timestamps and fix descriptive SVG metadata for byte comparisons."""

    buffer = io.BytesIO()
    figure.savefig(buffer, format="svg", metadata={
        "Date": None,
        "Creator": "FuzzyRoutines documentation",
        "Title": f"FuzzyRoutines: {name}",
        "Description": "Computed using the scalar public API; see the accompanying worked scenario.",
    })
    rendered = b"\n".join(line.rstrip() for line in buffer.getvalue().splitlines()) + b"\n"
    header = (
        b"<!--\nSPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies\n"
        b"SPDX-License-Identifier: Apache-2.0\n-->\n"
    )
    declarationEnd = rendered.index(b"\n") + 1
    return rendered[:declarationEnd] + header + rendered[declarationEnd:]


def Main(arguments=None) -> int:
    """Write or compare explicit SVG artifacts and optionally emit review PNGs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", required=True, type=Path, dest="outputDirectory")
    parser.add_argument("--preview-directory", type=Path, dest="previewDirectory")
    parser.add_argument("--check", action="store_true")
    parsedArguments = parser.parse_args(arguments)
    ConfigureStyle()
    if not parsedArguments.check:
        parsedArguments.outputDirectory.mkdir(parents=True, exist_ok=True)
    if parsedArguments.previewDirectory is not None:
        parsedArguments.previewDirectory.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, figure in BuildFigures().items():
        destination = parsedArguments.outputDirectory / f"{name}.svg"
        rendered = RenderSvg(figure, name)
        if parsedArguments.check:
            if not destination.is_file() or destination.read_bytes() != rendered:
                raise RuntimeError(f"stale or missing figure: {destination}")
        else:
            destination.write_bytes(rendered)
        if parsedArguments.previewDirectory is not None:
            figure.savefig(parsedArguments.previewDirectory / f"{name}.png", dpi=120)
        plt.close(figure)
        results[name] = len(rendered)
    print(json.dumps({"checked": parsedArguments.check, "svgBytes": results}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
