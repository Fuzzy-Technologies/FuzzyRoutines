# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Run repository-only Sugeno experiments against an isolated installed core.

Only explicit research, examples and tools namespaces are exposed. The checkout
root is never added to sys.path. Scientific source hashes and the actual loaded
core are checked together; plotting never loads the optional Torch experiment.
"""

import argparse
import contextlib
import hashlib
import importlib
import importlib.machinery
import importlib.metadata
import importlib.util
import io
import json
import math
import random
import sys
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_SOURCES = ("research/differentiable_sugeno.py", "research/run_sugeno.py", "examples/neural/run.py",
                    "fuzzyroutines/inference.py", "fuzzyroutines/encoding.py", "fuzzyroutines/presets.py")
MODEL_PARAMETERS = {"fixedRules": 0, "zeroOrder": 14, "firstOrder": 22, "fixedMembership": 12, "rawMlp": 337}


def Require(condition: bool, message: str) -> None:
    """Reject inconsistent evidence even when Python assertions are disabled."""

    if not condition:
        raise ValueError(message)


def RegisterNamespace(name: str, directory: Path) -> None:
    """Expose one repository namespace without exposing the checkout core package."""

    if name in sys.modules:
        Require(str(directory) in getattr(sys.modules[name], "__path__", ()), f"unexpected existing namespace: {name}")
        return

    specification = importlib.machinery.ModuleSpec(name, loader=None, is_package=True)
    specification.submodule_search_locations.append(str(directory))
    sys.modules[name] = importlib.util.module_from_spec(specification)


def ValidateSourceHashes(report: dict, projectRoot: Path = PROJECT_ROOT) -> None:
    """Require every declared calculation source and its actual bytes."""

    Require(set(report["sourceSha256"]) == set(RESEARCH_SOURCES), "research calculation source set changed")

    for relative, digest in report["sourceSha256"].items():
        Require(hashlib.sha256((projectRoot / relative).read_bytes()).hexdigest() == digest, f"research source hash mismatch: {relative}")


def ValidateReport(report: dict, *, epochs: int = 3, samples: int = 30, projectRoot: Path = PROJECT_ROOT) -> dict:
    """Audit data identities, scalar target meaning, errors and bounded research scope."""

    from fuzzyroutines import (
        Centroid,
        CreateUniversalFuzzyScale,
        UniversalFuzzyScaleDomains,
        UniversalFuzzyScalePolicy,
    )

    json.dumps(report, allow_nan=False)
    Require((report["schemaVersion"], report["task"], report["prototype"]) == (1, "synthetic-severity-exposure-v1", "bounded-differentiable-sugeno-v1"), "unexpected research schema/task")
    configuration = report["configuration"]
    Require((configuration["epochs"], configuration["sampleCount"]) == (epochs, samples), "unexpected research smoke budget")
    Require((configuration["dataSeed"], configuration["splitSeed"], configuration["networkSeed"]) == (1729, 1730, 1731), "unexpected research seeds")
    Require(configuration["checkpointSelection"] == "minimum validation MSE" and configuration["deterministicAlgorithms"] is True, "invalid research training policy")
    environment = report["environment"]
    Require((environment["device"], environment["dtype"], environment["threads"], environment["torch"]) == ("cpu", "float64", 1, "2.14.1+cpu"), "unexpected research CPU environment")
    Require(report["dependencyCost"] is None, "CI smoke must not measure optional import/distribution costs")
    ValidateSourceHashes(report, projectRoot)
    generator = random.Random(1729)
    observations = []

    for index in range(samples):
        severity, exposure = generator.random(), generator.random()
        observations.append((severity, exposure, 0.05 + 0.65 * severity + 0.30 * exposure))

    Require(report["datasetSha256"] == hashlib.sha256(json.dumps(observations, separators=(",", ":")).encode()).hexdigest(), "research data identity mismatch")
    indices = list(range(samples))
    random.Random(1730).shuffle(indices)
    splits = {"train": indices[:3 * samples // 5], "validation": indices[3 * samples // 5:4 * samples // 5], "heldOut": indices[4 * samples // 5:]}
    Require(report["splits"] == splits, "research split identities changed")
    Require(report["splitsSha256"] == hashlib.sha256(json.dumps(splits, sort_keys=True, separators=(",", ":")).encode()).hexdigest(), "research split hash mismatch")
    scale, policy = CreateUniversalFuzzyScale(), UniversalFuzzyScalePolicy()
    Require(report["termOrder"] == [term.name for term in scale.terms], "research term order changed")
    representatives = {term.name: float(Centroid(term.fuzzySet, domain)) for term, domain in zip(scale.terms, UniversalFuzzyScaleDomains(), strict=True)}
    scores = [observations[index][2] for index in splits["heldOut"]]
    labels = [scale.Fuzzify(value, policy).selectedTerms[0].name for value in scores]
    targets = [representatives[label] for label in labels]
    Require(report["heldOutInputs"] == [list(observations[index][:2]) for index in splits["heldOut"]], "research held-out inputs changed")
    Require(report["heldOutLatentScores"] == scores and report["heldOutLabels"] == labels, "research held-out targets changed")
    Require(len(report["heldOutTargets"]) == len(targets) and all(math.isclose(actual, expected, abs_tol=1e-14, rel_tol=1e-12) for actual, expected in zip(report["heldOutTargets"], targets, strict=True)), "research target is not the selected label centroid")
    Require(set(report["models"]) == set(MODEL_PARAMETERS), "research comparison set changed")

    for name, model in report["models"].items():
        Require(model["parameterCount"] == MODEL_PARAMETERS[name], "research parameter count changed")
        Require(model["bestEpoch"] is None if name == "fixedRules" else 1 <= model["bestEpoch"] <= epochs, "invalid research checkpoint")
        predictions, metrics = model["heldOutPredictions"], model["heldOut"]
        Require(len(predictions) == len(targets), "research prediction shape mismatch")

        for metric, reference in (("centroidRmse", targets), ("latentRmse", scores)):
            expected = math.sqrt(math.fsum((value - target) ** 2 for value, target in zip(predictions, reference, strict=True)) / len(reference))
            Require(math.isclose(metrics[metric], expected, abs_tol=1e-14, rel_tol=1e-12), f"research {name} {metric} mismatch")

        decoded = [scale.Fuzzify(value, policy).selectedTerms[0].name if 0 <= value <= 1 else None for value in predictions]
        Require(metrics["labelAccuracy"] == sum(actual == expected for actual, expected in zip(decoded, labels, strict=True)) / len(labels), "research label accuracy mismatch")
        Require(metrics["outOfDomainCount"] == sum(not 0 <= value <= 1 for value in predictions), "research out-of-domain errors were hidden")

        if name in {"zeroOrder", "firstOrder", "fixedMembership"}:
            Require(0 <= model["scalarParityMaximumAbsoluteError"] <= 1e-12, "research graph disagrees with scalar inference")

    return {"verified": True, "epochs": epochs, "samples": samples, "heldOut": len(targets), "datasetSha256": report["datasetSha256"]}


def InstalledProvenance(report: dict) -> dict:
    """Check the real loaded candidate and source hashes without admitting source imports."""

    RegisterNamespace("examples", PROJECT_ROOT / "examples")
    importlib.import_module("examples.neural.run").VerifyInstalledPackage()
    package = importlib.import_module("fuzzyroutines")
    packageRoot = Path(package.__file__).resolve().parent
    expectedVersion = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())["project"]["version"]
    Require(importlib.metadata.version("fuzzyroutines") == expectedVersion, "research candidate package version mismatch")
    ValidateSourceHashes(report)
    origins = {}

    for name, module in sorted(sys.modules.items()):
        if name == "fuzzyroutines" or name.startswith("fuzzyroutines."):
            origin = Path(module.__file__).resolve()
            Require(origin.is_relative_to(packageRoot), f"research loaded source core module: {name}")
            origins[name] = str(origin)

    for relative, digest in report["sourceSha256"].items():
        if relative.startswith("fuzzyroutines/"):
            installed = packageRoot / relative.removeprefix("fuzzyroutines/")
            Require(hashlib.sha256(installed.read_bytes()).hexdigest() == digest, f"installed research calculation source differs: {relative}")

    return {"packageVersion": expectedVersion, "packageOrigins": origins, "sourceSha256": report["sourceSha256"]}


def Main(arguments=None) -> int:
    """Run a bounded installed smoke or verify recorded figures without Torch."""

    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    smoke = commands.add_parser("smoke")
    smoke.add_argument("--output", type=Path, required=True)
    smoke.add_argument("--provenance", type=Path, required=True)
    figures = commands.add_parser("figures")
    figures.add_argument("--output-directory", type=Path, required=True, dest="outputDirectory")
    options = parser.parse_args(arguments)
    RegisterNamespace("examples", PROJECT_ROOT / "examples")
    importlib.import_module("examples.neural.run").VerifyInstalledPackage()

    if options.command == "smoke":
        RegisterNamespace("research", PROJECT_ROOT / "research")
        runner = importlib.import_module("research.run_sugeno")
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            Require(runner.Main(["--epochs", "3", "--samples", "30", "--output", str(options.output)]) == 0, "research runner failed")

        report = json.loads(options.output.read_text())
        Require(json.loads(stdout.getvalue()) == {name: model["heldOut"] for name, model in report["models"].items()}, "research stdout disagrees with report metrics")
        verification = {**ValidateReport(report), **InstalledProvenance(report)}
        options.provenance.parent.mkdir(parents=True, exist_ok=True)
        options.provenance.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n")
        print(stdout.getvalue(), end="")

    else:
        RegisterNamespace("tools", PROJECT_ROOT / "tools")
        plotting = importlib.import_module("tools.generate_sugeno_research_figures")
        report = json.loads(plotting.REPORT.read_text())
        provenance = InstalledProvenance(report)
        Require(plotting.Main(["--output-directory", str(options.outputDirectory), "--check"]) == 0, "research figures failed verification")
        print(json.dumps({"checked": True, **provenance}, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
