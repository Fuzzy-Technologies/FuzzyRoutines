# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Installed-wheel recipe contracts, independent reference values and preflight failures."""

import importlib.metadata
import json
import math
import runpy
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RECIPE = runpy.run_path(str(PROJECT_ROOT / "examples/agent_recipe.py"))


def test_UniversalRecipePreservesParametersAndKnownGrades():
    """Keep historical coefficients, term order and exact mathematical reference points."""

    report = RECIPE["BuildReport"]("universal-fuzzy-scale", 0.2, "2.0.0")
    assert report["result"]["selectedTerms"] == ["Low"]
    assert math.isclose(report["result"]["memberships"]["Low"], 0.5, abs_tol=1e-12)
    assert report["scale"]["universe"] == [0, 1]
    assert [term["name"] for term in report["scale"]["terms"]] == ["Min", "Low", "Med", "High", "Max"]
    assert report["scale"]["terms"][0]["centroidWindow"] == [0, 0.23]
    assert report["policy"]["tiePolicy"] == "last"
    assert report["policy"]["tieTolerance"] == 0
    assert report["checks"]["maximumAbsoluteError"] <= 1e-12
    midpoint = RECIPE["BuildReport"]("universal-fuzzy-scale", 0.5, "2.0.0")
    assert midpoint["result"]["memberships"]["Med"] == 1
    assert midpoint["result"]["memberships"]["Min"] > 0, "Do not clip the historical Min tail to its centroid window."


def test_RiskRecipeNormalizesExplicitlyAndAbstainsOnWeakCoverage():
    """Distinguish strong High membership from no match at the unchanged weak region."""

    strong = RECIPE["BuildReport"]("risk", 75, "2.0.0")
    weak = RECIPE["BuildReport"]("risk", 17, "2.0.0")
    assert strong["input"]["normalizedCoordinate"] == 0.75
    assert strong["result"]["selectedTerms"] == ["High"]
    assert strong["result"]["maximumMembership"] == 1
    assert weak["result"]["selectedTerms"] == []
    assert not weak["result"]["isMatch"]
    assert math.isclose(weak["result"]["maximumMembership"], 0.002129589894200199, abs_tol=1e-12)
    assert not strong["interpretation"]["gradesAreProbabilities"]
    assert strong["policy"]["minimumConfidence"] == 0.1


@pytest.mark.parametrize("scenario,value", [("risk", -1), ("risk", 101), ("universal-fuzzy-scale", 1.1), ("risk", float("nan")), ("risk", float("inf")), ("missing", 0.2)])
def test_RecipeRejectsUnknownScenarioAndInvalidInput(scenario, value):
    """Never clamp bad values or silently replace an unknown scientific scenario."""

    with pytest.raises(ValueError):
        RECIPE["BuildReport"](scenario, value, "2.0.0")


def test_PreflightRejectsUnsupportedPythonBeforePackageLookup(monkeypatch):
    """An unsupported interpreter must explain the historical pip fallback hazard."""

    monkeypatch.setattr(sys, "version_info", (3, 12, 0))

    with pytest.raises(RuntimeError, match="Python 3.12 may resolve historical 1.0.3"):
        RECIPE["Preflight"]("2.0.0")


def test_PreflightRejectsOldDistributionAndAcceptsExactCandidate(monkeypatch):
    """Require the caller's exact version even when modern imports might work."""

    monkeypatch.setattr(importlib.metadata, "version", lambda name: "1.0.3")

    with pytest.raises(RuntimeError, match="Expected fuzzyroutines 2.0.0, found 1.0.3"):
        RECIPE["Preflight"]("2.0.0")

    monkeypatch.setattr(importlib.metadata, "version", lambda name: "2.1.0.dev0")
    assert RECIPE["Preflight"]("2.1.0.dev0") == "2.1.0.dev0"


def test_PreflightReportsMissingInstallation(monkeypatch):
    """Give an exact installation command when no distribution metadata exists."""

    def MissingVersion(name):
        """Represent a clean interpreter with no installed FuzzyRoutines distribution."""

        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", MissingVersion)

    with pytest.raises(RuntimeError, match="pip install fuzzyroutines==2.0.0"):
        RECIPE["Preflight"]("2.0.0")


def test_JsonStdoutMatchesRequestedArtifact(tmpPath, monkeypatch, capsys):
    """Keep diagnostics off JSON stdout and make both evidence surfaces identical."""

    monkeypatch.setattr(importlib.metadata, "version", lambda name: "2.0.0")
    destination = tmpPath / "report.json"
    assert RECIPE["Main"](["--scenario", "risk", "--output", str(destination)]) == 0
    streams = capsys.readouterr()
    assert streams.err == ""
    assert json.loads(streams.out) == json.loads(destination.read_text(encoding="utf-8"))
    assert json.loads(streams.out)["checks"]["passed"]


def test_PreflightFailureProducesNoArtifact(tmpPath, monkeypatch, capsys):
    """Do not leave plausible JSON evidence after rejecting the wrong package."""

    monkeypatch.setattr(importlib.metadata, "version", lambda name: "1.0.3")
    destination = tmpPath / "report.json"
    assert RECIPE["Main"](["--output", str(destination)]) == 2
    streams = capsys.readouterr()
    assert streams.out == ""
    assert "found 1.0.3" in streams.err
    assert not destination.exists()


def test_PlotAndJsonCannotOverwriteEachOther(tmpPath, monkeypatch, capsys):
    """Reject a shared destination before producing either incompatible artifact."""

    monkeypatch.setattr(importlib.metadata, "version", lambda name: "2.0.0")
    destination = tmpPath / "report.svg"
    assert RECIPE["Main"](["--output", str(destination), "--plot", str(destination)]) == 2
    assert "different files" in capsys.readouterr().err
    assert not destination.exists()


def test_AgentInstructionsPreserveCommandsAcrossLocales():
    """Keep the same executable commands and link every locale from visible entrypoints."""

    from tools.locale_documentation import ProtectedPageParts

    english = (PROJECT_ROOT / "docs/site/content/en/agent-quickstart.md").read_text(encoding="utf-8")

    for locale in ("ru", "zh-CN"):
        translated = (PROJECT_ROOT / f"docs/site/content/{locale}/agent-quickstart.md").read_text(encoding="utf-8")
        assert ProtectedPageParts(translated) == ProtectedPageParts(english)

    for locale in ("en", "ru", "zh-CN"):
        index = (PROJECT_ROOT / f"docs/site/content/{locale}/index.md").read_text(encoding="utf-8")
        assert "agent-quickstart.md" in index

    # README uses the matching source route until new live pages are published.
    assert "docs/site/content/en/agent-quickstart.md" in (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for path in ("docs/index.html", "docs/llms.txt"):
        assert "/agent-quickstart/" in (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_PreflightCannotOptIntoHistoricalApiByChangingExpectedVersion(monkeypatch):
    """The version argument must not allow an unsupported old API through preflight."""

    monkeypatch.setattr(importlib.metadata, "version", lambda name: "1.0.3")

    with pytest.raises(RuntimeError, match="historical 1.x is unsupported"):
        RECIPE["Preflight"]("1.0.3")
