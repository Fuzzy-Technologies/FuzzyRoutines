# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Render deterministic research SVGs with the pinned documentation toolchain."""

from argparse import ArgumentParser
from pathlib import Path

from research.controlled_drift import (
    CHALLENGE_DRIFT_AT,
    CHALLENGE_RAMP_ROWS,
    DRIFT_AT,
    RECOVERY_ERROR,
    REFIT_PERIOD,
    SEED,
    GenerateChallengeStream,
    GenerateStream,
    RunPrequential,
)
from tools.generate_guide_figures import COLORS, ConfigureStyle, RenderSvg, plt


def RenderScenario(driftAt: int, *, challenge: bool = False) -> bytes:
    """Plot prequential absolute errors and the offsets used for prediction."""

    driftAt = CHALLENGE_DRIFT_AT if challenge else driftAt
    stream = GenerateChallengeStream() if challenge else GenerateStream(driftAt=driftAt)
    forecasts = tuple(RunPrequential(stream))
    figure, (errors, offsets) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, layout="constrained")

    try:
        title = f"Sugeno drift experiment | seed {SEED}, shift at index {driftAt}"

        if challenge:
            title += f", {CHALLENGE_RAMP_ROWS}-row ramp"

        figure.suptitle(title)
        for name, color in zip(("fixed", "periodic", "adaptive"), COLORS[:3], strict=True):
            errors.plot(
                [abs(getattr(row, name) - row.target) for row in forecasts],
                color=color, linewidth=1.4, label=name.capitalize(),
            )

        errors.axhline(RECOVERY_ERROR, color="#c6cede", linestyle=":", label="Recovery error limit")
        errors.set(ylabel="Absolute error")
        errors.legend(ncols=2, frameon=False)
        offsets.step(range(len(forecasts)), [row.periodicOffset for row in forecasts], where="post", color=COLORS[1], label="Periodic")
        offsets.step(range(len(forecasts)), [row.adaptiveOffset for row in forecasts], where="post", color=COLORS[2], label="Adaptive")
        offsets.set(xlabel="Observation index (zero based)", ylabel="Pre-update offset")
        offsets.legend(frameon=False)

        for axis in (errors, offsets):
            if challenge:
                axis.axvspan(driftAt, driftAt + CHALLENGE_RAMP_ROWS - 1, color="#c6cede", alpha=0.12)

            else:
                axis.axvline(driftAt, color="#c6cede", linestyle="--", linewidth=1)

            axis.grid(alpha=0.25)

        name = "controlled-drift-challenge" if challenge else f"controlled-drift-{driftAt}"

        return RenderSvg(figure, name)

    finally:
        plt.close(figure)


def Main() -> None:
    """Write SVGs for the default and half-period shift phases."""

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True, dest="outputDirectory")
    parser.add_argument("--challenge", action="store_true", help="also render the fixed gradual drift challenge")
    options = parser.parse_args()
    options.outputDirectory.mkdir(parents=True, exist_ok=True)
    ConfigureStyle()

    for driftAt in (DRIFT_AT, DRIFT_AT - REFIT_PERIOD // 2):
        (options.outputDirectory / f"controlled-drift-{driftAt}.svg").write_bytes(RenderScenario(driftAt))

    if options.challenge:
        (options.outputDirectory / "controlled-drift-challenge.svg").write_bytes(RenderScenario(CHALLENGE_DRIFT_AT, challenge=True))


if __name__ == "__main__":
    Main()
