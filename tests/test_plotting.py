# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Executable contracts for public scientific plot export."""

import subprocess
import sys
from fractions import Fraction
from xml.etree import ElementTree

import pytest

from fuzzyroutines import (
    ContinuousUniverse,
    CreateUniversalFuzzyScale,
    DiscreteUniverse,
    Gaussian,
    LinguisticTerm,
    ScalarFuzzySet,
    Triangle,
)
from fuzzyroutines.exceptions import InvalidDomainError
from fuzzyroutines.plotting import (
    ExportMembershipPlot,
    PlotSamplingError,
    _PreparePlotSeries,
)

_SVG_NS = {"svg": "http://www.w3.org/2000/svg"}


def test_ImportPlottingWithoutOptionalBackend():
    """Import the module without attempting Matplotlib or Pillow imports."""

    code = """
import sys
from importlib.abc import MetaPathFinder

class RejectBackend(MetaPathFinder):
    \"\"\"Make attempted optional imports visible even if errors are caught.\"\"\"

    def FindSpec(self, fullname, path=None, target=None):
        \"\"\"Reject any plotting backend package at import time.\"\"\"

        assert fullname.partition('.')[0] not in {'matplotlib', 'PIL'}, fullname

setattr(RejectBackend, "find_spec", RejectBackend.FindSpec)
sys.meta_path.insert(0, RejectBackend())
import fuzzyroutines.plotting
"""
    subprocess.run([sys.executable, "-c", code], check=True, timeout=10)


@pytest.mark.parametrize(("suffix", "signature", "options"), [
    (".png", b"\x89PNG\r\n\x1a\n", {"transparent": True}),
    (".JPEG", b"\xff\xd8", {"background": "#ffffff"}),
    (".svg", b"<?xml", {}),
])
def test_ExportPublicArtifactDeterministically(tmpPath, suffix, signature, options):
    """Publish each real format twice with stable bytes and Unicode filenames."""

    pytest.importorskip("matplotlib")
    directory = tmpPath / "review figures 温度"
    directory.mkdir()
    model = CreateUniversalFuzzyScale()
    first = ExportMembershipPlot(model, str(directory / f"first{suffix}"), sampleCount=5, **options)
    second = ExportMembershipPlot(model, directory / f"second{suffix}", sampleCount=5, **options)
    assert first.is_absolute() and second.is_absolute()
    assert first.read_bytes().startswith(signature)
    assert first.read_bytes() == second.read_bytes()


def test_ExportKnownOpenTriangleWithoutEvaluatingExcludedEndpoint(tmpPath):
    """Render the ADR triangle jump as separate paths and filled and open marks."""

    pytest.importorskip("matplotlib")
    universe = ContinuousUniverse(-1, 1, rightClosed=True)
    term = LinguisticTerm("Triangle", ScalarFuzzySet(universe, Triangle(-1, 0, 0)))
    series = _PreparePlotSeries(term, (-1, 1), 3)
    assert series.openMarkers == ((-1, 0), (0, 0))
    assert series.markers == ((0, 1),)
    assert all(point != -1 for path in series.paths for point, _ in path)
    assert len(series.paths) == 2
    assert series.paths[0][-1][0] < 0 < series.paths[1][0][0]
    assert series.paths[0][1][1] == pytest.approx(0.5)
    assert series.paths[1][1][1] == 0

    path = ExportMembershipPlot(term.fuzzySet, tmpPath / "jump.svg", sampleCount=3)
    root = ElementTree.parse(path).getroot()
    groups = {item.attrib["id"]: item for item in root.findall(".//svg:g[@id]", _SVG_NS)}
    assert "series-0-path-0" in groups and "series-0-path-1" in groups
    actual = groups["series-0-markers"].find(".//svg:use", _SVG_NS)
    opened = groups["series-0-open-markers"].findall(".//svg:use", _SVG_NS)
    assert actual is not None and "fill: #a99aff" in actual.attrib["style"]
    assert len(opened) == 2 and all("fill: none" in item.attrib["style"] for item in opened)


def test_PreparePlotSeriesRetainsHistoricalTailAndExactAnalyticKnot():
    """Evaluate historical terms in order and include an off-grid triangle apex."""

    scale = CreateUniversalFuzzyScale()
    minimum = _PreparePlotSeries(scale.terms[0], (0, 1), 3)
    assert minimum.paths[0][1] == (0.5, 1 / (1 + (8 * 0.5) ** 20))
    assert tuple(term.name for term in scale.terms) == ("Min", "Low", "Med", "High", "Max")

    apex = Fraction(37, 100)
    triangle = ScalarFuzzySet(ContinuousUniverse(0, 1, True, True), Triangle(0, apex, 1))
    prepared = _PreparePlotSeries(LinguisticTerm("Triangle", triangle), (0, 1), 4)
    exactPoint, exactGrade = prepared.paths[0][2]
    assert exactPoint is apex and exactGrade == 1


def test_ExportDiscreteSingletonAndUnknownContinuityWithoutJoining(tmpPath):
    """Keep exact singleton samples and render custom continuous samples as markers."""

    pytest.importorskip("matplotlib")
    points = []

    def Membership(point):
        """Record the original scalar input and include a zero grade."""

        points.append(point)

        return 0 if point <= 0.5 else 1

    singleton = Fraction(2, 5)
    discrete = ExportMembershipPlot(Membership, tmpPath / "discrete.svg", universe=DiscreteUniverse((singleton,)))
    assert len(points) == 1 and points[0] is singleton
    assert b'id="series-0-markers"' in discrete.read_bytes()
    assert b'id="series-0-path-0"' not in discrete.read_bytes()

    continuous = ExportMembershipPlot(
        Membership, tmpPath / "custom.svg", universe=ContinuousUniverse(0, 1, True, True), sampleCount=4,
    )
    assert b'id="series-0-markers"' in continuous.read_bytes()
    assert b'id="series-0-path-0"' not in continuous.read_bytes()


def test_ExportPlotGuardsExistingBytesAndReportsScalarFailure(tmpPath):
    """Reject collisions before evaluation and keep existing bytes on failure."""

    target = tmpPath / "existing.svg"
    target.write_bytes(b"previous bytes")
    points = []

    def Fail(point):
        """Record any evaluation and raise a caller error."""

        points.append(point)

        raise RuntimeError("missing observation")

    source = ScalarFuzzySet(DiscreteUniverse((0, 1)), Fail)
    with pytest.raises(FileExistsError):
        ExportMembershipPlot(source, target)

    assert not points
    with pytest.raises(PlotSamplingError, match=r"'Membership' at 0") as error:
        ExportMembershipPlot(source, target, overwrite=True)

    assert isinstance(error.value.__cause__, RuntimeError)
    assert target.read_bytes() == b"previous bytes"


def test_ExportUnboundedSourceRequiresExplicitWindow(tmpPath):
    """Require display limits rather than using an integration range."""

    source = ScalarFuzzySet(ContinuousUniverse(), Gaussian(0, 1))
    target = tmpPath / "unbounded.png"
    with pytest.raises(InvalidDomainError, match="explicit display window"):
        ExportMembershipPlot(source, target)

    assert not target.exists()
