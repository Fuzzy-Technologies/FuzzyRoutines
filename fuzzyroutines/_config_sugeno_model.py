# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private reconstruction of standalone v1 Sugeno models."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from ._config_inference import (
    _BindAntecedent,
    _BindInputs,
    _DeclareIdentity,
    _DecodePolicy,
    _InputBinding,
    _ReadStandaloneInference,
    _ResolveInput,
)
from ._config_json import ConfigPath
from ._config_scale_model import (
    ScaleModelDecodeError,
    _DecodeDefinitions,
    _Object,
    _Real,
    _ScaleModel,
)
from .domain import ContinuousUniverse
from .inference import AffineConsequent, ConstantConsequent, SugenoModel, SugenoRule


@dataclass(frozen=True, slots=True)
class _ConfiguredSugeno:
    """Immutable runtime model and ordered wire bindings for reconstruction."""

    model: SugenoModel
    definitions: _ScaleModel
    inputIds: tuple[str, ...]
    inputScaleIds: tuple[str, ...]
    ruleIds: tuple[str, ...]
    outputUniverseId: str


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

    document, inference = _ReadStandaloneInference(encoded, "sugeno")

    return _DecodeSugeno(document, inference, ())


def _DecodeSugeno(document: _Object, inference: _Object, path: ConfigPath) -> _ConfiguredSugeno:
    """Reconstruct a validated Sugeno envelope at its document-relative location."""

    definitions = _DecodeDefinitions(document, path)
    inferencePath = (*path, "inference")
    bindings = _BindInputs(cast(list[_Object], inference["inputs"]), definitions, (*inferencePath, "inputs"))
    outputId = cast(str, inference["outputUniverse"])
    outputUniverse = definitions.universes.get(outputId)

    if outputUniverse is None:
        raise ScaleModelDecodeError(
            "unresolved-reference", (*inferencePath, "outputUniverse"), f"Unknown model universe ID {outputId!r}.",
        )

    if not isinstance(outputUniverse, ContinuousUniverse):
        raise ScaleModelDecodeError(
            "invalid-value", (*inferencePath, "outputUniverse"), "The Sugeno output universe must be continuous.",
        )

    policy = _DecodePolicy(cast(_Object, inference["policy"]))
    knownRuleIds: set[str] = set()
    knownRuleNames: set[str] = set()
    ruleIds = []
    rules = []

    for index, rule in enumerate(cast(list[_Object], inference["rules"])):
        rulePath = (*inferencePath, "rules", index)
        ruleId, name = _DeclareIdentity(rule, knownRuleIds, knownRuleNames, rulePath, "rule")
        antecedent = _BindAntecedent(cast(_Object, rule["antecedent"]), bindings, (*rulePath, "antecedent"))
        consequent = _BindConsequent(
            cast(_Object, rule["consequent"]), bindings, outputUniverse, (*rulePath, "consequent"),
        )
        ruleIds.append(ruleId)
        rules.append(SugenoRule(name, antecedent, consequent, _Real(rule["weight"])))

    model = SugenoModel(tuple(binding.variable for binding in bindings.values()), tuple(rules), policy, outputUniverse)

    return _ConfiguredSugeno(
        model, definitions, tuple(bindings), tuple(binding.scaleId for binding in bindings.values()),
        tuple(ruleIds), outputId,
    )
