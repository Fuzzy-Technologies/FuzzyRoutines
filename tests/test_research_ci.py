# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Independent report-corruption and import-isolation checks for research CI."""

import hashlib
import json
import math
import random
import subprocess
import sys
from pathlib import Path

import pytest

from fuzzyroutines import (
    Centroid,
    CreateUniversalFuzzyScale,
    UniversalFuzzyScaleDomains,
    UniversalFuzzyScalePolicy,
)
from tools.research_ci import RESEARCH_SOURCES, ValidateReport

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def FakeReport(projectRoot):
    """Build an analytical report fixture; it is not a fitted research result."""

    generator = random.Random(1729)
    observations = []

    for index in range(30):
        severity, exposure = generator.random(), generator.random()
        observations.append((severity, exposure, 0.05 + 0.65 * severity + 0.30 * exposure))

    indices = list(range(30))
    random.Random(1730).shuffle(indices)
    splits = {"train": indices[:18], "validation": indices[18:24], "heldOut": indices[24:]}
    scale, policy = CreateUniversalFuzzyScale(), UniversalFuzzyScalePolicy()
    representatives = {term.name: float(Centroid(term.fuzzySet, domain)) for term, domain in zip(scale.terms, UniversalFuzzyScaleDomains(), strict=True)}
    scores = [observations[index][2] for index in splits["heldOut"]]
    labels = [scale.Fuzzify(value, policy).selectedTerms[0].name for value in scores]
    targets = [representatives[label] for label in labels]
    models = {}

    for name, count in (("fixedRules", 0), ("zeroOrder", 14), ("firstOrder", 22), ("fixedMembership", 12), ("rawMlp", 337)):
        predictions = targets.copy()

        if name == "firstOrder":
            predictions[0] = -0.1

        decoded = [scale.Fuzzify(value, policy).selectedTerms[0].name if 0 <= value <= 1 else None for value in predictions]
        metrics = {"centroidRmse": math.sqrt(sum((value - target) ** 2 for value, target in zip(predictions, targets, strict=True)) / 6),
                   "latentRmse": math.sqrt(sum((value - target) ** 2 for value, target in zip(predictions, scores, strict=True)) / 6),
                   "labelAccuracy": sum(left == right for left, right in zip(decoded, labels, strict=True)) / 6,
                   "outOfDomainCount": int(name == "firstOrder")}
        models[name] = {"parameterCount": count, "bestEpoch": None if name == "fixedRules" else 1,
                        "heldOutPredictions": predictions, "heldOut": metrics, "scalarParityMaximumAbsoluteError": 0.0}

    sourceHashes = {}

    for relative in RESEARCH_SOURCES:
        path = projectRoot / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"Scientific source fixture for {relative}\n")
        sourceHashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()

    return {"schemaVersion": 1, "task": "synthetic-severity-exposure-v1", "prototype": "bounded-differentiable-sugeno-v1",
            "configuration": {"epochs": 3, "sampleCount": 30, "dataSeed": 1729, "splitSeed": 1730, "networkSeed": 1731,
                              "checkpointSelection": "minimum validation MSE", "deterministicAlgorithms": True},
            "environment": {"device": "cpu", "dtype": "float64", "threads": 1, "torch": "2.14.1+cpu"},
            "sourceSha256": sourceHashes, "dependencyCost": None,
            "datasetSha256": hashlib.sha256(json.dumps(observations, separators=(",", ":")).encode()).hexdigest(),
            "splits": splits, "splitsSha256": hashlib.sha256(json.dumps(splits, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "termOrder": [term.name for term in scale.terms], "heldOutInputs": [list(observations[index][:2]) for index in splits["heldOut"]],
            "heldOutLatentScores": scores, "heldOutLabels": labels, "heldOutTargets": targets, "models": models}


def test_ResearchReportOracleKeepsOutOfDomainPredictions(tmpPath):
    """An invalid coordinate remains a numeric error, not a reason to discard the run."""

    report = FakeReport(tmpPath)
    verified = ValidateReport(report, projectRoot=tmpPath)
    assert verified["heldOut"] == 6
    assert verified["epochs"] == 3
    assert report["models"]["firstOrder"]["heldOut"]["outOfDomainCount"] == 1


@pytest.mark.parametrize("defect", ["metric", "data", "split", "source", "sourceSet", "domain", "parity", "parameters", "budget", "cost", "nonfinite"])
def test_ResearchReportOracleRejectsFalseEvidence(tmpPath, defect):
    """Reject independently corrupted scientific, scope and provenance claims."""

    report = FakeReport(tmpPath)

    if defect == "metric":
        report["models"]["rawMlp"]["heldOut"]["centroidRmse"] = 1

    elif defect == "data":
        report["datasetSha256"] = "wrong"

    elif defect == "split":
        report["splitsSha256"] = "wrong"

    elif defect == "source":
        report["sourceSha256"]["research/run_sugeno.py"] = "wrong"

    elif defect == "sourceSet":
        report["sourceSha256"].pop("fuzzyroutines/inference.py")

    elif defect == "domain":
        report["models"]["firstOrder"]["heldOut"]["outOfDomainCount"] = 0

    elif defect == "parity":
        report["models"]["zeroOrder"]["scalarParityMaximumAbsoluteError"] = 0.01

    elif defect == "parameters":
        report["models"]["fixedRules"]["parameterCount"] = 1

    elif defect == "budget":
        report["configuration"]["epochs"] = 400

    elif defect == "cost":
        report["dependencyCost"] = {"freshProcessImportSeconds": 1}

    elif defect == "nonfinite":
        report["models"]["firstOrder"]["heldOutPredictions"][0] = math.nan

    with pytest.raises(ValueError):
        ValidateReport(report, projectRoot=tmpPath)


def test_ResearchNamespaceDoesNotExposeCheckoutCore(tmpPath):
    """Load repository research with only stdlib available and no checkout sys.path entry."""

    (tmpPath / "research").mkdir()
    (tmpPath / "research/probe.py").write_text("value = 42\n")
    (tmpPath / "fuzzyroutines").mkdir()
    (tmpPath / "fuzzyroutines/__init__.py").write_text("raise AssertionError('checkout core must stay invisible')\n")
    code = """
import importlib.util
import runpy
import sys
from pathlib import Path

helper = runpy.run_path(sys.argv[1])
before = sys.path.copy()
helper["RegisterNamespace"]("research", Path(sys.argv[2]) / "research")
import research.probe
assert research.probe.value == 42
assert sys.path == before
assert importlib.util.find_spec("fuzzyroutines") is None
"""
    result = subprocess.run([sys.executable, "-I", "-S", "-c", code, str(PROJECT_ROOT / "tools/research_ci.py"), str(tmpPath)],
                            cwd=tmpPath, capture_output=True, text=True, check=False, timeout=30)
    assert result.returncode == 0, result.stderr
