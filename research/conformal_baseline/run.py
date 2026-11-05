# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Calibrate a fixed scalar Sugeno baseline on synthetic service latency."""

import json
import math
from collections.abc import Sequence
from fractions import Fraction
from random import Random
from statistics import mean

from fuzzyroutines import (
    ContinuousUniverse,
    LinguisticTerm,
    NegationPolicy,
    ScalarFuzzySet,
    SNormPolicy,
    TNormPolicy,
)
from fuzzyroutines.inference import (
    ConstantConsequent,
    FuzzyVariable,
    InferencePolicy,
    SugenoModel,
    SugenoRule,
    TermCondition,
)

type Observation = tuple[float, float]

TRAIN_SEED = 43001
CALIBRATION_SEED = 43002
TEST_SEED = 43003
TRAIN_COUNT = 200
CALIBRATION_COUNT = 199
TEST_COUNT = 1000


def Low(cpu: float) -> float:
    """Return the decreasing membership grade for low CPU utilization."""

    return 1 - cpu


def High(cpu: float) -> float:
    """Return the increasing membership grade for high CPU utilization."""

    return cpu


def LatencyModel() -> SugenoModel:
    """Build the two fixed rules and their expert latency estimates in ms."""

    unit = ContinuousUniverse(0, 1, True, True)
    cpu = FuzzyVariable("cpu", (
        LinguisticTerm("low", ScalarFuzzySet(unit, Low)),
        LinguisticTerm("high", ScalarFuzzySet(unit, High)),
    ))
    rules = (
        SugenoRule("low load", TermCondition("cpu", "low"), ConstantConsequent(80)),
        SugenoRule("high load", TermCondition("cpu", "high"), ConstantConsequent(240)),
    )
    policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))

    return SugenoModel((cpu,), rules, policy, ContinuousUniverse(0, 400, True, True))


def Observations(seed: int, count: int) -> tuple[Observation, ...]:
    """Draw CPU fractions and five-minute median latencies under one regime."""

    rng = Random(seed)
    rows = []

    for _ in range(count):
        cpu = rng.random()
        noise = (2 * rng.random() - 1) * (10 + 20 * cpu)
        latency = 90 + 130 * cpu + 40 * cpu**2 + noise
        rows.append((cpu, latency))

    return tuple(rows)


def ConformalRadius(scores: Sequence[float], coverage: Fraction) -> float:
    """Return the split-conformal order statistic or an unbounded radius."""

    if not scores:
        raise ValueError("Calibration requires at least one residual.")

    if not 0 < coverage < 1:
        raise ValueError("Coverage must lie strictly between zero and one.")

    if any(not math.isfinite(score) or score < 0 for score in scores):
        raise ValueError("Calibration residuals must be finite and nonnegative.")

    rank = math.ceil((len(scores) + 1) * coverage)

    if rank > len(scores):
        return math.inf

    return sorted(scores)[rank - 1]


def Residuals(model: SugenoModel, rows: Sequence[Observation], offset: float) -> tuple[float, ...]:
    """Compute signed residuals against an already frozen predictor."""

    return tuple(latency - (model.Evaluate({"cpu": cpu}).value + offset) for cpu, latency in rows)


def Experiment() -> dict[str, object]:
    """Fit only a training offset, calibrate radii, and evaluate held-out data."""

    model = LatencyModel()
    train = Observations(TRAIN_SEED, TRAIN_COUNT)
    calibration = Observations(CALIBRATION_SEED, CALIBRATION_COUNT)
    test = Observations(TEST_SEED, TEST_COUNT)
    offset = mean(Residuals(model, train, 0.0))
    calibrationScores = tuple(abs(residual) for residual in Residuals(model, calibration, offset))
    testScores = tuple(abs(residual) for residual in Residuals(model, test, offset))
    levels = {}

    for coverage in (Fraction(9, 10), Fraction(19, 20)):
        radius = ConformalRadius(calibrationScores, coverage)
        coveredCount = sum(score <= radius for score in testScores)
        levels[str(float(coverage))] = {
            "calibration_rank": math.ceil((CALIBRATION_COUNT + 1) * coverage),
            "covered_test_rows": coveredCount,
            "empirical_coverage": coveredCount / TEST_COUNT,
            "interval_width_ms": round(2 * radius, 6),
            "radius_ms": round(radius, 6),
        }

    return {
        "train": {"seed": TRAIN_SEED, "rows": TRAIN_COUNT},
        "calibration": {"seed": CALIBRATION_SEED, "rows": CALIBRATION_COUNT},
        "test": {"seed": TEST_SEED, "rows": TEST_COUNT},
        "train_offset_ms": round(offset, 6),
        "test_mean_absolute_error_ms": round(mean(testScores), 6),
        "levels": levels,
    }


def Main() -> None:
    """Print the reproducible report as standard JSON."""

    print(json.dumps(Experiment(), sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    Main()
