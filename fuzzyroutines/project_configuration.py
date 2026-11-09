# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Load and save self-contained v1 fuzzy projects in JSON or strict YAML."""

from typing import Literal

from ._config_project import DecodeProject
from ._project_snapshot import (
    LoadProjectJson,
    LoadProjectYaml,
    ProjectDefaults,
    ProjectEvaluation,
    ProjectPlot,
    ProjectSnapshot,
    _EncodeProjectBytes,
)
from .yaml_configuration import ConvertProjectJsonToYaml

__all__ = [
    "DumpProject",
    "LoadProject",
    "ProjectDefaults",
    "ProjectEvaluation",
    "ProjectPlot",
    "ProjectSnapshot",
]


def LoadProject(encoded: bytes, *, formatName: Literal["json", "yaml"] = "json") -> ProjectSnapshot:
    """Reconstruct named models and settings from one bounded v1 project.

    Args:
        encoded: UTF-8 project bytes in the selected format.
        formatName: Explicit input codec. JSON is the default.

    Returns:
        A read-only snapshot with explicit defaults and unevaluated scenarios.

    Raises:
        ConfigurationError: The document fails parsing or offline v1 validation.
        ImportError: A required optional configuration or YAML extra is missing.
        ValueError: The selected format is unsupported.
    """

    if formatName == "json":
        return LoadProjectJson(encoded)

    if formatName == "yaml":
        return LoadProjectYaml(encoded)

    raise ValueError("Choose project format 'json' or 'yaml'.")


def DumpProject(project: ProjectSnapshot, *, formatName: Literal["json", "yaml"] = "json") -> bytes:
    """Export a portable project without reading files or evaluating scenarios.

    Args:
        project: A validated snapshot obtained by loading a v1 project.
        formatName: Explicit output codec. JSON is the default.

    Returns:
        Validated, deterministic UTF-8 bytes with a final line feed.

    Raises:
        ConfigurationError: The snapshot cannot be represented as a valid v1 project.
        ImportError: A required optional configuration or YAML extra is missing.
        ValueError: The selected format is unsupported.
    """

    if formatName == "json":
        encoded = _EncodeProjectBytes(project)
        DecodeProject(encoded)

        return encoded

    if formatName == "yaml":
        return ConvertProjectJsonToYaml(_EncodeProjectBytes(project))

    raise ValueError("Choose project format 'json' or 'yaml'.")
