# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Headless historical-scale and illustrative risk recipes for an installed wheel.

Only the standard library and FuzzyRoutines are needed for JSON computation.
Plotting is an explicit optional Matplotlib dependency. The command performs no
network requests, rejects unsupported Python or mismatched package versions,
and writes only requested output files. Membership grades are not probabilities.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fuzzyroutines import LinguisticScale

SUPPORTED_PYTHON = ((3, 13), (3, 14))
TERM_NAMES = ("Min", "Low", "Med", "High", "Max")
COLORS = ("#a99aff", "#4dd8d0", "#ffd166", "#ff8c9d", "#8cdb91")
ABSOLUTE_TOLERANCE = 1e-12
COEFFICIENTS = (
    {"name": "Min", "family": "Hyperbolic", "parameters": [8, 20, 0], "centroidWindow": [0, 0.23]},
    {"name": "Low", "family": "Bell", "parameters": [0.17, 0.23, 0.34], "centroidWindow": [0.17, 0.40]},
    {"name": "Med", "family": "Bell", "parameters": [0.34, 0.40, 0.60], "centroidWindow": [0.34, 0.66]},
    {"name": "High", "family": "Bell", "parameters": [0.60, 0.66, 0.77], "centroidWindow": [0.60, 0.83]},
    {"name": "Max", "family": "SShoulder", "parameters": [0.77, 0.95], "centroidWindow": [0.77, 1]},
)


def Preflight(expectedVersion: str) -> str:
    """Require tested Python and the exact requested installed distribution.

    Args:
        expectedVersion: Exact release or candidate version installed by the user.

    Returns:
        The verified installed distribution version.

    Raises:
        RuntimeError: Python is unsupported, the package is absent, or its version
            differs. In particular, an old 1.0.3 installation is never accepted.
    """

    if platform.python_implementation() != "CPython" or sys.version_info[:2] not in SUPPORTED_PYTHON:
        raise RuntimeError("Use CPython 3.13 or 3.14 in a fresh environment; Python 3.12 may resolve historical 1.0.3.")

    try:
        installedVersion = importlib.metadata.version("fuzzyroutines")

    except importlib.metadata.PackageNotFoundError as error:
        raise RuntimeError(f"Install the declared wheel first: python -m pip install fuzzyroutines=={expectedVersion}") from error

    if installedVersion != expectedVersion:
        raise RuntimeError(
            f"Expected fuzzyroutines {expectedVersion}, found {installedVersion}. "
            "Use a clean environment and install the exact declared release or candidate wheel."
        )

    if not installedVersion.startswith("2."):
        raise RuntimeError("This recipe requires the modern FuzzyRoutines 2.x API; historical 1.x is unsupported.")

    return installedVersion


def RisingShoulder(coordinate: float, left: float, right: float) -> float:
    """Evaluate the independent piecewise quadratic reference on a finite interval."""

    if coordinate <= left:
        return 0.0

    if coordinate >= right:
        return 1.0

    if coordinate <= (left + right) / 2:
        return 2 * ((coordinate - left) / (right - left)) ** 2

    return 1 - 2 * ((right - coordinate) / (right - left)) ** 2


def ReferenceGrades(coordinate: float) -> tuple[float, ...]:
    """Evaluate the five historical formulas without calling FuzzyRoutines."""

    grades = [1 / (1 + (8 * coordinate) ** 20)]

    for left, plateauLeft, plateauRight in ((0.17, 0.23, 0.34), (0.34, 0.40, 0.60), (0.60, 0.66, 0.77)):
        grades.append(min(
            RisingShoulder(coordinate, left, plateauLeft),
            1 - RisingShoulder(coordinate, plateauRight, plateauRight + plateauLeft - left),
        ))

    grades.append(RisingShoulder(coordinate, 0.77, 0.95))

    return tuple(grades)


def BuildScale() -> LinguisticScale:
    """Construct the historical coefficients using only the published 2.0 root API.

    Every term uses the closed universe [0, 1]. Historical centroid windows are
    metadata, not clipping bounds. Newer factory APIs are not required here.
    """

    from fuzzyroutines import (
        Bell,
        ContinuousUniverse,
        Hyperbolic,
        LinguisticScale,
        LinguisticTerm,
        ScalarFuzzySet,
        SShoulder,
    )

    universe = ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True)
    models = (Hyperbolic(8, 20, 0), Bell(0.17, 0.23, 0.34), Bell(0.34, 0.40, 0.60),
              Bell(0.60, 0.66, 0.77), SShoulder(0.77, 0.95))

    return LinguisticScale(tuple(
        LinguisticTerm(name, ScalarFuzzySet(universe, model))
        for name, model in zip(TERM_NAMES, models, strict=True)
    ))


def BuildReport(scenario: str, value: float, installedVersion: str) -> dict[str, Any]:
    """Calculate grades, selection and independent numerical checks.

    Args:
        scenario: `universal-fuzzy-scale` accepts [0, 1]; `risk` accepts [0, 100].
        value: Finite illustrative score. Risk uses the declared linear x = score/100
            convention; no observations are fitted and no score is clamped.
        installedVersion: Distribution version already checked by `Preflight`.

    Returns:
        JSON-compatible evidence with all parameters, explicit policies and checks.

    Raises:
        ValueError: The scenario or input domain is invalid.
        ArithmeticError: The public API disagrees with independent reference values.
    """

    from fuzzyroutines import FuzzificationPolicy

    if scenario not in ("universal-fuzzy-scale", "risk"):
        raise ValueError(f"Unknown recipe: {scenario}")

    upperBound = 100.0 if scenario == "risk" else 1.0

    if not math.isfinite(value) or not 0 <= value <= upperBound:
        raise ValueError(f"{scenario} requires a finite value in [0, {upperBound:g}]; define normalization before classification.")

    coordinate = value / upperBound
    threshold = 0.1 if scenario == "risk" else 0.0
    scale = BuildScale()
    policy = FuzzificationPolicy(tiePolicy="last", tieTolerance=0, minimumConfidence=threshold)
    result = scale.Fuzzify(coordinate, policy)
    checkedCoordinates = (0, 0.125, 0.17, 0.2, 0.37, 0.5, 0.63, 0.75, 0.81, 0.86, 1, coordinate)
    maximumError = 0.0

    for checkedCoordinate in checkedCoordinates:
        actual = scale.Fuzzify(checkedCoordinate, policy)

        for item, expected in zip(actual.memberships, ReferenceGrades(checkedCoordinate), strict=True):
            error = abs(float(item.grade) - expected)
            maximumError = max(maximumError, error)

            if error > ABSOLUTE_TOLERANCE:
                raise ArithmeticError(f"Reference mismatch for {item.term.name} at {checkedCoordinate}: error={error}")

    return {
        "schemaVersion": 1,
        "recipeVersion": "1.0",
        "scenario": scenario,
        "environment": {"python": platform.python_version(), "fuzzyroutines": installedVersion},
        "input": {"value": value, "range": [0, upperBound], "normalizedCoordinate": coordinate,
                  "normalization": "x = score / 100" if scenario == "risk" else "already normalized"},
        "scale": {"name": "Historical Universal Fuzzy Scale", "universe": [0, 1],
                  "closedBoundaries": True, "terms": COEFFICIENTS},
        "policy": {"tiePolicy": "last", "tieTolerance": 0, "minimumConfidence": threshold,
                   "noMatch": "maximum membership <= minimumConfidence"},
        "result": {"memberships": {item.term.name: item.grade for item in result.memberships},
                   "maximumMembership": result.confidence,
                   "selectedTerms": [term.name for term in result.selectedTerms], "isMatch": result.isMatch},
        "checks": {"passed": True, "method": "independent piecewise formulas at declared coordinates",
                   "coordinates": checkedCoordinates, "absoluteTolerance": ABSOLUTE_TOLERANCE,
                   "relativeTolerance": 0, "maximumAbsoluteError": maximumError},
        "interpretation": {"gradesAreProbabilities": False, "normalizationIsIllustrative": scenario == "risk",
                           "weakCoverage": "Near x=0.17, the greatest membership is about 0.00212959; a 0.1 threshold abstains.",
                           "centroidWindows": "Retained for provenance only; never used to clip these curves.",
                           "tieBehavior": "Last exact maximum; floating-point near ties are not exact ties."},
        "artifacts": [],
    }


def DrawPlot(report: dict[str, Any], outputPath: Path) -> dict[str, Any]:
    """Save a deterministic headless SVG or PNG with curves and score interpretation.

    Args:
        report: Verified evidence produced by `BuildReport`.
        outputPath: Requested .svg or .png file; its parent directory must exist.

    Returns:
        Artifact path, format, content hash, and actual plotting dependency version.

    Raises:
        RuntimeError: Matplotlib is not installed.
        ValueError: The output extension is unsupported.
    """

    if outputPath.suffix not in (".svg", ".png"):
        raise ValueError("--plot must name an .svg or .png file")

    try:
        import matplotlib

    except ImportError as error:
        raise RuntimeError("Plotting is optional: install the documented requirements-plots.txt first, or omit --plot.") from error

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with plt.rc_context({
        "font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
        "svg.hashsalt": "fuzzyroutines-agent-recipe-v1", "figure.facecolor": "#121829",
        "axes.facecolor": "#121829", "axes.edgecolor": "#8490ab", "text.color": "#edf0f8",
        "axes.labelcolor": "#edf0f8", "xtick.color": "#c6cede", "ytick.color": "#c6cede",
        "grid.color": "#8490ab", "grid.alpha": 0.2,
    }):
        figure, axes = plt.subplots(1, 2, figsize=(11.5, 5.2), width_ratios=(1.4, 1))
        coordinate = report["input"]["normalizedCoordinate"]
        figure.suptitle("Historical scale → an input score → linguistic levels", x=0.06, ha="left", fontsize=17, fontweight="bold")
        figure.subplots_adjust(left=0.07, right=0.97, bottom=0.25, top=0.78, wspace=0.3)
        coordinates = [index / 400 for index in range(401)]
        scale = BuildScale()

        for term, color in zip(scale.terms, COLORS, strict=True):
            axes[0].plot(coordinates, [term.fuzzySet.Membership(item) for item in coordinates], color=color, label=term.name, linewidth=2.2)

        axes[0].set(xlabel="Normalized score x", ylabel="Membership grade", xlim=(0, 1), ylim=(-0.03, 1.08))
        axes[0].axvline(coordinate, color="#edf0f8", linestyle="--", linewidth=1)
        axes[0].axvspan(0.15, 0.19, color="#ffffff", alpha=0.08)
        axes[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=5, frameon=False, handlelength=1, columnspacing=0.8)
        axes[0].annotate("Weak coverage", (0.17, 0.04), (0.25, 0.24), fontsize=9,
                         arrowprops={"arrowstyle": "->", "color": "#edf0f8"})
        grades = tuple(report["result"]["memberships"].values())
        axes[1].barh(TERM_NAMES, grades, color=COLORS, height=0.55)
        axes[1].invert_yaxis()
        axes[1].set(xlabel="Membership grade", xlim=(0, 1.24), title=f"Input x = {coordinate:g}")

        for index, grade in enumerate(grades):
            axes[1].text(grade + 0.025, index, f"{grade:.4g}", va="center", fontsize=9)

        threshold = report["policy"]["minimumConfidence"]

        if threshold:
            axes[1].axvline(threshold, color="#edf0f8", linestyle=":", linewidth=1.4)
            axes[1].text(0.98, 0.04, f"Threshold = {threshold:g}", transform=axes[1].transAxes,
                         ha="right", color="#c6cede", fontsize=9)

        for axis in axes:
            axis.grid(True, axis="x")
            axis.spines[["top", "right"]].set_visible(False)

        selected = ", ".join(report["result"]["selectedTerms"]) or "NO MATCH — insufficient membership"
        figure.text(0.07, 0.13, f"Selected: {selected}", fontsize=11, color="#ffd166")
        figure.text(0.07, 0.055, "FuzzyRoutines · original coefficients · grades are not probabilities · illustrative normalization", fontsize=9, color="#aab6cf")
        metadata = {"Creator": "FuzzyRoutines", "Date": None} if outputPath.suffix == ".svg" else {"Software": "FuzzyRoutines"}

        try:
            figure.savefig(outputPath, format=outputPath.suffix[1:], dpi=160, metadata=metadata)

        finally:
            plt.close(figure)

    if outputPath.suffix == ".svg":
        content = outputPath.read_text(encoding="utf-8")
        licenseText = "<!-- SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies\nSPDX-License-Identifier: Apache-2.0 -->\n"
        licensedContent = content.replace("<svg ", licenseText + "<svg ", 1)
        outputPath.write_text("\n".join(line.rstrip() for line in licensedContent.splitlines()) + "\n", encoding="utf-8")

    return {"path": str(outputPath), "format": outputPath.suffix[1:],
            "sha256": hashlib.sha256(outputPath.read_bytes()).hexdigest(), "matplotlib": matplotlib.__version__}


def Main(arguments: list[str] | None = None) -> int:
    """Run an installed-wheel recipe, keeping JSON stdout separate from diagnostics.

    Args:
        arguments: CLI arguments; `None` reads the process command line.

    Returns:
        Zero on success, or two with an actionable stderr diagnostic on failure.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("universal-fuzzy-scale", "risk"), default="universal-fuzzy-scale")
    parser.add_argument("--value", type=float, help="normalized [0,1] coordinate, or illustrative [0,100] risk score")
    parser.add_argument("--expect-version", dest="expectedVersion", default="2.0.0", help="exact installed release or candidate version")
    parser.add_argument("--output", type=Path, help="optional JSON artifact; stdout always contains the same report")
    parser.add_argument("--plot", type=Path, help="optional .svg or .png output; requires Matplotlib")
    args = parser.parse_args(arguments)

    try:
        installedVersion = Preflight(args.expectedVersion)
        value = args.value if args.value is not None else (75.0 if args.scenario == "risk" else 0.2)
        report = BuildReport(args.scenario, value, installedVersion)

        if args.plot is not None:
            if args.output is not None and args.plot.resolve() == args.output.resolve():
                raise ValueError("--plot and --output must name different files")

            report["artifacts"].append(DrawPlot(report, args.plot))

        output = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"

        if args.output is not None:
            args.output.write_text(output, encoding="utf-8")

        sys.stdout.write(output)

    except (RuntimeError, ValueError, ArithmeticError, OSError, ImportError) as error:
        print(f"agent recipe: {error}", file=sys.stderr)

        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
