# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Validate actual pinned consumer expectations without executing its engine."""

import json

import pytest

from experiments.benchmark_public_batches import (
    BACKENDS,
    CONSUMER_FIXTURE,
    MODES,
    BuildOperation,
    CheckReplayParity,
)

pytest.importorskip("numpy")
FIXTURE = json.loads(CONSUMER_FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("replay", FIXTURE["replays"], ids=lambda case: case["name"])
@pytest.mark.parametrize("mode", MODES)
def test_PublicConsumerLabelsAndPercentagesMatchBothExecutionPaths(replay, mode):
    """Compare original independent expectations and complete modern scale evidence."""

    coordinates = replay["coordinates"]
    expectedCount = 17 if replay["function"] == "RiskLong" else 13
    assert len(coordinates) == len(replay["cases"]) == expectedCount
    operations = {backend: BuildOperation("universal_scale", backend, mode, (expectedCount,), coordinates)[0] for backend in BACKENDS}
    parity = CheckReplayParity(operations, replay)
    assert parity["classification_masks_exact"]
    assert parity["upstream_expected_labels_exact"]
    assert parity["upstream_expected_percentages_rounded_4_exact"]
    assert parity["maximum_absolute_error"] <= 1e-12


def test_ReplayDoesNotSilentlySubstituteSyntheticCoordinates():
    """Reject a mismatched declared shape instead of reshaping a generated grid."""

    with pytest.raises(ValueError, match="exactly fill"):
        BuildOperation("universal_scale", "numpy", "prepared_array", (16,), FIXTURE["replays"][0]["coordinates"])
