# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Determinism, causal label timing and metric anchors for the drift study."""

from pytest import approx

from research.controlled_drift import (
    DRIFT_AT,
    REFIT_PERIOD,
    GenerateStream,
    RunExperiment,
    RunPrequential,
)


def test_SeededExperimentReproducesMetrics():
    """Check repeatability, recovery and stable-phase adaptation in the seeded scenario."""

    report = RunExperiment()
    assert report == RunExperiment(), "Identical stream seeds must produce identical scientific metrics"
    assert report["fixed"]["recoveryOffset"] is None, "Fixed baseline cannot recover the injected intercept step"
    assert report["periodic"]["recoveryOffset"] == REFIT_PERIOD, "Periodic refit must wait for its next full window"
    assert report["adaptive"]["shiftedMae"] < report["fixed"]["shiftedMae"], "Adaptive comparison must exercise actual updates"
    assert report["adaptive"]["recoveryOffset"] is None, "The adaptive deadband can prevent recovery at the tighter threshold"
    assert report["adaptive"]["stableUpdates"] == 0, "Stable noise below the trigger must leave the intercept unchanged"
    assert report["periodic"]["stableUpdates"] > 0, "Scheduled refits must record even small stable-phase changes"


def test_ChangedLabelsCannotAffectCurrentOrEarlierPredictions():
    """Perturb a refit-boundary label and its suffix without leaking into forecasts."""

    stream = tuple(GenerateStream())
    pivot = DRIFT_AT - 1
    changed = tuple((coordinate, target if index < pivot else target + 0.5) for index, (coordinate, target) in enumerate(stream))
    originalRows = tuple(RunPrequential(stream))
    changedRows = tuple(RunPrequential(changed))

    for original, modified in zip(originalRows[:pivot + 1], changedRows[:pivot + 1], strict=True):
        assert (original.fixed, original.periodic, original.adaptive) == (
            modified.fixed, modified.periodic, modified.adaptive,
        ), "A label at the scoring time or later must not affect an earlier prediction"

    assert originalRows[pivot + 1].periodic != changedRows[pivot + 1].periodic, "The witness must exercise a real periodic refit"
    assert originalRows[pivot + 1].adaptive != changedRows[pivot + 1].adaptive, "The witness must exercise a real adaptive update"
    assert originalRows[pivot + 1].fixed == changedRows[pivot + 1].fixed, "The fixed baseline must ignore every revealed label"


def test_FixedSugenoMatchesIndependentRampAverage():
    """Anchor the baseline using the hand-computed weighted ramp value."""

    row, = RunPrequential(((0.25, 0.0),))
    assert (row.fixed, row.periodic, row.adaptive) == approx((0.3, 0.3, 0.3)), "All candidates must share the unshifted Sugeno baseline"
