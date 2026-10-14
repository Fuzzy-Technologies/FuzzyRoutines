# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Draw measured batch speed and memory directly from a checked benchmark record."""

import argparse
import io
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = runpy.run_path(str(Path(__file__).with_name("generate_guide_figures.py")))
COLORS = STYLE["COLORS"]
plt = STYLE["plt"]
EVIDENCE = ROOT / "docs/performance/evidence/public-batches-python314-linux.json"
OUTPUT = ROOT / "docs/site/content/en/assets/figures"
LABELS = {"gaussian": "Gaussian", "bell": "Bell", "universal_scale": "Universal scale"}


def BuildFigures(report):
    """Plot recorded medians and isolated process observations without extrapolation."""

    if any(not case["parity"]["passed"] for case in report["results"]):
        raise ValueError("cannot plot performance claims with failed parity")

    if report["configuration"]["repeats"] < 7:
        raise ValueError("performance figures require at least seven paired repeats")

    STYLE["ConfigureStyle"]()
    figures = {}
    commit = report["environment"]["git_commit"][:7]
    figure, axes = plt.subplots(1, 2, figsize=(11.5, 5.4), sharey=True)
    figure.suptitle("Explicit NumPy batches: measured workload speed", fontsize=17, fontweight="bold")

    for axis, mode, title in zip(axes, ("list_conversion", "prepared_array"), ("Python list conversion included", "Prepared NumPy input"), strict=True):
        for color, (workload, label) in zip(COLORS, LABELS.items()):
            cases = [case for case in report["results"] if case["mode"] == mode and case["workload"] == workload]
            cases.sort(key=lambda case: case["size"])
            axis.plot([case["size"] for case in cases], [case["wall_speedup"] for case in cases], color=color, marker="o", linewidth=2.2, label=label)

        axis.axhline(1.0, color="#edf0f8", alpha=0.6, linestyle="--", linewidth=1)
        axis.set(xscale="log", yscale="log", xlabel="Coordinates per batch", ylabel="Scalar time / NumPy time", title=title)
        axis.grid(True, which="both", alpha=0.15)
        axis.spines[["top", "right"]].set_visible(False)
        axis.legend(loc="upper left", frameon=False, fontsize=9)

    figure.subplots_adjust(left=0.075, right=0.98, bottom=0.20, top=0.82, wspace=0.30)
    repeats = report["configuration"]["repeats"]
    figure.text(0.075, 0.07, f"Source {commit} · {repeats} paired repeats · above 1 = faster NumPy · synthetic grids, not consumer throughput", fontsize=9)
    figures["numpy-batch-speed"] = figure

    figure, axes = plt.subplots(1, 2, figsize=(11.5, 5.4))
    largest = max(case["size"] for case in report["results"])
    cases = [case for case in report["results"] if case["mode"] == "list_conversion" and case["size"] == largest]
    figure.suptitle(f"Resource cost at {largest:,} coordinates", fontsize=17, fontweight="bold")

    for axis, key, title in zip(axes, ("rss_peak_bytes", "traced_operation_peak_bytes"), ("Whole-process peak RSS", "Traced operation peak"), strict=True):
        positions = list(range(len(cases)))

        for offset, backend, color in ((-0.18, "scalar", COLORS[0]), (0.18, "numpy", COLORS[1])):
            values = [case["memory"][backend][key] / (1024 * 1024) for case in cases]
            axis.bar([position + offset for position in positions], values, width=0.34, color=color, label=backend)

        axis.set_xticks(positions, [LABELS[case["workload"]] for case in cases])
        axis.set(title=title, ylabel="MiB")
        axis.grid(True, axis="y", alpha=0.2)
        axis.set_axisbelow(True)
        axis.spines[["top", "right"]].set_visible(False)

    figure.legend(*axes[0].get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(0.5, 0.91), ncol=2, frameon=False)
    figure.subplots_adjust(left=0.075, right=0.98, bottom=0.20, top=0.82, wspace=0.30)
    figure.text(0.075, 0.07, "Isolated processes · single memory samples · RSS includes interpreter/imports · full classification evidence returned", fontsize=9)
    figures["numpy-batch-memory"] = figure

    return figures


def RenderSvg(figure, name):
    """Render stable bytes with factual measurement provenance and no timestamp."""

    buffer = io.BytesIO()
    figure.savefig(buffer, format="svg", metadata={
        "Date": None, "Creator": "FuzzyRoutines documentation", "Title": name,
        "Description": "Measured source-candidate workloads; values come from public-batches-python314-linux.json.",
    })
    rendered = b"\n".join(line.rstrip() for line in buffer.getvalue().splitlines()) + b"\n"
    header = b"<!--\nSPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies\nSPDX-License-Identifier: Apache-2.0\n-->\n"
    declarationEnd = rendered.index(b"\n") + 1

    return rendered[:declarationEnd] + header + rendered[declarationEnd:]


def Main(arguments=None):
    """Write or deterministically verify committed measured-data SVG figures."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    parser.add_argument("--output-directory", type=Path, default=OUTPUT, dest="outputDirectory")
    parser.add_argument("--preview-directory", type=Path, dest="previewDirectory")
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args(arguments)
    report = json.loads(options.evidence.read_text())
    figures = BuildFigures(report)

    for name, figure in figures.items():
        output = options.outputDirectory / f"{name}.svg"
        rendered = RenderSvg(figure, name)

        if options.check:
            if not output.is_file() or output.read_bytes() != rendered:
                raise RuntimeError(f"stale or missing figure: {output}")

        else:
            options.outputDirectory.mkdir(parents=True, exist_ok=True)
            output.write_bytes(rendered)

        if options.previewDirectory:
            options.previewDirectory.mkdir(parents=True, exist_ok=True)
            figure.savefig(options.previewDirectory / f"{name}.png", dpi=120)

        plt.close(figure)

    print(json.dumps({"checked": options.check, "figures": sorted(figures)}))


if __name__ == "__main__":
    Main()
