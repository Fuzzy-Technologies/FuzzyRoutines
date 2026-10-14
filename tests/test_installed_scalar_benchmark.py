# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Untimed provenance gates, independent scalar oracles, and report integrity."""

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from experiments import benchmark_installed_scalar as benchmark
from tools import render_installed_scalar_comparison as renderer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = PROJECT_ROOT / "experiments/installed-scalar-comparison.template.json"
RUNNER = PROJECT_ROOT / "experiments/benchmark_installed_scalar.py"


def test_IsolatedPlanDoesNotInstallOrMeasureMissingArtifacts(tmpPath):
    """Allow a reviewable plan while refusing incomplete evidence before side effects."""

    config = json.loads(TEMPLATE.read_text())
    output = tmpPath / "not-created"
    config["output_directory"] = str(output)
    configPath = tmpPath / "plan.json"
    configPath.write_text(json.dumps(config))
    command = [sys.executable, "-I", str(RUNNER), "--config", str(configPath)]
    completed = subprocess.run(command, cwd=tmpPath, capture_output=True, check=True, text=True)
    plan = json.loads(completed.stdout)

    assert plan["mode"] == "plan_only_no_installation_no_measurement"
    assert len(plan["workloads"]) == len(set(plan["workloads"])) == 30
    assert plan["pending_artifacts"]["candidate"]["wheel"] is None
    assert not output.exists()
    refused = subprocess.run([*command, "--run"], cwd=tmpPath, capture_output=True, check=False, text=True)

    assert refused.returncode != 0
    assert "ValueError" in refused.stderr
    assert not output.exists()


def test_HyperbolicOracleAgreesWithIndependentQuadrature():
    """Catch an incorrect logarithm or arctangent branch in the centroid reference."""

    count = 8192
    area = []
    moment = []

    for index in range(count + 1):
        coordinate = index / count
        weight = 1 if index in (0, count) else 4 if index % 2 else 2
        grade = 1 / (1 + (7 * coordinate) ** 4)
        area.append(weight * grade)
        moment.append(weight * coordinate * grade)

    quadrature = math.fsum(moment) / math.fsum(area)

    assert math.isclose(benchmark.ClosedFormCentroids()["hyperbolic"], quadrature, abs_tol=1e-11, rel_tol=0)


def test_UntimedExistingWorkloadsPassIndependentReferences():
    """Check fixed existing scalar workloads without collecting any timings."""

    config = json.loads(TEMPLATE.read_text())
    cases = benchmark.BuildCases(config, PROJECT_ROOT / "tools")

    assert [case["name"] for case in cases] == benchmark.WorkloadNames()[2:]

    for case in cases:
        actual = case["summarize"](case["operation"]())
        passed = case["check"]() if "check" in case else benchmark.Close(actual, case["expected"], case["tolerance"])

        assert passed, case["name"]


def ReportFixture():
    """Return artificial test samples, never presented as measured evidence."""

    samples = [100, 200, 300, 400, 500, 600, 700]
    rounds = []
    iterations = {name: 2 for name in ("scalar", "scale_construction", "scale_lookup", "fuzzyset_construction", "fuzzyset_centroid")}

    for value in samples:
        artifacts = {}

        for label in benchmark.LABELS:
            operations = {}

            for name in benchmark.WorkloadNames()[2:]:
                units = 100 if name.endswith("_lookup") else 1
                operations[name] = {"ns_per_unit": value, "raw_elapsed_ns": value * 2 * units,
                                    "iterations": 2, "units_per_iteration": units}

            artifacts[label] = {"process_startup_ns": value, "package_import_ns": value,
                                "results": operations}

        rounds.append({"artifacts": artifacts})

    return {"kind": "installed-wheel-comparison", "parity_passed": True,
            "configuration": {"repeats": 7, "iterations": iterations}, "rounds": rounds,
            "results": {name: {"baseline": benchmark.Summary(samples), "candidate": benchmark.Summary(samples),
                               "baseline_over_candidate": 1.0} for name in benchmark.WorkloadNames()}}


@pytest.mark.parametrize("mutation", ("median", "ratio", "round"))
def test_RendererRejectsStatisticsDetachedFromRawRounds(mutation):
    """Prevent a report table from accepting edited medians, ratios, or samples."""

    report = ReportFixture()
    renderer.VerifyReport(report, benchmark)
    result = report["results"]["membership_hyperbolic"]

    if mutation == "median":
        result["baseline"]["median"] = 401

    elif mutation == "ratio":
        result["baseline_over_candidate"] = 2.0

    else:
        report["rounds"][0]["artifacts"]["baseline"]["results"]["membership_hyperbolic"]["ns_per_unit"] = 101

    with pytest.raises(ValueError, match="differ"):
        renderer.VerifyReport(report, benchmark)


@pytest.mark.parametrize(("field", "value"), (
    ("raw_elapsed_ns", 1_000_000_000),
    ("raw_elapsed_ns", 0),
    ("raw_elapsed_ns", True),
    ("iterations", 0),
    ("iterations", 3),
    ("units_per_iteration", 0),
    ("units_per_iteration", 2),
))
def test_RendererRejectsRatesDetachedFromElapsedTimeAndCounts(field, value):
    """Reject contradictory durations and invalid counts even with consistent summaries."""

    report = ReportFixture()
    operation = report["rounds"][0]["artifacts"]["baseline"]["results"]["membership_hyperbolic"]
    operation[field] = value

    with pytest.raises(ValueError, match="differ|invalid"):
        renderer.VerifyReport(report, benchmark)


def test_IsolatedDraftRendererLabelsAllUnmeasuredRows(tmpPath):
    """Keep the review draft explicit and usable outside the repository import path."""

    output = tmpPath / "draft.md"
    subprocess.run(
        [sys.executable, "-I", str(PROJECT_ROOT / "tools/render_installed_scalar_comparison.py"),
         "--draft", str(TEMPLATE), "--output", str(output)],
        cwd=tmpPath, check=True, capture_output=True, text=True,
    )
    document = output.read_text()

    assert "DRAFT — NOT MEASURED" in document
    assert document.count("not measured") == 30 * 3
    assert "Wrapper source commit: `pending`" in document
