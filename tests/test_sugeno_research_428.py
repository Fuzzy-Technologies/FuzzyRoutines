# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Check Task #428 plan reproducibility and observation ownership."""

import json
from pathlib import Path

from research.plan_sugeno_428 import BuildManifest


def test_MultiSeedPlanPartitionsRowsExactlyAndReproduces():
    """Keep train, validation and held-out identities separate for each seed."""

    manifest = BuildManifest()
    assert manifest == BuildManifest()
    runs = manifest["runs"]
    assert [(run["dataSeed"], run["splitSeed"], run["networkSeed"]) for run in runs] == [
        (1729, 1730, 1731), (2729, 2730, 2731), (3729, 3730, 3731),
    ]
    assert len({run["datasetSha256"] for run in runs}) == len(runs)
    assert len({run["splitsSha256"] for run in runs}) == len(runs)

    for run in runs:
        splits = run["splits"]
        assert tuple(len(splits[name]) for name in ("train", "validation", "heldOut")) == (360, 120, 120)
        assert sorted(index for split in splits.values() for index in split) == list(range(600))


def test_FirstSeedMatchesRecordedAdr0020ObservationIdentities():
    """Anchor the initial seed to the existing independent evidence artifact."""

    artifact = Path(__file__).resolve().parents[1] / "research" / "results" / "differentiable-sugeno.json"
    reference = json.loads(artifact.read_text(encoding="utf-8"))
    firstRun = BuildManifest()["runs"][0]
    assert firstRun["datasetSha256"] == reference["datasetSha256"]
    assert firstRun["splitsSha256"] == reference["splitsSha256"]
    assert {name: list(rows) for name, rows in firstRun["splits"].items()} == reference["splits"]
