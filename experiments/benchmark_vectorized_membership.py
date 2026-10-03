# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Compare scalar and optional array workloads without changing the package.

Run as ``python -m experiments.benchmark_vectorized_membership``. Timing is
observational: no speed threshold controls correctness or CI. Memory workers
use fresh processes so unrelated workloads cannot contaminate RSS high water.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc
import venv
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARITY_TOLERANCE = 1e-12
DEFAULT_SIZES = (1, 16, 1024, 100000)
FAMILY_CASES = {
    "hyperbolic": {"a": 2.0, "b": 1.5, "c": 0.0},
    "bell": {"a": -2.0, "b": 0.0, "c": 1.0},
    "parabolic": {"a": -2.0, "b": 2.0},
    "triangle": {"a": -2.0, "b": 2.0, "c": 0.5},
    "trapezium": {"a": -2.0, "b": 2.0, "c": -0.5, "d": 0.5},
    "exponential": {"a": 0.5, "b": 0.25},
    "sigmoidal": {"a": 2.0, "b": 0.5},
    "desirability": {},
}
WORKLOADS = (*FAMILY_CASES, "default_scale_classification")
BACKENDS = ("scalar", "numpy")
MODES = ("evaluation", "end_to_end")


def ValidateConfiguration(sizes, repeats, warmups, target_elements):
    """Reject settings that violate deterministic sampling requirements."""

    if not sizes or any(type(size) is not int or size < 1 for size in sizes):
        raise ValueError("sizes must contain positive integers")

    if repeats < 7 or warmups < 1 or target_elements < 1:
        raise ValueError("at least seven repeats, one warmup, and one target element are required")


def BuildCoordinates(size, classification=False):
    """Create exact deterministic binary64 coordinates from an integer grid."""

    left, width = (0.0, 1.0) if classification else (-5.0, 10.0)

    return [left + width * index / max(1, size - 1) for index in range(size)]


def BuildOperation(workload, backend, mode, size):
    """Bind a workload while keeping preconstruction outside evaluation timing."""

    from fuzzyroutines.FuzzyRoutines import FuzzyScale, MFunction

    values = BuildCoordinates(size, workload == "default_scale_classification")
    coordinates = None

    if backend == "numpy":
        import numpy as np

        from experiments.vectorized_membership import EvaluateMembership

        if mode == "evaluation":
            coordinates = np.asarray(values, dtype=np.float64)
            values = None

    if workload == "default_scale_classification":
        scale = FuzzyScale()
        names = [level["name"] for level in scale.levels]

        def Classify():
            """Select actual default-scale levels with later-level tie priority."""

            selected_scale = FuzzyScale() if mode == "end_to_end" else scale

            if backend == "scalar":
                return [names.index(selected_scale.Fuzzy(float(value))["name"]) for value in values]

            source = values if mode == "end_to_end" else coordinates
            grades = []

            for level in selected_scale.levels:
                function = level["fSet"].mFunction

                grades.append(EvaluateMembership(function.name.lower(), source, **function.parameters))

            # Reverse rows to implement the historical later-level tie rule.
            return len(grades) - 1 - np.argmax(np.stack(grades)[::-1], axis=0)

        return Classify, values, coordinates

    parameters = FAMILY_CASES[workload]
    scalar_function = MFunction(workload, **parameters)

    def Evaluate():
        """Include result allocation in both backend measurements."""

        if backend == "scalar":
            function = MFunction(workload, **parameters) if mode == "end_to_end" else scalar_function

            return [function.mju(float(value)) for value in values]

        source = values if mode == "end_to_end" else coordinates

        return EvaluateMembership(workload, source, **parameters)

    return Evaluate, values, coordinates


def CheckParity(scalar_operation, array_operation, classification=False):
    """Fail before timing if scalar grades or selected scale levels disagree."""

    import numpy as np

    expected = np.asarray(scalar_operation())
    actual = np.asarray(array_operation())
    maximum_error = float(np.max(np.abs(expected - actual), initial=0.0))
    passed = np.array_equal(expected, actual) if classification else np.allclose(
        expected, actual, rtol=0.0, atol=PARITY_TOLERANCE,
    )

    if expected.shape != actual.shape or not passed:
        raise RuntimeError("scalar parity failed; timing evidence is invalid")

    return {"passed": True, "maximum_absolute_error": maximum_error,
            "absolute_tolerance": 0.0 if classification else PARITY_TOLERANCE,
            "relative_tolerance": 0.0, "reference": "current MFunction.mju / FuzzyScale.Fuzzy"}


def Summarize(samples):
    """Retain raw samples and protocol statistics in nanoseconds per batch."""

    quartiles = statistics.quantiles(samples, n=4, method="inclusive")

    return {"raw_samples": samples, "median": statistics.median(samples),
            "minimum": min(samples), "maximum": max(samples),
            "interquartile_range": quartiles[2] - quartiles[0]}


def MeasurePair(operations, iterations, repeats, warmups):
    """Alternate backend order, exclude tracing, and record wall and process CPU."""

    samples = {backend: {"wall_ns": [], "cpu_ns": []} for backend in BACKENDS}

    for operation in operations.values():
        for _ in range(warmups):
            operation()

    for repeat in range(repeats):
        order = BACKENDS if repeat % 2 == 0 else BACKENDS[::-1]

        for backend in order:
            operation = operations[backend]
            wall_start = time.perf_counter_ns()
            cpu_start = time.process_time_ns()

            for _ in range(iterations):
                operation()

            cpu_elapsed = time.process_time_ns() - cpu_start
            wall_elapsed = time.perf_counter_ns() - wall_start
            samples[backend]["wall_ns"].append(wall_elapsed / iterations)
            samples[backend]["cpu_ns"].append(cpu_elapsed / iterations)

    return {backend: {timer: Summarize(values) for timer, values in samples[backend].items()}
            for backend in BACKENDS}


def GetRssBytes():
    """Read address-space RSS high water without Linux inherited pre-exec peaks."""

    if sys.platform.startswith("linux"):
        status = Path("/proc/self/status").read_text()
        peak_line = next(line for line in status.splitlines() if line.startswith("VmHWM:"))

        return int(peak_line.split()[1]) * 1024

    import resource

    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    return peak if sys.platform == "darwin" else peak * 1024


def MemoryWorker(workload, backend, mode, size):
    """Measure untraced RSS first, then an independently traced operation."""

    operation, values, coordinates = BuildOperation(workload, backend, mode, size)
    rss_before = GetRssBytes()
    result = operation()
    rss_after = GetRssBytes()
    output_payload = getattr(result, "nbytes", None)
    del result
    tracemalloc.start()
    result = operation()
    _, traced_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {"rss_high_water_before_bytes": rss_before,
            "rss_high_water_after_bytes": rss_after,
            "rss_high_water_increase_bytes": max(0, rss_after - rss_before),
            "traced_operation_peak_bytes": traced_peak,
            "array_output_payload_bytes": output_payload,
            "prepared_array_payload_bytes": coordinates.nbytes if coordinates is not None else None,
            "list_input_shallow_bytes": sys.getsizeof(values) if values is not None else None,
            "output_shallow_bytes": sys.getsizeof(result)}


def RunWorker(arguments):
    """Decode an isolated child result and propagate failures without evidence."""

    completed = subprocess.run(
        [sys.executable, "-m", "experiments.benchmark_vectorized_membership", *arguments],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )

    return json.loads(completed.stdout)


def ImportWorker(module):
    """Capture fresh-process import cost independently of process startup."""

    import importlib

    rss_before = GetRssBytes()
    wall_start = time.perf_counter_ns()
    cpu_start = time.process_time_ns()
    importlib.import_module(module)

    return {"wall_ns": time.perf_counter_ns() - wall_start,
            "cpu_ns": time.process_time_ns() - cpu_start,
            "rss_before_bytes": rss_before, "rss_after_bytes": GetRssBytes()}


def MeasureOfflineInstall(wheel, repeats):
    """Time cached-wheel installation into fresh environments without downloads."""

    import resource

    wheel = wheel.resolve()

    with zipfile.ZipFile(wheel) as archive:
        metadata_path = next(path for path in archive.namelist() if path.endswith(".dist-info/METADATA"))
        metadata = archive.read(metadata_path).decode("utf-8")
        unpacked_bytes = sum(item.file_size for item in archive.infolist())

    if "Name: numpy\n" not in metadata or "Version: 2.3.5\n" not in metadata:
        raise ValueError("offline installation evidence requires the pinned numpy 2.3.5 wheel")

    samples = []

    for _ in range(repeats):
        with tempfile.TemporaryDirectory(prefix="fr-numpy-install-") as directory:
            venv.EnvBuilder(with_pip=False).create(directory)
            executable = str(Path(directory) / "bin/python")
            usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
            started = time.perf_counter_ns()
            subprocess.run(
                [sys.executable, "-m", "pip", "--python", executable, "install", "--no-index",
                 "--no-deps", "--no-compile", "--disable-pip-version-check", str(wheel)],
                capture_output=True, text=True, check=True,
            )
            elapsed = time.perf_counter_ns() - started
            usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
            cpu_seconds = (usage_after.ru_utime + usage_after.ru_stime -
                           usage_before.ru_utime - usage_before.ru_stime)
            samples.append({"wall_ns": elapsed, "child_cpu_ns": cpu_seconds * 1e9})

    return {"wheel_filename": wheel.name, "wheel_bytes": wheel.stat().st_size,
            "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
            "wheel_uncompressed_member_bytes": unpacked_bytes, "raw_samples": samples,
            "wall_ns": Summarize([sample["wall_ns"] for sample in samples]),
            "child_cpu_ns": Summarize([sample["child_cpu_ns"] for sample in samples]),
            "method": "fresh venv; existing pip --python install --no-index --no-deps --no-compile",
            "exclusions": "venv creation, download, bytecode compilation; filesystem cache not flushed"}


def DependencyCost(repeats, wheel=None):
    """Record installed distribution size and fresh import samples, not downloads."""

    distribution = importlib.metadata.distribution("numpy")
    files = [distribution.locate_file(path) for path in distribution.files or ()]
    installed_bytes = sum(path.stat().st_size for path in files if path.is_file())
    imports = {}

    for module in ("fuzzyroutines", "numpy"):
        samples = [RunWorker(["--import-worker", module]) for _ in range(repeats)]
        imports[module] = {
            "raw_samples": samples,
            "wall_ns": Summarize([sample["wall_ns"] for sample in samples]),
            "cpu_ns": Summarize([sample["cpu_ns"] for sample in samples]),
        }

    return {"numpy_version": distribution.version, "installed_record_files_bytes": installed_bytes,
            "installed_record_file_count": len(files), "cold_process_import": imports,
            "installer_pip_version": importlib.metadata.version("pip"),
            "installation_command": "python -m pip install -r experiments/requirements-vectorized.txt",
            "network_download_time": "not measured; network/cache dependent",
            "offline_wheel_install": MeasureOfflineInstall(wheel, repeats) if wheel else None}


def GetEnvironment():
    """Record source hashes, exact runtime, resource limits, and host metadata."""

    paths = [Path(__file__), ROOT / "experiments/vectorized_membership.py",
             ROOT / "fuzzyroutines/FuzzyRoutines.py", ROOT / "fuzzyroutines/membership.py",
             ROOT / "fuzzyroutines/operators.py", ROOT / "fuzzyroutines/numeric.py"]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    cpu_model = platform.processor()

    if Path("/proc/cpuinfo").exists():
        cpu_model = next((line.partition(":")[2].strip() for line in
                          Path("/proc/cpuinfo").read_text().splitlines()
                          if line.startswith("model name")), cpu_model)

    cgroup = {}

    for name in ("cpu.max", "memory.max"):
        path = Path("/sys/fs/cgroup") / name
        cgroup[name] = path.read_text().strip() if path.exists() else None

    return {"python": sys.version, "executable": sys.executable,
            "implementation": platform.python_implementation(), "platform": platform.platform(),
            "processor": cpu_model, "logical_cpu_count": os.cpu_count(),
            "affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
            "physical_memory_bytes": os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"),
            "cgroup": cgroup, "git_commit": commit, "git_dirty": bool(status.strip()),
            "package_version": "2.0.0.dev0 (source tree)",
            "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in paths},
            "thread_environment": {key: os.environ.get(key) for key in
                                   ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}}


def BuildReport(sizes=DEFAULT_SIZES, repeats=7, warmups=1, target_elements=4096, memory=True, wheel=None):
    """Compare every declared workload with parity, timings, and isolated memory."""

    ValidateConfiguration(sizes, repeats, warmups, target_elements)

    if os.name != "posix":
        raise RuntimeError("full benchmark reports require POSIX RSS and child-CPU measurement")

    results = []

    for workload in WORKLOADS:
        for size in sizes:
            for mode in MODES:
                operations = {backend: BuildOperation(workload, backend, mode, size)[0]
                              for backend in BACKENDS}
                parity = CheckParity(operations["scalar"], operations["numpy"],
                                     workload == "default_scale_classification")
                iterations = max(1, min(256, target_elements // size))
                timings = MeasurePair(operations, iterations, repeats, warmups)
                memory_results = {}

                if memory and size in (min(sizes), max(sizes)):
                    memory_results = {backend: RunWorker([
                        "--memory-worker", workload, backend, mode, str(size),
                    ]) for backend in BACKENDS}

                results.append({"workload": workload, "size": size, "shape": [size],
                                "dtype": "float64", "mode": mode, "iterations": iterations,
                                "parity": parity, "timing": timings, "memory": memory_results,
                                "wall_speedup": timings["scalar"]["wall_ns"]["median"] /
                                timings["numpy"]["wall_ns"]["median"],
                                "cpu_speedup": timings["scalar"]["cpu_ns"]["median"] /
                                timings["numpy"]["cpu_ns"]["median"]})

    return {"schema_version": 1, "benchmark": "scalar-versus-isolated-numpy-membership",
            "environment": GetEnvironment(), "dependency": DependencyCost(repeats, wheel),
            "configuration": {"sizes": list(sizes), "repeats": repeats, "warmups": warmups,
                              "target_elements": target_elements, "seed": None,
                              "input_generator": "BuildCoordinates integer grid, no random input",
                              "command": [sys.executable, "-m", "experiments.benchmark_vectorized_membership",
                                          *sys.argv[1:]],
                              "timing_unit": "nanoseconds per whole batch, result allocation included",
                              "timers": ["time.perf_counter_ns", "time.process_time_ns"],
                              "memory": memory}, "results": results}


def Main(arguments=None):
    """Write an explicit report or serve one private isolated measurement worker."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", default=DEFAULT_SIZES)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--target-elements", type=int, default=4096)
    parser.add_argument("--skip-memory", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--numpy-wheel", type=Path, help="optional pinned wheel for offline install measurement")
    parser.add_argument("--memory-worker", nargs=4, help=argparse.SUPPRESS)
    parser.add_argument("--import-worker", choices=("numpy", "fuzzyroutines"), help=argparse.SUPPRESS)
    options = parser.parse_args(arguments)

    if options.memory_worker:
        workload, backend, mode, size = options.memory_worker
        report = MemoryWorker(workload, backend, mode, int(size))

    elif options.import_worker:
        report = ImportWorker(options.import_worker)

    else:
        report = BuildReport(options.sizes, options.repeats, options.warmups,
                             options.target_elements, not options.skip_memory, options.numpy_wheel)

    rendered = json.dumps(report, indent=2, sort_keys=True)

    if options.output:
        options.output.write_text(rendered + "\n", encoding="utf-8")

    print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
