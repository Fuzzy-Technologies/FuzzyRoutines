# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Bounded experiment evidence for held-out isolation and deterministic fitting."""

from types import SimpleNamespace

import pytest

torch = pytest.importorskip("torch")

from research import run_sugeno as runner
from research.run_sugeno import RunExperiment, Snapshot, TrainRules


@pytest.fixture(autouse=True)
def RestoreTorchSettings():
    """Keep experiment thread, RNG and determinism changes isolated from other tests."""

    threads = torch.get_num_threads()
    deterministic = torch.are_deterministic_algorithms_enabled()
    warnOnly = torch.is_deterministic_algorithms_warn_only_enabled()
    state = torch.random.get_rng_state().clone()

    yield

    torch.set_num_threads(threads)
    torch.use_deterministic_algorithms(deterministic, warn_only=warnOnly)
    torch.random.set_rng_state(state)


def test_HeldOutTargetsCannotSelectOrTrainRuleParameters():
    """Perturb every test target while retaining bit-identical learned state."""

    torch.set_num_threads(1)
    features = [[index / 30, (30 - index) / 30] for index in range(30)]
    targets = [[0.1 + 0.6 * row[0]] for row in features]
    splits = {"train": tuple(range(18)), "validation": tuple(range(18, 24)), "heldOut": tuple(range(24, 30))}
    original, originalEvidence = TrainRules(features, targets, splits, order=1, trainMembership=True, epochs=8)
    changedTargets = [[9999.0] if index in splits["heldOut"] else row for index, row in enumerate(targets)]
    changed, changedEvidence = TrainRules(features, changedTargets, splits, order=1, trainMembership=True, epochs=8)
    assert Snapshot(original) == Snapshot(changed), "Held-out targets must never affect trained rule parameters"
    assert originalEvidence == changedEvidence, "Checkpoint selection and learning curves must use only train/validation targets"
    assert originalEvidence["selected"] != originalEvidence["initial"], "The check must exercise actual parameter updates"


def test_ImportTimingExcludesInstalledFileSizeTraversal(monkeypatch):
    """Separate import timing from filesystem accounting with a deterministic clock."""

    clock = [0.0]

    def ImportProcess(*args, **kwargs):
        """Advance the virtual clock only for the isolated import subprocess."""

        clock[0] += 3

    def FileStat():
        """Make filesystem size measurement visibly slower than the import itself."""

        clock[0] += 7

        return SimpleNamespace(st_size=64)

    artifact = SimpleNamespace(is_file=lambda: True, stat=FileStat)
    distribution = SimpleNamespace(files=("torch",), locate_file=lambda path: artifact, requires=[])
    monkeypatch.setattr(runner.importlib.metadata, "distribution", lambda name: distribution)
    monkeypatch.setattr(runner.subprocess, "run", ImportProcess)
    monkeypatch.setattr(runner.time, "perf_counter", lambda: clock[0])
    measured = runner.DependencyEvidence()
    assert measured["freshProcessImportSeconds"] == 3, "Import timing must stop before filesystem traversal adds unrelated cost"
    assert measured["torchDistributionBytes"] == 64, "Dependency-size accounting must remain present as a separate measurement"


def test_SmallExperimentIsReproducibleAndKeepsTaskMetricsSeparate():
    """Repeat the bounded runner and compare scientific output without machine timings."""

    reports = [RunExperiment(sampleCount=30, epochs=3) for repetition in range(2)]

    for report in reports:
        report.pop("timings")

    assert reports[0] == reports[1], "Identical seeds and CPU configuration must reproduce data, checkpoints and predictions exactly"
    report = reports[0]
    assert [len(report["splits"][name]) for name in ("train", "validation", "heldOut")] == [18, 6, 6], "All comparisons must share the predeclared disjoint 60/20/20 split"
    assert report["models"]["fixedRules"]["parameterCount"] == 0, "Fixed-rule baseline must not train any parameter"
    assert [report["models"][name]["parameterCount"] for name in ("zeroOrder", "firstOrder", "fixedMembership", "rawMlp")] == [14, 22, 12, 337], "Report stored trainable scalar counts, including constrained gap logits"

    for model in report["models"].values():
        assert {"centroidRmse", "latentRmse", "labelAccuracy", "outOfDomainCount", "noMatchCount"} <= model["heldOut"].keys(), "Target regression and decoded-label diagnostics must remain separately visible"

        if "scalarParityMaximumAbsoluteError" in model:
            assert model["scalarParityMaximumAbsoluteError"] < 1e-12, "Trained frozen model must still agree with the scalar reference"


@pytest.mark.parametrize("epochs", (0, True, 2001))
def test_ResearchBudgetRejectsInvalidEpochCounts(epochs):
    """Reject accidental unbounded experiment budgets before constructing a graph."""

    with pytest.raises(ValueError, match="epochs"):
        TrainRules([[0.5, 0.5]], [[0.5]], {"train": (0,), "validation": (), "heldOut": ()}, order=1, trainMembership=True, epochs=epochs)
