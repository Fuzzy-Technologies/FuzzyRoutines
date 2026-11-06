# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Determinism, causal label timing and metric anchors for the drift study."""

from pytest import approx, mark, raises

from research.controlled_drift import (
    DRIFT_AT,
    REFIT_PERIOD,
    SAMPLE_COUNT,
    SEED,
    GenerateStream,
    RunEvidence,
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


def test_ShiftPhaseChangesRecoveryOnTheSameSeededStream():
    """Hold coordinates and noise constant while moving the drift between refits."""

    driftAt = DRIFT_AT - REFIT_PERIOD // 2
    aligned = tuple(GenerateStream())
    misaligned = tuple(GenerateStream(driftAt=driftAt))

    for index, ((coordinate, target), (otherCoordinate, otherTarget)) in enumerate(zip(aligned, misaligned, strict=True)):
        assert coordinate == otherCoordinate, "Changing drift phase must preserve coordinates"
        expectedShift = 0.25 if driftAt <= index < DRIFT_AT else 0
        assert otherTarget - target == approx(expectedShift), "Changing phase must only move the intercept step"

    report = RunExperiment(driftAt=driftAt)
    assert report["driftAt"] == driftAt, "The report must identify the evaluated split"
    assert report["periodic"]["recoveryOffset"] == 36, "The mixed refit window must delay full recovery by half a period"
    assert report["periodic"]["stableUpdates"] == 3, "Stable metrics must exclude refits after the moved drift"


def test_ExplicitSeedReproducesItsOwnScenario():
    """Keep the alternate seed deterministic and distinct from the default data."""

    seed = SEED + 1
    assert next(GenerateStream(seed=seed)) != next(GenerateStream()), "A new seed must change the generated stream"
    report = RunExperiment(seed=seed, driftAt=84)
    assert report == RunExperiment(seed=seed, driftAt=84), "An explicit seed and phase must reproduce the metrics"
    assert report["seed"] == seed, "The report must identify the evaluated seed"


def test_EvidenceCapturesStateBeforeUpdatesAndCountsActualOperations():
    """Check offset timing and refit cost at the mixed and all-shifted windows."""

    report = RunEvidence(driftAt=84)
    counts = report["operationCounts"]
    snapshots = {row["index"]: row for row in report["preUpdateSnapshots"]}
    assert counts["sharedSugenoEvaluations"] == SAMPLE_COUNT, "All candidates must share one evaluation per row"
    assert counts["periodicRefits"] == 9, "Only completed 24-row windows must trigger a refit"
    assert counts["periodicResidualsRead"] == 216, "Each completed refit reads 24 residuals"
    assert counts["periodicResidualCapacity"] == REFIT_PERIOD, "Residual retention must stay bounded"
    assert counts["adaptiveThresholdChecks"] == SAMPLE_COUNT, "The adaptive condition runs once per revealed label"
    assert counts["adaptiveStepAttempts"] == counts["adaptiveOffsetChanges"] == 8, "The seeded adaptive steps must actually change state"
    assert snapshots[84]["adaptive"] == 0, "The first shifted label must not change its own prediction state"
    assert snapshots[96]["periodic"] == approx(0.125, abs=0.015), "The first refit must mix both regimes"
    assert snapshots[120]["periodic"] == approx(0.25, abs=0.015), "The second refit must use shifted labels only"
    assert report == RunEvidence(driftAt=84), "Snapshot evidence must be exactly reproducible"


@mark.parametrize("driftAt", (0, SAMPLE_COUNT))
def test_DriftRequiresTwoNonemptyRegimes(driftAt):
    """Reject a phase that leaves no stable or shifted observations."""

    with raises(ValueError, match="Drift index must be between"):
        RunExperiment(driftAt=driftAt)


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
