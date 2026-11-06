# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Offline envelope dispatch and structural preflight for configuration v1.

The caller supplies the trusted local schema separately from the wire document.
This stage selects and checks root and inline envelopes. Full descendant schema
validation and semantic reconstruction run in later stages.
"""

from collections.abc import Mapping
from typing import Literal, cast

from ._config_json import (
    ConfigPath,
    ConfigPointer,
    ConfigurationError,
    JsonNumber,
    JsonValue,
)

type _EnvelopeKind = Literal["model", "project"]
type _Category = Literal["invalid-shape", "unsupported-kind", "unsupported-version"]


class ConfigEnvelopeError(ConfigurationError):
    """Configuration envelope rejection with stable category and JSON Pointer."""

    def __init__(self, category: _Category, path: ConfigPath, message: str) -> None:
        """Retain the normalized diagnostic independently of schema wording."""

        super().__init__(message, category=category, pointer=ConfigPointer(path))


def _SelectEnvelope(document: JsonValue, path: ConfigPath, *, inline: bool) -> _EnvelopeKind:
    """Select an allowed kind and verify the exact mathematical version."""

    if not isinstance(document, dict):
        raise ConfigEnvelopeError("invalid-shape", path, "Expected a configuration object.")

    kind = document.get("kind")

    if not isinstance(kind, str):
        raise ConfigEnvelopeError("invalid-shape", (*path, "kind"), "Expected a string envelope kind.")

    if kind != "model" and (kind != "project" or inline):
        raise ConfigEnvelopeError("unsupported-kind", (*path, "kind"), "Unsupported envelope kind.")

    version = document.get("schemaVersion")
    versionPath = (*path, "schemaVersion")

    if not isinstance(version, JsonNumber):
        raise ConfigEnvelopeError("invalid-shape", versionPath, "Expected an integral schema version.")

    exactVersion = version.ExactDecimal()

    if exactVersion != exactVersion.to_integral_value():
        raise ConfigEnvelopeError("invalid-shape", versionPath, "Expected an integral schema version.")

    if exactVersion != 1:
        raise ConfigEnvelopeError("unsupported-version", versionPath, "Unsupported schema version.")

    return cast(_EnvelopeKind, kind)


def _LocalShape(value: object) -> Mapping[str, object]:
    """Read a trusted schema object or fail on an invalid local schema."""

    if not isinstance(value, dict):
        raise TypeError("The local configuration schema lacks an object definition.")

    return cast(Mapping[str, object], value)


def _ResolveLocalShape(value: object, definitions: Mapping[str, object]) -> Mapping[str, object]:
    """Resolve at most one internal definition reference used by envelope fields."""

    shape = _LocalShape(value)
    reference = shape.get("$ref")

    if reference is None:
        return shape

    if not isinstance(reference, str) or not reference.startswith("#/$defs/"):
        raise ValueError("Configuration envelope preflight requires internal schema references.")

    return _LocalShape(definitions.get(reference.removeprefix("#/$defs/")))


def _CheckEnvelopeShape(
    document: dict[str, JsonValue],
    kind: _EnvelopeKind,
    definitions: Mapping[str, object],
    path: ConfigPath,
) -> None:
    """Check the selected schema's closed envelope and immediate object fields."""

    shape = _LocalShape(definitions.get(kind))
    fields = _LocalShape(shape.get("properties"))
    required = shape.get("required")

    if not isinstance(required, list) or shape.get("additionalProperties") is not False:
        raise ValueError("The local configuration schema lacks a closed envelope definition.")

    for field in required:
        if field not in document:
            raise ConfigEnvelopeError("invalid-shape", (*path, field), "Missing required envelope field.")

    for field in sorted(document):
        fieldPath = (*path, field)

        if field not in fields:
            raise ConfigEnvelopeError("invalid-shape", fieldPath, "Unknown envelope field.")

        fieldShape = _ResolveLocalShape(fields[field], definitions)
        alternatives = fieldShape.get("oneOf")
        requiresObject = fieldShape.get("type") == "object" or (
            isinstance(alternatives, list) and bool(alternatives)
            and all(_LocalShape(alternative).get("type") == "object" for alternative in alternatives)
        )

        if requiresObject:
            value = document[field]

            if not isinstance(value, dict):
                raise ConfigEnvelopeError("invalid-shape", fieldPath, "Expected an object envelope field.")

            minimum = fieldShape.get("minProperties")

            if isinstance(minimum, int) and len(value) < minimum:
                raise ConfigEnvelopeError("invalid-shape", fieldPath, "Too few entries in envelope field.")


def CheckConfigEnvelope(document: JsonValue, schema: Mapping[str, object]) -> _EnvelopeKind:
    """Dispatch root and inline configuration envelopes and check their outer shape.

    Args:
        document: Complete wire value returned by the bounded JSON parser.
        schema: Trusted v1 schema data loaded locally by the caller.

    Returns:
        The root kind used to select subsequent full validation. The wire
        document remains available with its original numeric tokens.

    Raises:
        ConfigEnvelopeError: The wire value fails envelope dispatch or preflight.
        TypeError: A required local schema object is missing.
        ValueError: A required local schema definition is invalid.
    """

    kind = _SelectEnvelope(document, (), inline=False)
    assert isinstance(document, dict), "Successful dispatch requires an object."
    definitions = _LocalShape(schema.get("$defs"))
    models = document.get("models")
    inlineModels: list[tuple[ConfigPath, dict[str, JsonValue]]] = []

    if kind == "project" and isinstance(models, dict):
        for modelId, model in sorted(models.items()):
            path: ConfigPath = ("models", modelId)
            _SelectEnvelope(model, path, inline=True)
            assert isinstance(model, dict), "Successful inline dispatch requires an object."
            inlineModels.append((path, model))

    _CheckEnvelopeShape(document, kind, definitions, ())

    for path, model in inlineModels:
        _CheckEnvelopeShape(model, "model", definitions, path)

    return kind
