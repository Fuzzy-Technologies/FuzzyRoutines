# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Render optional neural-example evidence without retraining or importing Torch.

Requires docs/requirements-plots.txt and the candidate FuzzyRoutines package.
The committed experiment report supplies every fitted curve and metric;
fixed membership curves and the illustrative target regions use the public API.
"""

import argparse
import hashlib
import io
import json
import runpy
from pathlib import Path

from fuzzyroutines import CreateUniversalFuzzyScale, UniversalFuzzyScalePolicy

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def CreatePanels(plottingHelpers, title):
    """Apply the documentation palette to a spacious two-by-two scientific figure."""

    figure, axes = plottingHelpers["plt"].subplots(2, 2, figsize=(13.2, 9.8))
    figure.suptitle(title, fontsize=20, fontweight="bold", x=0.06, ha="left")
    figure.subplots_adjust(left=0.075, right=0.97, top=0.86, bottom=0.105, wspace=0.26, hspace=0.50)
    figure.text(0.06, 0.035, "FuzzyRoutines + PyTorch CPU  ·  synthetic data  ·  fixed fuzzy terms, trained network weights", fontsize=10, color="#aab6cf")

    for axis in axes.flat:
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(True, alpha=0.15)
        axis.set_axisbelow(True)

    return figure, tuple(axes.flat)


def BuildFigures(report, plottingHelpers):
    """Plot recorded model outputs with the exact fixed scale and scalar target rule."""

    colors = (*plottingHelpers["COLORS"], "#8cdb91")
    scale = CreateUniversalFuzzyScale()
    figure, axes = CreatePanels(plottingHelpers, "Fixed fuzzy inputs, learned network, explicit output decoding")
    coordinates = [index / 400 for index in range(401)]

    for term, color in zip(scale.terms, colors, strict=True):
        axes[0].plot(coordinates, [term.fuzzySet.Membership(value) for value in coordinates], color=color, linewidth=2, label=term.name)

    axes[0].set(title="A  Historical input memberships", xlabel="Normalized severity or exposure", ylabel="Membership grade", xlim=(0, 1), ylim=(-0.03, 1.10))
    axes[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.01), ncol=5, fontsize=9, frameon=False)
    axes[0].annotate("Weak coverage at x = 0.17", (0.17, 0.003), xytext=(0.35, 0.25), fontsize=10, arrowprops={"arrowstyle": "->", "color": "#edf0f8"})
    centroid = report["scalarAblations"]["centroid"]

    for key, color, label in (("trainMse", colors[0], "Training"), ("validationMse", colors[1], "Validation")):
        axes[1].semilogy([item["epoch"] for item in centroid["history"]], [item[key] for item in centroid["history"]], color=color, linewidth=2, label=label)

    axes[1].axvline(centroid["bestEpoch"], color=colors[2], linestyle=":", label=f"Selected epoch {centroid['bestEpoch']}")
    axes[1].set(title="B  Centroid-input MLP learning", xlabel="Epoch", ylabel="Mean squared error")
    axes[1].legend(fontsize=9, frameon=False)
    severity = report["slice"]["severity"]
    axes[2].plot(severity, report["slice"]["centroidTargets"], color="#edf0f8", linewidth=2, label="Centroid target")
    axes[2].plot(severity, report["slice"]["latentScores"], color="#8490ab", linestyle="--", linewidth=1.5, label="Latent score")

    for representation, color, label in zip(("raw", "centroid", "memberships"), colors[:3], ("Raw", "Centroid", "Full grades"), strict=True):
        axes[2].plot(severity, report["scalarAblations"][representation]["slicePredictions"], color=color, linewidth=2, label=label)

    axes[2].set(title="C  Prediction slice at exposure = 0.5", xlabel="Normalized severity", ylabel="Output coordinate", xlim=(0, 1))
    axes[2].legend(fontsize=9, ncol=2, frameon=False)
    prediction = centroid["probes"][2]

    if prediction["memberships"] is None:
        axes[3].text(0.5, 0.5, f"Prediction rejected: {prediction['status']}", transform=axes[3].transAxes, ha="center")

    else:
        axes[3].bar(report["termOrder"], prediction["memberships"], color=colors, width=0.65)

    axes[3].set(title="D  Decode one scalar prediction", xlabel="Ordered output term", ylabel="Membership grade", ylim=(0, 1.12))
    axes[3].text(0.03, 0.96, f"Inputs (0.37, 0.63)\nPredicted coordinate {prediction['value']:.4f} → {prediction['label']}", transform=axes[3].transAxes, va="top", fontsize=10,
                 bbox={"facecolor": "#121829", "edgecolor": "none", "alpha": 0.9, "pad": 3})
    figures = {"neural-integration": figure}
    figure, axes = CreatePanels(plottingHelpers, "Held-out ablations and a separate membership-output task")
    names = ("Train mean", "Raw", "Centroid", "Full grades")
    results = (report["baseline"], *(report["scalarAblations"][name]["heldOut"] for name in ("raw", "centroid", "memberships")))
    rmse = [result["centroidRmse"] for result in results]
    accuracy = [result["labelAccuracy"] for result in results]

    for axis, values, title, ylabel, limit in ((axes[0], rmse, "A  Same centroid target for every scalar model", "Held-out RMSE", max(rmse) * 1.20),
                                             (axes[1], accuracy, "B  Decode scalar outputs to linguistic labels", "Held-out label accuracy", 1.12)):
        bars = axis.bar(names, values, color=("#8490ab", *colors[:3]), width=0.65)
        axis.bar_label(bars, labels=[f"{value:.3f}" for value in values], padding=4, color="#edf0f8", fontsize=10)
        axis.set(title=title, ylabel=ylabel, ylim=(0, limit))

    axes[1].axhline(report["baseline"]["majorityLabelAccuracy"], color=colors[3], linestyle=":", label="Training-majority label baseline")
    axes[1].legend(fontsize=9, loc="upper left", frameon=False)
    grid = [index / 60 for index in range(61)]
    policy = UniversalFuzzyScalePolicy()
    termIndices = {name: index for index, name in enumerate(report["termOrder"])}
    labels = [[termIndices[scale.Fuzzify(0.05 + 0.65 * severity + 0.30 * exposure, policy).selectedTerms[0].name] for severity in grid] for exposure in grid]
    from matplotlib.colors import ListedColormap

    axes[2].imshow(labels, origin="lower", extent=(0, 1, 0, 1), interpolation="nearest", aspect="auto", cmap=ListedColormap(colors), vmin=-0.5, vmax=4.5, alpha=0.75)
    axes[2].set(title="C  Reference linguistic regions", xlabel="Normalized severity", ylabel="Normalized exposure")

    for name, severity, exposure in (("Min", 0.06, 0.08), ("Low", 0.19, 0.22), ("Med", 0.47, 0.45), ("High", 0.77, 0.68), ("Max", 0.9, 0.92)):
        axes[2].text(severity, exposure, name, ha="center", color="#121829", fontweight="bold", fontsize=10)

    axes[2].scatter((0.4, 0.6), (0.9, 0.9), c="#121829", edgecolors="#edf0f8", s=65, zorder=3)
    axes[2].annotate("Same centroid inputs;\ndifferent target labels", (0.5, 0.9), xytext=(0.26, 0.55), color="#121829", fontweight="bold", fontsize=10,
                     arrowprops={"arrowstyle": "->", "color": "#121829"})
    weak = report["gradeHead"]["weakCoverageProbe"]
    positions = list(range(5))
    axes[3].bar([value - 0.18 for value in positions], weak["targetGrades"], width=0.36, color="#edf0f8", label="Target grades")
    axes[3].bar([value + 0.18 for value in positions], weak["predictedGrades"], width=0.36, color=colors, label="Predicted grades")
    axes[3].set_xticks(positions, report["termOrder"])
    axes[3].set(title="D  Five-grade head at weak coverage", xlabel="Ordered output term", ylabel="Membership grade", ylim=(0, max(*weak["targetGrades"], *weak["predictedGrades"]) * 1.5))
    axes[3].legend(fontsize=9, frameon=False, loc="upper right")
    axes[3].text(0.03, 0.96, f"Target score = 0.17\nTarget grade sum = {sum(weak['targetGrades']):.5f}", transform=axes[3].transAxes, va="top", fontsize=9)
    figures["neural-ablation"] = figure

    return figures


def RenderSvg(figure, name):
    """Fix scientific provenance and metadata without timestamps."""

    buffer = io.BytesIO()
    figure.savefig(buffer, format="svg", metadata={"Date": None, "Creator": "FuzzyRoutines documentation", "Title": f"FuzzyRoutines: {name}",
                                                 "Description": "Fixed scalar memberships and recorded PyTorch CPU experiment; see examples/neural/reference.json."})
    rendered = b"\n".join(line.rstrip() for line in buffer.getvalue().splitlines()) + b"\n"
    header = b"<!--\nSPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies\nSPDX-License-Identifier: Apache-2.0\n-->\n"
    declarationEnd = rendered.index(b"\n") + 1

    return rendered[:declarationEnd] + header + rendered[declarationEnd:]


def Main(arguments=None) -> int:
    """Write or compare two deterministic figures from a source-matched report."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=PROJECT_ROOT / "examples/neural/reference.json")
    parser.add_argument("--output-directory", required=True, type=Path, dest="outputDirectory")
    parser.add_argument("--preview-directory", type=Path, dest="previewDirectory")
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args(arguments)
    report = json.loads(options.report.read_text(encoding="utf-8"))

    if report["exampleSha256"] != hashlib.sha256((PROJECT_ROOT / "examples/neural/run.py").read_bytes()).hexdigest():
        raise RuntimeError("neural report was produced by a different example source")

    helpers = runpy.run_path(str(Path(__file__).with_name("generate_guide_figures.py")))
    helpers["ConfigureStyle"]()
    figures = BuildFigures(report, helpers)
    sizes = {}

    for name, figure in figures.items():
        rendered = RenderSvg(figure, name)
        destination = options.outputDirectory / f"{name}.svg"

        if options.check:
            if not destination.is_file() or destination.read_bytes() != rendered:
                raise RuntimeError(f"stale or missing figure: {destination}")

        else:
            options.outputDirectory.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(rendered)

        if options.previewDirectory is not None:
            options.previewDirectory.mkdir(parents=True, exist_ok=True)
            figure.savefig(options.previewDirectory / f"{name}.png", dpi=120)

        helpers["plt"].close(figure)
        sizes[name] = len(rendered)

    print(json.dumps({"checked": options.check, "figures": sizes}, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
