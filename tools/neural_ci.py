# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Select optional neural checks and independently audit an installed smoke report.

Scope selection uses only the established CI policy JSON and standard library.
Report verification imports the active scalar package, never Torch. Training
and plotting remain separate scopes; neither adds a dependency to core gates.
"""

import argparse
import hashlib
import json
import math
import os
import random
import subprocess
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = PROJECT_ROOT / "_build/neural-ci/scope.json"
NEURAL_TESTS = ("tests/test_neural_example.py",)
RESEARCH_TESTS = ("tests/test_differentiable_sugeno.py", "tests/test_sugeno_research.py")
NEURAL_PLOT_TESTS = ("tests/test_neural_figures.py",)
RESEARCH_PLOT_TESTS = ("tests/test_sugeno_research_figures.py",)
TRAINING_TESTS = NEURAL_TESTS + RESEARCH_TESTS
PLOT_TESTS = NEURAL_PLOT_TESTS + RESEARCH_PLOT_TESTS


def SelectScope(policy: dict) -> dict:
    """Select complete optional groups only for a full gate or reviewed test paths."""

    if not isinstance(policy.get("full"), bool) or not isinstance(policy.get("tests"), list):
        raise TypeError("neural scope requires validated full/tests CI policy fields")

    if not all(isinstance(path, str) for path in policy["tests"]):
        raise TypeError("neural test scope must contain paths")

    selected = set(policy["tests"])
    training = [path for path in TRAINING_TESTS if policy["full"] or path in selected]
    plots = [path for path in PLOT_TESTS if policy["full"] or path in selected]

    return {"training": bool(training), "plots": bool(plots), "active": bool(training or plots),
            "neural": bool(set(training) & set(NEURAL_TESTS)), "research": bool(set(training) & set(RESEARCH_TESTS)),
            "neuralPlots": bool(set(plots) & set(NEURAL_PLOT_TESTS)), "researchPlots": bool(set(plots) & set(RESEARCH_PLOT_TESTS)),
            "trainingTests": training, "plotTests": plots}


def Require(condition: bool, message: str) -> None:
    """Fail report verification explicitly, including under optimized Python."""

    if not condition:
        raise ValueError(message)


def FiniteTree(value) -> None:
    """Reject non-finite numbers anywhere in a parsed report."""

    if isinstance(value, float):
        Require(math.isfinite(value), "non-finite report number")

    elif isinstance(value, dict):
        for child in value.values():
            FiniteTree(child)

    elif isinstance(value, list):
        for child in value:
            FiniteTree(child)


def ValidateReport(report: dict, *, expectedVersion: str, epochs: int, samples: int) -> dict:
    """Recompute scalar metrics and data identities independently of the training script."""

    from fuzzyroutines import (
        Centroid,
        CreateUniversalFuzzyScale,
        UniversalFuzzyScaleDomains,
        UniversalFuzzyScalePolicy,
    )

    FiniteTree(report)
    Require(report["schemaVersion"] == 1 and report["task"] == "synthetic-severity-exposure-v1", "unexpected neural report schema/task")
    configuration = report["configuration"]
    Require(configuration["epochs"] == epochs and configuration["sampleCount"] == samples, "unexpected smoke budget")
    Require((configuration["dataSeed"], configuration["splitSeed"], configuration["networkSeed"]) == (1729, 1730, 1731), "unexpected experiment seeds")
    Require(configuration["checkpointSelection"] == "minimum validation MSE" and configuration["deterministicAlgorithms"] is True, "invalid training selection policy")
    environment = report["environment"]
    Require(environment["fuzzyroutines"] == expectedVersion, "smoke did not use the candidate package version")
    Require((environment["device"], environment["dtype"], environment["threads"], environment["torch"]) == ("cpu", "float64", 1, "2.14.1+cpu"), "unexpected CPU numerical environment")
    Require(report["exampleSha256"] == hashlib.sha256((PROJECT_ROOT / "examples/neural/run.py").read_bytes()).hexdigest(), "report source hash mismatch")
    generator = random.Random(1729)
    observations = []

    for index in range(samples):
        severity, exposure = generator.random(), generator.random()
        observations.append((severity, exposure, 0.05 + 0.65 * severity + 0.30 * exposure))

    digest = hashlib.sha256(json.dumps(observations, separators=(",", ":")).encode()).hexdigest()
    Require(report["datasetSha256"] == digest, "synthetic data identity mismatch")
    indices = list(range(samples))
    random.Random(1730).shuffle(indices)
    expectedSplits = {"train": indices[:3 * samples // 5], "validation": indices[3 * samples // 5:4 * samples // 5], "heldOut": indices[4 * samples // 5:]}
    Require(report["splits"] == expectedSplits, "split identities or disjointness changed")
    scale, policy = CreateUniversalFuzzyScale(), UniversalFuzzyScalePolicy()
    termNames = [term.name for term in scale.terms]
    Require(report["termOrder"] == termNames, "membership column order changed")
    expectedScores = [observations[index][2] for index in expectedSplits["heldOut"]]
    expectedLabels = [scale.Fuzzify(value, policy).selectedTerms[0].name for value in expectedScores]
    Require(report["heldOutLatentScores"] == expectedScores and report["heldOutLabels"] == expectedLabels, "held-out observations or labels changed")
    targets = report["heldOutTargets"]
    Require(len(targets) == len(expectedScores), "scalar target shape mismatch")
    representatives = {term.name: float(Centroid(term.fuzzySet, domain)) for term, domain in zip(scale.terms, UniversalFuzzyScaleDomains(), strict=True)}
    Require(all(math.isclose(value, representatives[label], rel_tol=1e-12, abs_tol=1e-14) for value, label in zip(targets, expectedLabels, strict=True)), "scalar target is not the selected label centroid")
    trainTargets = [representatives[scale.Fuzzify(observations[index][2], policy).selectedTerms[0].name] for index in expectedSplits["train"]]
    trainingMean = math.fsum(trainTargets) / len(trainTargets)
    Require(math.isclose(report["baseline"]["meanTrainingTarget"], trainingMean, rel_tol=1e-12, abs_tol=1e-14), "baseline used data outside the training split")
    Require(set(report["scalarAblations"]) == {"raw", "centroid", "memberships"}, "scalar ablation set changed")

    for name, width in (("raw", 2), ("centroid", 2), ("memberships", 10)):
        model = report["scalarAblations"][name]
        predictions = model["heldOutPredictions"]
        Require(model["inputWidth"] == width and len(predictions) == len(targets), "scalar prediction shape mismatch")
        Require(1 <= model["bestEpoch"] <= epochs and model["validationMse"] >= 0, "invalid validation-selected checkpoint")
        metrics = model["heldOut"]

        for key, reference in (("centroidRmse", targets), ("latentRmse", expectedScores)):
            expected = math.sqrt(math.fsum((value - target) ** 2 for value, target in zip(predictions, reference, strict=True)) / len(reference))
            Require(math.isclose(metrics[key], expected, rel_tol=1e-12, abs_tol=1e-14), f"{name} {key} does not match predictions")

        decoded = [scale.Fuzzify(value, policy).selectedTerms[0].name if 0 <= value <= 1 else None for value in predictions]
        accuracy = sum(actual == expected for actual, expected in zip(decoded, expectedLabels, strict=True)) / len(expectedLabels)
        Require(metrics["labelAccuracy"] == accuracy, f"{name} label accuracy does not match predictions")
        Require(metrics["outOfDomainCount"] == sum(not 0 <= value <= 1 for value in predictions), "out-of-domain errors were hidden")

    gradeHead = report["gradeHead"]
    Require(1 <= gradeHead["bestEpoch"] <= epochs and 0 <= gradeHead["heldOutGradeRmse"] <= 1, "invalid grade-head evidence")
    gradeRange = gradeHead["predictedGradeSumRange"]
    Require(len(gradeRange) == 2 and 0 <= gradeRange[0] <= gradeRange[1] <= 5, "invalid independent grade-sum range")
    weakGrades = gradeHead["weakCoverageProbe"]["predictedGrades"]
    Require(len(weakGrades) == 5 and all(0 <= grade <= 1 for grade in weakGrades), "grade-head shape or bounds changed")
    Require([item["value"] for item in report["outOfDomainExamples"]] == [-0.05, 1.05], "out-of-domain probes were clipped")
    Require(all(item["status"] == "out-of-domain" and item["label"] is None for item in report["outOfDomainExamples"]), "out-of-domain probes were decoded")

    return {"verified": True, "samples": samples, "heldOut": len(targets), "epochs": epochs,
            "packageVersion": expectedVersion, "datasetSha256": digest}


def Main(arguments=None) -> int:
    """Select scopes, execute selected feature files or audit a bounded smoke report."""

    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    select = commands.add_parser("scope")
    select.add_argument("--policy", type=Path, default=PROJECT_ROOT / "_build/ci-policy.json")
    execute = commands.add_parser("run-tests")
    execute.add_argument("--group", choices=("training", "plots"), required=True)
    execute.add_argument("--python", type=Path, required=True)
    verify = commands.add_parser("verify-report")
    verify.add_argument("--report", type=Path, required=True)
    verify.add_argument("--stdout", type=Path, required=True)
    verify.add_argument("--epochs", type=int, default=30)
    verify.add_argument("--samples", type=int, default=90)
    options = parser.parse_args(arguments)

    if options.command == "scope":
        scope = SelectScope(json.loads(options.policy.read_text(encoding="utf-8")))
        SCOPE_PATH.parent.mkdir(parents=True, exist_ok=True)
        SCOPE_PATH.write_text(json.dumps(scope, indent=2) + "\n", encoding="utf-8")

        if outputPath := os.environ.get("GITHUB_OUTPUT"):
            with Path(outputPath).open("a", encoding="utf-8") as output:
                output.writelines(f"{key}={str(scope[key]).lower()}\n" for key in ("training", "plots", "active", "neural", "research", "neuralPlots", "researchPlots"))

        print(json.dumps(scope, sort_keys=True))

    elif options.command == "run-tests":
        scope = json.loads(SCOPE_PATH.read_text(encoding="utf-8"))
        selected = scope["trainingTests" if options.group == "training" else "plotTests"]
        allowed = TRAINING_TESTS if options.group == "training" else PLOT_TESTS
        Require(bool(selected) and set(selected) <= set(allowed), "missing or unsafe optional test selection")

        return subprocess.run([str(options.python), "-m", "pytest", "-q", *selected,
                               f"--junitxml={SCOPE_PATH.parent / (options.group + '.xml')}"], cwd=PROJECT_ROOT, check=False).returncode

    else:
        Require(options.report.read_bytes() == options.stdout.read_bytes(), "smoke stdout and report file differ")
        metadata = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        result = ValidateReport(json.loads(options.report.read_text(encoding="utf-8")), expectedVersion=metadata["project"]["version"], epochs=options.epochs, samples=options.samples)
        print(json.dumps(result, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
