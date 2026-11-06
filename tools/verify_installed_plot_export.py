# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Installed-wheel verification for the optional scientific plot exporter.

Run this command with `python -I` in each prepared wheel environment. Core
mode checks the dependency boundary. Plot mode uses the installed backend to
write and inspect repeat exports. The command performs no installation or
network access, creates only the new artifact directory and its contents,
and emits a JSON report to stdout on success.
"""

import argparse
import importlib
import importlib.util
import json
import os
import sys
from collections.abc import Sequence
from hashlib import sha256
from importlib.metadata import distribution, version
from pathlib import Path
from xml.etree import ElementTree

_BACKENDS = ("matplotlib", "PIL", "numpy")
_SVG_NS = {"svg": "http://www.w3.org/2000/svg", "dc": "http://purl.org/dc/elements/1.1/"}


def _Require(condition: bool, message: str) -> None:
    """Fail the installed check independently of interpreter optimization flags."""

    if not condition:
        raise RuntimeError(message)


def _InstalledPackagePath() -> Path:
    """Require the wheel package and public plot module to resolve inside this environment."""

    wheel = distribution("fuzzyroutines")
    packageSpec = importlib.util.find_spec("fuzzyroutines")

    if packageSpec is None or packageSpec.origin is None or wheel.read_text("WHEEL") is None:
        raise RuntimeError("The active environment must contain an installed FuzzyRoutines wheel.")

    packagePath = Path(packageSpec.origin).resolve()
    installedPath = Path(str(wheel.locate_file("fuzzyroutines/__init__.py"))).resolve()
    _Require(packagePath == installedPath, f"FuzzyRoutines resolves outside its installed wheel: {packagePath}")
    _Require(packagePath.is_relative_to(Path(sys.prefix).resolve()), f"Wheel is outside the active environment: {packagePath}")
    plotModule = importlib.import_module("fuzzyroutines.plotting")
    plotOrigin = plotModule.__file__

    if plotOrigin is None:
        raise RuntimeError("The installed plot module must have a file origin.")

    plotPath = Path(plotOrigin).resolve()
    _Require(plotPath == packagePath.with_name("plotting.py"), f"Plot module is outside the installed wheel: {plotPath}")
    _Require(all(name not in sys.modules for name in _BACKENDS), "Importing the scalar and plot APIs loaded an optional backend.")

    return packagePath


def _CheckCore(artifactDirectory: Path) -> dict[str, object]:
    """Verify scalar evaluation and a clear plot failure in a dependency-free install."""

    _Require(all(importlib.util.find_spec(name) is None for name in _BACKENDS), "Core probe requires no Matplotlib, Pillow or NumPy.")
    scalar = importlib.import_module("fuzzyroutines")
    exporter = importlib.import_module("fuzzyroutines.plotting")
    universe = scalar.ContinuousUniverse(0, 1, True, True)
    source = scalar.ScalarFuzzySet(universe, scalar.Triangle(0, 0.5, 1))
    _Require(source.Membership(0.5) == 1, "Scalar triangle evaluation must work without plot dependencies.")
    destination = artifactDirectory / "missing-extra.svg"

    try:
        exporter.ExportMembershipPlot(source, destination)

    except ImportError as error:
        _Require("fuzzyroutines[plot]" in str(error), "Missing backend error must name the installation extra.")

    else:
        raise RuntimeError("Plotting without the optional backend must fail with ImportError.")

    _Require(not any(artifactDirectory.iterdir()), "A missing backend must leave no output or staged file.")

    return {"scalarApexGrade": 1, "missingExtra": "fuzzyroutines[plot]"}


def _CheckArtifacts(artifactDirectory: Path) -> dict[str, object]:
    """Export stable PNG, JPEG and SVG witnesses and report their toolchain."""

    os.environ["MPLCONFIGDIR"] = str(artifactDirectory / "matplotlib-config")
    scalar = importlib.import_module("fuzzyroutines")
    exporter = importlib.import_module("fuzzyroutines.plotting")
    source = scalar.CreateUniversalFuzzyScale()
    minTailGrade = source.terms[0].fuzzySet.Membership(0.5)
    _Require(minTailGrade == 1 / (1 + 4 ** 20), "Historical Min must be evaluated outside its centroid window.")
    exports = artifactDirectory / "review figures 温度"
    exports.mkdir()
    label = "Temperature (°C)"
    digests = {}

    for suffix, options, signature in (
        ("png", {"transparent": True}, b"\x89PNG\r\n\x1a\n"),
        ("jpg", {"background": "#ffffff"}, b"\xff\xd8"),
        ("svg", {}, b"<?xml"),
    ):
        first = exports / f"membership.{suffix}"
        second = exports / f"repeated.{suffix}"
        exporter.ExportMembershipPlot(source, first, coordinateLabel=label, **options)
        exporter.ExportMembershipPlot(source, second, coordinateLabel=label, **options)
        payload = first.read_bytes()
        _Require(payload.startswith(signature), f"{suffix} output must have its file signature.")
        _Require(payload == second.read_bytes(), f"Repeated {suffix} export must reproduce the complete bytes.")
        _Require(first.name.encode() not in payload and second.name.encode() not in payload, f"{suffix} leaked a filename.")
        digests[suffix] = sha256(payload).hexdigest()

    _CheckRasterArtifacts(exports)
    _CheckSvgArtifact(exports / "membership.svg", label)
    fontManager = importlib.import_module("matplotlib.font_manager")
    freetype = importlib.import_module("matplotlib.ft2font")
    pillowFeatures = importlib.import_module("PIL.features")
    font = Path(fontManager.findfont("DejaVu Sans", fallback_to_default=False))

    return {
        "artifactSha256": digests,
        "minTailGrade": minTailGrade,
        "matplotlib": version("matplotlib"),
        "pillow": version("pillow"),
        "numpy": version("numpy"),
        "freeType": freetype.__freetype_version__,
        "jpegCodec": pillowFeatures.version_codec("jpg"),
        "font": font.name,
        "fontSha256": sha256(font.read_bytes()).hexdigest(),
    }


def _CheckRasterArtifacts(exports: Path) -> None:
    """Decode the rasters and verify canvas size, compositing and stable encoding options."""

    image = importlib.import_module("PIL.Image")
    jpegPlugin = importlib.import_module("PIL.JpegImagePlugin")

    with image.open(exports / "membership.png") as raster:
        _Require(raster.size == (1728, 848) and raster.mode == "RGBA", "PNG must have the default RGBA canvas.")
        _Require(raster.getpixel((0, 0))[3] == 0, "Transparent PNG must preserve zero corner alpha.")
        _Require(raster.info.get("Software") == "FuzzyRoutines", "PNG must identify FuzzyRoutines as the creator.")

    with image.open(exports / "membership.jpg") as raster:
        _Require(raster.size == (1728, 848) and raster.mode == "RGB", "JPEG must have the default RGB canvas.")
        _Require(all(channel >= 254 for channel in raster.getpixel((0, 0))), "JPEG must use the requested white background.")
        _Require(raster.info.get("dpi") == (160, 160) and jpegPlugin.get_sampling(raster) == 0, "JPEG must use 160 DPI and 4:4:4.")
        _Require(not raster.getexif(), "JPEG must omit generated EXIF metadata.")


def _CheckSvgArtifact(destination: Path, coordinateLabel: str) -> None:
    """Verify editable labels, palette order and stable SVG geometry and metadata."""

    root = ElementTree.parse(destination).getroot()
    _Require(root.tag == f"{{{_SVG_NS['svg']}}}svg", "The vector export must be SVG XML.")
    _Require(root.get("viewBox") == "0 0 777.6 381.6", "SVG must use the default canvas size in points.")
    labels = [element.text for element in root.findall(".//svg:text", _SVG_NS)]
    expected = ("Min", "Low", "Med", "High", "Max")
    _Require(coordinateLabel in labels, "SVG must preserve the declared unit label as editable text.")
    _Require(tuple(label for label in labels if label in expected) == expected, "SVG legend must retain historical order.")
    groups = {element.get("id"): element for element in root.findall(".//svg:g[@id]", _SVG_NS)}

    for index, color in enumerate(("#a99aff", "#4dd8d0", "#ffd166", "#ff8c9d", "#8cdb91")):
        pathGroup = groups.get(f"series-{index}-path-0")

        if pathGroup is None:
            raise RuntimeError(f"Historical SVG term {expected[index]} needs an independent path.")

        _Require(color.encode() in ElementTree.tostring(pathGroup), f"Historical SVG term {expected[index]} lost its palette slot.")

    _Require(root.find(".//dc:date", _SVG_NS) is None, "SVG must omit the generated date.")


def Main(arguments: Sequence[str] | None = None) -> int:
    """Run the selected installed probe and emit its evidence as JSON."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("core", "plot"), required=True)
    parser.add_argument("--artifact-directory", type=Path, dest="artifactDirectory", required=True)
    options = parser.parse_args(arguments)
    _Require(bool(sys.flags.isolated), "Run this verifier with the installed interpreter and -I.")
    packagePath = _InstalledPackagePath()
    artifactDirectory = options.artifactDirectory.resolve()
    artifactDirectory.mkdir()
    result = _CheckCore(artifactDirectory) if options.mode == "core" else _CheckArtifacts(artifactDirectory)
    report = {
        "mode": options.mode,
        "python": sys.version.split()[0],
        "fuzzyroutines": version("fuzzyroutines"),
        "packageOrigin": str(packagePath),
        **result,
    }
    print(json.dumps(report, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
