# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Verify worked calculations, standalone guide snippets, and artifact boundaries.

The source runner can use its checkout when no installation exists. The package
and documentation CI additionally execute the same examples in isolated Python
against installed distributions; the installed verifier rejects source imports.
"""

import json
import os
import runpy
import subprocess
import sys
from math import isclose
from pathlib import Path
from xml.etree import ElementTree

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = runpy.run_path(str(PROJECT_ROOT / "tools" / "verify_installed_executables.py"))
SCENARIOS = ("temperature", "risk", "sensors", "alarm", "alpha-cuts", "centroid", "scale-audit", "custom")
CANONICAL_EXAMPLES = VERIFIER["LoadCanonicalGuideExamples"]()


def RunPython(arguments, workingDirectory):
    """Use isolated installed Python when available and keep source fallback explicit."""

    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    probe = subprocess.run(
        [sys.executable, "-I", "-c", "import fuzzyroutines"],
        cwd=workingDirectory, env=environment, capture_output=True, text=True, timeout=30, check=False,
    )
    isolatedArguments = ["-I"] if probe.returncode == 0 else []
    if not isolatedArguments:
        environment["PYTHONPATH"] = str(PROJECT_ROOT)
    return subprocess.run(
        [sys.executable, *isolatedArguments, *arguments],
        cwd=workingDirectory, env=environment, capture_output=True, text=True, timeout=30, check=False,
    )


def test_AllWorkedScenariosVerifyIndependentOraclesWithoutFiles(tmpPath):
    """Execute all eight calculations and check key mathematical and policy outcomes."""

    initialEntries = set(tmpPath.iterdir())
    result = RunPython([str(PROJECT_ROOT / "examples" / "guide.py")], tmpPath)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert set(report) == set(SCENARIOS)
    assert report["temperature"]["selected"] == "Comfort"
    assert not report["risk"]["cautiousIsMatch"]
    assert report["alpha-cuts"]["discreteCut"] == [11, 12, 13]
    assert not report["alpha-cuts"]["sampledIsExact"]
    assert isclose(report["centroid"]["triangleCentroid"], 10 / 3, abs_tol=1e-12)
    assert isclose(report["centroid"]["compositeCentroid"], 44 / 9, abs_tol=1e-9)
    assert isclose(report["centroid"]["coarseAbsoluteError"], 2 / 9, abs_tol=1e-12)
    assert report["scale-audit"]["gapSamples"] == [0, 4, 5, 6, 10]
    assert report["custom"]["originalHeight"] == 0.5
    assert report["custom"]["normalizedHeight"] == 1
    assert set(tmpPath.iterdir()) == initialEntries


@pytest.mark.parametrize("scenarioName", SCENARIOS)
def test_IndividualScenarioIsSelectableAndDeterministic(scenarioName, tmpPath):
    """Keep each documented CLI scenario independently usable with stable JSON output."""

    command = [str(PROJECT_ROOT / "examples" / "guide.py"), "--scenario", scenarioName]
    first = RunPython(command, tmpPath)
    second = RunPython(command, tmpPath)
    assert first.returncode == second.returncode == 0, first.stderr + second.stderr
    assert first.stdout == second.stdout
    assert set(json.loads(first.stdout)) == {scenarioName}


@pytest.mark.parametrize("exampleName,snippet", CANONICAL_EXAMPLES.items())
def test_CanonicalPythonSnippetRunsAlone(exampleName, snippet, tmpPath):
    """Execute the exact published Python fence without state from another snippet."""

    result = RunPython(["-c", snippet], tmpPath)
    assert result.returncode == 0, f"{exampleName}:\n{result.stdout}\n{result.stderr}"


def test_SnippetDiscoveryRejectsEmptyGuidesAndPreservesPageOrder(tmpPath):
    """Avoid silently accepting no examples or losing multiple fences on one page."""

    loader = VERIFIER["LoadCanonicalGuideExamples"]
    with pytest.raises(RuntimeError, match="no Python examples"):
        loader(tmpPath)
    (tmpPath / "z.md").write_text("```python\nassert True\n```\n", encoding="utf-8")
    (tmpPath / "a.md").write_text("```python\nassert 1 == 1\n```\n```python\nassert 2 == 2\n```\n", encoding="utf-8")
    assert tuple(loader(tmpPath)) == ("canonical-a-1", "canonical-a-2", "canonical-z-1")


def test_HelpAndInvalidScenarioDoNotComputeOrCreateArtifacts(tmpPath):
    """Keep help informative and invalid selection a standard CLI error."""

    initialEntries = set(tmpPath.iterdir())
    script = str(PROJECT_ROOT / "examples" / "guide.py")
    helpResult = RunPython([script, "--help"], tmpPath)
    assert helpResult.returncode == 0 and "--scenario" in helpResult.stdout
    invalidResult = RunPython([script, "--scenario", "unavailable"], tmpPath)
    assert invalidResult.returncode == 2 and "invalid choice" in invalidResult.stderr
    assert not invalidResult.stdout
    assert set(tmpPath.iterdir()) == initialEntries


def test_FiguresAreAccessibleAndPlottingDependenciesStayOutsideRuntime():
    """Require descriptive SVG metadata, paired prose, and docs-only plotting dependencies."""

    figureRoot = PROJECT_ROOT / "docs" / "site" / "content" / "en" / "assets" / "figures"
    pageRoot = figureRoot.parents[1] / "guides"
    for figureName in (*SCENARIOS, "membership-families"):
        source = (figureRoot / f"{figureName}.svg").read_text(encoding="utf-8")
        assert "SPDX-License-Identifier: Apache-2.0" in source
        tree = ElementTree.fromstring(source)
        assert tree.tag == "{http://www.w3.org/2000/svg}svg"
        assert tree.find("{http://www.w3.org/2000/svg}title") is not None
        assert "Computed using the scalar public API" in source
        page = (pageRoot / f"{figureName}.md").read_text(encoding="utf-8")
        assert f"../assets/figures/{figureName}.svg" in page
    metadata = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    exampleSource = (PROJECT_ROOT / "examples" / "guide.py").read_text(encoding="utf-8")
    assert "matplotlib" not in metadata and "numpy" not in metadata
    assert "import matplotlib" not in exampleSource and "import numpy" not in exampleSource
