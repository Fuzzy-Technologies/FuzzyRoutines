# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Explicit JSON and YAML byte conversions for validated v1 projects.

Install `fuzzyroutines[config,yaml]` to perform conversions. File access and
format selection belong to the caller. Importing this module leaves the
optional parser and schema validator unloaded.
"""

from importlib.util import find_spec as FindSpec

__all__ = ["ConvertProjectJsonToYaml", "ConvertProjectYamlToJson"]


def _RequireYaml() -> None:
    """Report the optional installation before importing its implementation."""

    if FindSpec("yaml") is None:
        raise ImportError("Install fuzzyroutines[config,yaml] to convert YAML projects.")


def ConvertProjectJsonToYaml(encoded: bytes) -> bytes:
    """Validate a v1 JSON project and convert it to deterministic block YAML.

    Args:
        encoded: One bounded UTF-8 v1 JSON project.

    Returns:
        UTF-8 block YAML with exact number tokens, sorted mappings, preserved
        array order, and a final LF.

    Raises:
        ConfigurationError: Parsing or shared v1 validation fails, or the output exceeds the limit.
        ImportError: An optional parser or schema dependency is unavailable.
    """

    _RequireYaml()
    from ._config_yaml import ConvertProjectJsonToYaml as EncodeProjectYaml

    return EncodeProjectYaml(encoded)


def ConvertProjectYamlToJson(encoded: bytes) -> bytes:
    """Validate a v1 YAML project and convert it to deterministic compact JSON.

    Args:
        encoded: One bounded UTF-8 v1 YAML project in the strict data subset.

    Returns:
        UTF-8 JSON with exact number tokens, sorted mappings, preserved
        array order, and a final LF.

    Raises:
        ConfigurationError: Parsing or shared v1 validation fails, or the output exceeds the limit.
        ImportError: An optional parser or schema dependency is unavailable.
    """

    _RequireYaml()
    from ._config_yaml import ConvertProjectYamlToJson as EncodeProjectJson

    return EncodeProjectJson(encoded)
