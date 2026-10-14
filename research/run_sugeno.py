# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Compare a bounded trainable Sugeno graph with fixed rules and the shared MLP.

This CPU-only repository experiment reuses Task #328 data, splits, targets and
MLP training. Checkpoints use validation MSE only. JSON contains reproducible
scientific values and separately identified machine-dependent timing evidence.
No public tensor API, real risk model or ANFIS hybrid learner is implemented.
"""

import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path

import torch

from examples.neural.run import (
    CreateCodec,
    GenerateObservations,
    Predict,
    ScalarMetrics,
    SelectedLabel,
    SplitIndices,
    SyntheticScore,
    TrainModel,
)
from research.differentiable_sugeno import (
    DifferentiableSugeno,
    MembershipParameters,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = ("research/differentiable_sugeno.py", "research/run_sugeno.py", "examples/neural/run.py", "fuzzyroutines/inference.py", "fuzzyroutines/encoding.py", "fuzzyroutines/presets.py")


def Snapshot(model: DifferentiableSugeno) -> dict:
    """Serialize parameter values at an explicit evaluation-only graph boundary."""

    centers, widths = MembershipParameters(model.rawGaps, model.rawWidths)

    return {"centers": centers.detach().tolist(), "widths": widths.detach().tolist(),
            "rawGaps": model.rawGaps.detach().tolist(), "rawWidths": model.rawWidths.detach().tolist(),
            "consequences": model.consequences.detach().tolist(), "ruleWeights": model.ruleWeights.tolist()}


def TrainRules(features: list[list[float]], targets: list[list[float]], splits: dict[str, tuple[int, ...]], *, order: int, trainMembership: bool, epochs: int) -> tuple[DifferentiableSugeno, dict]:
    """Select a gradient-trained rule checkpoint exclusively by validation MSE.

    The same fixed preprocessing, full-batch Adam learning rate and epoch
    budget as the shared MLP are used. Held-out identities are never indexed.
    """

    if isinstance(epochs, bool) or not isinstance(epochs, int) or not 1 <= epochs <= 2000:
        raise ValueError("epochs must be an integer between 1 and 2000")

    if not features or len(features) != len(targets) or set(splits) != {"train", "validation", "heldOut"}:
        raise ValueError("aligned features, targets and all three splits are required")

    if any(len(row) != 1 or not math.isfinite(row[0]) for row in targets):
        raise ValueError("targets must contain one finite scalar per observation")

    if any(not indices for indices in splits.values()) or sorted(index for indices in splits.values() for index in indices) != list(range(len(features))):
        raise ValueError("splits must be non-empty, disjoint and cover every observation")

    model = DifferentiableSugeno(order, trainMembership=trainMembership)
    initial = Snapshot(model)
    optimizer = torch.optim.Adam(model.Parameters(), lr=0.01)
    trainInputs = torch.tensor([features[index] for index in splits["train"]], dtype=torch.float64)
    trainTargets = torch.tensor([targets[index][0] for index in splits["train"]], dtype=torch.float64)
    validationInputs = torch.tensor([features[index] for index in splits["validation"]], dtype=torch.float64)
    validationTargets = torch.tensor([targets[index][0] for index in splits["validation"]], dtype=torch.float64)
    bestValidation = math.inf
    bestEpoch = 0
    bestParameters = tuple(value.detach().clone() for value in model.Parameters())
    history = []

    for epoch in range(1, epochs + 1):
        optimizer.zero_grad(set_to_none=True)
        loss = torch.nn.functional.mse_loss(model.Evaluate(trainInputs), trainTargets)
        loss.backward()
        optimizer.step()

        with torch.no_grad():
            trainMse = float(torch.nn.functional.mse_loss(model.Evaluate(trainInputs), trainTargets))
            validationMse = float(torch.nn.functional.mse_loss(model.Evaluate(validationInputs), validationTargets))

        if not all(math.isfinite(value) for value in (trainMse, validationMse)):
            raise ArithmeticError("non-finite Sugeno training evidence")

        if validationMse < bestValidation:
            bestValidation, bestEpoch = validationMse, epoch
            bestParameters = tuple(value.detach().clone() for value in model.Parameters())

        if epoch == 1 or epoch % 10 == 0 or epoch == epochs:
            history.append({"epoch": epoch, "trainMse": trainMse, "validationMse": validationMse})

    with torch.no_grad():
        for parameter, bestValue in zip(model.Parameters(), bestParameters, strict=True):
            parameter.copy_(bestValue)

    return model, {"bestEpoch": bestEpoch, "validationMse": bestValidation, "history": history,
                   "parameterCount": sum(value.numel() for value in model.Parameters()),
                   "initial": initial, "selected": Snapshot(model)}


def PredictRules(model: DifferentiableSugeno, rows: list[list[float]]) -> list[float]:
    """Evaluate immutable observations outside the training gradient graph."""

    with torch.no_grad():
        return model.Evaluate(torch.tensor(rows, dtype=torch.float64)).tolist()


def DependencyEvidence() -> dict:
    """Measure installed Torch files and a fresh-process import, without a resolver."""

    distribution = importlib.metadata.distribution("torch")
    paths = tuple(distribution.locate_file(path) for path in distribution.files or ())
    start = time.perf_counter()
    subprocess.run([sys.executable, "-c", "import torch"], check=True, stdout=subprocess.DEVNULL)
    importSeconds = time.perf_counter() - start

    return {"torchDistributionBytes": sum(path.stat().st_size for path in paths if path.is_file()),
            "freshProcessImportSeconds": importSeconds,
            "directRequirements": distribution.requires or [],
            "interpretation": "Uncompressed installed Torch distribution only; transitive dependencies excluded. Fresh process wall time includes Python startup, with existing OS caches."}


def RunExperiment(*, seed: int = 1729, epochs: int = 400, sampleCount: int = 600, measureDependencies: bool = False) -> dict:
    """Run the predeclared comparison on common held-out centroid targets."""

    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    observations = GenerateObservations(seed, sampleCount)
    splits = SplitIndices(sampleCount, seed + 1)
    codec = CreateCodec()
    representatives = {name: float(codec.EncodeLabel(name)) for name in codec.termNames}
    labels = [SelectedLabel(codec, observation.score) for observation in observations]
    features = [[observation.severity, observation.exposure] for observation in observations]
    targets = [[representatives[label]] for label in labels]
    heldOutInputs = [features[index] for index in splits["heldOut"]]
    heldOutTargets = [targets[index][0] for index in splits["heldOut"]]
    heldOutScores = [observations[index].score for index in splits["heldOut"]]
    heldOutLabels = [labels[index] for index in splits["heldOut"]]
    sliceInputs = [[index / 100, 0.5] for index in range(101)]
    sliceTargets = [representatives[SelectedLabel(codec, SyntheticScore(*row))] for row in sliceInputs]
    models = {}
    timings = {}
    fixed = DifferentiableSugeno(0, trainMembership=False, trainConsequences=False)
    models["fixedRules"] = {"parameterCount": 0, "selected": Snapshot(fixed), "bestEpoch": None,
                            "heldOutPredictions": PredictRules(fixed, heldOutInputs), "slicePredictions": PredictRules(fixed, sliceInputs)}

    for name, order, trainMembership in (("zeroOrder", 0, True), ("firstOrder", 1, True), ("fixedMembership", 1, False)):
        start = time.perf_counter()
        model, evidence = TrainRules(features, targets, splits, order=order, trainMembership=trainMembership, epochs=epochs)
        timings[name] = {"trainingWallSeconds": time.perf_counter() - start}
        evidence.update({"heldOutPredictions": PredictRules(model, heldOutInputs), "slicePredictions": PredictRules(model, sliceInputs)})
        scalar = model.ScalarReference()
        scalarPredictions = [scalar.Evaluate({"input0": row[0], "input1": row[1]}).value for row in heldOutInputs]
        evidence["scalarParityMaximumAbsoluteError"] = max(abs(first - second) for first, second in zip(evidence["heldOutPredictions"], scalarPredictions, strict=True))
        models[name] = evidence

    start = time.perf_counter()
    mlp = TrainModel(features, targets, splits, seed=seed + 2, epochs=epochs)
    timings["rawMlp"] = {"trainingWallSeconds": time.perf_counter() - start}
    models["rawMlp"] = {"parameterCount": mlp.parameterCount, "bestEpoch": mlp.bestEpoch,
                        "validationMse": mlp.validationMse, "history": mlp.history,
                        "heldOutPredictions": [row[0] for row in Predict(mlp.model, heldOutInputs)],
                        "slicePredictions": [row[0] for row in Predict(mlp.model, sliceInputs)]}

    for evidence in models.values():
        evidence["heldOut"] = ScalarMetrics(evidence["heldOutPredictions"], heldOutTargets, heldOutScores, heldOutLabels, codec)

    dataset = [(item.severity, item.exposure, item.score) for item in observations]
    meanTarget = math.fsum(targets[index][0] for index in splits["train"]) / len(splits["train"])

    return {
        "schemaVersion": 1, "task": "synthetic-severity-exposure-v1", "prototype": "bounded-differentiable-sugeno-v1",
        "configuration": {"dataSeed": seed, "splitSeed": seed + 1, "networkSeed": seed + 2, "epochs": epochs,
                          "sampleCount": sampleCount, "learningRate": 0.01, "checkpointSelection": "minimum validation MSE",
                          "deterministicAlgorithms": True, "ruleInitialization": "fixed centers .25/.75, widths .25, constants .15/.4/.6/.85; affine slopes zero"},
        "environment": {"python": platform.python_version(), "torch": torch.__version__, "platform": platform.system(),
                        "machine": platform.machine(), "device": "cpu", "dtype": "float64", "threads": 1},
        "sourceSha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCE_PATHS},
        "datasetSha256": hashlib.sha256(json.dumps(dataset, separators=(",", ":")).encode()).hexdigest(),
        "splitsSha256": hashlib.sha256(json.dumps(splits, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "splits": splits, "termOrder": codec.termNames, "centroids": representatives,
        "heldOutInputs": heldOutInputs, "heldOutTargets": heldOutTargets, "heldOutLatentScores": heldOutScores, "heldOutLabels": heldOutLabels,
        "meanTrainingTargetBaseline": ScalarMetrics([meanTarget] * len(heldOutTargets), heldOutTargets, heldOutScores, heldOutLabels, codec),
        "models": models, "slice": {"inputs": sliceInputs, "targets": sliceTargets}, "timings": timings,
        "dependencyCost": DependencyEvidence() if measureDependencies else None,
        "limitations": "One synthetic dataset/split and one deterministic initialization, not real risk data. Four manually fixed initial rules are a small illustrative baseline, not an optimized fuzzy expert system. Affine and learned constants can leave [0,1]; violations are reported without clipping. Timing is machine-dependent. No hyperparameter search or held-out tuning.",
    }


def Main(arguments=None) -> int:
    """Write the measured prototype evidence as JSON; no network or GPU is used."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--epochs", type=int, default=400)
    parser.add_argument("--samples", type=int, default=600)
    parser.add_argument("--measure-dependencies", action="store_true", dest="measureDependencies")
    options = parser.parse_args(arguments)
    start = time.perf_counter()
    report = RunExperiment(seed=options.seed, epochs=options.epochs, sampleCount=options.samples, measureDependencies=options.measureDependencies)
    report["timings"]["experimentWallSeconds"] = time.perf_counter() - start
    options.output.parent.mkdir(parents=True, exist_ok=True)
    options.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({name: evidence["heldOut"] for name, evidence in report["models"].items()}, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
