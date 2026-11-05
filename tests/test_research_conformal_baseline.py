# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Check the independent references for the split-conformal research baseline."""

import json
import math
from fractions import Fraction
from pathlib import Path

import pytest

from research.conformal_baseline import run


def test_FixedSugenoMatchesTheTwoRampReference():
    """Verify the scalar engine against the known weighted mean."""

    model = run.LatencyModel()
    values = [model.Evaluate({"cpu": cpu}).value for cpu in (0.0, 0.25, 1.0)]
    assert values == pytest.approx((80, 120, 240)), "Two ramp weights must sum to one and interpolate the consequents."


def test_ConformalRadiusUsesFiniteSampleRankAndTies():
    """Separate the corrected calibration rank from an ordinary quantile."""

    scores = (4.0, 2.0, 3.0, 2.0)
    assert run.ConformalRadius(scores, Fraction(3, 5)) == 3.0, "The corrected third order statistic must retain ties."
    assert run.ConformalRadius(scores, Fraction(4, 5)) == 4.0, "Rank equal to the sample size must use its maximum."
    assert run.ConformalRadius(scores, Fraction(9, 10)) == math.inf, "A rank past the sample requires an unbounded interval."


@pytest.mark.parametrize(
    ("scores", "coverage"),
    [((), Fraction(1, 2)), ((math.nan,), Fraction(1, 2)), ((-1,), Fraction(1, 2)), ((1,), Fraction(1))],
)
def test_ConformalRadiusRejectsInvalidCalibration(scores, coverage):
    """Require finite, nonnegative residuals and an interior coverage level."""

    with pytest.raises(ValueError):
        run.ConformalRadius(scores, coverage)


def test_HeldOutRowsCannotChangeOffsetOrRadius(monkeypatch):
    """Mutate the test targets and require frozen train/calibration outputs."""

    baseline = run.Experiment()
    original = run.Observations

    def ShiftTest(seed, count):
        """Shift all test latencies without changing any other split."""

        rows = original(seed, count)

        if seed == run.TEST_SEED:
            return tuple((cpu, latency + 1000) for cpu, latency in rows)

        return rows

    monkeypatch.setattr(run, "Observations", ShiftTest)
    shifted = run.Experiment()
    assert shifted["train_offset_ms"] == baseline["train_offset_ms"], "Held-out targets must not enter offset fitting."

    for level, result in shifted["levels"].items():
        assert result["radius_ms"] == baseline["levels"][level]["radius_ms"], "Held-out targets must not enter calibration."
        assert result["covered_test_rows"] == 0, "A large held-out shift must be visible in measured coverage."


def test_ExperimentReproducesTheCommittedReport():
    """Require deterministic measurements for the declared generator and splits."""

    evidence = Path(__file__).resolve().parents[1] / "research/conformal_baseline/results.json"
    assert run.Experiment() == json.loads(evidence.read_text(encoding="utf-8")), "The committed report must match a fresh experiment."
