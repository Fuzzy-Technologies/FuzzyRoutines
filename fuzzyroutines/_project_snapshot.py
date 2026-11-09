# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Typed snapshots of validated v1 JSON and YAML projects."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from ._config_export import _Binary64, _EncodeJsonBytes, _EncodeModel, _Object
from ._config_project import DecodeProject, _ConfiguredProject
from .configuration import ModelConfiguration
from .yaml_configuration import _RequireYaml


@dataclass(frozen=True, slots=True)
class ProjectDefaults:
    """Explicit selections for one named model, plot and evaluation.

    Attributes:
        modelId: Exact default model ID.
        plotId: Default plot ID when declared.
        evaluationId: Default evaluation ID when declared.
    """

    modelId: str
    plotId: str | None
    evaluationId: str | None


@dataclass(frozen=True, slots=True)
class ProjectPlot:
    """Presentation settings bound to one named model and scale.

    Attributes:
        modelId: Exact model ID in the project.
        scaleId: Exact scale ID in the selected model.
        title: Optional display title.
        xLabel: Optional horizontal-axis label.
        termColors: Opaque color overrides keyed by exact term ID.
    """

    modelId: str
    scaleId: str
    title: str | None
    xLabel: str | None
    termColors: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class ProjectEvaluation:
    """Input coordinates and trace choice for one unevaluated scenario.

    Attributes:
        modelId: Exact model ID in the project.
        inputs: Finite coordinates keyed by the model's wire input IDs.
        trace: Whether the scenario requests a trace when evaluated explicitly.
    """

    modelId: str
    inputs: Mapping[str, float]
    trace: bool


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    """Read-only named models and project settings produced by loading.

    Attributes:
        models: Standalone configurations keyed by exact project model ID.
        defaults: Explicit selections, if declared in the source document.
        units: Display labels keyed by model ID and then local universe ID.
        plots: Presentation settings keyed by plot ID.
        evaluations: Unevaluated scenarios keyed by evaluation ID.
    """

    models: Mapping[str, ModelConfiguration]
    defaults: ProjectDefaults | None
    units: Mapping[str, Mapping[str, str]]
    plots: Mapping[str, ProjectPlot]
    evaluations: Mapping[str, ProjectEvaluation]

    def SelectModel(self, modelId: str | None = None) -> ModelConfiguration:
        """Select an exact model ID or use the declared model default.

        Raises:
            KeyError: The ID is unknown or no model default was declared.
        """

        if modelId is None:
            if self.defaults is None:
                raise KeyError("An explicit project model ID is required.")

            modelId = self.defaults.modelId

        return self.models[modelId]


def LoadProjectJson(encoded: bytes) -> ProjectSnapshot:
    """Load a complete v1 JSON project without accessing files or evaluating models.

    Args:
        encoded: One bounded UTF-8 project document.

    Returns:
        A read-only snapshot of models, defaults, units, plots and evaluations.

    Raises:
        ConfigurationError: Project parsing or validation fails.
        ImportError: The optional configuration validator is unavailable.
    """

    return _BuildProjectSnapshot(DecodeProject(encoded))


def LoadProjectYaml(encoded: bytes) -> ProjectSnapshot:
    """Load a complete v1 YAML project without accessing files or evaluating models.

    Args:
        encoded: One bounded UTF-8 project document in the strict YAML subset.

    Returns:
        A read-only snapshot of models, defaults, units, plots and evaluations.

    Raises:
        ConfigurationError: Project parsing or validation fails.
        ImportError: The optional YAML parser or configuration validator is unavailable.
    """

    _RequireYaml()
    from ._config_yaml import DecodeYamlProject

    return _BuildProjectSnapshot(DecodeYamlProject(encoded))


def _BuildProjectSnapshot(project: _ConfiguredProject) -> ProjectSnapshot:
    """Wrap validated project bindings in the same snapshot for both codecs."""

    defaults = project.defaults
    selection = None if defaults is None else ProjectDefaults(
        defaults.modelId, defaults.plotId, defaults.evaluationId,
    )
    models = MappingProxyType({modelId: ModelConfiguration(model) for modelId, model in project.models.items()})
    plots = MappingProxyType({
        plotId: ProjectPlot(plot.modelId, plot.scaleId, plot.title, plot.xLabel, plot.termColors)
        for plotId, plot in project.plots.items()
    })
    evaluations = MappingProxyType({
        evaluationId: ProjectEvaluation(evaluation.modelId, evaluation.inputs, evaluation.trace)
        for evaluationId, evaluation in project.evaluations.items()
    })

    return ProjectSnapshot(models, selection, project.units, plots, evaluations)


def _EncodePlot(plot: ProjectPlot) -> _Object:
    """Preserve explicit plot settings while omitting absent optional fields."""

    wire: _Object = {"model": plot.modelId, "scale": plot.scaleId}

    if plot.title is not None:
        wire["title"] = plot.title

    if plot.xLabel is not None:
        wire["xLabel"] = plot.xLabel

    if plot.termColors:
        wire["termColors"] = {termId: color for termId, color in plot.termColors.items()}

    return wire


def _EncodeProjectBytes(project: ProjectSnapshot) -> bytes:
    """Encode an entire project for validation without evaluating its models."""

    wire: _Object = {
        "kind": "project",
        "schemaVersion": 1,
        "models": {
            modelId: _EncodeModel(model._snapshot, ("models", modelId))
            for modelId, model in sorted(project.models.items())
        },
    }
    defaults = project.defaults

    if defaults is not None:
        selection: _Object = {"model": defaults.modelId}

        if defaults.plotId is not None:
            selection["plot"] = defaults.plotId

        if defaults.evaluationId is not None:
            selection["evaluation"] = defaults.evaluationId

        wire["defaults"] = selection

    presentation: _Object = {}

    if project.units:
        presentation["units"] = {
            modelId: {universeId: label for universeId, label in units.items()}
            for modelId, units in project.units.items()
        }

    if project.plots:
        presentation["plots"] = {plotId: _EncodePlot(plot) for plotId, plot in project.plots.items()}

    if presentation:
        wire["presentation"] = presentation

    if project.evaluations:
        wire["evaluations"] = {
            evaluationId: {
                "model": evaluation.modelId,
                "inputs": {
                    inputId: _Binary64(value, ("evaluations", evaluationId, "inputs", inputId))
                    for inputId, value in sorted(evaluation.inputs.items())
                },
                "trace": evaluation.trace,
            }
            for evaluationId, evaluation in sorted(project.evaluations.items())
        }

    return _EncodeJsonBytes(wire)
