# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Render recorded neuro-fuzzy evidence without importing Torch or retraining.

The input JSON is produced by `python -m research.run_sugeno`. Every artist uses
recorded predictions, losses or constrained parameters. Stable SVG output can
be checked byte-for-byte; optional PNG previews support visual inspection.
"""

import argparse
import json
import math
from pathlib import Path

from tools.generate_guide_figures import COLORS, ConfigureStyle, RenderSvg, plt

REPORT = Path(__file__).resolve().parents[1] / "research/results/differentiable-sugeno.json"
MODEL_NAMES = ("fixedRules", "zeroOrder", "firstOrder", "fixedMembership", "rawMlp")
MODEL_LABELS = ("Fixed rules", "Trainable zero order", "Trainable first order", "Fixed memberships", "Raw-input MLP")
MODEL_COLORS = ("#8290aa", COLORS[1], COLORS[3], COLORS[0], COLORS[2])


def BuildFigures(report: dict | None = None) -> dict:
    """Plot constrained membership changes, observed learning and output failures."""

    report = json.loads(REPORT.read_text(encoding="utf-8")) if report is None else report
    models = report["models"]
    figure, axes = plt.subplots(2, 2, figsize=(12.8, 9.2))
    figure.subplots_adjust(left=0.08, right=0.96, top=0.84, bottom=0.12, hspace=0.5, wspace=0.32)
    figure.suptitle("Learning a Sugeno model", x=0.08, y=0.97, ha="left", fontsize=22, fontweight="bold")
    splitSizes = " / ".join(str(len(report["splits"][name])) for name in ("train", "validation", "heldOut"))
    figure.text(0.08, 0.91, f"4 rules  ·  same {splitSizes} split  ·  {report['configuration']['epochs']} epochs  ·  validation-selected checkpoints", fontsize=11, color="#c6cede")
    coordinates = [index / 400 for index in range(401)]

    for dimension, label in enumerate(("Severity", "Exposure")):
        axis = axes[0, dimension]

        for term, color in enumerate(COLORS[:2]):
            for phase, style, legend in (("initial", "--", "initial"), ("selected", "-", "learned")):
                snapshot = models["firstOrder"][phase]
                center, width = snapshot["centers"][dimension][term], snapshot["widths"][dimension][term]
                grades = [math.exp(-0.5 * ((value - center) / width)**2) for value in coordinates]
                axis.plot(coordinates, grades, color=color, linestyle=style, linewidth=2.2 if phase == "selected" else 1.5, alpha=1 if phase == "selected" else 0.6, label=f"Term {term + 1}: {legend}")

        axis.set(title=f"{label}: first-order memberships", xlabel=f"Normalized {label.lower()}", ylabel="Membership grade", ylim=(0, 1.08))
        axis.legend(frameon=False, fontsize=8, ncols=2, loc="lower center")

    for name, label, color in zip(MODEL_NAMES[1:], MODEL_LABELS[1:], MODEL_COLORS[1:], strict=True):
        history = models[name]["history"]
        axes[1, 0].plot([row["epoch"] for row in history], [math.sqrt(row["validationMse"]) for row in history], color=color, linewidth=2, label=label)

    axes[1, 0].set(title="Validation learning curves", xlabel="Full-batch epoch", ylabel="Centroid-target RMSE (log scale)", yscale="log", ylim=(0.05, 0.6))
    axes[1, 0].set_yticks((0.05, 0.1, 0.2, 0.5), labels=("0.05", "0.10", "0.20", "0.50"))
    axes[1, 0].minorticks_off()
    axes[1, 0].legend(frameon=False, fontsize=8)
    errors = [models[name]["heldOut"]["centroidRmse"] for name in MODEL_NAMES]
    bars = axes[1, 1].barh(MODEL_LABELS, errors, color=MODEL_COLORS, height=0.55)
    axes[1, 1].bar_label(bars, labels=[f"{value:.4f}" for value in errors], padding=5, fontsize=9)
    axes[1, 1].invert_yaxis()
    axes[1, 1].set(title="Held-out error: lower is better", xlabel="Centroid-target RMSE", xlim=(0, 0.12))

    for axis in axes.flat:
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(True, alpha=0.3)
        axis.set_axisbelow(True)

    figure.text(0.08, 0.045, "Learning memberships did not reduce centroid-target RMSE versus learning only affine consequences.", fontsize=10, color="#c6cede")
    figures = {"sugeno-research-learning": figure}
    figure, axes = plt.subplots(1, 2, figsize=(12.8, 5.8))
    figure.subplots_adjust(left=0.08, right=0.96, top=0.76, bottom=0.2, wspace=0.3)
    figure.suptitle("Check the predictions, not only the loss", x=0.08, y=0.96, ha="left", fontsize=21, fontweight="bold")
    figure.text(0.08, 0.86, "The target is a selected historical level's centroid; the models return continuous numbers.", fontsize=11, color="#c6cede")
    severity = [row[0] for row in report["slice"]["inputs"]]
    axes[0].plot(severity, report["slice"]["targets"], color="#edf2ff", linewidth=2, drawstyle="steps-mid", label="Centroid target")

    for name, label, color in zip(MODEL_NAMES[1:], MODEL_LABELS[1:], MODEL_COLORS[1:], strict=True):
        axes[0].plot(severity, models[name]["slicePredictions"], color=color, linewidth=1.8, label=label)

    axes[0].set(title="Response slice: exposure = 0.5", xlabel="Normalized severity", ylabel="Scalar output", ylim=(0, 1.05))
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    predictions = models["firstOrder"]["heldOutPredictions"]
    targets = report["heldOutTargets"]
    valid = [index for index, value in enumerate(predictions) if 0 <= value <= 1]
    outside = [index for index, value in enumerate(predictions) if not 0 <= value <= 1]
    axes[1].scatter([targets[index] for index in valid], [predictions[index] for index in valid], color=COLORS[0], alpha=0.65, s=28, label="Within [0,1]")
    axes[1].scatter([targets[index] for index in outside], [predictions[index] for index in outside], color=COLORS[3], marker="^", s=85, label=f"Outside domain: {len(outside)} / {len(targets)}", zorder=4)
    axes[1].plot((0, 1), (0, 1), color="#c6cede", linestyle="--", linewidth=1, label="Exact target")
    axes[1].axhspan(1, 1.08, color=COLORS[3], alpha=0.14)
    axes[1].axhline(1, color=COLORS[3], linewidth=1)
    axes[1].set(title="First-order model: held-out outputs", xlabel="Target label centroid", ylabel="Predicted scalar", xlim=(0, 1), ylim=(0, 1.08))
    axes[1].legend(frameon=False, fontsize=8, loc="upper left")

    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(True, alpha=0.3)

    figure.text(0.08, 0.055, "Outputs outside the decoder's domain are counted as invalid; no clipping or replacement is applied.", fontsize=10, color=COLORS[3])
    figures["sugeno-research-predictions"] = figure

    return figures


def Main(arguments=None) -> int:
    """Write or verify deterministic SVGs and optional PNG previews from evidence."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, required=True, dest="outputDirectory")
    parser.add_argument("--preview-directory", type=Path, dest="previewDirectory")
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args(arguments)
    ConfigureStyle()

    if not options.check:
        options.outputDirectory.mkdir(parents=True, exist_ok=True)

    if options.previewDirectory:
        options.previewDirectory.mkdir(parents=True, exist_ok=True)

    for name, figure in BuildFigures(json.loads(options.report.read_text(encoding="utf-8"))).items():
        path = options.outputDirectory / f"{name}.svg"
        rendered = RenderSvg(figure, name)

        if options.check:
            if not path.is_file() or path.read_bytes() != rendered:
                raise RuntimeError(f"stale or missing research figure: {path}")

        else:
            path.write_bytes(rendered)

        if options.previewDirectory:
            figure.savefig(options.previewDirectory / f"{name}.png", dpi=120)

        plt.close(figure)

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
