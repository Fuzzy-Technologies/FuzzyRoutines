# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Compare three intercept policies on one chronological synthetic Sugeno stream."""

from argparse import ArgumentParser
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
    periodicOffset: float
    adaptiveOffset: float
    periodicRefit: bool
    adaptiveStep: bool


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


def GenerateStream(*, seed: int = SEED, driftAt: int = DRIFT_AT) -> Iterator[tuple[float, float]]:
    """Yield a fixed-length stream with an intercept jump of 0.25.

    Args:
        seed: Seed for the coordinates and bounded observation noise.
        driftAt: Zero-based index of the first shifted observation. Both
            regimes must contain at least one observation.

    Raises:
        ValueError: If the drift index does not split the stream.
    """

    if type(driftAt) is not int or not 0 < driftAt < SAMPLE_COUNT:
        raise ValueError(f"Drift index must be between 1 and {SAMPLE_COUNT - 1}.")

    random = Random(seed)

    for index in range(SAMPLE_COUNT):
        coordinate = random.random()
        offset = 0.25 if index >= driftAt else 0
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
        periodicRefit = index % REFIT_PERIOD == 0

        if periodicRefit:
            periodicNext = min(OFFSET_CAP, max(-OFFSET_CAP, fmean(residuals)))

        error = target - adaptive
        adaptiveStep = abs(error) > UPDATE_TRIGGER

        if adaptiveStep:
            step = min(UPDATE_CAP, max(-UPDATE_CAP, error / 2))
            adaptiveNext = min(OFFSET_CAP, max(-OFFSET_CAP, adaptiveOffset + step))

        yield Forecast(
            target, fixed, periodic, adaptive,
            periodicNext - periodicOffset, adaptiveNext - adaptiveOffset,
            periodicOffset, adaptiveOffset, periodicRefit, adaptiveStep,
        )

        periodicOffset = periodicNext
        adaptiveOffset = adaptiveNext


def _Metrics(
    predictions: tuple[float, ...],
    targets: tuple[float, ...],
    updates: tuple[float, ...],
    driftAt: int,
) -> dict[str, float | int | None]:
    """Measure errors, substantial stable-phase updates and drift recovery."""

    errors = tuple(abs(prediction - target) for prediction, target in zip(predictions, targets, strict=True))
    stable = errors[:driftAt]
    shifted = errors[driftAt:]
    recovery = next((
        offset
        for offset in range(len(shifted) - RECOVERY_WINDOW + 1)
        if max(shifted[offset:offset + RECOVERY_WINDOW]) <= RECOVERY_ERROR
    ), None)

    return {
        "stableMae": fmean(stable),
        "shiftedMae": fmean(shifted),
        "stableUpdates": sum(update != 0 for update in updates[:driftAt]),
        "falseAdaptations": sum(abs(update) >= FALSE_ADAPTATION_STEP for update in updates[:driftAt]),
        "recoveryOffset": recovery,
    }


def RunExperiment(*, seed: int = SEED, driftAt: int = DRIFT_AT) -> dict:
    """Return the comparison for a chosen seed and chronological regime split."""

    forecasts = tuple(RunPrequential(GenerateStream(seed=seed, driftAt=driftAt)))
    targets = tuple(row.target for row in forecasts)

    return {
        "seed": seed,
        "sampleCount": SAMPLE_COUNT,
        "driftAt": driftAt,
        "falseAdaptationStep": FALSE_ADAPTATION_STEP,
        "recoveryError": RECOVERY_ERROR,
        "recoveryWindow": RECOVERY_WINDOW,
        "fixed": _Metrics(tuple(row.fixed for row in forecasts), targets, (0.0,) * len(forecasts), driftAt),
        "periodic": _Metrics(tuple(row.periodic for row in forecasts), targets, tuple(row.periodicUpdate for row in forecasts), driftAt),
        "adaptive": _Metrics(tuple(row.adaptive for row in forecasts), targets, tuple(row.adaptiveUpdate for row in forecasts), driftAt),
    }


def RunEvidence(*, seed: int = SEED, driftAt: int = DRIFT_AT) -> dict:
    """Return pre-update offset snapshots and deterministic operation counts.

    Snapshots surround drift and the next two scheduled refits. Offsets are
    added to both fixed rule consequences. Counts describe operations and
    state capacity in the experiment rather than wall time or memory bytes.
    """

    forecasts = tuple(RunPrequential(GenerateStream(seed=seed, driftAt=driftAt)))
    firstRefit = (driftAt // REFIT_PERIOD + 1) * REFIT_PERIOD
    indices = sorted({0, driftAt - 1, driftAt, firstRefit, firstRefit + REFIT_PERIOD, len(forecasts) - 1})
    refits = sum(row.periodicRefit for row in forecasts)

    return {
        "seed": seed,
        "driftAt": driftAt,
        "operationCounts": {
            "sharedSugenoEvaluations": len(forecasts),
            "periodicRefits": refits,
            "periodicResidualsRead": refits * REFIT_PERIOD,
            "periodicResidualCapacity": REFIT_PERIOD,
            "adaptiveThresholdChecks": len(forecasts),
            "adaptiveStepAttempts": sum(row.adaptiveStep for row in forecasts),
            "adaptiveOffsetChanges": sum(row.adaptiveUpdate != 0 for row in forecasts),
        },
        "preUpdateSnapshots": [
            {"index": index, "fixed": 0.0, "periodic": forecasts[index].periodicOffset, "adaptive": forecasts[index].adaptiveOffset}
            for index in indices if index < len(forecasts)
        ],
    }


def Main() -> None:
    """Print the selected reproducible experiment as JSON."""

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--drift-at", type=int, default=DRIFT_AT, dest="driftAt")
    parser.add_argument("--evidence", action="store_true", help="print offset snapshots and operation counts")
    options = parser.parse_args()
    run = RunEvidence if options.evidence else RunExperiment

    try:
        report = run(seed=options.seed, driftAt=options.driftAt)

    except ValueError as error:
        parser.error(str(error))

    print(dumps(report, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    Main()
