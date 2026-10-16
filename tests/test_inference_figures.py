# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Compare inference teaching graphics with independent elementary formulas."""

import json
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = runpy.run_path(str(PROJECT_ROOT / "tools/generate_inference_figures.py"))
buildFigures = GENERATOR["BuildFigures"]
configureStyle = GENERATOR["configureStyle"]
renderSvg = GENERATOR["renderSvg"]
plt = GENERATOR["plt"]


@pytest.fixture(scope="module", name="inferenceFigures")
def InferenceFigures():
    """Build the exact artists once and close the plotting resources afterward."""

    configureStyle()
    figures = buildFigures()

    yield figures

    for figure in figures.values():
        plt.close(figure)


def test_MamdaniPlotUsesReferenceCurvesAndCentroid(inferenceFigures):
    """Check every displayed sample against the hand-derived max-min envelope."""

    axes = inferenceFigures["inference-mamdani"].axes
    references = (
        (0, 0, lambda x: 1 - x),
        (0, 1, lambda x: x),
        (2, 0, lambda x: min(0.75, 1 - x)),
        (2, 1, lambda x: min(0.25, x)),
        (3, 0, lambda x: max(min(0.75, 1 - x), min(0.25, x))),
    )

    for axisIndex, lineIndex, reference in references:
        line = axes[axisIndex].lines[lineIndex]
        assert list(line.get_ydata()) == pytest.approx([reference(x) for x in line.get_xdata()], rel=0, abs=1e-14), "Plotted membership must match its independently derived formula"

    assert list(axes[3].lines[1].get_xdata()) == pytest.approx([37 / 96] * 2, rel=0, abs=1e-12), "Centroid marker must match the exact moment ratio"
    assert [bar.get_height() for bar in axes[1].patches] == [0.75, 0.25], "Firing bars must preserve rule order and degrees"


def test_SugenoPlotShowsConsequencesAndWeightedContributions(inferenceFigures):
    """Verify all bars against rational zero/first-order rule calculations."""

    axes = inferenceFigures["inference-sugeno"].axes
    assert [bar.get_height() for bar in axes[0].patches] == pytest.approx([0.2, 0.8, 0.15, 0.2], rel=0, abs=1e-15), "Zero-order plot must separate consequences from contributions"
    assert [bar.get_height() for bar in axes[1].patches] == [0.125, 0.625, 0.09375, 0.15625], "First-order plot must show the evaluated affine consequences"


def test_InferenceFiguresAreDeterministicAndCurrent(inferenceFigures):
    """Require committed SVG bytes to match deterministic regenerated plots."""

    directory = Path(__file__).parents[1] / "docs/site/content/en/assets/figures"

    for name, figure in inferenceFigures.items():
        assert renderSvg(figure, name) == (directory / f"{name}.svg").read_bytes(), "Committed inference graph must be regenerated after changing the model or plotting code"


def test_InferenceFigureCliDoesNotRequireCheckoutToolsOnImportPath(tmpPath):
    """Run the direct script with only the core package exposed to imports.

    This local regression exercises helper isolation; CI separately runs the
    command with -I against the built wheel from outside the source checkout.
    """

    packageRoot = tmpPath / "package"
    shutil.copytree(PROJECT_ROOT / "fuzzyroutines", packageRoot / "fuzzyroutines", ignore=shutil.ignore_patterns("__pycache__"))
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(packageRoot)
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "tools/generate_inference_figures.py"),
         "--output-directory", str(PROJECT_ROOT / "docs/site/content/en/assets/figures"), "--check"],
        cwd=tmpPath, env=environment, capture_output=True, text=True, check=False, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["checked"] is True
    assert set(report["svgBytes"]) == {"inference-mamdani", "inference-sugeno", "inference-support"}


def test_SupportPlotRetainsBothContributions(inferenceFigures):
    """Verify the audit figure against independent triangle areas and centers."""

    axis = inferenceFigures["inference-support"].axes[0]
    expected = (0.02 * 0.18 + 0.15 * 0.75) / 0.17

    assert list(axis.lines[2].get_xdata()) == pytest.approx([expected, expected], rel=0, abs=1e-14), "The marker must include both triangle moments"

    for line, shape in zip(axis.lines[:2], ((0.16, 0.18, 0.20), (0.60, 0.75, 0.90)), strict=True):
        left, peak, right = shape
        values = [max(0, min((coordinate - left) / (peak - left), (right - coordinate) / (right - peak))) for coordinate in line.get_xdata()]
        assert list(line.get_ydata()) == pytest.approx(values, rel=0, abs=1e-14), "Displayed triangles must match their independent piecewise definitions"
