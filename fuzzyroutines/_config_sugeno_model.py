# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private reconstruction of standalone v1 Sugeno models."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from ._config_json import ConfigPath, DecodeConfigJson
from ._config_scale_model import (
    ScaleModelDecodeError,
    _DecodeDefinitions,
    _Object,
    _Real,
    _ScaleModel,
)
from ._config_schema import ReadConfigV1Schema
from ._config_structure import CheckConfigStructure
from .domain import ContinuousUniverse
from .inference import (
    AffineConsequent,
    AllOf,
    Antecedent,
    AnyOf,
    ConstantConsequent,
    FuzzyVariable,
    InferencePolicy,
    NotCondition,
    SugenoModel,
    SugenoRule,
    TermCondition,
)
from .operators import NegationPolicy, SNormPolicy, TNormPolicy


@dataclass(frozen=True, slots=True)
class _InputBinding:
    """One wire input ID's scale, exact variable name and scoped term names."""

    variable: FuzzyVariable
    scaleId: str
    termNamesById: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class _ConfiguredSugeno:
    """Immutable runtime model and ordered wire bindings for reconstruction."""

    model: SugenoModel
    definitions: _ScaleModel
    inputIds: tuple[str, ...]
    inputScaleIds: tuple[str, ...]
    ruleIds: tuple[str, ...]
    outputUniverseId: str


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


def _BindInputs(inputs: list[_Object], definitions: _ScaleModel) -> dict[str, _InputBinding]:
    """Bind variable IDs to exact names and term scopes in declaration order."""

    knownIds: set[str] = set()
    knownNames: set[str] = set()
    bindings = {}
    termMaps: dict[str, dict[str, str]] = {}

    for index, definition in enumerate(inputs):
        path = ("inference", "inputs", index)
        inputId, name = _DeclareIdentity(definition, knownIds, knownNames, path, "input")
        scaleId = cast(str, definition["scale"])

        if scaleId not in definitions.scales:
            raise ScaleModelDecodeError(
                "unresolved-reference", (*path, "scale"), f"Unknown model scale ID {scaleId!r}.",
            )

        scale = definitions.scales[scaleId]

        if scaleId not in termMaps:
            termMaps[scaleId] = {
                termId: term.name
                for termId, term in zip(scale.termIds, scale.scale.terms, strict=True)
            }

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


def _BindConsequent(
    definition: _Object,
    bindings: Mapping[str, _InputBinding],
    universe: ContinuousUniverse,
    path: ConfigPath,
) -> ConstantConsequent | AffineConsequent:
    """Bind constant or ordered affine output without evaluating it."""

    if definition["kind"] == "constant":
        value = _Real(definition["value"])

        if not universe.Contains(value):
            raise ScaleModelDecodeError(
                "invalid-value", (*path, "value"), "The constant consequent must belong to the output universe.",
            )

        return ConstantConsequent(value)

    coefficients = []
    knownInputs: set[str] = set()

    for index, coefficient in enumerate(cast(list[_Object], definition["coefficients"])):
        inputId = cast(str, coefficient["input"])
        inputPath = (*path, "coefficients", index, "input")
        binding = _ResolveInput(inputId, bindings, inputPath)

        if inputId in knownInputs:
            raise ScaleModelDecodeError("duplicate-id", inputPath, f"Repeated affine coefficient for input ID {inputId!r}.")

        knownInputs.add(inputId)
        coefficients.append((binding.variable.name, _Real(coefficient["value"])))

    return AffineConsequent(_Real(definition["intercept"]), tuple(coefficients))


def _DecodePolicy(definition: _Object) -> InferencePolicy:
    """Reconstruct all explicit antecedent logic operator policies."""

    negation = cast(_Object, definition["negation"])

    return InferencePolicy(
        TNormPolicy(cast(str, definition["conjunction"])),
        SNormPolicy(cast(str, definition["disjunction"])),
        NegationPolicy(cast(str, negation["family"]), _Real(negation["alpha"]) if "alpha" in negation else None),
    )


def DecodeSugenoModel(encoded: bytes) -> _ConfiguredSugeno:
    """Decode a standalone v1 Sugeno model without evaluating rules or terms.

    Args:
        encoded: One bounded UTF-8 configuration document.

    Returns:
        An immutable Sugeno model with its ordered wire bindings.

    Raises:
        ValueError: The document fails parsing, shape or model semantics,
            or is outside the standalone Sugeno contract.
    """

    wire = DecodeConfigJson(encoded)
    CheckConfigStructure(wire, ReadConfigV1Schema())
    document = cast(_Object, wire)

    if document["kind"] != "model":
        raise ScaleModelDecodeError("unsupported-model", ("kind",), "Expected a standalone model.")

    inference = cast(_Object, document.get("inference"))

    if not inference or inference["kind"] != "sugeno":
        raise ScaleModelDecodeError("unsupported-model", ("inference",), "Expected a Sugeno inference definition.")

    definitions = _DecodeDefinitions(document)
    bindings = _BindInputs(cast(list[_Object], inference["inputs"]), definitions)
    outputId = cast(str, inference["outputUniverse"])
    outputUniverse = definitions.universes.get(outputId)

    if outputUniverse is None:
        raise ScaleModelDecodeError(
            "unresolved-reference", ("inference", "outputUniverse"), f"Unknown model universe ID {outputId!r}.",
        )

    if not isinstance(outputUniverse, ContinuousUniverse):
        raise ScaleModelDecodeError(
            "invalid-value", ("inference", "outputUniverse"), "The Sugeno output universe must be continuous.",
        )

    policy = _DecodePolicy(cast(_Object, inference["policy"]))
    knownRuleIds: set[str] = set()
    knownRuleNames: set[str] = set()
    ruleIds = []
    rules = []

    for index, rule in enumerate(cast(list[_Object], inference["rules"])):
        path = ("inference", "rules", index)
        ruleId, name = _DeclareIdentity(rule, knownRuleIds, knownRuleNames, path, "rule")
        antecedent = _BindAntecedent(cast(_Object, rule["antecedent"]), bindings, (*path, "antecedent"))
        consequent = _BindConsequent(
            cast(_Object, rule["consequent"]), bindings, outputUniverse, (*path, "consequent"),
        )
        ruleIds.append(ruleId)
        rules.append(SugenoRule(name, antecedent, consequent, _Real(rule["weight"])))

    model = SugenoModel(tuple(binding.variable for binding in bindings.values()), tuple(rules), policy, outputUniverse)

    return _ConfiguredSugeno(
        model, definitions, tuple(bindings), tuple(binding.scaleId for binding in bindings.values()),
        tuple(ruleIds), outputId,
    )
