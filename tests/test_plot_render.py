# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Headless PNG and SVG evidence for independent membership plot artists."""

from io import BytesIO
from xml.etree import ElementTree

import pytest

from fuzzyroutines._plot_export import WritePlotExport
from fuzzyroutines._plot_render import PlotSeries, RenderPlot
from fuzzyroutines.exceptions import InvalidDomainError, InvalidParameterError

_SVG_NS = {"svg": "http://www.w3.org/2000/svg"}


def test_RenderReproducibleSvgWithIndependentPathsAndHistoricalColors(tmpPath):
    """Check actual SVG bytes, palette order, path separation and editable labels."""

    matplotlib = pytest.importorskip("matplotlib")
    backend = matplotlib.get_backend()
    series = (
        PlotSeries("Min", (((0, 0), (0.4, 1)), ((0.6, 0), (1, 0))), ((0.5, 1),)),
        PlotSeries("Low"),
        PlotSeries("Med", markers=((0.1, 0), (0.7, 0.5))),
        PlotSeries("High", markers=((0.8, 0.7),)),
        PlotSeries("Max", markers=((1, 1),)),
    )

    def Encode(outputFormat):
        """Render the same source without receiving a destination name."""

        return RenderPlot(series, (0, 1), outputFormat, title="Membership curves", coordinateLabel="Temperature (\N{DEGREE SIGN}C)")

    first = WritePlotExport(tmpPath / "first.svg", Encode)
    with matplotlib.rc_context({"font.family": "serif", "figure.facecolor": "yellow", "svg.hashsalt": "different"}):
        second = WritePlotExport(tmpPath / "second.svg", Encode)
        assert matplotlib.rcParams["svg.hashsalt"] == "different"
        assert matplotlib.rcParams["figure.facecolor"] == "yellow"

    assert matplotlib.get_backend() == backend
    rendered = first.read_bytes()
    assert rendered == second.read_bytes(), "Filename and caller style must not affect SVG bytes."
    root = ElementTree.fromstring(rendered)
    assert root.attrib["viewBox"] == "0 0 777.6 381.6"
    assert b"<dc:date" not in rendered and b"first.svg" not in rendered
    groups = {entry.attrib["id"]: entry for entry in root.findall(".//svg:g[@id]", _SVG_NS)}

    for pathIndex in (0, 1):
        path = groups[f"series-0-path-{pathIndex}"].find("svg:path", _SVG_NS)
        assert path is not None and "#a99aff" in path.attrib["style"]
        assert path.attrib["d"].count("M ") == 1 and path.attrib["d"].count("L ") == 1

    for index, color in ((0, "#a99aff"), (2, "#ffd166"), (3, "#ff8c9d"), (4, "#8cdb91")):
        group = groups[f"series-{index}-markers"]
        assert color.encode("ascii") in ElementTree.tostring(group)
        assert group.find(".//svg:use", _SVG_NS) is not None

    assert "series-2-path-0" not in groups
    labels = [entry.text for entry in root.findall(".//svg:text", _SVG_NS)]
    assert [label for label in labels if label in {"Min", "Low", "Med", "High", "Max"}] == [
        "Min", "Low", "Med", "High", "Max",
    ]
    assert "Temperature (\N{DEGREE SIGN}C)" in labels


@pytest.mark.parametrize(("transparent", "alpha"), [(False, 255), (True, 0)])
def test_RenderPngDimensionsAlphaAndStableMetadata(transparent, alpha):
    """Decode the real PNG to verify canvas dimensions, background and metadata."""

    pytest.importorskip("matplotlib")
    imageModule = pytest.importorskip("PIL.Image")
    series = (PlotSeries("Min", markers=((0.5, 0.5),)),)
    content = RenderPlot(series, (0, 1), "png", title="Raster", transparent=transparent)
    assert content == RenderPlot(series, (0, 1), "png", title="Raster", transparent=transparent)

    with imageModule.open(BytesIO(content)) as raster:
        assert raster.size == (1728, 848)
        assert raster.mode == "RGBA"
        corner = raster.getpixel((0, 0))
        assert corner[3] == alpha

        if not transparent:
            assert corner[:3] == (18, 24, 41)

        assert raster.info["Software"] == "FuzzyRoutines"
        assert "date" not in raster.info


def test_RenderSvgOutlinesAndRejectsUnsupportedGlyphs():
    """Select SVG outlines explicitly and reject missing glyphs without fallback."""

    pytest.importorskip("matplotlib")
    series = (PlotSeries("Min", markers=((0.5, 0.5),)),)
    content = RenderPlot(series, (0, 1), "svg", title="Outlines", svgTextAsPaths=True)
    root = ElementTree.fromstring(content)
    assert root.findall(".//svg:path", _SVG_NS)
    assert not root.findall(".//svg:text", _SVG_NS)

    with pytest.raises(InvalidParameterError, match=r"U\+6E29"):
        RenderPlot(series, (0, 1), "svg", title="\u6e29")


def test_RenderRejectsEmptyDataBeforeLoadingTheBackend():
    """Fail with a domain error when every series is clipped."""

    with pytest.raises(InvalidDomainError, match="no renderable samples"):
        RenderPlot((PlotSeries("Empty"),), (0, 1), "svg", title="Empty")
