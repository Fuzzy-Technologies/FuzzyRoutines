# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Offline structural validation of v1 configuration data.

The schema comes from the caller's trusted local resource. Draft 2020-12
validation uses the design toolchain and a registry without a remote
retriever. The original wire tree remains intact for semantic validation.
"""

import importlib
from collections.abc import Mapping
from typing import Any, Self

from ._config_envelope import CheckConfigEnvelope, ConfigEnvelopeError
from ._config_json import ConfigPath, JsonNumber, JsonValue


class _SchemaNumber(float):
    """Binary64 schema view with an exact source token for integer checks."""

    wire: JsonNumber

    def __new__(cls, wire: JsonNumber) -> Self:
        """Wrap the validated binary64 value and retain its source number."""

        number = super().__new__(cls, wire.binary64)
        number.wire = wire

        return number


type _SchemaValue = None | bool | str | _SchemaNumber | list[_SchemaValue] | dict[str, _SchemaValue]


def _SchemaView(value: JsonValue) -> _SchemaValue:
    """Project wire numbers to binary64 while retaining token provenance."""

    if isinstance(value, JsonNumber):
        return _SchemaNumber(value)

    if isinstance(value, dict):
        return {key: _SchemaView(value[key]) for key in sorted(value)}

    if isinstance(value, list):
        return [_SchemaView(item) for item in value]

    return value


def _IsExactSchemaInteger(checker: object, value: object) -> bool:
    """Test integrality before binary64 rounding can erase a fraction."""

    if isinstance(value, _SchemaNumber):
        exact = value.wire.ExactDecimal()

        return exact == exact.to_integral_value()

    return type(value) is int


def _VariantErrorPath(error: Any, path: ConfigPath) -> ConfigPath:
    """Diagnose the chosen kind or family rather than unrelated variants."""

    if not isinstance(error.instance, dict):
        return path

    for index, alternative in enumerate(error.schema["oneOf"]):
        for field in ("kind", "family"):
            tag = alternative.get("properties", {}).get(field, {}).get("const")

            if isinstance(tag, str) and error.instance.get(field) == tag:
                for candidate in error.context:
                    if candidate.schema_path[0] == index:
                        return _SchemaErrorPath(candidate)

    for alternative in error.schema["oneOf"]:
        for field in ("kind", "family"):
            if "const" in alternative.get("properties", {}).get(field, {}):
                return (*path, field)

    return path


def _SchemaErrorPath(error: Any) -> ConfigPath:
    """Locate an offending value or property without parsing library messages."""

    path: ConfigPath = tuple(error.absolute_path)

    if "propertyNames" in error.schema_path and isinstance(error.instance, str):
        return (*path, error.instance)

    if error.validator == "oneOf":
        return _VariantErrorPath(error, path)

    if error.validator == "required":
        return (*path, next(field for field in error.validator_value if field not in error.instance))

    if error.validator == "additionalProperties" and error.validator_value is False:
        extra = sorted(error.instance.keys() - error.schema["properties"].keys())

        return (*path, extra[0])

    return path


def CheckConfigStructure(document: JsonValue, schema: Mapping[str, object]) -> None:
    """Validate all descendants against the selected local v1 schema.

    Args:
        document: Complete wire value returned by the bounded JSON parser.
        schema: Trusted Draft 2020-12 v1 schema data supplied by the caller.

    Raises:
        ConfigEnvelopeError: Dispatch or structural validation rejects the data.
        ImportError: The private Draft 2020-12 validation toolchain is unavailable.
    """

    kind = CheckConfigEnvelope(document, schema)
    selectedSchema = {key: value for key, value in schema.items() if key != "oneOf"}
    selectedSchema["$ref"] = f"#/$defs/{kind}"

    # Use the same validator and offline registry as the schema design fixture.
    jsonSchema = importlib.import_module("jsonschema")
    registry = importlib.import_module("referencing").Registry()
    baseValidator = jsonSchema.Draft202012Validator
    checker = baseValidator.TYPE_CHECKER.redefine("integer", _IsExactSchemaInteger)
    validator = jsonSchema.validators.extend(baseValidator, type_checker=checker)
    issue = next(validator(selectedSchema, registry=registry).iter_errors(_SchemaView(document)), None)

    if issue is not None:
        raise ConfigEnvelopeError(
            "invalid-shape",
            _SchemaErrorPath(issue),
            "Configuration data does not satisfy the selected v1 schema.",
        )
