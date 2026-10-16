# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Check plotted benchmark values against raw samples, never timing thresholds."""

import json
import os
import runpy
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURES = runpy.run_path(str(PROJECT_ROOT / "tools/generate_batch_figures.py"))


@pytest.mark.parametrize(("evidencePath", "outputDirectory", "evidenceName"), (
    (FIGURES["EVIDENCE"], FIGURES["OUTPUT"], None),
    (PROJECT_ROOT / "docs/performance/evidence/public-batches-installed-python314.json", FIGURES["OUTPUT"] / "installed-candidate", "public-batches-installed-python314.json"),
    (PROJECT_ROOT / "docs/performance/evidence/post-audit-installed/batches.json", FIGURES["OUTPUT"] / "post-audit", "batches.json"),
))
def test_SpeedCurvesUsePairedSampleMediansAndMemoryBarsUseRecordedBytes(evidencePath, outputDirectory, evidenceName):
    """Independently recompute every displayed speed ratio and memory bar."""

    report = json.loads(evidencePath.read_text())
    figures = FIGURES["BuildFigures"](report)

    try:
        for axis, mode in zip(figures["numpy-batch-speed"].axes, ("list_conversion", "prepared_array"), strict=True):
            for line, workload in zip(axis.lines[:3], FIGURES["LABELS"], strict=True):
                cases = sorted((case for case in report["results"] if case["mode"] == mode and case["workload"] == workload), key=lambda case: case["size"])
                expected = [statistics.median(case["timing"]["scalar"]["wall_ns"]["raw_samples"]) / statistics.median(case["timing"]["numpy"]["wall_ns"]["raw_samples"]) for case in cases]
                assert list(line.get_xdata()) == [case["size"] for case in cases]
                assert list(line.get_ydata()) == pytest.approx(expected, rel=1e-12)

        largest = max(case["size"] for case in report["results"])
        cases = [case for case in report["results"] if case["mode"] == "list_conversion" and case["size"] == largest]

        for axis, key in zip(figures["numpy-batch-memory"].axes, ("rss_peak_bytes", "traced_operation_peak_bytes"), strict=True):
            expected = [case["memory"][backend][key] / 2**20 for backend in ("scalar", "numpy") for case in cases]
            assert [bar.get_height() for bar in axis.patches] == pytest.approx(expected, rel=1e-12)

        for name, figure in figures.items():
            assert FIGURES["RenderSvg"](figure, name, evidenceName) == (outputDirectory / f"{name}.svg").read_bytes()

    finally:
        for figure in figures.values():
            FIGURES["plt"].close(figure)


def test_BatchFigureCliDoesNotRequireTheCheckoutToolsPackage(tmpPath):
    """Check isolated CLI output, reproducibility and drift rejection with core source only."""

    packageRoot = tmpPath / "package"
    shutil.copytree(PROJECT_ROOT / "fuzzyroutines", packageRoot / "fuzzyroutines",
                    ignore=shutil.ignore_patterns("__pycache__"))
    environment = dict(os.environ, PYTHONPATH=str(packageRoot))
    command = [sys.executable, str(PROJECT_ROOT / "tools/generate_batch_figures.py")]
    helpResult = subprocess.run(command + ["--help"], cwd=tmpPath, env=environment,
                                capture_output=True, text=True, check=False, timeout=30)
    assert helpResult.returncode == 0 and "--check" in helpResult.stdout, helpResult.stderr
    outputRoot = tmpPath / "figures"
    reportPath = tmpPath / "stdout.json"

    with reportPath.open("w", encoding="utf-8") as stdout:
        result = subprocess.run(command + ["--output-directory", str(outputRoot)], cwd=tmpPath,
                                env=environment, stdout=stdout, stderr=subprocess.PIPE, text=True,
                                check=False, timeout=30)

    assert result.returncode == 0, result.stderr
    assert json.loads(reportPath.read_text()) == {"checked": False, "figures": ["numpy-batch-memory", "numpy-batch-speed"]}

    for name in ("numpy-batch-speed", "numpy-batch-memory"):
        assert (outputRoot / f"{name}.svg").read_bytes() == (PROJECT_ROOT / f"docs/site/content/en/assets/figures/{name}.svg").read_bytes()

    checked = subprocess.run(command + ["--output-directory", str(outputRoot), "--check"], cwd=tmpPath,
                             env=environment, capture_output=True, text=True, check=False, timeout=30)
    assert checked.returncode == 0 and json.loads(checked.stdout)["checked"], checked.stderr
    (outputRoot / "numpy-batch-speed.svg").write_text("stale", encoding="utf-8")
    drift = subprocess.run(command + ["--output-directory", str(outputRoot), "--check"], cwd=tmpPath,
                           env=environment, capture_output=True, text=True, check=False, timeout=30)
    assert drift.returncode != 0 and "stale or missing figure" in drift.stderr


def test_ExplicitEvidenceMetadataKeepsDefaultFiguresByteIdentical():
    """New provenance names cannot relabel the unchanged historical figure record."""

    figures = FIGURES["BuildFigures"](json.loads(FIGURES["EVIDENCE"].read_text()))

    try:
        for name, figure in figures.items():
            original = (PROJECT_ROOT / f"docs/site/content/en/assets/figures/{name}.svg").read_bytes()
            assert FIGURES["RenderSvg"](figure, name) == original
            updated = FIGURES["RenderSvg"](figure, name, "public-batches-installed-python314.json")
            assert b"Measured workloads; values come from public-batches-installed-python314.json." in updated
            assert b"values come from public-batches-python314-linux.json" not in updated

    finally:
        for figure in figures.values():
            FIGURES["plt"].close(figure)
