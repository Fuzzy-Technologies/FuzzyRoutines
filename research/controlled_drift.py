# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Compare three intercept policies on one chronological synthetic Sugeno stream."""

from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from json import dumps
from random import Random
from statistics import fmean

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

SEED = 431
DRIFT_AT = 96
SAMPLE_COUNT = 224
REFIT_PERIOD = 24
RECOVERY_WINDOW = 8
RECOVERY_ERROR = 0.05
FALSE_ADAPTATION_STEP = 0.01
UPDATE_TRIGGER = 0.08
UPDATE_CAP = 0.025
OFFSET_CAP = 0.30
UNIT = ContinuousUniverse(0, 1, True, True)


@dataclass(frozen=True, slots=True)
class Forecast:
    """Three pre-update predictions and the label revealed after scoring."""

    target: float
    fixed: float
    periodic: float
    adaptive: float
    periodicUpdate: float
    adaptiveUpdate: float


def _Low(coordinate: float) -> float:
    """Return the decreasing unit ramp."""

    return 1 - coordinate


def _High(coordinate: float) -> float:
    """Return the increasing unit ramp."""

    return coordinate


def _Baseline() -> SugenoModel:
    """Build the scalar Sugeno oracle with expected output 0.2 + 0.4x."""

    variable = FuzzyVariable("x", (
        LinguisticTerm("low", ScalarFuzzySet(UNIT, _Low)),
        LinguisticTerm("high", ScalarFuzzySet(UNIT, _High)),
    ))
    rules = (
        SugenoRule("low rule", TermCondition("x", "low"), ConstantConsequent(0.2)),
        SugenoRule("high rule", TermCondition("x", "high"), ConstantConsequent(0.6)),
    )
    policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))

    return SugenoModel((variable,), rules, policy, UNIT)


def GenerateStream() -> Iterator[tuple[float, float]]:
    """Yield unit coordinates with an intercept jump of 0.25 and bounded noise."""

    random = Random(SEED)

    for index in range(SAMPLE_COUNT):
        coordinate = random.random()
        offset = 0.25 if index >= DRIFT_AT else 0
        target = 0.2 + 0.4 * coordinate + offset + random.uniform(-0.015, 0.015)

        yield coordinate, target


def RunPrequential(stream: Iterable[tuple[float, float]]) -> Iterator[Forecast]:
    """Predict each observation before updating either intercept.

    The same shift applied to both Sugeno consequences is equivalent to
    shifting the normalized scalar prediction. Periodic refit uses the
    last 24 residuals, including the just-scored label. Adaptation uses
    only the just-scored residual and a bounded step when its magnitude
    exceeds the trigger. Neither update sees the known drift location.
    """

    baseline = _Baseline()
    residuals: deque[float] = deque(maxlen=REFIT_PERIOD)
    periodicOffset = adaptiveOffset = 0.0

    for index, (coordinate, target) in enumerate(stream, start=1):
        fixed = baseline.Evaluate({"x": coordinate}).value
        periodic = fixed + periodicOffset
        adaptive = fixed + adaptiveOffset
        residuals.append(target - fixed)
        periodicNext = periodicOffset
        adaptiveNext = adaptiveOffset

        if index % REFIT_PERIOD == 0:
            periodicNext = min(OFFSET_CAP, max(-OFFSET_CAP, fmean(residuals)))

        error = target - adaptive

        if abs(error) > UPDATE_TRIGGER:
            step = min(UPDATE_CAP, max(-UPDATE_CAP, error / 2))
            adaptiveNext = min(OFFSET_CAP, max(-OFFSET_CAP, adaptiveOffset + step))

        yield Forecast(target, fixed, periodic, adaptive, periodicNext - periodicOffset, adaptiveNext - adaptiveOffset)

        periodicOffset = periodicNext
        adaptiveOffset = adaptiveNext


def _Metrics(
    predictions: tuple[float, ...],
    targets: tuple[float, ...],
    updates: tuple[float, ...],
) -> dict[str, float | int | None]:
    """Measure errors, substantial stable-phase updates and drift recovery."""

    errors = tuple(abs(prediction - target) for prediction, target in zip(predictions, targets, strict=True))
    stable = errors[:DRIFT_AT]
    shifted = errors[DRIFT_AT:]
    recovery = next((
        offset
        for offset in range(len(shifted) - RECOVERY_WINDOW + 1)
        if max(shifted[offset:offset + RECOVERY_WINDOW]) <= RECOVERY_ERROR
    ), None)

    return {
        "stableMae": fmean(stable),
        "shiftedMae": fmean(shifted),
        "stableUpdates": sum(update != 0 for update in updates[:DRIFT_AT]),
        "falseAdaptations": sum(abs(update) >= FALSE_ADAPTATION_STEP for update in updates[:DRIFT_AT]),
        "recoveryOffset": recovery,
    }


def RunExperiment() -> dict:
    """Return the seeded comparison with explicit measurement thresholds."""

    forecasts = tuple(RunPrequential(GenerateStream()))
    targets = tuple(row.target for row in forecasts)

    return {
        "seed": SEED,
        "sampleCount": SAMPLE_COUNT,
        "driftAt": DRIFT_AT,
        "falseAdaptationStep": FALSE_ADAPTATION_STEP,
        "recoveryError": RECOVERY_ERROR,
        "recoveryWindow": RECOVERY_WINDOW,
        "fixed": _Metrics(tuple(row.fixed for row in forecasts), targets, (0.0,) * len(forecasts)),
        "periodic": _Metrics(tuple(row.periodic for row in forecasts), targets, tuple(row.periodicUpdate for row in forecasts)),
        "adaptive": _Metrics(tuple(row.adaptive for row in forecasts), targets, tuple(row.adaptiveUpdate for row in forecasts)),
    }


if __name__ == "__main__":
    print(dumps(RunExperiment(), sort_keys=True, indent=2, allow_nan=False))
