# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Recompute reported metrics and verify optional neural figures without Torch."""

import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

import pytest

from fuzzyroutines import CreateUniversalFuzzyScale, UniversalFuzzyScalePolicy
from tools.documentation_gates import ValidateSourceLinks

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURES = ("neural-integration", "neural-ablation")


def test_NeuralReferenceMetricsAgreeWithStoredPredictions():
    """Use direct arithmetic and scalar decisions rather than the example metric helper."""

    report = json.loads((PROJECT_ROOT / "examples/neural/reference.json").read_text())
    assert report["exampleSha256"] == hashlib.sha256((PROJECT_ROOT / "examples/neural/run.py").read_bytes()).hexdigest()
    assert report["configuration"]["checkpointSelection"] == "minimum validation MSE"
    assert report["configuration"]["sampleCount"] == 600
    assert sorted(index for indices in report["splits"].values() for index in indices) == list(range(600))
    scale = CreateUniversalFuzzyScale()
    policy = UniversalFuzzyScalePolicy()
    targets = report["heldOutTargets"]

    for model in report["scalarAblations"].values():
        predictions = model["heldOutPredictions"]
        expectedRmse = math.sqrt(math.fsum((value - target) ** 2 for value, target in zip(predictions, targets, strict=True)) / len(targets))
        labels = [scale.Fuzzify(value, policy).selectedTerms[0].name if 0 <= value <= 1 else None for value in predictions]
        accuracy = sum(left == right for left, right in zip(labels, report["heldOutLabels"], strict=True)) / len(labels)
        assert model["heldOut"]["centroidRmse"] == pytest.approx(expectedRmse, abs=1e-15)
        assert model["heldOut"]["labelAccuracy"] == accuracy
        assert model["heldOut"]["outOfDomainCount"] == sum(not 0 <= value <= 1 for value in predictions)


def test_NeuralFiguresHaveAccessibleProvenanceAndLocalizedNarratives():
    """Every scientific illustration has a title, actual-data provenance and three explanations."""

    for name in FIGURES:
        source = (PROJECT_ROOT / f"docs/site/content/en/assets/figures/{name}.svg").read_text()
        tree = ElementTree.fromstring(source)
        assert tree.find("{http://www.w3.org/2000/svg}title") is not None
        assert "recorded PyTorch CPU experiment" in source
        assert "SPDX-License-Identifier: Apache-2.0" in source

        for locale in ("en", "ru", "zh-CN"):
            narrative = (PROJECT_ROOT / f"docs/site/content/{locale}/guides/neural-integration.md").read_text()
            prefix = "../assets" if locale == "en" else "../../en/assets"
            assert f"{prefix}/figures/{name}.svg" in narrative

    pages = tuple(PROJECT_ROOT / f"docs/site/content/{locale}/guides/neural-integration.md" for locale in ("en", "ru", "zh-CN"))
    assert ValidateSourceLinks(PROJECT_ROOT, pages) == ()


def test_NeuralFigureCliNeedsNoTorchAndRejectsDrift(tmpPath):
    """Run a direct script with only the core package exposed, then detect stale output."""

    pytest.importorskip("matplotlib")
    packageRoot = tmpPath / "package"
    shutil.copytree(PROJECT_ROOT / "fuzzyroutines", packageRoot / "fuzzyroutines", ignore=shutil.ignore_patterns("__pycache__"))
    (packageRoot / "torch.py").write_text("raise AssertionError('figure rendering must not import Torch')\n")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(packageRoot)
    command = [sys.executable, str(PROJECT_ROOT / "tools/generate_neural_figures.py"), "--output-directory", str(tmpPath)]
    generated = subprocess.run(command, cwd=tmpPath, env=environment, capture_output=True, text=True, check=False, timeout=60)
    assert generated.returncode == 0, generated.stderr
    assert set(json.loads(generated.stdout)["figures"]) == set(FIGURES)
    checked = subprocess.run([*command, "--check"], cwd=tmpPath, env=environment, capture_output=True, text=True, check=False, timeout=60)
    assert checked.returncode == 0 and json.loads(checked.stdout)["checked"], checked.stderr
    (tmpPath / "neural-integration.svg").write_text("stale")
    drift = subprocess.run([*command, "--check"], cwd=tmpPath, env=environment, capture_output=True, text=True, check=False, timeout=60)
    assert drift.returncode != 0 and "stale or missing figure" in drift.stderr
