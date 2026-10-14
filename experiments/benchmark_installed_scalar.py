# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Prepare or run an isolated comparison of two explicitly supplied wheels.

Default mode only prints a plan. --run installs local, hash-verified wheels
without dependencies and measures them in alternating fresh CPython processes.
Existing repository workload builders are loaded from pinned Git bytes, never
added to sys.path. Their checkout-oriented GetGitMetadata is deliberately unused.
"""

import argparse
import functools
import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import math
import os
import platform
import re
import statistics
import subprocess
import sys
import time
import venv
from datetime import UTC, datetime
from pathlib import Path

LABELS = ("baseline", "candidate")
HARNESSES = ("benchmark_membership_operators.py", "benchmark_scale_lookup.py", "benchmark_fuzzyset_centroid.py")


def Digest(data):
    """Return a reproducible artifact identity."""

    return hashlib.sha256(data).hexdigest()


def Git(config, *arguments):
    """Read immutable repository objects without changing the checkout."""

    return subprocess.check_output(["git", "-C", config["repository"], *arguments])


def WriteJson(path, value):
    """Write one explicitly requested evidence file."""

    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def Summary(values):
    """Summarize retained samples using the repository's inclusive IQR convention."""

    lower, _, upper = statistics.quantiles(values, n=4, method="inclusive")

    return {"raw_samples": values, "minimum": min(values), "median": statistics.median(values),
            "maximum": max(values), "interquartile_range": upper - lower}


def Environment():
    """Record host/interpreter limits without changing affinity or process priority."""

    cpu = platform.processor()
    cpuInfo = Path("/proc/cpuinfo")

    if cpuInfo.is_file():
        cpu = next((line.split(":", 1)[1].strip() for line in cpuInfo.read_text().splitlines() if line.startswith("model name")), cpu)

    limits = {name: path.read_text().strip() for name in ("cpu.max", "memory.max")
              if (path := Path("/sys/fs/cgroup") / name).is_file()}
    base = Path(getattr(sys, "_base_executable", sys.executable)).resolve()

    return {"python": sys.version, "implementation": platform.python_implementation(),
            "base_executable": str(base), "base_executable_sha256": Digest(base.read_bytes()),
            "executable": sys.executable, "platform": platform.platform(), "processor": cpu,
            "logical_cpu_count": os.cpu_count(), "affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
            "physical_memory_bytes": os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"),
            "cgroup": limits, "thread_environment": {name: os.environ.get(name) for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}}


def WorkloadNames():
    """Describe the fixed plan without importing or timing either package."""

    names = ["membership_" + name for name in ("hyperbolic", "bell", "parabolic", "triangle", "trapezium", "exponential", "sigmoidal", "desirability")]
    names += [prefix + "_" + name for name in ("logic", "algebraic", "boundary", "drastic") for prefix in ("tnorm", "sconorm")]
    names += ["scale_" + name + "_" + operation for name in ("default", "universal") for operation in ("construction", "lookup")]
    names += ["fuzzyset_" + name + "_" + operation for name in ("hyperbolic", "bell", "triangle", "parabolic") for operation in ("construction", "centroid")]

    return ["process_startup", "package_import", *names]


def Validate(config):
    """Fail before installation when artifact identity or sampling inputs are absent."""

    if platform.python_implementation() != "CPython" or sys.version_info[:2] != (3, 14):
        raise ValueError("run both artifacts with the same CPython 3.14 interpreter")

    if config["repeats"] < 7 or config["warmups"] < 1 or any(value < 1 for value in config["iterations"].values()):
        raise ValueError("require at least seven repeats, one warmup, and positive iterations")

    if not re.fullmatch("[0-9a-f]{40}", config["harness_commit"] or ""):
        raise ValueError("pin a full harness commit, separately from both package commits")

    if not re.fullmatch("[0-9a-f]{40}", config["workload_commit"] or ""):
        raise ValueError("pin the historical workload commit separately from the new wrapper")

    for label in LABELS:
        artifact = config[label]

        if not re.fullmatch("[0-9a-f]{64}", artifact["wheel_sha256"] or "") or not re.fullmatch("[0-9a-f]{40}", artifact["source_commit"] or ""):
            raise ValueError(f"supply verified wheel SHA256 and source commit for {label}")

        for key in ("wheel", "provenance_json"):
            if not artifact[key] or not Path(artifact[key]).is_file():
                raise ValueError(f"supply the actual {label} {key}")

        if not artifact["version"] or not artifact["source_evidence_url"]:
            raise ValueError(f"supply {label} version and provenance URL")


@functools.cache
def Evidence():
    """Load the shared stdlib verifier by filename under isolated Python."""

    path = Path(__file__).with_name("installed_wheel_evidence.py")
    spec = importlib.util.spec_from_file_location("installed_wheel_evidence", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def LoadHarness(path, name):
    """Load a pinned script by filename without exposing its checkout on sys.path."""

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def Close(actual, expected, tolerance):
    """Compare structured observations independently of timing measurements."""

    if isinstance(expected, dict):
        return isinstance(actual, dict) and actual.keys() == expected.keys() and all(Close(actual[key], value, tolerance) for key, value in expected.items())

    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(Close(left, right, tolerance) for left, right in zip(actual, expected))

    if isinstance(expected, (float, int)) and not isinstance(expected, bool):
        return math.isclose(actual, expected, abs_tol=tolerance, rel_tol=0.0)

    return actual == expected


def ClosedFormCentroids():
    """Return exact mathematical references for the four pinned shape inputs.

    The hyperbolic area follows the integral of 1/(1+u**4), u=7*x;
    its first moment is atan(49)/98. The bell and triangle are symmetric.
    For the rising quadratic shoulder, area=1/2 and first moment=17/48.
    No reference invokes FuzzyRoutines or a numerical integration package.
    """

    rootTwo = math.sqrt(2)
    upper = 7.0
    area = (math.log((upper * upper + rootTwo * upper + 1) / (upper * upper - rootTwo * upper + 1)) / (4 * rootTwo)
            + math.atan2(rootTwo * upper, 1 - upper * upper) / (2 * rootTwo)) / upper

    return {"hyperbolic": (math.atan(49) / 98) / area, "bell": 0.55, "triangle": 0.5, "parabolic": 17 / 24}


def BuildCases(config, harnessDirectory):
    """Reuse existing workload builders while supplying independent scalar oracles."""

    membership, scales, centroids = [LoadHarness(harnessDirectory / filename, "pinned_" + filename[:-3]) for filename in HARNESSES]
    cases = []

    for case in membership.BuildWorkloads():
        cases.append({"name": case["name"], "operation": case["operation"], "summarize": float,
                      "check": case["parity_check"], "reference": "existing analytical/reference scalar oracle",
                      "tolerance": 1e-12, "iterations": config["iterations"]["scalar"], "units": 1})

    for scaleName, scaleClass in scales.SCALES.items():
        names = ["Min", "Med", "High"] if scaleName == "default" else ["Min", "Low", "Med", "High", "Max"]
        cases.append({"name": f"scale_{scaleName}_construction", "operation": scaleClass,
                      "summarize": lambda value: [level["name"] for level in value.levels],
                      "expected": names, "reference": "declared historical term order", "tolerance": 0,
                      "iterations": config["iterations"]["scale_construction"], "units": 1})
        cases.append({"name": f"scale_{scaleName}_lookup", "operation": scales.BuildLookupWorkload(scaleClass()),
                      "summarize": lambda value: value,
                      "expected": {"selected_level": "Med", "lookups_per_sample": scales.LOOKUPSAMPLES, "membership_evaluations": scales.LOOKUPSAMPLES * len(names)},
                      "reference": "central plateau winner and exactly one evaluation per declared term", "tolerance": 0,
                      "iterations": config["iterations"]["scale_lookup"], "units": scales.LOOKUPSAMPLES})

    expectedCentroids = ClosedFormCentroids()

    for shape in centroids.SHAPES:
        for operation in ("construction", "centroid"):
            function = (lambda selected=shape: centroids.BuildFuzzySet(selected)) if operation == "construction" else centroids.BuildFuzzySet(shape)._Defuz
            summarize = (lambda value: float(value.Defuz())) if operation == "construction" else float
            cases.append({"name": f"fuzzyset_{shape}_{operation}", "operation": function, "summarize": summarize,
                          "expected": expectedCentroids[shape], "reference": "independent closed-form centroid over [0,1]",
                          "tolerance": 1e-10, "iterations": config["iterations"]["fuzzyset_" + operation], "units": 1})

    if [case["name"] for case in cases] != WorkloadNames()[2:]:
        raise ValueError("pinned harness workload names/order changed")

    return cases


def Worker(config, label, measure):
    """Verify installed origins, then separate import, warmup, parity and evaluation."""

    artifact = config["verified_artifacts"][label]
    identity = Evidence().VerifyInstalledPackage(artifact, requireNoNumpy=True)
    packageDirectory = Path(identity["package_origin"]).parent

    if "fuzzyroutines" in sys.modules:
        raise ValueError("the package must not be imported before its fresh import measurement")

    started = time.perf_counter_ns() if measure else 0
    package = importlib.import_module("fuzzyroutines")
    importlib.import_module("fuzzyroutines.FuzzyRoutines")
    importDuration = time.perf_counter_ns() - started if measure else None

    if Path(package.__file__).resolve().parent != packageDirectory:
        raise ValueError("loaded package is not the installed wheel")

    cases = BuildCases(config, Path(config["harness_snapshot"]))
    results = {}

    for case in cases:
        observed = case["summarize"](case["operation"]())
        passed = case["check"]() if "check" in case else Close(observed, case["expected"], case["tolerance"])

        if not passed:
            raise ValueError(f"independent parity failed before timing {case['name']}")

        for _ in range(config["warmups"]):
            case["operation"]()

        elapsed = None

        if measure:
            started = time.perf_counter_ns()

            for _ in range(case["iterations"]):
                case["operation"]()

            elapsed = time.perf_counter_ns() - started

        results[case["name"]] = {"observation": observed, "parity_passed": True, "reference": case["reference"],
                                 "expected": case.get("expected", "analytical closure in pinned membership/operator harness"),
                                 "absolute_tolerance": case["tolerance"], "relative_tolerance": 0.0,
                                 "raw_elapsed_ns": elapsed, "iterations": case["iterations"], "units_per_iteration": case["units"],
                                 "ns_per_unit": elapsed / case["iterations"] / case["units"] if measure else None}

    finalIdentity = Evidence().VerifyInstalledPackage(artifact, requireNoNumpy=True)

    return {"artifact": label, "environment": Environment(), "package_origin": str(Path(package.__file__).resolve()),
            "loaded_module_origins": finalIdentity["loaded_module_origins"],
            "installed_distributions": sorted((item.metadata["Name"], item.version) for item in importlib.metadata.distributions()),
            "package_import_ns": importDuration, "results": results}


def Run(configPath, config):
    """Install supplied wheels offline and collect seven alternating paired rounds."""

    Validate(config)
    harnessIdentity = Evidence().VerifyHarness(
        Path(config["repository"]), config["harness_commit"],
        paths=("experiments/benchmark_installed_scalar.py", "experiments/installed_wheel_evidence.py", "tools/render_installed_scalar_comparison.py"),
    )

    if Path(__file__).resolve() != Path(config["repository"]).resolve() / "experiments/benchmark_installed_scalar.py":
        raise ValueError("run the exact published wrapper from the configured clean harness checkout")

    artifacts = {label: Evidence().VerifyWheel(config, label) for label in LABELS}
    output = Path(config["output_directory"]).resolve()
    output.mkdir(parents=True, exist_ok=False)
    snapshot = output / "harness"
    snapshot.mkdir()
    manifest = {}

    for filename in HARNESSES:
        data = Git(config, "show", config["workload_commit"] + ":tools/" + filename)
        (snapshot / filename).write_bytes(data)
        manifest[filename] = Digest(data)

    config = {**config, "verified_artifacts": artifacts, "harness_snapshot": str(snapshot)}
    executionConfig = output / "execution-config.json"
    WriteJson(executionConfig, config)
    interpreters = {}
    commands = []
    runner = Path(__file__).resolve()

    for label in LABELS:
        environment = output / (label + "-venv")
        venv.EnvBuilder(with_pip=False).create(environment)
        interpreters[label] = str(environment / "bin/python")
        command = [sys.executable, "-m", "pip", "--python", interpreters[label], "install", "--no-index", "--no-deps", "--no-compile", "--no-input", artifacts[label]["wheel"]]
        subprocess.run(command, check=True, capture_output=True, text=True)
        commands.append(command)

    def Invoke(label, measure):
        """Capture one isolated child report, keeping the checkout off sys.path."""

        command = [interpreters[label], "-I", str(runner), "--config", str(executionConfig), "--worker", label]

        if measure:
            command.append("--measure-worker")

        commands.append(command)
        try:
            completed = subprocess.run(command, cwd=output, check=True, capture_output=True, text=True)

        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"isolated {label} worker failed before accepting evidence:\n{error.stderr}") from error

        return json.loads(completed.stdout)

    preflight = {label: Invoke(label, False) for label in LABELS}
    hostKeys = ("python", "implementation", "base_executable_sha256", "platform", "processor", "affinity", "cgroup")

    if any(preflight["baseline"]["environment"][key] != preflight["candidate"]["environment"][key] for key in hostKeys):
        raise ValueError("artifact environments are not comparable")

    for name, case in preflight["baseline"]["results"].items():
        if not Close(preflight["candidate"]["results"][name]["observation"], case["observation"], case["absolute_tolerance"]):
            raise ValueError(f"cross-version numerical parity failed: {name}")

    for label in LABELS:
        for _ in range(config["warmups"]):
            subprocess.run([interpreters[label], "-I", "-c", "pass"], cwd=output, check=True, capture_output=True)

    rounds = []

    for index in range(config["repeats"]):
        order = LABELS if index % 2 == 0 else tuple(reversed(LABELS))
        observations = {}

        for label in order:
            started = time.perf_counter_ns()
            subprocess.run([interpreters[label], "-I", "-c", "pass"], cwd=output, check=True, capture_output=True)
            startup = time.perf_counter_ns() - started
            observations[label] = Invoke(label, True)
            observations[label]["process_startup_ns"] = startup

        rounds.append({"index": index, "order": list(order), "artifacts": observations})
        WriteJson(output / f"round-{index + 1:02}.json", rounds[-1])
        print(f"Completed paired round {index + 1}/{config['repeats']}", file=sys.stderr, flush=True)

    results = {}

    for name in WorkloadNames():
        result = {}

        for label in LABELS:
            samples = []

            for roundResult in rounds:
                observed = roundResult["artifacts"][label]
                samples.append(observed[name + "_ns"] if name in ("process_startup", "package_import") else observed["results"][name]["ns_per_unit"])

            result[label] = Summary(samples)

        result["baseline_over_candidate"] = result["baseline"]["median"] / result["candidate"]["median"]
        result["unit"] = "nanoseconds_per_lookup" if name.endswith("_lookup") else "nanoseconds_per_operation"
        results[name] = result

    report = {"schema_version": 1, "kind": "installed-wheel-comparison", "completed_at": datetime.now(UTC).isoformat(),
              "artifacts": artifacts, "environment": Environment(), "preflight": preflight, "rounds": rounds,
              "harness": {"source_commit": config["harness_commit"], "published_wrapper_identity": harnessIdentity, "workload_source_commit": config["workload_commit"], "snapshot_kind": "exact committed Git objects, no working-tree overlay",
                          "snapshot_dirty": False,
                          "files_sha256": manifest, "runner_sha256": Digest(runner.read_bytes()), "input_config_sha256": Digest(configPath.read_bytes()),
                          "legacy_git_field_meaning": "Existing harness GetGitMetadata identifies harness checkout, not installed package; it is not called here."},
              "configuration": config, "executed_commands": commands, "process_startup_command_template": ["<artifact-venv>/bin/python", "-I", "-c", "pass"],
              "invocation": [sys.executable, "-I", str(runner), "--config", str(configPath.resolve()), "--run"],
              "timer": "time.perf_counter_ns", "input_generator": "fixed literals in the three hash-pinned harnesses; no RNG", "seed": None, "results": results,
              "parity_passed": True, "limitations": ["shared host, no timing acceptance thresholds", "fresh-process imports, not cold filesystem cache", "startup control includes subprocess launch and teardown", "tracemalloc disabled during operation timing; old traced timings are not comparable", "scale lookup includes existing counting instrumentation", "no optional runtime dependencies installed"]}
    WriteJson(output / "comparison.json", report)

    return {"report": str(output / "comparison.json"), "workloads": len(results), "parity_passed": True}


def Main():
    """Require --run before installing or measuring; planning is read-only."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--worker", choices=LABELS)
    parser.add_argument("--measure-worker", action="store_true", dest="measureWorker")
    options = parser.parse_args()
    config = json.loads(options.config.read_text())

    if options.worker:
        result = Worker(config, options.worker, options.measureWorker)

    elif options.run:
        result = Run(options.config, config)

    else:
        result = {"mode": "plan_only_no_installation_no_measurement", "workloads": WorkloadNames(), "repeats": config["repeats"],
                  "pending_artifacts": {label: config[label] for label in LABELS}, "harness_commit": config["harness_commit"], "workload_commit": config["workload_commit"],
                  "run_command": [sys.executable, "-I", str(Path(__file__).resolve()), "--config", str(options.config.resolve()), "--run"]}

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    Main()
