# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Typed snapshots of validated v1 JSON and YAML projects."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from ._config_project import DecodeProject, _ConfiguredProject
from .configuration import ModelConfiguration
from .yaml_configuration import _RequireYaml


@dataclass(frozen=True, slots=True)
class ProjectDefaults:
    """Explicit selections for one named model, plot and evaluation."""

    modelId: str
    plotId: str | None
    evaluationId: str | None


@dataclass(frozen=True, slots=True)
class ProjectPlot:
    """Presentation settings bound to one named model and scale."""

    modelId: str
    scaleId: str
    title: str | None
    xLabel: str | None
    termColors: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class ProjectEvaluation:
    """Input coordinates and trace choice for one unevaluated scenario."""

    modelId: str
    inputs: Mapping[str, float]
    trace: bool


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    """Read-only named models and project settings produced by loading."""

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
