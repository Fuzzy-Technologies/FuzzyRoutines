# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Check plotted data against elementary mathematics independent of the API.

Matplotlib is an optional documentation dependency. Documentation CI installs
it explicitly and runs these checks against the installed library, then checks
the committed SVG bytes. The ordinary dependency-free test run skips this module.
"""

import runpy
from fractions import Fraction
from itertools import pairwise
from math import exp
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLOT_TOOL = runpy.run_path(str(PROJECT_ROOT / "tools" / "generate_guide_figures.py"))


def TriangleReference(coordinate, left, peak, right):
    """Use the two straight-line segments of a nondegenerate triangle."""

    return max(0, min((coordinate - left) / (peak - left), (right - coordinate) / (right - peak)))


def ShoulderReference(coordinate, left, right):
    """Use the normalized quadratic shoulder and reflection about its midpoint."""

    fraction = max(0, min(1, (coordinate - left) / (right - left)))
    if fraction <= 0.5:
        return 2 * fraction**2
    return 1 - 2 * (1 - fraction)**2


@pytest.fixture(scope="module", name="guideFigures")
def GuideFigures():
    """Build exactly the artists that the deterministic SVG exporter serializes."""

    PLOT_TOOL["ConfigureStyle"]()
    figures = PLOT_TOOL["BuildFigures"]()
    yield figures
    for figure in figures.values():
        PLOT_TOOL["plt"].close(figure)


CURVE_REFERENCES = (
    ("temperature", 0, 0, 0, 40, lambda x: TriangleReference(x, 16, 22, 28)),
    ("temperature", 0, 1, 0, 40, lambda x: ShoulderReference(x, 22, 30)),
    ("risk", 0, 0, 0, 100, lambda x: TriangleReference(x, 0, 20, 50)),
    ("risk", 0, 1, 0, 100, lambda x: TriangleReference(x, 25, 50, 75)),
    ("risk", 0, 2, 0, 100, lambda x: ShoulderReference(x, 50, 90)),
    ("alarm", 0, 0, 40, 120, lambda x: ShoulderReference(x, 60, 100)),
    ("alarm", 0, 1, 40, 120, lambda x: ShoulderReference(x, 90, 110)),
    ("alarm", 0, 2, 40, 120, lambda x: min(ShoulderReference(x, 60, 100), 1 - ShoulderReference(x, 90, 110))),
    ("alpha-cuts", 0, 0, 10, 14, lambda x: TriangleReference(x, 10, 12, 14)),
    ("centroid", 0, 0, 0, 8, lambda x: TriangleReference(x, 0, 2, 8)),
    ("operators", 0, 0, 0, 1, lambda x: min(x, 0.6)),
    ("operators", 0, 1, 0, 1, lambda x: 0.6 * x),
    ("operators", 1, 0, 0, 1, lambda x: max(x, 0.6)),
    ("operators", 1, 1, 0, 1, lambda x: x + 0.6 - 0.6 * x),
    ("scale-audit", 0, 0, 0, 10, lambda x: TriangleReference(x, 0, 2, 6)),
    ("scale-audit", 0, 1, 0, 10, lambda x: TriangleReference(x, 4, 8, 10)),
    ("scale-audit", 1, 0, 0, 10, lambda x: TriangleReference(x, 0, 2, 4)),
    ("scale-audit", 1, 1, 0, 10, lambda x: TriangleReference(x, 6, 8, 10)),
    ("membership-families", 0, 0, -3, 3, lambda x: 1 / (1 + max(x, 0)**2)),
    ("membership-families", 1, 0, -3, 3, lambda x: min(ShoulderReference(x, -2, -1), 1 - ShoulderReference(x, 1, 2))),
    ("membership-families", 2, 0, -3, 3, lambda x: ShoulderReference(x, -2, 2)),
    ("membership-families", 3, 0, -3, 3, lambda x: TriangleReference(x, -2, 0, 2)),
    ("membership-families", 4, 0, -3, 3, lambda x: max(0, min(1, x + 2, 2 - x))),
    ("membership-families", 5, 0, -3, 3, lambda x: exp(-x**2 / 2)),
    ("membership-families", 6, 0, -3, 3, lambda x: 1 / (1 + exp(-2 * x))),
    ("membership-families", 7, 0, -3, 3, lambda x: exp(-exp(-x))),
)


UNIVERSAL_REFERENCES = (
    lambda x: 1 / (1 + (8 * x)**20),
    lambda x: min(ShoulderReference(x, 0.17, 0.23), 1 - ShoulderReference(x, 0.34, 0.40)),
    lambda x: min(ShoulderReference(x, 0.34, 0.40), 1 - ShoulderReference(x, 0.60, 0.66)),
    lambda x: min(ShoulderReference(x, 0.60, 0.66), 1 - ShoulderReference(x, 0.77, 0.83)),
    lambda x: ShoulderReference(x, 0.77, 0.95),
)
CURVE_REFERENCES += tuple(
    ("universal-fuzzy-scale", panel, curve, 0, 1, reference)
    for panel in range(2)
    for curve, reference in enumerate(UNIVERSAL_REFERENCES)
)


@pytest.mark.parametrize("figureName,axisIndex,lineIndex,left,right,reference", CURVE_REFERENCES)
def test_EveryPlottedCurveMatchesIndependentFormula(guideFigures, figureName, axisIndex, lineIndex, left, right, reference):
    """Verify all 401 coordinates and grades, rather than comparing API with itself."""

    line = guideFigures[figureName].axes[axisIndex].lines[lineIndex]
    coordinates = [left + (right - left) * index / 400 for index in range(401)]
    assert list(line.get_xdata()) == pytest.approx(coordinates, rel=1e-12, abs=1e-12)
    assert list(line.get_ydata()) == pytest.approx([reference(x) for x in coordinates], rel=1e-12, abs=1e-12)


def AssertPoints(collection, expected):
    """Compare the actual plotted scatter offsets, including exact endpoint zeros."""

    points = collection.get_offsets().tolist()
    assert len(points) == len(expected)
    for actual, reference in zip(points, expected, strict=True):
        assert actual == pytest.approx(reference, rel=1e-12, abs=1e-12)


def test_EveryContinuousDisplayCurveHasAnIndependentReference(guideFigures):
    """Prevent a future figure or added curve from escaping scientific checks."""

    plotted = {
        (name, axisIndex, lineIndex)
        for name, figure in guideFigures.items()
        for axisIndex, axis in enumerate(figure.axes)
        for lineIndex, line in enumerate(axis.lines)
        if len(line.get_xdata()) == 401
    }
    referenced = {(name, axisIndex, lineIndex) for name, axisIndex, lineIndex, _, _, _ in CURVE_REFERENCES}

    assert plotted == referenced


def test_MeasurementMarkersAndRiskThresholdMatchWorkedNumbers(guideFigures):
    """Keep highlighted measurements and the abstention threshold on their curves."""

    temperature = guideFigures["temperature"].axes[0]
    AssertPoints(temperature.collections[0], ((24, 2 / 3), (24, 1 / 8)))
    assert list(temperature.lines[2].get_xdata()) == [24, 24]
    assert temperature.get_xlabel() == "Temperature (°C)"
    risk = guideFigures["risk"].axes[0]
    AssertPoints(risk.collections[0], ((65, 2 / 5), (65, 9 / 32)))
    assert list(risk.lines[3].get_ydata()) == [0.45, 0.45]
    assert list(risk.lines[4].get_xdata()) == [65, 65]
    assert max(2 / 5, 9 / 32) < 0.45
    assert list(guideFigures["alarm"].axes[0].lines[3].get_xdata()) == [100, 100]


def test_SensorBarsShowTheFourDeclaredScalarPolicies(guideFigures):
    """Independently combine half and three-quarters, then check bars and labels."""

    axis = guideFigures["sensors"].axes[0]
    first, second = Fraction(1, 2), Fraction(3, 4)
    expected = (first, second, min(first, second), first * second, max(first, second), first + second - first * second)
    assert [bar.get_height() for bar in axis.patches] == pytest.approx([float(value) for value in expected])
    assert [text.get_text() for text in axis.texts] == [f"{float(value):g}" for value in expected]


def test_AlphaCutAndAuditMarkersDistinguishDiscreteAndContinuousData(guideFigures):
    """Check all observations, inclusive weak-cut boundaries, and finite-grid gaps."""

    alpha = guideFigures["alpha-cuts"].axes[0]
    coordinates = [10 + index / 2 for index in range(9)]
    AssertPoints(alpha.collections[0], [(x, TriangleReference(x, 10, 12, 14)) for x in coordinates])
    AssertPoints(alpha.collections[1], ((11, 0.5), (12, 1), (13, 0.5)))
    assert list(alpha.lines[1].get_ydata()) == [0.5, 0.5]
    AssertPoints(guideFigures["scale-audit"].axes[1].collections[0], [(x, 0) for x in (0, 4, 5, 6, 10)])


def test_CentroidMarkersAndLegendMatchExactRationalMoments(guideFigures):
    """Recompute the four-node area and first moment with exact fractions."""

    axis = guideFigures["centroid"].axes[0]
    coordinates = tuple(Fraction(value, 3) for value in (0, 8, 16, 24))
    grades = tuple(TriangleReference(x, 0, 2, 8) for x in coordinates)
    area = sum((right - left) * (first + second) / 2 for (left, right), (first, second) in zip(pairwise(coordinates), pairwise(grades), strict=True))
    moment = sum((right - left) * (left * first + right * second) / 2 for (left, right), (first, second) in zip(pairwise(coordinates), pairwise(grades), strict=True))
    analytical = Fraction(0 + 2 + 8, 3)
    coarse = moment / area
    assert area == Fraction(32, 9) and moment == Fraction(1024, 81)
    assert coarse == Fraction(32, 9)
    assert coarse - analytical == Fraction(2, 9)
    assert (coarse - analytical) / analytical == Fraction(1, 15)
    assert list(axis.lines[1].get_xdata()) == pytest.approx([float(x) for x in coordinates])
    assert list(axis.lines[1].get_ydata()) == pytest.approx([float(value) for value in grades])
    assert list(axis.lines[2].get_xdata()) == pytest.approx([float(analytical)] * 2)
    assert list(axis.lines[3].get_xdata()) == pytest.approx([float(coarse)] * 2)
    labels = [text.get_text() for text in axis.get_legend().get_texts()]
    assert labels == ["Triangle membership", "4 sampled coordinates", "Analytical centroid: 3.333333", "4-point moments: 3.555556"]


def test_NormalizationDrawsOnlyTheDeclaredDiscretePoints(guideFigures):
    """Reject misleading interpolation and verify normalization preserves coordinates."""

    axis = guideFigures["custom"].axes[0]
    assert not axis.lines
    AssertPoints(axis.collections[0], ((0, 0), (25, 0.25), (50, 0.5)))
    AssertPoints(axis.collections[1], ((0, 0), (25, 0.5), (50, 1)))


def test_TitlesAndLegendsFitWithoutOverlappingEachOther(guideFigures):
    """Catch clipped titles or legends hiding panel headings at the export size."""

    for figure in guideFigures.values():
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        titleBounds = figure._suptitle.get_window_extent(renderer)
        assert figure.bbox.contains(titleBounds.x0, titleBounds.y0)
        assert figure.bbox.contains(titleBounds.x1, titleBounds.y1)
        for axis in figure.axes:
            legend = axis.get_legend()
            if legend is None:
                continue
            legendBounds = legend.get_window_extent(renderer)
            assert figure.bbox.contains(legendBounds.x0, legendBounds.y0)
            assert figure.bbox.contains(legendBounds.x1, legendBounds.y1)
            assert not legendBounds.overlaps(titleBounds)
            if axis.get_title():
                assert not legendBounds.overlaps(axis.title.get_window_extent(renderer))


def test_UniversalLegendFollowsCurveOrderFromLeftToRight(guideFigures):
    """Keep the visible legend in scale order instead of column-major wrapping."""

    figure = guideFigures["universal-fuzzy-scale"]
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()

    for axis in figure.axes:
        legend = axis.get_legend()
        labels = legend.get_texts()
        bounds = [label.get_window_extent(renderer) for label in labels]
        assert [label.get_text() for label in labels] == ["Min", "Low", "Med", "High", "Max"]
        assert all(first.x1 < second.x0 for first, second in pairwise(bounds)), "Legend order must follow increasing scale coordinates."
        assert len({round(bound.y0, 4) for bound in bounds}) == 1, "All five levels must share one legend row."
        assert [handle.get_color() for handle in legend.legend_handles] == [line.get_color() for line in axis.lines]
