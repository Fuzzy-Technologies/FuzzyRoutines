# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Shared scoped bindings for scalar inference in v1 model envelopes."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from ._config_json import ConfigPath, DecodeConfigJson
from ._config_scale_model import (
    ScaleDefinition,
    ScaleModelDecodeError,
    _Object,
    _Real,
    _ScaleModel,
)
from ._config_schema import ReadConfigV1Schema
from ._config_structure import CheckConfigStructure
from .inference import (
    AllOf,
    Antecedent,
    AnyOf,
    FuzzyVariable,
    InferencePolicy,
    NotCondition,
    TermCondition,
)
from .operators import NegationPolicy, SNormPolicy, TNormPolicy


@dataclass(frozen=True, slots=True)
class _InputBinding:
    """One wire input ID's scale, exact variable name and scoped term names."""

    variable: FuzzyVariable
    scaleId: str
    termNamesById: Mapping[str, str]


def _DeclareIdentity(
    definition: _Object, knownIds: set[str], knownNames: set[str], path: ConfigPath, namespace: str,
) -> tuple[str, str]:
    """Read an ordered declaration with unique exact IDs and nonblank names."""

    identifier = cast(str, definition["id"])
    name = cast(str, definition["name"])

    if identifier in knownIds:
        raise ScaleModelDecodeError("duplicate-id", (*path, "id"), f"Repeated {namespace} ID {identifier!r}.")

    if not name.strip():
        raise ScaleModelDecodeError("invalid-value", (*path, "name"), f"The {namespace} name must be nonblank.")

    if name in knownNames:
        raise ScaleModelDecodeError("duplicate-name", (*path, "name"), f"Repeated {namespace} name {name!r}.")

    knownIds.add(identifier)
    knownNames.add(name)

    return identifier, name


def _ResolveScale(scaleId: str, definitions: _ScaleModel, path: ConfigPath) -> ScaleDefinition:
    """Resolve a scale by its exact local model ID."""

    if scaleId not in definitions.scales:
        raise ScaleModelDecodeError("unresolved-reference", path, f"Unknown model scale ID {scaleId!r}.")

    return definitions.scales[scaleId]


def _TermNames(scale: ScaleDefinition) -> dict[str, str]:
    """Index exact runtime term names by the IDs of this scale only."""

    return {termId: term.name for termId, term in zip(scale.termIds, scale.scale.terms, strict=True)}


def _BindInputs(inputs: list[_Object], definitions: _ScaleModel, path: ConfigPath) -> dict[str, _InputBinding]:
    """Bind variable IDs to exact names and term scopes in declaration order."""

    knownIds: set[str] = set()
    knownNames: set[str] = set()
    bindings = {}
    termMaps: dict[str, dict[str, str]] = {}

    for index, definition in enumerate(inputs):
        inputPath = (*path, index)
        inputId, name = _DeclareIdentity(definition, knownIds, knownNames, inputPath, "input")
        scaleId = cast(str, definition["scale"])
        scale = _ResolveScale(scaleId, definitions, (*inputPath, "scale"))

        if scaleId not in termMaps:
            termMaps[scaleId] = _TermNames(scale)

        bindings[inputId] = _InputBinding(FuzzyVariable(name, scale.scale.terms), scaleId, termMaps[scaleId])

    return bindings


def _ResolveInput(inputId: str, bindings: Mapping[str, _InputBinding], path: ConfigPath) -> _InputBinding:
    """Resolve an input ID in this inference definition only."""

    if inputId not in bindings:
        raise ScaleModelDecodeError("unresolved-reference", path, f"Unknown inference input ID {inputId!r}.")

    return bindings[inputId]


def _BindAntecedent(definition: _Object, bindings: Mapping[str, _InputBinding], path: ConfigPath) -> Antecedent:
    """Translate a bounded ordered expression to typed scalar conditions."""

    kind = definition["kind"]

    if kind == "term":
        inputId = cast(str, definition["input"])
        binding = _ResolveInput(inputId, bindings, (*path, "input"))
        termId = cast(str, definition["term"])

        if termId not in binding.termNamesById:
            raise ScaleModelDecodeError(
                "unresolved-reference", (*path, "term"), f"Unknown term ID {termId!r} for input ID {inputId!r}.",
            )

        return TermCondition(binding.variable.name, binding.termNamesById[termId])

    if kind == "not":
        return NotCondition(_BindAntecedent(cast(_Object, definition["operand"]), bindings, (*path, "operand")))

    operands = tuple(
        _BindAntecedent(operand, bindings, (*path, "operands", index))
        for index, operand in enumerate(cast(list[_Object], definition["operands"]))
    )

    return AllOf(operands) if kind == "all" else AnyOf(operands)


def _DecodePolicy(definition: _Object) -> InferencePolicy:
    """Reconstruct all explicit antecedent logic operator policies."""

    negation = cast(_Object, definition["negation"])

    return InferencePolicy(
        TNormPolicy(cast(str, definition["conjunction"])),
        SNormPolicy(cast(str, definition["disjunction"])),
        NegationPolicy(cast(str, negation["family"]), _Real(negation["alpha"]) if "alpha" in negation else None),
    )


def _ReadStandaloneInference(encoded: bytes, kind: str) -> tuple[_Object, _Object]:
    """Read a structurally valid standalone model of the requested inference kind."""

    wire = DecodeConfigJson(encoded)
    CheckConfigStructure(wire, ReadConfigV1Schema())
    document = cast(_Object, wire)

    if document["kind"] != "model":
        raise ScaleModelDecodeError("unsupported-model", ("kind",), "Expected a standalone model.")

    inference = cast(_Object, document.get("inference"))

    if not inference or inference["kind"] != kind:
        raise ScaleModelDecodeError("unsupported-model", ("inference",), f"Expected {kind} inference.")

    return document, inference
