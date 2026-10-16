# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Verify installed batch dispatch and evidence identities without running timings."""

import copy
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

from experiments import installed_batch_benchmark as benchmark


def MeasuredFixture():
    """Use seven analytical sample values with independently known summary fields."""

    summary = {"raw_samples": [1, 2, 3, 4, 5, 6, 7], "median": 4, "minimum": 1, "maximum": 7, "interquartile_range": 3}
    result = {"parity": {"passed": True}, "timing": {backend: {timer: copy.deepcopy(summary) for timer in ("wall_ns", "cpu_ns")} for backend in ("scalar", "numpy")}, "wall_speedup": 1.0}

    return {"configuration": {"repeats": 7}, "results": [result]}


def test_IndependentSummaryAuditDoesNotRequireFasterNumpy():
    """Correct retained samples pass even when the optional backend is slower."""

    report = MeasuredFixture()
    values = report["results"][0]["timing"]["numpy"]["wall_ns"]

    for key in ("median", "minimum", "maximum", "interquartile_range"):
        values[key] *= 2

    values["raw_samples"] = [value * 2 for value in values["raw_samples"]]
    report["results"][0]["wall_speedup"] = 0.5
    benchmark.ValidateMeasurements(report, 1)


@pytest.mark.parametrize("mutation", ["matrix", "repeats", "parity", "median", "iqr", "ratio", "samples", "nonfinite"])
def test_RawEvidenceRejectsMisleadingSummaryOrMissingSamples(mutation):
    """A plausible summary cannot conceal missing, nonfinite or inconsistent raw evidence."""

    report = MeasuredFixture()
    case = report["results"][0]
    summary = case["timing"]["scalar"]["wall_ns"]

    if mutation == "matrix":
        report["results"] = []

    elif mutation == "repeats":
        report["configuration"]["repeats"] = 6

    elif mutation == "parity":
        case["parity"]["passed"] = False

    elif mutation == "median":
        summary["median"] = 5

    elif mutation == "iqr":
        summary["interquartile_range"] = 4

    elif mutation == "ratio":
        case["wall_speedup"] = 2

    elif mutation == "samples":
        summary["raw_samples"].pop()

    else:
        summary["raw_samples"][0] = float("nan")

    with pytest.raises(ValueError):
        benchmark.ValidateMeasurements(report, 1)


def test_ChildWorkersAlwaysRetainIsolatedInterpreterAndExplicitPayload(tmpPath, monkeypatch):
    """Source-oriented worker calls are replaced for both memory and import evidence."""

    public, common = types.SimpleNamespace(), types.SimpleNamespace()
    config = {"output_directory": str(tmpPath), "candidate": {"wheel_sha256": "a" * 64}}
    calls, commands = [], []

    def Capture(command, **options):
        """Record subprocess construction without starting a measured worker."""

        calls.append((command, options))

        return types.SimpleNamespace(stdout=json.dumps({"installed_package": {"wheel_sha256": "a" * 64}, "wall_ns": 1}))

    monkeypatch.setattr(benchmark.subprocess, "run", Capture)
    configPath = tmpPath / "config.json"
    benchmark.BindInstalledWorkers(public, common, configPath, config, commands)
    public.RunMemory("universal_scale", "numpy", "prepared_array", (3, 5))
    common.RunWorker(["--import-worker", "fuzzyroutines"])
    assert len(calls) == len(commands) == 2
    assert all(command[:2] == [sys.executable, "-I"] and options["cwd"] == str(tmpPath) for command, options in calls)
    assert json.loads(commands[0][-1]) == ["universal_scale", "numpy", "prepared_array", [3, 5], None]
    assert json.loads(commands[1][-1]) == "fuzzyroutines"

    with pytest.raises(ValueError, match="unexpected dependency"):
        common.RunWorker(["--memory-worker", "numpy"])


def test_ChildCannotSilentlyMeasureAnotherWheel(tmpPath, monkeypatch):
    """A child result with another artifact digest fails before entering the report."""

    public, common = types.SimpleNamespace(), types.SimpleNamespace()
    config = {"output_directory": str(tmpPath), "candidate": {"wheel_sha256": "a" * 64}}
    monkeypatch.setattr(benchmark.subprocess, "run", lambda *args, **kwargs: types.SimpleNamespace(stdout=json.dumps({"installed_package": {"wheel_sha256": "b" * 64}})))
    benchmark.BindInstalledWorkers(public, common, tmpPath / "config.json", config, [])

    with pytest.raises(ValueError, match="different candidate"):
        common.RunWorker(["--import-worker", "numpy"])


def test_FinalReportSeparatesInstalledPackageFromHarnessSource(monkeypatch):
    """A harness revision or source-tree version cannot masquerade as the measured wheel."""

    report = {"environment": {"git_commit": "harness", "git_dirty": False, "package_version": "source tree", "source_sha256": {"source": "ignored"}}, "configuration": {}, "limitations": ["source checkout"]}
    artifact = {"source_commit": "c" * 40, "version": "2.1.0", "package_file_sha256": {"fuzzyroutines/__init__.py": "d" * 64}, "wheel_sha256": "e" * 64}
    config = {"verified_candidate": artifact, "invocation": ["python", "-I", "runner.py"], "repeats": 7, "input_config_sha256": "f" * 64}
    installed = {"package_origin": "/venv/site-packages/fuzzyroutines/__init__.py", "loaded_module_origins": {"fuzzyroutines": "/venv/site-packages/fuzzyroutines/__init__.py"}}
    monkeypatch.setattr(benchmark, "VerifyWorker", lambda config: installed)
    result = benchmark.FinishReport(report, config, {"source_commit": "a" * 40, "dirty": False}, [], "installed-fixture")
    assert result["environment"]["git_commit"] == "c" * 40
    assert result["environment"]["harness_git_commit"] == "a" * 40
    assert result["environment"]["git_dirty"] is None
    assert result["environment"]["source_sha256"] == artifact["package_file_sha256"]
    assert result["environment"]["package_version"] == "2.1.0"
    assert result["baseline"]["wheel_sha256"] == artifact["wheel_sha256"]
    assert result["provenance"]["input_config_sha256"] == "f" * 64
    assert result["configuration"]["paired_backend_order"][:3] == [["scalar", "numpy"], ["numpy", "scalar"], ["scalar", "numpy"]]


def test_PlanModeDoesNotInstallImportPackageOrRequireFinalArtifacts(tmpPath):
    """An incomplete template remains useful without installing or timing anything."""

    config = tmpPath / "plan.json"
    config.write_text(json.dumps({"candidate": {}, "harness_commit": None, "repeats": 7}))
    result = subprocess.run([sys.executable, "-I", str(Path(benchmark.__file__).resolve()), "--config", str(config)], cwd=tmpPath, capture_output=True, text=True, check=True)
    plan = json.loads(result.stdout)
    assert plan["mode"] == "plan_only_no_installation_no_measurement"
    assert (plan["synthetic_cases"], plan["public_replay_cases"], plan["public_replay_mode_groups"]) == (24, 30, 4)
    assert not (tmpPath / "environment").exists()


def test_RestrictedExperimentsNamespaceDoesNotExposeSourceCore(tmpPath):
    """Isolated no-site execution loads measurement helpers while core remains absent."""

    script = """import importlib.util, json, sys
spec = importlib.util.spec_from_file_location('batch_harness', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
before = list(sys.path)
module.LoadWorkloads()
assert sys.path == before
assert importlib.util.find_spec('fuzzyroutines') is None
assert 'numpy' not in sys.modules
print(json.dumps({'isolated': True, 'sourceCoreExposed': False}))
"""
    result = subprocess.run([sys.executable, "-I", "-S", "-c", script, str(Path(benchmark.__file__).resolve())], cwd=tmpPath, capture_output=True, text=True, check=True)
    assert json.loads(result.stdout) == {"isolated": True, "sourceCoreExposed": False}
