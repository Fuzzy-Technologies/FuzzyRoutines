# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Optional plotting evidence for installed-wheel agent recipes.

Documentation CI supplies the pinned Matplotlib toolchain. Core-only environments
skip these checks; the library and JSON recipe never require plotting packages.
"""

import runpy
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")
from matplotlib.figure import Figure

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RECIPE = runpy.run_path(str(PROJECT_ROOT / "examples/agent_recipe.py"))


def ShoulderReference(coordinate, left, right):
    """Evaluate the normalized quadratic shoulder independently of the library."""

    fraction = max(0, min(1, (coordinate - left) / (right - left)))

    return 2 * fraction ** 2 if fraction <= 0.5 else 1 - 2 * (1 - fraction) ** 2


def test_AgentPlotUsesVerifiedCurvesAndReportedGrades(tmpPath, monkeypatch):
    """Inspect actual plotted artists, term colors, threshold and abstention label."""

    import matplotlib.pyplot as plt

    plt.switch_backend("Agg")
    captured = []
    originalSave = Figure.savefig

    def CaptureFigure(figure, *args, **kwargs):
        """Retain the actual exported artists without replacing the renderer."""

        captured.append(figure)

        return originalSave(figure, *args, **kwargs)

    monkeypatch.setattr(Figure, "savefig", CaptureFigure)
    report = RECIPE["BuildReport"]("risk", 17, "2.0.0")
    RECIPE["DrawPlot"](report, tmpPath / "risk.svg")
    curveAxis, gradeAxis = captured[0].axes
    references = (
        lambda x: 1 / (1 + (8 * x) ** 20),
        lambda x: min(ShoulderReference(x, 0.17, 0.23), 1 - ShoulderReference(x, 0.34, 0.40)),
        lambda x: min(ShoulderReference(x, 0.34, 0.40), 1 - ShoulderReference(x, 0.60, 0.66)),
        lambda x: min(ShoulderReference(x, 0.60, 0.66), 1 - ShoulderReference(x, 0.77, 0.83)),
        lambda x: ShoulderReference(x, 0.77, 0.95),
    )
    coordinates = [index / 400 for index in range(401)]

    for line, reference, color in zip(curveAxis.lines[:5], references, RECIPE["COLORS"], strict=True):
        assert list(line.get_xdata()) == coordinates
        assert list(line.get_ydata()) == pytest.approx([reference(x) for x in coordinates], abs=1e-12, rel=0)
        assert line.get_color() == color

    assert [bar.get_width() for bar in gradeAxis.patches] == list(report["result"]["memberships"].values())
    assert list(gradeAxis.lines[0].get_xdata()) == [0.1, 0.1]
    assert "NO MATCH" in captured[0].texts[1].get_text()


def test_AgentSvgReproducesCommittedFigureAndPngIsDeterministic(tmpPath):
    """Keep published graph bytes and repeatable PNG output tied to the executable recipe."""

    report = RECIPE["BuildReport"]("risk", 17, "2.0.0")
    svgPath = tmpPath / "risk.svg"
    RECIPE["DrawPlot"](report, svgPath)
    assert svgPath.read_bytes() == (PROJECT_ROOT / "docs/site/content/en/assets/figures/agent-risk.svg").read_bytes()
    first = RECIPE["DrawPlot"](report, tmpPath / "first.png")
    second = RECIPE["DrawPlot"](report, tmpPath / "second.png")
    assert first["sha256"] == second["sha256"], "Fixed data, fonts and metadata must reproduce the same PNG bytes."
