# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Measure public array operations and same-revision scalar references.

Run from a checkout with the optional NumPy dependency. The report records the
actual source hashes and never labels a source run as an installed release.
Shared measurement mechanics are reused from the reviewed ADR-0015 experiment;
all mathematical workloads call the current public package APIs.
"""

import argparse
import hashlib
import importlib.metadata
import json
import math
import subprocess
import sys
import tracemalloc
from pathlib import Path

from experiments.benchmark_vectorized_membership import (
    DependencyCost,
    GetEnvironment,
    GetRssBytes,
    MeasurePair,
)

ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ("gaussian", "bell", "universal_scale")
BACKENDS = ("scalar", "numpy")
MODES = ("prepared_array", "list_conversion")
CONSUMER_FIXTURE = ROOT / "tests/fixtures/public_consumer_batches.json"


def BuildOperation(workload, backend, mode, shape, coordinates=None):
    """Build equivalent fixed mathematical models with separately declared inputs."""

    from fuzzyroutines import (
        Bell,
        CreateUniversalFuzzyScale,
        Gaussian,
        UniversalFuzzyScalePolicy,
    )
    from fuzzyroutines.batches import EvaluateMembershipBatch, FuzzifyBatch

    size = math.prod(shape)
    flat = [index / max(1, size - 1) for index in range(size)] if coordinates is None else list(coordinates)

    if len(flat) != size:
        raise ValueError("recorded coordinates must exactly fill the declared shape")

    values = flat

    if len(shape) == 2:
        values = [flat[index:index + shape[1]] for index in range(0, size, shape[1])]

    if backend == "numpy" and mode == "prepared_array":
        import numpy as np

        values = np.asarray(values, dtype=np.float64).reshape(shape)

    if backend == "numpy":
        # The NumPy closure must not retain an unused original flat Python list,
        # especially in a prepared-array memory observation.
        flat = None

    if workload == "universal_scale":
        scale = CreateUniversalFuzzyScale()
        policy = UniversalFuzzyScalePolicy()

        def Classify():
            """Return all membership and selection evidence on both execution paths."""

            if backend == "scalar":
                return [scale.Fuzzify(value, policy) for value in flat]

            return FuzzifyBatch(scale, values, policy, backend="numpy")

        return Classify, values

    function = Gaussian(0.5, 0.25) if workload == "gaussian" else Bell(0.17, 0.23, 0.34)

    def Evaluate():
        """Evaluate the same immutable model without including its construction."""

        if backend == "scalar":
            return [float(function(value)) for value in flat]

        return EvaluateMembershipBatch(function, values, backend="numpy")

    return Evaluate, values


def CheckParity(operations, workload):
    """Validate complete grades and decision masks before recording any speed."""

    import numpy as np

    expected = operations["scalar"]()
    actual = operations["numpy"]()

    if workload == "universal_scale":
        reference = np.array([[float(score.grade) for score in result.memberships] for result in expected])
        grades = actual.memberships.reshape(reference.shape)
        selected = actual.selected.reshape(reference.shape)
        tied = actual.tied.reshape(reference.shape)

        for index, result in enumerate(expected):
            if selected[index].tolist() != [score.term in result.selectedTerms for score in result.memberships]:
                raise AssertionError("batch and scalar selected terms differ")

            if tied[index].tolist() != [score.term in result.tiedTerms for score in result.memberships]:
                raise AssertionError("batch and scalar tied terms differ")

    else:
        reference = np.array(expected)
        grades = actual.reshape(reference.shape)

    np.testing.assert_allclose(grades, reference, rtol=0.0, atol=1e-12)

    return {"passed": True, "absolute_tolerance": 1e-12, "relative_tolerance": 0.0,
            "maximum_absolute_error": float(np.max(np.abs(grades - reference), initial=0.0)),
            "classification_masks_exact": workload == "universal_scale"}


def MemoryWorker(workload, backend, mode, shape, coordinates=None):
    """Measure each backend in a fresh process with no prior other-backend import."""

    operation, values = BuildOperation(workload, backend, mode, shape, coordinates)
    before = GetRssBytes()
    result = operation()
    after = GetRssBytes()
    del result
    tracemalloc.start()
    result = operation()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if workload == "universal_scale" and backend == "numpy":
        payload = sum(getattr(result, name).nbytes for name in ("memberships", "confidence", "tied", "selected"))

    else:
        payload = getattr(result, "nbytes", None)

    return {"rss_before_bytes": before, "rss_peak_bytes": after,
            "rss_high_water_increase_bytes": max(0, after - before),
            "traced_operation_peak_bytes": peak, "output_array_payload_bytes": payload,
            "input_array_payload_bytes": getattr(values, "nbytes", None),
            "input_shallow_bytes": sys.getsizeof(values)}


def RunMemory(workload, backend, mode, shape, coordinates=None):
    """Execute one isolated memory observation, propagating worker failures."""

    command = [sys.executable, "-m", "experiments.benchmark_public_batches", "--memory-worker",
               workload, backend, mode, "x".join(str(size) for size in shape)]

    if coordinates is not None:
        command.extend(["--coordinates", json.dumps(coordinates)])

    completed = subprocess.run(
        command,
        cwd=ROOT, check=True, capture_output=True, text=True,
    )

    return json.loads(completed.stdout)


def BuildReport(shapes, repeats=7, warmups=1, memory=True, wheel=None):
    """Record paired time and memory evidence without adding CI speed thresholds."""

    if repeats < 7 or warmups < 1:
        raise ValueError("at least seven repeats and one warmup are required")

    if not shapes or any(len(shape) not in (1, 2) or any(size < 1 for size in shape) for shape in shapes):
        raise ValueError("benchmark shapes must have one or two positive dimensions")

    environment = GetEnvironment()
    sourcePaths = ("fuzzyroutines/batches.py", "fuzzyroutines/membership.py",
                   "fuzzyroutines/linguistic.py", "fuzzyroutines/presets.py",
                   "experiments/benchmark_public_batches.py")
    environment["source_sha256"] = {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in sourcePaths
    }
    environment["numpy_version"] = importlib.metadata.version("numpy")
    results = []

    for workload in WORKLOADS:
        for shape in shapes:
            for mode in MODES:
                operations = {backend: BuildOperation(workload, backend, mode, shape)[0] for backend in BACKENDS}
                parity = CheckParity(operations, workload)
                iterations = max(1, min(128, 1024 // math.prod(shape)))
                timing = MeasurePair(operations, iterations, repeats, warmups)
                measurements = {}

                if memory and math.prod(shape) in (min(map(math.prod, shapes)), max(map(math.prod, shapes))):
                    measurements = {backend: RunMemory(workload, backend, mode, shape) for backend in BACKENDS}

                results.append({"workload": workload, "shape": list(shape), "size": math.prod(shape),
                                "mode": mode, "iterations": iterations, "parity": parity,
                                "timing": timing, "memory": measurements,
                                "wall_speedup": timing["scalar"]["wall_ns"]["median"] / timing["numpy"]["wall_ns"]["median"]})

        print(f"Measured {workload}: paired timings and isolated memory", file=sys.stderr, flush=True)

    print("Measuring optional dependency imports and installation", file=sys.stderr, flush=True)
    dependency = DependencyCost(repeats, wheel)
    dependency["installation_command"] = "python -m pip install numpy==2.3.5"

    return {"schema_version": 1, "benchmark": "public-batches-source-candidate",
            "environment": environment, "dependency": dependency,
            "baseline": {"kind": "same-revision canonical scalar APIs", "git_commit": environment["git_commit"]},
            "configuration": {"shapes": [list(shape) for shape in shapes], "repeats": repeats,
                              "warmups": warmups, "seed": None,
                              "input_generator": "deterministic inclusive [0,1] grid, reshaped in C order",
                              "command": [sys.executable, "-m", "experiments.benchmark_public_batches", *sys.argv[1:]],
                              "timers": ["time.perf_counter_ns", "time.process_time_ns"],
                              "memory": memory, "unit": "nanoseconds per batch, result allocation included",
                              "scalar_input": "flat Python list in both modes",
                              "numpy_input": "prepared ndarray or nested Python list, as named"},
            "limitations": ["source checkout, not an installed release wheel",
                            "synthetic shapes; no authorized FMA/robot consumer trace available",
                            "memory observations are single samples, RSS is whole-process high water",
                            "no universal crossover or application throughput claim"],
            "results": results}


def CheckReplayParity(operations, replay):
    """Check grades/masks plus independent labels and percentages from the consumer."""

    parity = CheckParity(operations, "universal_scale")
    expected = [[case["expected_label"]] for case in replay["cases"]]
    scalar = [[term.name for term in result.selectedTerms] for result in operations["scalar"]()]
    result = operations["numpy"]()
    numpy = [[name for name, selected in zip(result.termNames, row, strict=True) if selected] for row in result.selected]

    if scalar != expected or numpy != expected:
        raise AssertionError("classification contradicts the pinned consumer's expected labels")

    if len(replay["coordinates"]) != len(replay["cases"]):
        raise AssertionError("consumer coordinates and expected results differ in length")

    for coordinate, case in zip(replay["coordinates"], replay["cases"], strict=True):
        if round(100 * coordinate, 4) != case["expected_percent_rounded_4"]:
            raise AssertionError("coordinate contradicts the pinned consumer's expected percentage")

    parity["upstream_expected_labels_exact"] = True
    parity["upstream_expected_percentages_rounded_4_exact"] = True

    return parity


def BuildConsumerReport(repeats=7, warmups=1, memory=True):
    """Measure actual public-test vectors without treating them as production batches."""

    if repeats < 7 or warmups < 1:
        raise ValueError("at least seven repeats and one warmup are required")

    fixture = json.loads(CONSUMER_FIXTURE.read_text(encoding="utf-8"))
    environment = GetEnvironment()
    sourcePaths = ("fuzzyroutines/batches.py", "fuzzyroutines/membership.py",
                   "fuzzyroutines/linguistic.py", "fuzzyroutines/presets.py",
                   "experiments/benchmark_public_batches.py", "tools/extract_consumer_replay.py",
                   "tests/fixtures/public_consumer_batches.json")
    environment["source_sha256"] = {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in sourcePaths
    }
    environment["numpy_version"] = importlib.metadata.version("numpy")
    results = []

    for replay in fixture["replays"]:
        coordinates = replay["coordinates"]
        shape = (len(coordinates),)

        for mode in MODES:
            operations = {backend: BuildOperation("universal_scale", backend, mode, shape, coordinates)[0] for backend in BACKENDS}
            parity = CheckReplayParity(operations, replay)
            iterations = max(1, min(128, 1024 // len(coordinates)))
            timing = MeasurePair(operations, iterations, repeats, warmups)
            measurements = {backend: RunMemory("universal_scale", backend, mode, shape, coordinates) for backend in BACKENDS} if memory else {}
            results.append({"workload": replay["name"], "shape": list(shape), "size": len(coordinates),
                            "coordinates": coordinates, "upstream_test": replay["test"],
                            "expected_labels": [case["expected_label"] for case in replay["cases"]],
                            "mode": mode, "iterations": iterations, "parity": parity,
                            "timing": timing, "memory": measurements,
                            "wall_speedup": timing["scalar"]["wall_ns"]["median"] / timing["numpy"]["wall_ns"]["median"]})

        print(f"Measured public test replay {replay['name']}", file=sys.stderr, flush=True)

    dependencyPath = "docs/performance/evidence/public-batches-python314-linux.json"

    return {"schema_version": 1, "benchmark": "public-consumer-test-replays-source-candidate",
            "environment": environment, "consumer": fixture["source"], "fixture_scope": fixture["scope"],
            "baseline": {"kind": "same-revision canonical scalar APIs", "git_commit": environment["git_commit"]},
            "dependency_evidence": {"path": dependencyPath,
                                    "sha256": hashlib.sha256((ROOT / dependencyPath).read_bytes()).hexdigest(),
                                    "scope": "Prior separately pinned synthetic run; import/installation costs were not remeasured here."},
            "configuration": {"repeats": repeats, "warmups": warmups, "seed": None,
                              "input_generator": "ordered normalized coordinates extracted from pinned public positive-test cases",
                              "command": [sys.executable, "-m", "experiments.benchmark_public_batches", *sys.argv[1:]],
                              "timers": ["time.perf_counter_ns", "time.process_time_ns"],
                              "memory": memory, "unit": "nanoseconds per replay group, result allocation included",
                              "scalar_input": "flat Python list in both modes",
                              "numpy_input": "prepared ndarray or Python list, as named",
                              "excluded": "price normalization, model construction, consumer engine, network access"},
            "limitations": ["source checkout, not an installed release wheel",
                            "test replay groups, not measured production distributions",
                            "memory observations are single samples, RSS is whole-process high water",
                            "no private FMA/robot integration or throughput claim"],
            "results": results}


def Main(arguments=None):
    """Write explicit source evidence or an isolated worker observation."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--shapes", nargs="+", default=["1", "16", "32x32", "100000"])
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--no-memory", action="store_true", dest="noMemory")
    parser.add_argument("--numpy-wheel", type=Path, dest="numpyWheel")
    parser.add_argument("--memory-worker", nargs=4, dest="memoryWorker")
    parser.add_argument("--coordinates", type=json.loads)
    parser.add_argument("--consumer-replays", action="store_true", dest="consumerReplays")
    options = parser.parse_args(arguments)

    if options.memoryWorker:
        workload, backend, mode, shapeText = options.memoryWorker
        result = MemoryWorker(workload, backend, mode, tuple(int(size) for size in shapeText.split("x")), options.coordinates)

    elif options.consumerReplays:
        if options.numpyWheel:
            parser.error("consumer replay uses separately recorded dependency costs; omit --numpy-wheel")

        result = BuildConsumerReport(options.repeats, memory=not options.noMemory)

    else:
        shapes = tuple(tuple(int(size) for size in value.split("x")) for value in options.shapes)
        result = BuildReport(shapes, options.repeats, memory=not options.noMemory, wheel=options.numpyWheel)

    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"

    if options.output:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(encoded, encoding="utf-8")

    else:
        print(encoded, end="")


if __name__ == "__main__":
    Main()
