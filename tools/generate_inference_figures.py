# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Generate reproducible stage plots for the actual Mamdani/Sugeno example.

Run with `python -I tools/generate_inference_figures.py --output-directory PATH`
after installing the candidate package and docs/requirements-plots.txt.
Plotting remains a documentation-only dependency. --check compares bytes;
--preview-directory writes optional PNG previews for visual inspection.
"""

import argparse
import json
import runpy
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
plottingHelpers = runpy.run_path(str(Path(__file__).with_name("generate_guide_figures.py")))
COLORS = plottingHelpers["COLORS"]
configureStyle = plottingHelpers["ConfigureStyle"]
renderSvg = plottingHelpers["RenderSvg"]
plt = plottingHelpers["plt"]


def BuildSupportModel():
    """Construct the two disjoint fully fired consequents from the release audit."""

    from fuzzyroutines import (
        ContinuousUniverse,
        IntegrationDomain,
        LinguisticTerm,
        NegationPolicy,
        ScalarFuzzySet,
        SNormPolicy,
        TNormPolicy,
        Triangle,
    )
    from fuzzyroutines.inference import (
        FuzzyVariable,
        InferencePolicy,
        MamdaniModel,
        MamdaniRule,
        TermCondition,
    )

    universe = ContinuousUniverse(0, 1, True, True)
    inputs = (FuzzyVariable("x", (LinguisticTerm("on", ScalarFuzzySet(universe, Triangle(0, 0.5, 1))),)),)
    output = FuzzyVariable("y", (
        LinguisticTerm("small", ScalarFuzzySet(universe, Triangle(0.16, 0.18, 0.20))),
        LinguisticTerm("large", ScalarFuzzySet(universe, Triangle(0.60, 0.75, 0.90))),
    ))
    policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))
    rules = tuple(MamdaniRule(term.name, TermCondition("x", "on"), term.name) for term in output.terms)

    return MamdaniModel(inputs, output, rules, policy, TNormPolicy("logic"), SNormPolicy("logic")).Evaluate({"x": 0.5}, IntegrationDomain(0, 1))


def BuildFigures() -> dict:
    """Plot actual input grades, activations, aggregates and scalar contributions."""

    example = runpy.run_path(str(PROJECT_ROOT / "examples" / "inference.py"))
    example["Run"]()
    mamdani, zeroOrder, firstOrder = example["BuildModels"]()
    result = mamdani.Evaluate({"risk": 0.25}, example["IntegrationDomain"](0, 1))
    coordinates = tuple(index / 400 for index in range(401))
    figure, axes = plt.subplots(2, 2, figsize=(11.8, 8.7))
    figure.subplots_adjust(left=0.08, right=0.97, top=0.85, bottom=0.13, hspace=0.48, wspace=0.25)
    figure.suptitle("Mamdani  ·  rules shape an output fuzzy set", fontsize=19, fontweight="bold", x=0.08, ha="left", y=0.97)
    figure.text(0.08, 0.91, "Two monitoring rules: low risk → low response; high risk → high response", fontsize=11, color="#c6cede")

    for axis in axes.flat:
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(True)
        axis.set_ylim(0, 1.08)
        axis.set_yticks((0, 0.25, 0.5, 0.75, 1))

    for term, color in zip(mamdani.inputs[0].terms, COLORS, strict=False):
        axes[0, 0].plot(coordinates, [term.fuzzySet.Membership(value) for value in coordinates], color=color, linewidth=2.5, label=term.name)
        axes[0, 0].scatter([0.25], [term.fuzzySet.Membership(0.25)], color=color, s=65, zorder=4)

    axes[0, 0].axvline(0.25, color=COLORS[2], linestyle="--", label="input = 0.25")
    axes[0, 0].set(title="1  Fuzzify the input", xlabel="Normalized risk x", ylabel="Membership grade")
    axes[0, 0].legend(frameon=False, fontsize=9, loc="upper right")
    strengths = [trace.firingStrength for trace in result.rules]
    bars = axes[0, 1].bar(["Low rule", "High rule"], strengths, color=COLORS[:2], width=0.5)
    axes[0, 1].bar_label(bars, labels=[f"{value:.2f}" for value in strengths], padding=6)
    axes[0, 1].set(title="2  Fire rules with unit weights", ylabel="Firing strength α")

    for trace, color in zip(result.rules, COLORS, strict=False):
        values = [trace.activatedSet.Membership(value) for value in coordinates]
        axes[1, 0].plot(coordinates, values, color=color, linewidth=2.5, label=trace.name)
        axes[1, 0].fill_between(coordinates, values, color=color, alpha=0.12)

    axes[1, 0].set(title="3  Clip each consequent with min", xlabel="Response y", ylabel="Activated membership")
    axes[1, 0].legend(frameon=False, fontsize=9)
    aggregate = [result.outputSet.Membership(value) for value in coordinates]
    axes[1, 1].fill_between(coordinates, aggregate, color=COLORS[0], alpha=0.35)
    axes[1, 1].plot(coordinates, aggregate, color=COLORS[0], linewidth=2.5, label="max envelope")
    axes[1, 1].axvline(result.value, color=COLORS[2], linewidth=2, linestyle="--", label=f"centroid = {result.value:.6f}")
    axes[1, 1].set(title="4  Aggregate, then balance the area", xlabel="Response y", ylabel="Aggregated membership")
    axes[1, 1].legend(frameon=False, fontsize=9)
    figure.text(0.08, 0.045, "Area = 1/2    ·    First moment = 37/192    ·    Centroid = 37/96 ≈ 0.385417", fontsize=12, color=COLORS[2])
    figures = {"inference-mamdani": figure}
    figure, axes = plt.subplots(1, 2, figsize=(11.8, 5.5))
    figure.subplots_adjust(left=0.08, right=0.97, top=0.73, bottom=0.25, wspace=0.3)
    figure.suptitle("Sugeno  ·  rules contribute numbers", fontsize=19, fontweight="bold", x=0.08, ha="left", y=0.96)
    figure.text(0.08, 0.85, "The same input x = 0.25 and firing strengths (0.75, 0.25); different output models", fontsize=11, color="#c6cede")

    for axis, model, title in zip(axes, (zeroOrder, firstOrder), ("Zero order: constants", "First order: affine functions"), strict=True):
        current = model.Evaluate({"risk": 0.25})
        consequences = [trace.consequentValue for trace in current.rules]
        contributions = [trace.contribution for trace in current.rules]
        axis.bar((0, 1), consequences, width=0.55, edgecolor=COLORS[:2], facecolor="none", linewidth=2, label="consequent zᵢ")
        bars = axis.bar((0, 1), contributions, width=0.35, color=COLORS[:2], alpha=0.85, label="weighted contribution")
        axis.bar_label(bars, labels=[f"{value:.5g}" for value in contributions], padding=5, fontsize=10)
        axis.axhline(current.value, color=COLORS[2], linestyle="--", linewidth=2, label=f"output = {current.value:.2f}")
        axis.set(title=title, ylabel="Response / contribution", xticks=(0, 1), xticklabels=("Low rule", "High rule"), ylim=(0, 1))
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y")
        axis.legend(frameon=False, fontsize=9, loc="upper left")

    figure.text(0.08, 0.09, "Zero order: 0.75 × 0.20 + 0.25 × 0.80 = 0.35\nFirst order: 0.75 × 0.125 + 0.25 × 0.625 = 0.25", fontsize=11, color=COLORS[2], linespacing=1.7)
    figures["inference-sugeno"] = figure

    support = BuildSupportModel()
    coordinates = sorted({index / 500 for index in range(501)} | {0.16, 0.18, 0.20, 0.60, 0.75, 0.90})
    figure, axis = plt.subplots(figsize=(11.8, 5.5))
    figure.subplots_adjust(left=0.08, right=0.97, top=0.76, bottom=0.24)
    figure.suptitle("Mamdani  ·  every fired consequent contributes", fontsize=19, fontweight="bold", x=0.08, ha="left", y=0.96)
    figure.text(0.08, 0.86, "Two disjoint triangles, both fired at strength 1; aggregate = pointwise maximum", fontsize=11, color="#c6cede")

    for trace, color, label in zip(support.rules, COLORS, ("Small: area 0.02, center 0.18", "Large: area 0.15, center 0.75"), strict=False):
        values = [trace.activatedSet.Membership(value) for value in coordinates]
        axis.plot(coordinates, values, color=color, linewidth=2.5, label=label)
        axis.fill_between(coordinates, values, color=color, alpha=0.2)

    axis.axvline(support.value, color=COLORS[2], linewidth=2, linestyle="--", label=f"Full centroid = {support.value:.6f}")
    axis.axvline(0.75, color="#a8afc1", linewidth=1.5, linestyle=":", label="Large term alone = 0.75")
    axis.set(xlabel="Output coordinate y", ylabel="Activated membership", xlim=(0, 1), ylim=(0, 1.08))
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(True)
    axis.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(0.25, 1.02))
    figure.text(0.08, 0.09, "Independent area balance: (0.02 × 0.18 + 0.15 × 0.75) / 0.17 = 1161/1700 ≈ 0.682941", fontsize=11, color=COLORS[2])
    figures["inference-support"] = figure

    return figures


def Main(arguments=None) -> int:
    """Write deterministic SVGs or check byte identity with committed figures."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, required=True, dest="outputDirectory")
    parser.add_argument("--preview-directory", type=Path, dest="previewDirectory")
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args(arguments)
    configureStyle()

    if not options.check:
        options.outputDirectory.mkdir(parents=True, exist_ok=True)

    if options.previewDirectory is not None:
        options.previewDirectory.mkdir(parents=True, exist_ok=True)

    sizes = {}

    for name, figure in BuildFigures().items():
        destination = options.outputDirectory / f"{name}.svg"
        rendered = renderSvg(figure, name)

        if options.check:
            if not destination.is_file() or destination.read_bytes() != rendered:
                raise RuntimeError(f"stale or missing figure: {destination}")

        else:
            destination.write_bytes(rendered)

        if options.previewDirectory is not None:
            figure.savefig(options.previewDirectory / f"{name}.png", dpi=120)

        plt.close(figure)
        sizes[name] = len(rendered)

    print(json.dumps({"checked": options.check, "svgBytes": sizes}, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
