# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Render deterministic research SVGs with the pinned documentation toolchain."""

from argparse import ArgumentParser
from pathlib import Path

from research.controlled_drift import (
    DRIFT_AT,
    RECOVERY_ERROR,
    REFIT_PERIOD,
    SEED,
    GenerateStream,
    RunPrequential,
)
from tools.generate_guide_figures import COLORS, ConfigureStyle, RenderSvg, plt


def RenderScenario(driftAt: int) -> bytes:
    """Plot prequential absolute errors and the offsets used for prediction."""

    forecasts = tuple(RunPrequential(GenerateStream(driftAt=driftAt)))
    figure, (errors, offsets) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, layout="constrained")

    try:
        figure.suptitle(f"Sugeno drift experiment | seed {SEED}, shift at index {driftAt}")
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
            axis.axvline(driftAt, color="#c6cede", linestyle="--", linewidth=1)
            axis.grid(alpha=0.25)

        return RenderSvg(figure, f"controlled-drift-{driftAt}")

    finally:
        plt.close(figure)


def Main() -> None:
    """Write SVGs for the default and half-period shift phases."""

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True, dest="outputDirectory")
    options = parser.parse_args()
    options.outputDirectory.mkdir(parents=True, exist_ok=True)
    ConfigureStyle()

    for driftAt in (DRIFT_AT, DRIFT_AT - REFIT_PERIOD // 2):
        (options.outputDirectory / f"controlled-drift-{driftAt}.svg").write_bytes(RenderScenario(driftAt))


if __name__ == "__main__":
    Main()
