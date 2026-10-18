# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Compare complete FuzzifyBatch calls in two separately installed environments.

Supply interpreters containing the baseline and corrected wheels and NumPy
2.3.5. Workers run with -I, verify installed origins, and never import checkout
package code. Seven alternating pairs exclude setup, validation and tracing.
This experiment measures installed wheels supplied by the coordinator; it does
not establish their CI provenance. Retain wheel/source hashes separately.
"""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path


def Worker(case):
    """Serve warmed, parity-checked full public calls from an isolated install."""

    import numpy as np

    import fuzzyroutines
    from fuzzyroutines import (
        ContinuousUniverse,
        CreateUniversalFuzzyScale,
        FuzzificationPolicy,
        LinguisticScale,
        LinguisticTerm,
        ScalarFuzzySet,
        Triangle,
        UniversalFuzzyScalePolicy,
    )
    from fuzzyroutines.batches import FuzzifyBatch

    if not sys.flags.isolated or not Path(fuzzyroutines.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise ValueError("worker must load an installed package under -I")

    if np.__version__ != "2.3.5":
        raise ValueError("both environments require NumPy 2.3.5")

    if case["scale"] == "historical":
        scale, policy = CreateUniversalFuzzyScale(), UniversalFuzzyScalePolicy()

    else:
        universe = ContinuousUniverse(0, 1, True, True)
        scale = LinguisticScale(tuple(
            LinguisticTerm(str(index), ScalarFuzzySet(universe, Triangle(index / 8, (index + 1) / 8, (index + 2) / 8)))
            for index in range(7)
        ))
        policy = FuzzificationPolicy(tiePolicy="first", tieTolerance=1e-12)

    coordinates = np.linspace(0, 1, case["size"])
    values = coordinates if case["mode"] == "prepared_array" else coordinates.tolist()

    def Operation():
        """Include conversion, grades, both classification scans and result copies."""

        return FuzzifyBatch(scale, values, policy, backend="numpy")

    actual = Operation()
    indices = np.unique(np.linspace(0, case["size"] - 1, min(case["size"], 1024), dtype=int))
    maximumError = 0.0

    for index in indices:
        expected = scale.Fuzzify(float(coordinates[index]), policy)
        grades = [float(score.grade) for score in expected.memberships]
        maximumError = max(maximumError, float(np.max(np.abs(actual.memberships[index] - grades))))
        assert np.allclose(actual.memberships[index], grades, rtol=0, atol=1e-12)
        assert actual.selected[index].tolist() == [score.term in expected.selectedTerms for score in expected.memberships]
        assert actual.tied[index].tolist() == [score.term in expected.tiedTerms for score in expected.memberships]

    digest = hashlib.sha256()

    for field in ("memberships", "confidence", "tied", "selected"):
        digest.update(getattr(actual, field).tobytes())

    Operation()
    print(json.dumps({"origin": fuzzyroutines.__file__, "version": importlib.metadata.version("fuzzyroutines"),
                      "numpy": np.__version__, "python": sys.version, "package_hashes": {
                          path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in Path(fuzzyroutines.__file__).parent.glob("*.py")},
                      "parity_points": len(indices), "maximum_absolute_error": maximumError,
                      "full_result_sha256": digest.hexdigest()}), flush=True)

    for line in sys.stdin:
        request = json.loads(line)

        if request == "memory":
            tracemalloc.start()
            Operation()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            result = {"traced_peak_bytes": peak}

        else:
            wallStart, cpuStart = time.perf_counter_ns(), time.process_time_ns()

            for _ in range(request):
                Operation()

            result = {"wall_ns": (time.perf_counter_ns() - wallStart) / request,
                      "cpu_ns": (time.process_time_ns() - cpuStart) / request}

        print(json.dumps(result), flush=True)


def Ask(worker, request):
    """Exchange one measurement request with an already initialized worker."""

    worker.stdin.write(json.dumps(request) + "\n")
    worker.stdin.flush()
    response = worker.stdout.readline()

    if not response:
        raise RuntimeError(f"worker exited with status {worker.poll()}")

    return json.loads(response)


def Run(options):
    """Alternate complete calls across installations and preserve every raw sample."""

    rows = []

    for scale in ("historical", "custom"):
        for size in (16, 200000):
            for mode in ("prepared_array", "list_conversion"):
                case = {"scale": scale, "size": size, "mode": mode}
                workers = {}
                samples = {label: [] for label in ("baseline", "candidate")}
                identities = {}
                iterations = 100 if size == 16 else 3

                try:
                    for label in samples:
                        command = [getattr(options, label + "Python"), "-I", str(Path(__file__).resolve()), "--worker", json.dumps(case)]
                        worker = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
                        workers[label] = worker
                        identities[label] = json.loads(worker.stdout.readline())

                    assert identities["baseline"]["full_result_sha256"] == identities["candidate"]["full_result_sha256"]

                    for repeat in range(7):
                        order = ("baseline", "candidate") if repeat % 2 == 0 else ("candidate", "baseline")

                        for label in order:
                            samples[label].append(Ask(workers[label], iterations))

                    memory = {label: Ask(worker, "memory") for label, worker in workers.items()}
                    medians = {label: statistics.median(sample["wall_ns"] for sample in raw) for label, raw in samples.items()}
                    row = {"case": case, "iterations_per_sample": iterations, "warmups": 2,
                           "identities": identities, "raw_samples": samples, "memory": memory,
                           "median_wall_ns": medians, "baseline_over_candidate": medians["baseline"] / medians["candidate"]}
                    rows.append(row)
                    options.output.write_text(json.dumps({"platform": platform.platform(), "rows": rows}, indent=2) + "\n")
                    print(json.dumps({"case": case, "speed_ratio": row["baseline_over_candidate"]}), flush=True)

                finally:
                    for worker in workers.values():
                        worker.stdin.close()

                    for worker in workers.values():
                        if worker.wait() != 0:
                            raise RuntimeError("measurement worker failed")


def Main():
    """Require explicit installed interpreters and an unused output path."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-python", dest="baselinePython")
    parser.add_argument("--candidate-python", dest="candidatePython")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--worker")
    options = parser.parse_args()

    if options.worker:
        Worker(json.loads(options.worker))

    else:
        if not options.baselinePython or not options.candidatePython or not options.output or options.output.exists():
            parser.error("supply both installed interpreters and a new output file")

        Run(options)


if __name__ == "__main__":
    Main()
