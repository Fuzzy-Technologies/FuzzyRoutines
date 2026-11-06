# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private reconstruction of scalar Mamdani v1 model envelopes."""

from dataclasses import dataclass
from typing import cast

from ._config_inference import (
    _BindAntecedent,
    _BindInputs,
    _DeclareIdentity,
    _DecodePolicy,
    _ReadStandaloneInference,
    _ResolveScale,
    _TermNames,
)
from ._config_json import ConfigPath
from ._config_scale_model import (
    ScaleModelDecodeError,
    _DecodeCentroidPolicy,
    _DecodeDefinitions,
    _DecodeWindow,
    _Object,
    _Real,
    _ScaleModel,
)
from .defuzzification import CentroidPolicy
from .domain import ContinuousUniverse, IntegrationDomain
from .inference import FuzzyVariable, MamdaniModel, MamdaniRule
from .operators import SNormPolicy, TNormPolicy


@dataclass(frozen=True, slots=True)
class MamdaniCentroid:
    """An explicitly declared closed integration window and its policy."""

    domain: IntegrationDomain
    policy: CentroidPolicy


@dataclass(frozen=True, slots=True)
class _ConfiguredMamdani:
    """Immutable Mamdani runtime model and declared wire IDs and centroid."""

    model: MamdaniModel
    definitions: _ScaleModel
    inputIds: tuple[str, ...]
    inputScaleIds: tuple[str, ...]
    ruleIds: tuple[str, ...]
    outputId: str
    outputScaleId: str
    centroid: MamdaniCentroid | None


def DecodeMamdaniModel(encoded: bytes) -> _ConfiguredMamdani:
    """Decode a standalone v1 Mamdani model without evaluating it.

    Args:
        encoded: One bounded UTF-8 configuration document.

    Returns:
        The immutable model, ordered bindings and optional centroid settings.

    Raises:
        ValueError: Parsing, structural or semantic validation fails.
    """

    document, inference = _ReadStandaloneInference(encoded, "mamdani")

    return _DecodeMamdani(document, inference, ())


def _DecodeMamdani(document: _Object, inference: _Object, path: ConfigPath) -> _ConfiguredMamdani:
    """Reconstruct an output scale, ordered rules and optional centroid policy."""

    definitions = _DecodeDefinitions(document, path)
    inferencePath = (*path, "inference")
    bindings = _BindInputs(cast(list[_Object], inference["inputs"]), definitions, (*inferencePath, "inputs"))
    outputPath = (*inferencePath, "output")
    output = cast(_Object, inference["output"])
    outputId, outputName = _DeclareIdentity(output, set(bindings), set(), outputPath, "output variable")
    outputScaleId = cast(str, output["scale"])
    outputScale = _ResolveScale(outputScaleId, definitions, (*outputPath, "scale"))
    universe = definitions.universes[outputScale.universeId]

    if not isinstance(universe, ContinuousUniverse):
        raise ScaleModelDecodeError("invalid-value", (*outputPath, "scale"), "The output scale must be continuous.")

    centroid = None

    if "centroid" in inference:
        centroidDefinition = cast(_Object, inference["centroid"])
        centroid = MamdaniCentroid(
            _DecodeWindow(cast(_Object, centroidDefinition["domain"]), universe, (*inferencePath, "centroid", "domain")),
            _DecodeCentroidPolicy(cast(_Object, centroidDefinition["policy"])),
        )

    outputTermNames = _TermNames(outputScale)
    knownRuleIds: set[str] = set()
    knownRuleNames: set[str] = set()
    ruleIds = []
    rules = []

    for index, rule in enumerate(cast(list[_Object], inference["rules"])):
        rulePath = (*inferencePath, "rules", index)
        antecedent = _BindAntecedent(cast(_Object, rule["antecedent"]), bindings, (*rulePath, "antecedent"))
        termId = cast(str, rule["consequent"])

        if termId not in outputTermNames:
            raise ScaleModelDecodeError(
                "unresolved-reference", (*rulePath, "consequent"),
                f"Unknown term ID {termId!r} in output scale ID {outputScaleId!r}.",
            )

        ruleId, name = _DeclareIdentity(rule, knownRuleIds, knownRuleNames, rulePath, "rule")
        ruleIds.append(ruleId)
        rules.append(MamdaniRule(name, antecedent, outputTermNames[termId], _Real(rule["weight"])))

    model = MamdaniModel(
        tuple(binding.variable for binding in bindings.values()),
        FuzzyVariable(outputName, outputScale.scale.terms),
        tuple(rules),
        _DecodePolicy(cast(_Object, inference["policy"])),
        TNormPolicy(cast(str, inference["activation"])),
        SNormPolicy(cast(str, inference["aggregation"])),
    )

    return _ConfiguredMamdani(
        model, definitions, tuple(bindings), tuple(binding.scaleId for binding in bindings.values()),
        tuple(ruleIds), outputId, outputScaleId, centroid,
    )
