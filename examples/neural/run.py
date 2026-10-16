# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Train small CPU networks with fixed fuzzy inputs and interpretable outputs.

The synthetic severity/exposure relation is illustrative, not a measured risk
model. JSON contains fixed splits, validation-selected checkpoints, held-out
metrics, boundary diagnostics and figure data. Torch is imported only when
training starts. No network, GPU, Docker, pretrained model or hidden data is
used; this script does not define trainable fuzzy rules.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import math
import platform
import random
import sysconfig
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import fuzzyroutines
from fuzzyroutines import (
    CreateUniversalFuzzyScale,
    LinguisticCodec,
    UniversalFuzzyScaleDomains,
    UniversalFuzzyScalePolicy,
)

if TYPE_CHECKING:
    import torch

REPRESENTATIONS = ("raw", "centroid", "memberships")


@dataclass(frozen=True, slots=True)
class Observation:
    """One synthetic observation in a fixed closed-unit coordinate system."""

    severity: float
    exposure: float
    score: float


@dataclass(frozen=True, slots=True)
class TrainingResult:
    """A validation-selected network with its bounded training evidence."""

    model: torch.nn.Module
    bestEpoch: int
    validationMse: float
    history: tuple[dict[str, float | int], ...]
    parameterCount: int


def CreateCodec() -> LinguisticCodec:
    """Declare the original windows and last-exact-maximum winner policy."""

    return LinguisticCodec(CreateUniversalFuzzyScale(), UniversalFuzzyScaleDomains(), UniversalFuzzyScalePolicy())


def SyntheticScore(severity: float, exposure: float) -> float:
    """Evaluate the fixed relation 0.05 + 0.65 severity + 0.30 exposure."""

    for coordinate in (severity, exposure):
        if isinstance(coordinate, bool) or not isinstance(coordinate, (int, float)):
            raise TypeError("synthetic inputs must be real scalar coordinates")

        if not math.isfinite(coordinate) or not 0 <= coordinate <= 1:
            raise ValueError("synthetic inputs must belong to [0, 1]")

    return 0.05 + 0.65 * severity + 0.30 * exposure


def GenerateObservations(seed: int, sampleCount: int) -> tuple[Observation, ...]:
    """Generate bounded observations from an explicit local random stream."""

    if isinstance(sampleCount, bool) or not isinstance(sampleCount, int) or not 30 <= sampleCount <= 10000:
        raise ValueError("sampleCount must be an integer between 30 and 10000")

    generator = random.Random(seed)
    coordinates = tuple((generator.random(), generator.random()) for index in range(sampleCount))

    return tuple(Observation(severity, exposure, SyntheticScore(severity, exposure)) for severity, exposure in coordinates)


def SplitIndices(sampleCount: int, seed: int) -> dict[str, tuple[int, ...]]:
    """Split identities 60/20/20 using a separate local random stream."""

    indices = list(range(sampleCount))
    random.Random(seed).shuffle(indices)
    trainEnd = 3 * sampleCount // 5
    validationEnd = 4 * sampleCount // 5

    return {"train": tuple(indices[:trainEnd]), "validation": tuple(indices[trainEnd:validationEnd]), "heldOut": tuple(indices[validationEnd:])}


def SelectedLabel(codec: LinguisticCodec, coordinate: float) -> str:
    """Require the preset's single selected label without a fallback."""

    result = codec.DecodePrediction(coordinate)

    if len(result.selectedTerms) != 1:
        raise ValueError("the example requires exactly one selected linguistic label")

    return result.selectedTerms[0].name


def EncodeFeatures(observations: tuple[Observation, ...], representation: str, codec: LinguisticCodec) -> list[list[float]]:
    """Encode each input as raw coordinates, label centroids or ten ordered grades."""

    if representation not in REPRESENTATIONS:
        raise ValueError(f"unknown representation: {representation}")

    representatives = {name: float(codec.EncodeLabel(name)) for name in codec.termNames} if representation == "centroid" else {}
    features = []

    for observation in observations:
        coordinates = (observation.severity, observation.exposure)

        if representation == "raw":
            row = list(coordinates)

        elif representation == "centroid":
            row = [representatives[SelectedLabel(codec, coordinate)] for coordinate in coordinates]

        else:
            row = [float(grade) for coordinate in coordinates for grade in codec.EncodeMemberships(coordinate)]

        features.append(row)

    return features


def TrainModel(features: list[list[float]], targets: list[list[float]], splits: dict[str, tuple[int, ...]], *, seed: int, epochs: int, boundedGrades: bool = False) -> TrainingResult:
    """Fit full batches and select only by validation MSE, never held-out targets.

    All preprocessing is fixed; no scaler is fitted. Scalar ablations share
    architecture width, optimizer, loss, epoch budget and split identities.
    Input dimensions differ, so parameter counts are reported explicitly.
    """

    import torch

    if isinstance(epochs, bool) or not isinstance(epochs, int) or not 1 <= epochs <= 2000:
        raise ValueError("epochs must be an integer between 1 and 2000")

    if not features or len(features) != len(targets):
        raise ValueError("features and targets must be non-empty aligned rows")

    for rows in (features, targets):
        width = len(rows[0])

        if not width or any(len(row) != width for row in rows):
            raise ValueError("each input and target tensor must have a fixed non-zero width")

        if not all(math.isfinite(value) for row in rows for value in row):
            raise ValueError("input and target tensors must contain finite values")

    if any(not indices for indices in splits.values()) or set(splits) != {"train", "validation", "heldOut"}:
        raise ValueError("train, validation and held-out splits must all be present and non-empty")

    flatIndices = tuple(index for indices in splits.values() for index in indices)

    if sorted(flatIndices) != list(range(len(features))):
        raise ValueError("split identities must be disjoint and cover every observation once")

    torch.manual_seed(seed)
    layers: list[torch.nn.Module] = [torch.nn.Linear(len(features[0]), 16, dtype=torch.float64), torch.nn.Tanh(),
                                    torch.nn.Linear(16, 16, dtype=torch.float64), torch.nn.Tanh(),
                                    torch.nn.Linear(16, len(targets[0]), dtype=torch.float64)]

    if boundedGrades:
        layers.append(torch.nn.Sigmoid())

    model = torch.nn.Sequential(*layers)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    trainFeatures = torch.tensor([features[index] for index in splits["train"]], dtype=torch.float64)
    trainTargets = torch.tensor([targets[index] for index in splits["train"]], dtype=torch.float64)
    validationFeatures = torch.tensor([features[index] for index in splits["validation"]], dtype=torch.float64)
    validationTargets = torch.tensor([targets[index] for index in splits["validation"]], dtype=torch.float64)
    bestValidation = math.inf
    bestEpoch = 0
    bestState = copy.deepcopy(model.state_dict())
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        loss = torch.nn.functional.mse_loss(model(trainFeatures), trainTargets)
        loss.backward()
        optimizer.step()
        model.eval()

        with torch.no_grad():
            trainMse = float(torch.nn.functional.mse_loss(model(trainFeatures), trainTargets))
            validationMse = float(torch.nn.functional.mse_loss(model(validationFeatures), validationTargets))

        if not all(math.isfinite(value) for value in (trainMse, validationMse)):
            raise ArithmeticError("non-finite training evidence")

        if validationMse < bestValidation:
            bestValidation, bestEpoch = validationMse, epoch
            bestState = copy.deepcopy(model.state_dict())

        if epoch == 1 or epoch % 10 == 0 or epoch == epochs:
            history.append({"epoch": epoch, "trainMse": trainMse, "validationMse": validationMse})

    model.load_state_dict(bestState)
    model.eval()

    return TrainingResult(model, bestEpoch, bestValidation, tuple(history), sum(parameter.numel() for parameter in model.parameters()))


def Predict(model: torch.nn.Module, rows: list[list[float]]) -> list[list[float]]:
    """Evaluate fixed CPU rows without retaining a gradient graph."""

    import torch

    with torch.no_grad():
        return model(torch.tensor(rows, dtype=torch.float64)).tolist()


def InterpretPrediction(codec: LinguisticCodec, prediction: float) -> dict:
    """Record invalid model outputs explicitly, without passing clipped values to the codec."""

    if not math.isfinite(prediction):
        return {"value": None, "status": "non-finite", "label": None, "memberships": None}

    if not 0 <= prediction <= 1:
        return {"value": prediction, "status": "out-of-domain", "label": None, "memberships": None}

    result = codec.DecodePrediction(prediction)

    return {"value": prediction, "status": "matched" if result.isMatch else "no-match", "label": result.selectedTerms[0].name if result.isMatch else None,
            "memberships": [float(item.grade) for item in result.memberships], "confidence": float(result.confidence)}


def ScalarMetrics(predictions: list[float], targets: list[float], latentScores: list[float], labels: list[str], codec: LinguisticCodec) -> dict:
    """Report centroid-target and latent-score errors separately with decoded labels."""

    if not predictions or not len(predictions) == len(targets) == len(latentScores) == len(labels):
        raise ValueError("metric rows must be non-empty and aligned")

    if not all(math.isfinite(value) for value in predictions):
        raise ArithmeticError("non-finite model predictions")

    interpretations = [InterpretPrediction(codec, value) for value in predictions]

    return {
        "centroidRmse": math.sqrt(math.fsum((value - target) ** 2 for value, target in zip(predictions, targets, strict=True)) / len(targets)),
        "latentRmse": math.sqrt(math.fsum((value - target) ** 2 for value, target in zip(predictions, latentScores, strict=True)) / len(targets)),
        "labelAccuracy": sum(item["label"] == label for item, label in zip(interpretations, labels, strict=True)) / len(labels),
        "outOfDomainCount": sum(item["status"] == "out-of-domain" for item in interpretations),
        "noMatchCount": sum(item["status"] == "no-match" for item in interpretations),
        "predictionRange": [min(predictions), max(predictions)],
    }


def RunExperiment(*, seed: int = 1729, epochs: int = 400, sampleCount: int = 600) -> dict:
    """Run the three scalar ablations and a separate independent-grade target task."""

    import torch

    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    observations = GenerateObservations(seed, sampleCount)
    splits = SplitIndices(sampleCount, seed + 1)
    codec = CreateCodec()
    representatives = {name: float(codec.EncodeLabel(name)) for name in codec.termNames}
    labels = [SelectedLabel(codec, item.score) for item in observations]
    targets = [[representatives[label]] for label in labels]
    heldOutTargets = [targets[index][0] for index in splits["heldOut"]]
    heldOutScores = [observations[index].score for index in splits["heldOut"]]
    heldOutLabels = [labels[index] for index in splits["heldOut"]]
    meanTarget = math.fsum(targets[index][0] for index in splits["train"]) / len(splits["train"])
    trainLabelCounts = Counter(labels[index] for index in splits["train"])
    majorityLabel = max(codec.termNames, key=lambda name: trainLabelCounts[name])
    baseline = ScalarMetrics([meanTarget] * len(heldOutTargets), heldOutTargets, heldOutScores, heldOutLabels, codec)
    baseline.update({"meanTrainingTarget": meanTarget, "majorityTrainingLabel": majorityLabel,
                     "majorityLabelAccuracy": heldOutLabels.count(majorityLabel) / len(heldOutLabels)})
    sliceRows = tuple(Observation(index / 100, 0.5, SyntheticScore(index / 100, 0.5)) for index in range(101))
    probeRows = tuple(Observation(severity, exposure, SyntheticScore(severity, exposure)) for severity, exposure in
                      ((0.0, 0.0), (0.17, 0.17), (0.37, 0.63), (0.75, 0.65), (1.0, 1.0)))
    scalarResults = {}

    for representation in REPRESENTATIONS:
        features = EncodeFeatures(observations, representation, codec)
        trained = TrainModel(features, targets, splits, seed=seed + 2, epochs=epochs)
        predictions = [row[0] for row in Predict(trained.model, [features[index] for index in splits["heldOut"]])]
        scalarResults[representation] = {
            "inputWidth": len(features[0]), "parameterCount": trained.parameterCount,
            "bestEpoch": trained.bestEpoch, "validationMse": trained.validationMse,
            "history": trained.history, "heldOut": ScalarMetrics(predictions, heldOutTargets, heldOutScores, heldOutLabels, codec),
            "heldOutPredictions": predictions,
            "slicePredictions": [row[0] for row in Predict(trained.model, EncodeFeatures(sliceRows, representation, codec))],
            "probes": [InterpretPrediction(codec, row[0]) for row in Predict(trained.model, EncodeFeatures(probeRows, representation, codec))],
        }

    fullFeatures = EncodeFeatures(observations, "memberships", codec)
    gradeTargets = [[float(grade) for grade in codec.EncodeMemberships(item.score)] for item in observations]
    gradeModel = TrainModel(fullFeatures, gradeTargets, splits, seed=seed + 2, epochs=epochs, boundedGrades=True)
    gradePredictions = Predict(gradeModel.model, [fullFeatures[index] for index in splits["heldOut"]])
    gradeErrors = [(predicted - expected) ** 2 for row, index in zip(gradePredictions, splits["heldOut"], strict=True)
                   for predicted, expected in zip(row, gradeTargets[index], strict=True)]
    weakProbe = (Observation(0.1, 11 / 60, 0.17),)
    weakGrades = Predict(gradeModel.model, EncodeFeatures(weakProbe, "memberships", codec))[0]
    collisionRows = (Observation(0.4, 0.9, SyntheticScore(0.4, 0.9)), Observation(0.6, 0.9, SyntheticScore(0.6, 0.9)))
    packageVersion = "source"

    try:
        packageVersion = importlib.metadata.version("fuzzyroutines")

    except importlib.metadata.PackageNotFoundError:
        pass

    datasetHash = hashlib.sha256(json.dumps([(item.severity, item.exposure, item.score) for item in observations], separators=(",", ":")).encode()).hexdigest()

    return {
        "schemaVersion": 1, "task": "synthetic-severity-exposure-v1",
        "exampleSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "environment": {"python": platform.python_version(), "torch": torch.__version__, "fuzzyroutines": packageVersion,
                        "platform": platform.system(), "machine": platform.machine(), "device": "cpu", "dtype": "float64", "threads": 1},
        "configuration": {"seed": seed, "dataSeed": seed, "splitSeed": seed + 1, "networkSeed": seed + 2,
                          "epochs": epochs, "sampleCount": sampleCount, "hiddenWidths": [16, 16], "learningRate": 0.01,
                          "checkpointSelection": "minimum validation MSE", "deterministicAlgorithms": True},
        "termOrder": codec.termNames, "integrationDomains": [(domain.left, domain.right) for domain in codec.integrationDomains],
        "centroids": representatives, "datasetSha256": datasetHash, "splits": splits,
        "heldOutTargets": heldOutTargets, "heldOutLatentScores": heldOutScores, "heldOutLabels": heldOutLabels,
        "baseline": baseline, "scalarAblations": scalarResults,
        "gradeHead": {"target": "independent memberships of the continuous synthetic score, not label centroids",
                      "bestEpoch": gradeModel.bestEpoch, "parameterCount": gradeModel.parameterCount,
                      "validationMse": gradeModel.validationMse, "history": gradeModel.history,
                      "heldOutGradeRmse": math.sqrt(math.fsum(gradeErrors) / len(gradeErrors)),
                      "predictedGradeSumRange": [min(map(sum, gradePredictions)), max(map(sum, gradePredictions))],
                      "weakCoverageProbe": {"inputs": [0.1, 11 / 60], "targetScore": 0.17,
                                            "targetGrades": [float(grade) for grade in codec.EncodeMemberships(0.17)], "predictedGrades": weakGrades}},
        "slice": {"exposure": 0.5, "severity": [item.severity for item in sliceRows], "latentScores": [item.score for item in sliceRows],
                  "centroidTargets": [representatives[SelectedLabel(codec, item.score)] for item in sliceRows]},
        "probeInputs": [(item.severity, item.exposure) for item in probeRows],
        "outOfDomainExamples": [InterpretPrediction(codec, value) for value in (-0.05, 1.05)],
        "informationLoss": {"inputs": [(item.severity, item.exposure) for item in collisionRows],
                            "centroidFeatures": EncodeFeatures(collisionRows, "centroid", codec),
                            "targetLabels": [SelectedLabel(codec, item.score) for item in collisionRows],
                            "fullMembershipFeatures": EncodeFeatures(collisionRows, "memberships", codec)},
    }


def VerifyInstalledPackage() -> None:
    """Require matching distribution metadata and a non-editable site-packages import."""

    try:
        distribution = importlib.metadata.distribution("fuzzyroutines")

    except importlib.metadata.PackageNotFoundError as error:
        raise RuntimeError("installed smoke requires an installed fuzzyroutines distribution") from error

    origin = Path(fuzzyroutines.__file__).resolve()
    expected = Path(distribution.locate_file("fuzzyroutines/__init__.py")).resolve()
    packageRoots = {Path(sysconfig.get_path(name)).resolve() for name in ("purelib", "platlib")}

    if origin != expected or not any(origin.is_relative_to(root) for root in packageRoots):
        raise RuntimeError("installed smoke resolved a source checkout or editable package")


def Main(arguments=None) -> int:
    """Write deterministic experiment JSON to stdout and optionally to a file.

    Args:
        arguments: CLI arguments; `None` reads current process arguments.

    Returns:
        Zero after a finite complete experiment report.

    Raises:
        RuntimeError: Installed verification resolves source or editable code,
            or distribution metadata does not match the imported package.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--epochs", type=int, default=400)
    parser.add_argument("--samples", type=int, default=600)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-installed", action="store_true", dest="verifyInstalled")
    options = parser.parse_args(arguments)

    if options.verifyInstalled:
        VerifyInstalledPackage()

    report = RunExperiment(seed=options.seed, epochs=options.epochs, sampleCount=options.samples)
    serialized = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"

    if options.output is not None:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(serialized, encoding="utf-8")

    print(serialized, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
