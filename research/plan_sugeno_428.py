# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Emit the fixed Task #428 benchmark plan without importing Torch or training."""

import argparse
import hashlib
import json

from examples.neural.run import GenerateObservations, SplitIndices

DATA_SEEDS = (1729, 2729, 3729)
SAMPLE_COUNT = 600
EPOCH_COUNT = 400


def Digest(value: object, *, sortKeys: bool = False) -> str:
    """Hash the compact JSON representation used by the Sugeno evidence runner."""

    return hashlib.sha256(json.dumps(value, separators=(",", ":"), sort_keys=sortKeys).encode("utf-8")).hexdigest()


def BuildManifest() -> dict:
    """Return the declared shared benchmark splits and dataset fingerprints."""

    runs = []

    for seed in DATA_SEEDS:
        observations = GenerateObservations(seed, SAMPLE_COUNT)
        dataset = [(row.severity, row.exposure, row.score) for row in observations]
        splits = SplitIndices(SAMPLE_COUNT, seed + 1)
        runs.append({
            "dataSeed": seed,
            "splitSeed": seed + 1,
            "networkSeed": seed + 2,
            "datasetSha256": Digest(dataset),
            "splitsSha256": Digest(splits, sortKeys=True),
            "splits": splits,
        })

    return {
        "schemaVersion": 1,
        "task": "synthetic-severity-exposure-v1",
        "sampleCount": SAMPLE_COUNT,
        "epochs": EPOCH_COUNT,
        "models": ("fixedRules", "fixedMembership", "zeroOrder", "firstOrder", "rawMlp"),
        "runs": runs,
    }


def Main(arguments: list[str] | None = None) -> int:
    """Write the benchmark plan as deterministic JSON to standard output."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(arguments)
    print(json.dumps(BuildManifest(), indent=2, sort_keys=True, allow_nan=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
