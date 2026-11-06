# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private v1 project reconstruction without plotting or evaluating models."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import cast

from ._config_inference import _ResolveScale
from ._config_json import ConfigPath, DecodeConfigJson, JsonValue
from ._config_mamdani_model import _ConfiguredMamdani, _DecodeMamdani
from ._config_scale_model import (
    ScaleModelDecodeError,
    _DecodeDefinitions,
    _Object,
    _Real,
    _ScaleModel,
)
from ._config_schema import ReadConfigV1Schema
from ._config_structure import CheckConfigStructure
from ._config_sugeno_model import _ConfiguredSugeno, _DecodeSugeno

type _ProjectModel = _ScaleModel | _ConfiguredMamdani | _ConfiguredSugeno
type _ModelResult = _ProjectModel | ScaleModelDecodeError


@dataclass(frozen=True, slots=True)
class _ProjectDefaults:
    """Explicit entry IDs for one model and its optional plot and scenario."""

    modelId: str
    plotId: str | None
    evaluationId: str | None


@dataclass(frozen=True, slots=True)
class _ProjectPlot:
    """Display metadata scoped to a selected scale, with partial term colors."""

    modelId: str
    scaleId: str
    title: str | None
    xLabel: str | None
    termColors: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class _ProjectEvaluation:
    """Unevaluated in-universe coordinates keyed by exact wire input IDs."""

    modelId: str
    inputs: Mapping[str, float]
    trace: bool


@dataclass(frozen=True, slots=True)
class _ConfiguredProject:
    """Inline models with separately owned presentation and evaluation data."""

    models: Mapping[str, _ProjectModel]
    defaults: _ProjectDefaults | None
    units: Mapping[str, Mapping[str, str]]
    plots: Mapping[str, _ProjectPlot]
    evaluations: Mapping[str, _ProjectEvaluation]


def _Section(definition: _Object, key: str) -> _Object:
    """Read an optional object section after complete structural validation."""

    return cast(_Object, definition.get(key, {}))


def _RequireId(identifier: str, scope: Mapping[str, object], path: ConfigPath, namespace: str) -> None:
    """Require an exact ID in the indicated local namespace."""

    if identifier not in scope:
        raise ScaleModelDecodeError("unresolved-reference", path, f"Unknown {namespace} ID {identifier!r}.")


def _ReadLabel(label: str, path: ConfigPath) -> str:
    """Preserve exact Unicode spelling while rejecting all-whitespace labels."""

    if not label.strip():
        raise ScaleModelDecodeError("invalid-value", path, "A display label must be nonblank.")

    return label


def _BindDefaults(
    defaults: _Object, models: _Object, plots: _Object, evaluations: _Object,
) -> _ProjectDefaults:
    """Check explicit defaults against declared entries and their shared model."""

    modelId = cast(str, defaults["model"])

    for field, scope in (("evaluation", evaluations), ("model", models), ("plot", plots)):
        if field not in defaults:
            continue

        identifier = cast(str, defaults[field])
        path = ("defaults", field)
        _RequireId(identifier, scope, path, f"project {field}")

        if field != "model" and cast(_Object, scope[identifier])["model"] != modelId:
            raise ScaleModelDecodeError(
                "invalid-relationship", path, f"The default {field} must select model ID {modelId!r}.",
            )

    return _ProjectDefaults(modelId, cast(str | None, defaults.get("plot")), cast(str | None, defaults.get("evaluation")))


def _BindModel(document: _Object, path: ConfigPath) -> _ModelResult:
    """Build one model, deferring its error until earlier project fields are checked."""

    inference = _Section(document, "inference")

    try:
        if not inference:
            return _DecodeDefinitions(document, path)

        if inference["kind"] == "mamdani":
            return _DecodeMamdani(document, inference, path)

        return _DecodeSugeno(document, inference, path)

    except ScaleModelDecodeError as error:
        return error


def _BindEvaluation(
    definition: _Object, models: Mapping[str, _ModelResult], path: ConfigPath,
) -> _ProjectEvaluation | None:
    """Bind a scenario to exactly its selected inference inputs without running it."""

    modelId = cast(str, definition["model"])
    modelPath = (*path, "model")
    _RequireId(modelId, models, modelPath, "project model")
    model = models[modelId]

    if isinstance(model, ScaleModelDecodeError):
        # Input membership depends on the selected model's valid geometry.
        return None

    if isinstance(model, _ScaleModel):
        raise ScaleModelDecodeError("invalid-relationship", modelPath, "A scenario requires a model with inference.")

    coordinates = _Section(definition, "inputs")
    inputVariables = dict(zip(model.inputIds, model.model.inputs, strict=True))
    inputs = {}

    for inputId in sorted(coordinates.keys() | inputVariables.keys()):
        inputPath = (*path, "inputs", inputId)
        _RequireId(inputId, inputVariables, inputPath, f"input of model {modelId!r}")

        if inputId not in coordinates:
            raise ScaleModelDecodeError("invalid-value", inputPath, f"Missing coordinate for input ID {inputId!r}.")

        coordinate = _Real(coordinates[inputId])

        if not inputVariables[inputId].terms[0].fuzzySet.universe.Contains(coordinate):
            raise ScaleModelDecodeError("invalid-value", inputPath, "The coordinate is outside its input universe.")

        inputs[inputId] = coordinate

    return _ProjectEvaluation(modelId, MappingProxyType(inputs), cast(bool, definition["trace"]))


def _Definitions(model: _ProjectModel) -> _ScaleModel:
    """Return model-local scales and universes for any inline variant."""

    return model if isinstance(model, _ScaleModel) else model.definitions


def _BindPlots(plots: _Object, models: Mapping[str, _ProjectModel]) -> dict[str, _ProjectPlot]:
    """Validate each display override against the selected model and scale IDs."""

    bindings = {}
    termIdsByScale: dict[tuple[str, str], set[str]] = {}

    for plotId, rawDefinition in sorted(plots.items()):
        path = ("presentation", "plots", plotId)
        definition = cast(_Object, rawDefinition)
        modelId = cast(str, definition["model"])
        _RequireId(modelId, models, (*path, "model"), "project model")
        scaleId = cast(str, definition["scale"])
        scale = _ResolveScale(scaleId, _Definitions(models[modelId]), (*path, "scale"))
        colors = cast(dict[str, str], _Section(definition, "termColors"))

        if colors:
            scaleKey = (modelId, scaleId)

            if scaleKey not in termIdsByScale:
                termIdsByScale[scaleKey] = set(scale.termIds)

            for termId in sorted(colors):
                if termId not in termIdsByScale[scaleKey]:
                    raise ScaleModelDecodeError(
                        "unresolved-reference", (*path, "termColors", termId),
                        f"Unknown term ID {termId!r} for scale ID {scaleId!r} in model ID {modelId!r}.",
                    )

        title = _ReadLabel(cast(str, definition["title"]), (*path, "title")) if "title" in definition else None
        xLabel = _ReadLabel(cast(str, definition["xLabel"]), (*path, "xLabel")) if "xLabel" in definition else None
        bindings[plotId] = _ProjectPlot(modelId, scaleId, title, xLabel, MappingProxyType(colors))

    return bindings


def _BindUnits(units: _Object, models: Mapping[str, _ProjectModel]) -> dict[str, Mapping[str, str]]:
    """Bind display unit labels to universe IDs local to their named model."""

    bindings: dict[str, Mapping[str, str]] = {}

    for modelId, rawLabels in sorted(units.items()):
        path = ("presentation", "units", modelId)
        _RequireId(modelId, models, path, "project model")
        universes = _Definitions(models[modelId]).universes
        labels = {}

        for universeId, rawLabel in sorted(cast(_Object, rawLabels).items()):
            labelPath = (*path, universeId)
            _RequireId(universeId, universes, labelPath, f"universe of model {modelId!r}")
            labels[universeId] = _ReadLabel(cast(str, rawLabel), labelPath)

        bindings[modelId] = MappingProxyType(labels)

    return bindings


def DecodeProject(encoded: bytes) -> _ConfiguredProject:
    """Decode a v1 project with inline models, explicit selections and scenarios.

    Args:
        encoded: One bounded UTF-8 configuration document.

    Returns:
        Immutable named models and bound settings, with no executed scenarios.

    Raises:
        ValueError: Parsing, structural or semantic validation fails.
    """

    return _DecodeProjectData(DecodeConfigJson(encoded))


def _DecodeProjectData(wire: JsonValue) -> _ConfiguredProject:
    """Validate a parsed v1 wire tree and reconstruct its unevaluated project."""

    CheckConfigStructure(wire, ReadConfigV1Schema())
    document = cast(_Object, wire)

    if document["kind"] != "project":
        raise ScaleModelDecodeError("unsupported-model", ("kind",), "Expected a project envelope.")

    presentation = _Section(document, "presentation")
    models = _Section(document, "models")
    plots = _Section(presentation, "plots")
    evaluations = _Section(document, "evaluations")
    defaults = _BindDefaults(_Section(document, "defaults"), models, plots, evaluations) if "defaults" in document else None
    candidates = {
        key: _BindModel(cast(_Object, definition), ("models", key))
        for key, definition in sorted(models.items())
    }
    boundEvaluations = {}

    for key, definition in sorted(evaluations.items()):
        evaluation = _BindEvaluation(cast(_Object, definition), candidates, ("evaluations", key))

        if evaluation is not None:
            boundEvaluations[key] = evaluation

    boundModels = {}

    for key, candidate in candidates.items():
        if isinstance(candidate, ScaleModelDecodeError):
            raise candidate

        boundModels[key] = candidate

    boundPlots = _BindPlots(plots, boundModels)
    boundUnits = _BindUnits(_Section(presentation, "units"), boundModels)

    return _ConfiguredProject(
        MappingProxyType(boundModels), defaults, MappingProxyType(boundUnits),
        MappingProxyType(boundPlots), MappingProxyType(boundEvaluations),
    )
