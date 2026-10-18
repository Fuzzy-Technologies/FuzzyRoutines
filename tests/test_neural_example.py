# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Independent scientific and execution boundaries for the optional CPU example."""

import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from examples.neural.run import (
    CreateCodec,
    EncodeFeatures,
    GenerateObservations,
    InterpretPrediction,
    Observation,
    Predict,
    ScalarMetrics,
    SelectedLabel,
    SplitIndices,
    SyntheticScore,
    TrainModel,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_NeuralSyntheticTaskAndIndependentSplits():
    """Check the analytical task and identity isolation before representation changes."""

    assert SyntheticScore(0, 0) == 0.05
    assert SyntheticScore(1, 1) == 1
    assert SyntheticScore(0.4, 0.9) == pytest.approx(0.58)
    observations = GenerateObservations(1729, 600)
    assert observations == GenerateObservations(1729, 600)
    assert observations != GenerateObservations(1730, 600)
    splits = SplitIndices(600, 1730)
    assert [len(splits[name]) for name in ("train", "validation", "heldOut")] == [360, 120, 120]
    assert sorted(index for indices in splits.values() for index in indices) == list(range(600))
    assert set(splits["train"]).isdisjoint(splits["heldOut"])
    assert all(0 <= item.severity <= 1 and 0 <= item.exposure <= 1 and 0.05 <= item.score <= 1 for item in observations)


@pytest.mark.parametrize("value", [-0.01, 1.01, math.nan, math.inf, -math.inf])
def test_NeuralPhysicalDomainIsExplicit(value):
    """No automatic clipping may hide invalid normalized observations."""

    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        SyntheticScore(value, 0.5)


def test_NeuralEncodingLossAndWeakCoverageAreVisible():
    """Exhibit identical centroid features with unequal target labels, not a round trip."""

    codec = CreateCodec()
    rows = tuple(Observation(value, 0.9, SyntheticScore(value, 0.9)) for value in (0.4, 0.6))
    assert EncodeFeatures(rows, "raw", codec) == [[0.4, 0.9], [0.6, 0.9]]
    centroidRows = EncodeFeatures(rows, "centroid", codec)
    assert centroidRows[0] == centroidRows[1]
    assert [SelectedLabel(codec, row.score) for row in rows] == ["Med", "High"]
    fullRows = EncodeFeatures(rows, "memberships", codec)
    assert all(len(row) == 10 for row in fullRows)
    assert 0 < max(abs(left - right) for left, right in zip(*fullRows, strict=True)) < 1e-10
    assert fullRows[0][:5] == list(codec.EncodeMemberships(0.4))
    assert fullRows[0][5:] == list(codec.EncodeMemberships(0.9))
    weakGrades = codec.EncodeMemberships(0.17)
    assert 0 < sum(weakGrades) < 0.003
    assert weakGrades[1:] == (0, 0, 0, 0)

    with pytest.raises(ValueError, match="unknown"):
        codec.EncodeLabel("unknown")


def test_NeuralPredictionMetricsKeepOutOfDomainErrors():
    """A numeric model error stays in the RMSE and fails linguistic decoding."""

    codec = CreateCodec()
    predictions = [-0.05, 1.05]
    metrics = ScalarMetrics(predictions, [0, 1], [0, 1], ["Min", "Max"], codec)
    assert metrics["centroidRmse"] == pytest.approx(0.05)
    assert metrics["outOfDomainCount"] == 2
    assert metrics["labelAccuracy"] == 0
    assert metrics["predictionRange"] == predictions
    assert InterpretPrediction(codec, math.nan)["status"] == "non-finite"
    assert InterpretPrediction(codec, 0)["label"] == "Min"
    assert InterpretPrediction(codec, 1)["label"] == "Max"


def test_NeuralCheckpointCannotObserveHeldOutTargets():
    """Poison only held-out labels and independently recompute selected validation loss."""

    torch = pytest.importorskip("torch")
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    features = [[index / 29, (29 - index) / 29] for index in range(30)]
    targets = [[0.1 + 0.8 * row[0]] for row in features]
    splits = SplitIndices(30, 1730)
    poisonedTargets = [row.copy() for row in targets]

    for index in splits["heldOut"]:
        poisonedTargets[index] = [1000.0]

    trained = TrainModel(features, targets, splits, seed=1731, epochs=20)
    poisoned = TrainModel(features, poisonedTargets, splits, seed=1731, epochs=20)
    assert trained.bestEpoch == poisoned.bestEpoch
    assert trained.history == poisoned.history
    assert all(torch.equal(left, right) for left, right in zip(trained.model.parameters(), poisoned.model.parameters(), strict=True))
    selectedPredictions = Predict(trained.model, [features[index] for index in splits["validation"]])
    validationMse = math.fsum((row[0] - targets[index][0]) ** 2 for row, index in zip(selectedPredictions, splits["validation"], strict=True)) / len(selectedPredictions)
    assert validationMse == pytest.approx(trained.validationMse, abs=1e-15)
    assert trained.validationMse <= min(row["validationMse"] for row in trained.history)

    with pytest.raises(ValueError, match="disjoint"):
        TrainModel(features, targets, {**splits, "heldOut": splits["train"]}, seed=1731, epochs=1)

    with pytest.raises(ValueError, match="fixed non-zero width"):
        TrainModel([[], *features[1:]], targets, splits, seed=1731, epochs=1)


def test_NeuralCliHelpNeedsNoTorchAndInstalledGuardRejectsCheckout(tmpPath):
    """Help stays usable without optional dependencies; installed claims need isolation."""

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    script = PROJECT_ROOT / "examples/neural/run.py"
    helpResult = subprocess.run([sys.executable, "-S", str(script), "--help"], env=environment, cwd=tmpPath,
                                text=True, capture_output=True, check=False, timeout=30)
    assert helpResult.returncode == 0 and "--verify-installed" in helpResult.stdout
    guarded = subprocess.run([sys.executable, str(script), "--verify-installed"], env=environment, cwd=tmpPath,
                             text=True, capture_output=True, check=False, timeout=30)
    assert guarded.returncode != 0 and "installed smoke" in guarded.stderr


def test_NeuralInstalledGuardRejectsForeignSourceWithMetadata(tmpPath):
    """Source outside this checkout must not masquerade as a wheel via local metadata."""

    packageRoot = tmpPath / "other-checkout"
    shutil.copytree(PROJECT_ROOT / "fuzzyroutines", packageRoot / "fuzzyroutines", ignore=shutil.ignore_patterns("__pycache__"))
    metadata = packageRoot / "fuzzyroutines-2.1.dist-info"
    metadata.mkdir()
    (metadata / "METADATA").write_text("Metadata-Version: 2.1\nName: fuzzyroutines\nVersion: 2.1\n")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(packageRoot)
    guarded = subprocess.run([sys.executable, str(PROJECT_ROOT / "examples/neural/run.py"), "--verify-installed", "--epochs", "1", "--samples", "30"],
                             env=environment, cwd=tmpPath, text=True, capture_output=True, check=False, timeout=30)
    assert guarded.returncode != 0 and "source checkout or editable package" in guarded.stderr


def test_NeuralCliProducesFiniteBoundedEvidence(tmpPath):
    """Exercise all heads with a small budget and validate report semantics."""

    pytest.importorskip("torch")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    output = tmpPath / "neural.json"
    result = subprocess.run([sys.executable, str(PROJECT_ROOT / "examples/neural/run.py"), "--epochs", "30", "--samples", "90", "--output", str(output)],
                            env=environment, cwd=tmpPath, text=True, capture_output=True, check=False, timeout=120)
    assert result.returncode == 0, result.stderr
    assert output.read_text() == result.stdout
    report = json.loads(result.stdout)
    assert report["environment"]["device"] == "cpu"
    assert len(report["splits"]["heldOut"]) == 18
    assert report["termOrder"] == ["Min", "Low", "Med", "High", "Max"]

    for representation, width in (("raw", 2), ("centroid", 2), ("memberships", 10)):
        model = report["scalarAblations"][representation]
        assert model["inputWidth"] == width
        assert 1 <= model["bestEpoch"] <= 30
        assert math.isfinite(model["heldOut"]["centroidRmse"])
        assert 0 <= model["heldOut"]["labelAccuracy"] <= 1
        assert len(model["heldOutPredictions"]) == 18

    assert all(0 <= value <= 1 for value in report["gradeHead"]["weakCoverageProbe"]["predictedGrades"])
    assert report["outOfDomainExamples"][0]["value"] == -0.05
    assert report["outOfDomainExamples"][1]["value"] == 1.05
