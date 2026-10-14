# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Measure the public batch workloads using only an exact installed CI wheel.

Default mode prints a plan. Explicit --run creates a new offline environment;
the retained workload builders and paired timers are unchanged. Only their
source-oriented worker spawning and provenance are replaced. Batch, memory and
import workers use -I and expose only the experiments namespace, not checkout core.
Old source reports are never read as measurements or overwritten.
"""

import argparse
import importlib
import importlib.machinery
import importlib.metadata
import importlib.util
import json
import math
import platform
import statistics
import subprocess
import sys
import venv
import zipfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHAPES = ((1,), (16,), (32, 32), (10000,))
HARNESS_FILES = ("experiments/installed_batch_benchmark.py", "experiments/installed_wheel_evidence.py",
                 "experiments/benchmark_public_batches.py", "experiments/benchmark_vectorized_membership.py",
                 "experiments/vectorized_membership.py", "tools/extract_consumer_replay.py",
                 "tests/fixtures/public_consumer_batches.json")


def LoadEvidence():
    """Read the shared artifact verifier without adding any checkout to sys.path."""

    specification = importlib.util.spec_from_file_location("installed_wheel_evidence", Path(__file__).with_name("installed_wheel_evidence.py"))
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)

    return module


EVIDENCE = LoadEvidence()


def WriteJson(path, value):
    """Persist complete evidence with strict finite JSON numbers."""

    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def LoadWorkloads():
    """Expose only the exact experiments directory, never the source core package."""

    if "experiments" in sys.modules:
        if str(ROOT / "experiments") not in getattr(sys.modules["experiments"], "__path__", ()):
            raise ValueError("unexpected experiments namespace")

    else:
        specification = importlib.machinery.ModuleSpec("experiments", loader=None, is_package=True)
        specification.submodule_search_locations.append(str(ROOT / "experiments"))
        sys.modules["experiments"] = importlib.util.module_from_spec(specification)

    return importlib.import_module("experiments.benchmark_public_batches"), importlib.import_module("experiments.benchmark_vectorized_membership")


def Validate(config):
    """Require the agreed bounded matrix, isolation and immutable artifact inputs."""

    if not sys.flags.isolated or platform.python_implementation() != "CPython" or sys.version_info[:2] != (3, 14):
        raise ValueError("run with isolated CPython 3.14: python -I")

    paths = (config["repository"], config["output_directory"], config["numpy_wheel"]["path"], config["candidate"]["wheel"], config["candidate"]["provenance_json"])

    if any(not Path(path).is_absolute() for path in paths):
        raise ValueError("artifact, repository and output paths must be absolute")

    if Path(config["repository"]).resolve() != ROOT:
        raise ValueError("run the harness from its declared clean repository")

    if config["repeats"] < 7 or config["warmups"] != 1 or tuple(map(tuple, config["shapes"])) != SHAPES:
        raise ValueError("require seven or more paired repeats, one warmup and the fixed 24-case matrix")

    if Path(config["output_directory"]).resolve().is_relative_to(ROOT):
        raise ValueError("write measurements outside the clean harness checkout")

    numpyWheel = Path(config["numpy_wheel"]["path"])

    if EVIDENCE.Digest(numpyWheel.read_bytes()) != config["numpy_wheel"]["sha256"]:
        raise ValueError("NumPy wheel digest mismatch")

    with zipfile.ZipFile(numpyWheel) as archive:
        metadata = archive.read(next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))).decode()

    if "Name: numpy\n" not in metadata or "Version: 2.3.5\n" not in metadata:
        raise ValueError("pin the NumPy 2.3.5 wheel used by the original batch study")


def VerifyWorker(config):
    """Record loaded installed origins after each measurement outside timed regions."""

    installed = EVIDENCE.VerifyInstalledPackage(config["verified_candidate"], requireNoNumpy=False)

    return {"package_origin": installed["package_origin"], "package_version": installed["package_version"],
            "loaded_module_origins": installed["loaded_module_origins"], "wheel_sha256": config["candidate"]["wheel_sha256"]}


def ChildCommand(configPath, kind, payload=None):
    """Keep the same environment and isolation for memory and fresh-import workers."""

    command = [sys.executable, "-I", str(Path(__file__).resolve()), "--config", str(configPath), "--worker", kind]

    if payload is not None:
        command.extend(["--case", json.dumps(payload, separators=(",", ":"))])

    return command


def BindInstalledWorkers(public, common, configPath, config, commands):
    """Replace source-only subprocess dispatch while retaining scientific operations."""

    def Invoke(kind, payload):
        """Run a fresh installed worker and retain its exact invocation."""

        command = ChildCommand(configPath, kind, payload)
        commands.append(command)
        completed = subprocess.run(command, cwd=config["output_directory"], check=True, capture_output=True, text=True)
        result = json.loads(completed.stdout)

        if result["installed_package"]["wheel_sha256"] != config["candidate"]["wheel_sha256"]:
            raise ValueError("worker measured a different candidate wheel")

        return result

    def Memory(workload, backend, mode, shape, coordinates=None):
        """Keep traced allocations and process RSS in independent backend workers."""

        return Invoke("memory", [workload, backend, mode, list(shape), coordinates])

    def Import(arguments):
        """Permit only the original fresh-process package and NumPy import probes."""

        if len(arguments) != 2 or arguments[0] != "--import-worker" or arguments[1] not in ("fuzzyroutines", "numpy"):
            raise ValueError("unexpected dependency worker")

        return Invoke("import", arguments[1])

    setattr(public, "RunMemory", Memory)
    setattr(common, "RunWorker", Import)


def ValidateMeasurements(report, expectedCases):
    """Recompute timing summaries and ratios; never impose a speed threshold."""

    repeats = report["configuration"]["repeats"]

    if len(report["results"]) != expectedCases or repeats < 7:
        raise ValueError("incomplete benchmark matrix or repeats")

    for case in report["results"]:
        if not case["parity"]["passed"]:
            raise ValueError("failed numerical parity invalidates timing evidence")

        for backend in ("scalar", "numpy"):
            for timer in ("wall_ns", "cpu_ns"):
                observed = case["timing"][backend][timer]
                samples = observed["raw_samples"]

                if len(samples) != repeats or any(not math.isfinite(value) or value <= 0 for value in samples):
                    raise ValueError("timing raw samples must be positive finite and complete")

                lower, _, upper = statistics.quantiles(samples, n=4, method="inclusive")
                expected = {"median": statistics.median(samples), "minimum": min(samples), "maximum": max(samples), "interquartile_range": upper - lower}

                if any(observed[name] != value for name, value in expected.items()):
                    raise ValueError("timing summary disagrees with raw samples")

        expectedRatio = case["timing"]["scalar"]["wall_ns"]["median"] / case["timing"]["numpy"]["wall_ns"]["median"]

        if case["wall_speedup"] != expectedRatio:
            raise ValueError("speed ratio disagrees with raw samples")


def FinishReport(report, config, harness, commands, kind):
    """Label measured wheel and execution harness separately without source claims."""

    artifact = config["verified_candidate"]
    installed = VerifyWorker(config)
    environment = report["environment"]
    environment.update({"git_commit": artifact["source_commit"], "git_dirty": None,
                        "package_version": artifact["version"], "package_origin": installed["package_origin"],
                        "package_module_origins": installed["loaded_module_origins"],
                        "source_sha256": artifact["package_file_sha256"], "harness_git_commit": harness["source_commit"]})
    report["benchmark"] = kind
    report["measurement_completed_at"] = datetime.now(UTC).isoformat()
    report["baseline"] = {"kind": "canonical scalar APIs from the same installed candidate wheel", "git_commit": artifact["source_commit"], "wheel_sha256": artifact["wheel_sha256"]}
    report["configuration"]["command"] = config["invocation"]
    report["configuration"]["paired_backend_order"] = [["scalar", "numpy"] if index % 2 == 0 else ["numpy", "scalar"] for index in range(config["repeats"])]
    report["provenance"] = {"candidate": artifact, "harness": harness, "executed_commands": list(commands),
                            "input_config_sha256": config["input_config_sha256"],
                            "git_field_meaning": "package source identity proven against wheel bytes; installed wheels have no Git dirty state",
                            "source_report_adaptation": "unchanged public builders/parity/paired timers; isolated installed memory/import dispatch and corrected provenance"}
    report["limitations"][0] = "installed CI candidate on a shared host, not a published PyPI release"
    report["limitations"].append("fresh-process imports; verification reads package bytes before timing; filesystem caches are not flushed")

    return report


def Execute(configPath, config):
    """Collect the two additive reports using the already-installed exact candidate."""

    Validate(config)
    harness = EVIDENCE.VerifyHarness(ROOT, config["harness_commit"], HARNESS_FILES)
    EVIDENCE.VerifyInstalledPackage(config["verified_candidate"], requireNoNumpy=False)

    if importlib.metadata.version("numpy") != "2.3.5":
        raise ValueError("installed NumPy version differs from the pinned experiment")

    public, common = LoadWorkloads()
    commands = []
    BindInstalledWorkers(public, common, configPath, config, commands)
    synthetic = public.BuildReport(SHAPES, repeats=config["repeats"], warmups=config["warmups"], memory=True, wheel=Path(config["numpy_wheel"]["path"]))
    ValidateMeasurements(synthetic, 24)
    synthetic = FinishReport(synthetic, config, harness, commands, "public-batches-installed-candidate")
    synthetic["dependency"]["actual_environment_install_command"] = config["install_command"]
    output = Path(config["output_directory"])
    syntheticPath = output / "public-batches-installed-python314.json"
    WriteJson(syntheticPath, synthetic)
    consumer = public.BuildConsumerReport(repeats=config["repeats"], warmups=config["warmups"], memory=True)
    ValidateMeasurements(consumer, 4)
    consumer = FinishReport(consumer, config, harness, commands, "public-consumer-replays-installed-candidate")
    consumer["dependency_evidence"] = {"path": syntheticPath.name, "sha256": EVIDENCE.Digest(syntheticPath.read_bytes()), "scope": "Same installed candidate and environment; dependency costs measured once in the accompanying synthetic run."}
    EVIDENCE.VerifyHarness(ROOT, config["harness_commit"], HARNESS_FILES)
    VerifyWorker(config)
    consumerPath = output / "public-consumer-replays-installed-python314.json"
    WriteJson(consumerPath, consumer)

    return {"reports": [str(syntheticPath), str(consumerPath)], "synthetic_cases": 24, "public_replay_cases": 30,
            "public_replay_mode_groups": 4, "paired_repeats": config["repeats"], "parity_passed": True}


def Run(configPath, config):
    """Install only supplied local wheels in a new environment before measuring."""

    Validate(config)
    EVIDENCE.VerifyHarness(ROOT, config["harness_commit"], HARNESS_FILES)
    artifact = EVIDENCE.VerifyWheel(config, "candidate")
    output = Path(config["output_directory"]).resolve()
    output.mkdir(parents=True, exist_ok=False)
    environment = output / "environment"
    venv.EnvBuilder(with_pip=True).create(environment)
    executable = str(environment / "bin/python")
    install = [executable, "-m", "pip", "install", "--no-index", "--no-deps", "--no-compile", "--disable-pip-version-check", artifact["wheel"], str(Path(config["numpy_wheel"]["path"]).resolve())]
    subprocess.run(install, check=True, capture_output=True, text=True)
    execution = {**config, "verified_candidate": artifact, "install_command": install,
                 "input_config_sha256": EVIDENCE.Digest(configPath.read_bytes()),
                 "invocation": [sys.executable, "-I", str(Path(__file__).resolve()), "--config", str(configPath.resolve()), "--run"]}
    executionPath = output / "execution-config.json"
    WriteJson(executionPath, execution)
    command = [executable, *ChildCommand(executionPath, "execute")[1:]]
    completed = subprocess.run(command, cwd=output, check=True, text=True, stdout=subprocess.PIPE)
    result = json.loads(completed.stdout)
    WriteJson(output / "completed.json", {**result, "execution_command": command})

    return result


def Main(arguments=None):
    """Print a read-only plan unless an explicit run or isolated worker is selected."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--worker", choices=("execute", "memory", "import"))
    parser.add_argument("--case", type=json.loads)
    options = parser.parse_args(arguments)
    config = json.loads(options.config.read_text())

    if options.worker == "execute":
        result = Execute(options.config, config)

    elif options.worker:
        if not sys.flags.isolated:
            raise ValueError("measurement workers require python -I")

        EVIDENCE.VerifyInstalledPackage(config["verified_candidate"], requireNoNumpy=False)
        public, common = LoadWorkloads()

        if options.worker == "memory":
            workload, backend, mode, shape, coordinates = options.case
            result = public.MemoryWorker(workload, backend, mode, tuple(shape), coordinates)

        else:
            if options.case not in ("fuzzyroutines", "numpy"):
                raise ValueError("unsupported import probe")

            result = common.ImportWorker(options.case)

        result["installed_package"] = VerifyWorker(config)

    elif options.run:
        result = Run(options.config, config)

    else:
        result = {"mode": "plan_only_no_installation_no_measurement", "synthetic_cases": 24, "public_replay_cases": 30,
                  "public_replay_mode_groups": 4, "shapes": list(map(list, SHAPES)), "repeats": config["repeats"],
                  "candidate": config["candidate"], "harness_commit": config["harness_commit"]}

    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
