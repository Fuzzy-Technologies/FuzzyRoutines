# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""End-to-end reproduction evidence for the optional encoding illustration."""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_EncodingFigureHasAccessibleProvenanceAndPairedNarratives():
    """Keep the illustration accessible and explained in every supported locale."""

    source = (PROJECT_ROOT / "docs/site/content/en/assets/figures/linguistic-encoding.svg").read_text()
    tree = ElementTree.fromstring(source)
    assert tree.find("{http://www.w3.org/2000/svg}title") is not None
    assert "SPDX-License-Identifier: Apache-2.0" in source
    assert "Computed using the scalar public API" in source

    for locale in ("en", "ru", "zh-CN"):
        pagePath = PROJECT_ROOT / f"docs/site/content/{locale}/guides/linguistic-encoding.md"
        figurePath = PROJECT_ROOT / "docs/site/content/en/assets/figures/linguistic-encoding.svg"
        figureLinks = re.findall(r"\]\(([^)]+linguistic-encoding\.svg)\)", pagePath.read_text())
        assert figureLinks, "The translated narrative must link its explanatory figure"
        assert all((pagePath.parent / link).resolve() == figurePath.resolve() for link in figureLinks)


def test_EncodingFigureCliWritesVerifiesAndDetectsDrift(tmpPath):
    """Exercise the direct CLI without making checkout tools importable as a package."""

    pytest.importorskip("matplotlib")
    # Only core source is exposed for this local regression; installed-wheel CI
    # separately invokes the same script with -I against the built artifact.
    packageRoot = tmpPath / "package"
    shutil.copytree(PROJECT_ROOT / "fuzzyroutines", packageRoot / "fuzzyroutines", ignore=shutil.ignore_patterns("__pycache__"))
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(packageRoot)
    command = [sys.executable, str(PROJECT_ROOT / "tools/generate_encoding_figure.py")]
    helpResult = subprocess.run([*command, "--help"], cwd=tmpPath, env=environment, capture_output=True, text=True, check=False, timeout=30)
    assert helpResult.returncode == 0 and "--check" in helpResult.stdout
    reportPath = tmpPath / "report.json"

    with reportPath.open("w") as stdout:
        result = subprocess.run([*command, "--output-directory", str(tmpPath), "--preview-directory", str(tmpPath)],
                                cwd=tmpPath, env=environment, stdout=stdout, stderr=subprocess.PIPE, text=True, check=False, timeout=30)

    assert result.returncode == 0, result.stderr
    report = json.loads(reportPath.read_text())
    figurePath = tmpPath / "linguistic-encoding.svg"
    assert report["svgBytes"] == figurePath.stat().st_size
    assert (tmpPath / "linguistic-encoding.png").stat().st_size > 0
    checked = subprocess.run([*command, "--output-directory", str(tmpPath), "--check"],
                             cwd=tmpPath, env=environment, capture_output=True, text=True, check=False, timeout=30)
    assert checked.returncode == 0 and json.loads(checked.stdout)["checked"], checked.stderr
    figurePath.write_text("stale")
    drift = subprocess.run([*command, "--output-directory", str(tmpPath), "--check"],
                           cwd=tmpPath, env=environment, capture_output=True, text=True, check=False, timeout=30)
    assert drift.returncode != 0 and "stale or missing figure" in drift.stderr
