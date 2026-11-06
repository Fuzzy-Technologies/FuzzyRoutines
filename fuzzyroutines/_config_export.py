# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic JSON export for configured v1 scalar models."""

from collections.abc import Mapping
from fractions import Fraction
from json import dumps
from math import isfinite
from typing import cast

from ._config_json import (
    _MAX_ANTECEDENT_DEPTH,
    _SURROGATE,
    ConfigPath,
    ConfigPointer,
    ConfigurationError,
)
from ._config_mamdani_model import DecodeMamdaniModel, _ConfiguredMamdani
from ._config_scale_model import DecodeScaleModel, ScaleDefinition, _ScaleModel
from ._config_sugeno_model import DecodeSugenoModel, _ConfiguredSugeno
from .defuzzification import CentroidPolicy
from .domain import ContinuousUniverse, DiscreteUniverse, IntegrationDomain
from .fuzzysets import ScalarFuzzySet
from .inference import (
    AffineConsequent,
    AllOf,
    Antecedent,
    AnyOf,
    ConstantConsequent,
    FuzzyVariable,
    InferencePolicy,
    MamdaniModel,
    MamdaniRule,
    NotCondition,
    SugenoModel,
    SugenoRule,
    TermCondition,
)
from .linguistic import FuzzificationPolicy, LinguisticScale, LinguisticTerm
from .membership import MembershipFunction
from .operators import NegationPolicy, SNormPolicy, TNormPolicy

type _Wire = None | bool | str | int | float | list[_Wire] | dict[str, _Wire]
type _Object = dict[str, _Wire]
type _Model = _ScaleModel | _ConfiguredMamdani | _ConfiguredSugeno

_MAX_EXACT_DEPTH = (1 << 53) - 1


class ConfigExportError(ConfigurationError):
    """Unsupported model source data identified by its prospective wire path."""

    category = "unsupported-source"

    def __init__(self, path: ConfigPath, message: str) -> None:
        """Record a precise wire pointer and the reason export cannot proceed."""

        super().__init__(message, category=self.category, pointer=ConfigPointer(path))


def _Binary64(value: object, path: ConfigPath) -> float:
    """Convert trusted finite real source types only when the value is exact."""

    if type(value) not in (int, float, Fraction):
        raise ConfigExportError(path, "Choose a built-in real scalar representable as binary64.")

    try:
        converted = float(cast(int | float | Fraction, value))

    except OverflowError as error:
        raise ConfigExportError(path, "The source number is outside the finite binary64 range.") from error

    if not isfinite(converted) or converted != value:
        raise ConfigExportError(path, "The source number is not exactly representable as finite binary64.")

    return converted


def _EncodeUniverse(universe: object, path: ConfigPath) -> _Object:
    """Record the exact coordinates and boundary ownership of an allowed universe."""

    if type(universe) is ContinuousUniverse:
        return {
            "kind": "continuous",
            "left": None if universe.left is None else _Binary64(universe.left, (*path, "left")),
            "leftClosed": universe.leftClosed,
            "right": None if universe.right is None else _Binary64(universe.right, (*path, "right")),
            "rightClosed": universe.rightClosed,
        }

    if type(universe) is DiscreteUniverse:
        return {
            "kind": "discrete",
            "points": [_Binary64(point, (*path, "points", index)) for index, point in enumerate(universe.points)],
        }

    raise ConfigExportError(path, "Choose an explicit built-in continuous or discrete universe.")


def _RequireMembership(source: object, path: ConfigPath) -> MembershipFunction:
    """Reject callbacks, historical adapters and subclasses without consulting them."""

    if type(source) is not MembershipFunction:
        raise ConfigExportError(path, "Choose an explicit built-in membership family or keep the evaluator in code.")

    return source


def _EncodeMembership(source: object, path: ConfigPath) -> _Object:
    """Export an allowlisted built-in family with exact modern parameters."""

    membership = _RequireMembership(source, path)
    return {
        "family": membership.family,
        "parameters": {
            key: _Binary64(value, (*path, "parameters", key))
            for key, value in sorted(membership.parameters.items())
        },
    }


def _EncodeWindow(domain: IntegrationDomain, path: ConfigPath) -> _Object:
    """Export the exact bounds of a closed numerical integration window."""

    if type(domain) is not IntegrationDomain:
        raise ConfigExportError(path, "Choose an explicit built-in integration domain.")

    return {"left": _Binary64(domain.left, (*path, "left")), "right": _Binary64(domain.right, (*path, "right"))}


def _EncodeCentroid(policy: CentroidPolicy, path: ConfigPath) -> _Object:
    """Export exact tolerances and the integral v1 subdivision limit."""

    if type(policy) is not CentroidPolicy:
        raise ConfigExportError(path, "Choose an explicit built-in centroid policy.")

    depth = policy.maximumDepth

    if type(depth) is not int or not 0 <= depth <= _MAX_EXACT_DEPTH:
        raise ConfigExportError((*path, "maximumDepth"), "Choose an integer depth in the v1 range.")

    return {
        "absoluteTolerance": _Binary64(policy.absoluteTolerance, (*path, "absoluteTolerance")),
        "relativeTolerance": _Binary64(policy.relativeTolerance, (*path, "relativeTolerance")),
        "maximumDepth": depth,
    }


def _EncodeFuzzification(policy: FuzzificationPolicy, path: ConfigPath) -> _Object:
    """Export explicit tie selection and its exact numerical thresholds."""

    if type(policy) is not FuzzificationPolicy:
        raise ConfigExportError(path, "Choose an explicit built-in fuzzification policy.")

    return {
        "tiePolicy": policy.tiePolicy,
        "minimumConfidence": _Binary64(policy.minimumConfidence, (*path, "minimumConfidence")),
        "tieTolerance": _Binary64(policy.tieTolerance, (*path, "tieTolerance")),
    }


def _RequireAligned(path: ConfigPath, length: int, *bindings: tuple[object, ...]) -> None:
    """Reject incomplete ordered wire bindings before pairing them with runtime data."""

    if any(len(binding) != length for binding in bindings):
        raise ConfigExportError(path, "Provide one wire binding for each runtime declaration.")


def _EncodeTerm(
    term: LinguisticTerm, termId: str, membershipId: str,
    definitions: _ScaleModel, universeId: str, path: ConfigPath,
) -> _Object:
    """Export a term after verifying it uses its declared built-in definitions."""

    if type(term) is not LinguisticTerm or type(term.fuzzySet) is not ScalarFuzzySet:
        raise ConfigExportError(path, "Choose an explicit built-in linguistic term and scalar fuzzy set.")

    membershipPath = (*path, "membership")
    source = _RequireMembership(term.fuzzySet.membershipFunction, membershipPath)
    declared = definitions.memberships.get(membershipId)

    if source is not declared and (
        declared is None or _JsonText(_EncodeMembership(source, membershipPath))
        != _JsonText(_EncodeMembership(declared, membershipPath))
    ):
        raise ConfigExportError(membershipPath, "Bind the term to its exact membership definition.")

    universe = term.fuzzySet.universe
    declaredUniverse = definitions.universes.get(universeId)

    if universe is not declaredUniverse and (
        declaredUniverse is None or _JsonText(_EncodeUniverse(universe, path))
        != _JsonText(_EncodeUniverse(declaredUniverse, path))
    ):
        raise ConfigExportError(path, "Bind the term to the exact scale universe.")

    return {"id": termId, "membership": membershipId, "name": term.name}


def _EncodeScale(configured: ScaleDefinition, definitions: _ScaleModel, path: ConfigPath) -> _Object:
    """Preserve term declaration order and independently optional scale policies."""

    if type(configured.scale) is not LinguisticScale:
        raise ConfigExportError(path, "Choose an explicit built-in linguistic scale.")

    terms = configured.scale.terms
    _RequireAligned((*path, "terms"), len(terms), configured.termIds, configured.membershipIds)
    encoded: _Object = {
        "universe": configured.universeId,
        "terms": [
            _EncodeTerm(term, termId, membershipId, definitions, configured.universeId, (*path, "terms", index))
            for index, (term, termId, membershipId) in enumerate(
                zip(terms, configured.termIds, configured.membershipIds, strict=True)
            )
        ],
    }

    if configured.fuzzification is not None:
        encoded["fuzzification"] = _EncodeFuzzification(configured.fuzzification, (*path, "fuzzification"))

    if configured.representatives is not None:
        representatives = configured.representatives
        representativePath = (*path, "representatives")
        _RequireAligned((*representativePath, "windows"), len(terms), representatives.domains)
        encoded["representatives"] = {
            "policy": _EncodeCentroid(representatives.policy, (*representativePath, "policy")),
            "windows": {
                termId: _EncodeWindow(domain, (*representativePath, "windows", termId))
                for termId, domain in zip(configured.termIds, representatives.domains, strict=True)
            },
        }

    return encoded


def _EncodeDefinitions(definitions: _ScaleModel) -> _Object:
    """Map runtime definitions to their explicit v1 IDs without deriving presets."""

    return {
        "kind": "model",
        "schemaVersion": 1,
        "memberships": {
            key: _EncodeMembership(value, ("memberships", key))
            for key, value in sorted(definitions.memberships.items())
        },
        "universes": {
            key: _EncodeUniverse(value, ("universes", key))
            for key, value in sorted(definitions.universes.items())
        },
        "scales": {
            key: _EncodeScale(value, definitions, ("scales", key))
            for key, value in sorted(definitions.scales.items())
        },
    }


def _EncodePolicy(policy: InferencePolicy, path: ConfigPath) -> _Object:
    """Export explicit built-in operators and preserve exact negation parameters."""

    if type(policy) is not InferencePolicy:
        raise ConfigExportError(path, "Choose an explicit built-in inference policy.")

    for field, operator, expected in (
        ("conjunction", policy.conjunction, TNormPolicy),
        ("disjunction", policy.disjunction, SNormPolicy),
        ("negation", policy.negation, NegationPolicy),
    ):
        if type(operator) is not expected:
            raise ConfigExportError((*path, field), "Choose an explicit built-in operator policy.")

    negation: _Object = {"family": policy.negation.family}

    if policy.negation.alpha is not None:
        negation["alpha"] = _Binary64(policy.negation.alpha, (*path, "negation", "alpha"))

    return {"conjunction": policy.conjunction.family, "disjunction": policy.disjunction.family, "negation": negation}


def _EncodeVariable(
    variable: FuzzyVariable, variableId: str, scaleId: str, definitions: _ScaleModel, path: ConfigPath,
) -> tuple[_Object, dict[str, str]]:
    """Verify the declared scale and index its exact term names for reference binding."""

    if type(variable) is not FuzzyVariable:
        raise ConfigExportError(path, "Choose an explicit built-in fuzzy variable.")

    configured = definitions.scales.get(scaleId)
    scalePath = (*path, "scale")

    if configured is None or len(configured.scale.terms) != len(variable.terms):
        raise ConfigExportError(scalePath, "Bind the variable to its exact scale definition.")

    if variable.terms is not configured.scale.terms:
        for index, (term, expected, termId, membershipId) in enumerate(zip(
            variable.terms, configured.scale.terms, configured.termIds, configured.membershipIds, strict=True,
        )):
            if term is expected:
                continue

            termPath = ("scales", scaleId, "terms", index)
            _EncodeTerm(term, termId, membershipId, definitions, configured.universeId, termPath)

            if term.name != expected.name:
                raise ConfigExportError(scalePath, "Preserve the term names and order of the declared scale.")

    names = {term.name: termId for term, termId in zip(variable.terms, configured.termIds, strict=True)}

    return {"id": variableId, "name": variable.name, "scale": scaleId}, names


def _Reference(name: str, names: Mapping[str, str], path: ConfigPath) -> str:
    """Translate one runtime name to its declared wire ID."""

    if name not in names:
        raise ConfigExportError(path, f"No wire binding exists for runtime name {name!r}.")

    return names[name]


def _EncodeAntecedent(
    expression: Antecedent, names: Mapping[str, str], terms: Mapping[str, dict[str, str]],
    path: ConfigPath, depth: int = 1,
) -> _Object:
    """Export allowed ordered expression nodes while bounding recursion."""

    if depth > _MAX_ANTECEDENT_DEPTH:
        raise ConfigExportError(path, "Antecedent depth exceeds the v1 limit.")

    if type(expression) is TermCondition:
        inputId = _Reference(expression.variable, names, (*path, "input"))
        termId = _Reference(expression.term, terms[expression.variable], (*path, "term"))

        return {"kind": "term", "input": inputId, "term": termId}

    if type(expression) is NotCondition:
        return {"kind": "not", "operand": _EncodeAntecedent(expression.operand, names, terms, (*path, "operand"), depth + 1)}

    if type(expression) in (AllOf, AnyOf):
        condition = cast(AllOf | AnyOf, expression)
        return {
            "kind": "all" if type(condition) is AllOf else "any",
            "operands": [
                _EncodeAntecedent(operand, names, terms, (*path, "operands", index), depth + 1)
                for index, operand in enumerate(condition.operands)
            ],
        }

    raise ConfigExportError(path, "Choose an explicit built-in antecedent node.")


def _EncodeSugenoConsequent(
    consequent: ConstantConsequent | AffineConsequent, names: Mapping[str, str], path: ConfigPath,
) -> _Object:
    """Export a constant or ordered affine consequent without evaluating it."""

    if type(consequent) is ConstantConsequent:
        return {"kind": "constant", "value": _Binary64(consequent.value, (*path, "value"))}

    if type(consequent) is not AffineConsequent:
        raise ConfigExportError(path, "Choose an explicit built-in constant or affine consequent.")

    return {
        "kind": "affine",
        "intercept": _Binary64(consequent.intercept, (*path, "intercept")),
        "coefficients": [
            {
                "input": _Reference(name, names, (*path, "coefficients", index, "input")),
                "value": _Binary64(value, (*path, "coefficients", index, "value")),
            }
            for index, (name, value) in enumerate(consequent.coefficients)
        ],
    }


def _EncodeInference(configured: _ConfiguredMamdani | _ConfiguredSugeno) -> _Object:
    """Export ordered bindings and inference settings from one configured model."""

    model = configured.model
    definitions = configured.definitions
    path = ("inference",)

    if type(model) not in (MamdaniModel, SugenoModel):
        raise ConfigExportError(path, "Choose an explicit built-in Mamdani or Sugeno model.")

    _RequireAligned((*path, "inputs"), len(model.inputs), configured.inputIds, configured.inputScaleIds)
    _RequireAligned((*path, "rules"), len(model.rules), configured.ruleIds)
    inputs: list[_Wire] = []
    names = {}
    terms = {}

    for index, (variable, variableId, scaleId) in enumerate(
        zip(model.inputs, configured.inputIds, configured.inputScaleIds, strict=True)
    ):
        encoded, termNames = _EncodeVariable(variable, variableId, scaleId, definitions, (*path, "inputs", index))
        inputs.append(encoded)
        names[variable.name] = variableId
        terms[variable.name] = termNames

    inference: _Object = {"inputs": inputs, "policy": _EncodePolicy(model.policy, (*path, "policy"))}
    outputTerms: dict[str, str] = {}

    if isinstance(configured, _ConfiguredMamdani):
        mamdani = configured.model
        output, outputTerms = _EncodeVariable(
            mamdani.output, configured.outputId, configured.outputScaleId, definitions, (*path, "output"),
        )

        for field, operator, expected in (
            ("activation", mamdani.activation, TNormPolicy), ("aggregation", mamdani.aggregation, SNormPolicy),
        ):
            if type(operator) is not expected:
                raise ConfigExportError((*path, field), "Choose an explicit built-in norm policy.")

        inference.update({
            "kind": "mamdani", "output": output, "activation": mamdani.activation.family,
            "aggregation": mamdani.aggregation.family,
        })

        if configured.centroid is not None:
            inference["centroid"] = {
                "domain": _EncodeWindow(configured.centroid.domain, (*path, "centroid", "domain")),
                "policy": _EncodeCentroid(configured.centroid.policy, (*path, "centroid", "policy")),
            }

    else:
        outputId = configured.outputUniverseId
        outputPath = (*path, "outputUniverse")
        universe = configured.model.outputUniverse
        declared = definitions.universes.get(outputId)

        if universe is not declared and (
            declared is None or _JsonText(_EncodeUniverse(universe, outputPath)) != _JsonText(_EncodeUniverse(declared, outputPath))
        ):
            raise ConfigExportError(outputPath, "Bind the output to its exact continuous universe definition.")

        inference.update({"kind": "sugeno", "outputUniverse": outputId})

    rules: list[_Wire] = []

    for index, (rule, ruleId) in enumerate(zip(model.rules, configured.ruleIds, strict=True)):
        rulePath = (*path, "rules", index)
        consequentPath = (*rulePath, "consequent")

        if type(rule) is MamdaniRule:
            consequent: _Wire = _Reference(rule.consequent, outputTerms, consequentPath)

        elif type(rule) is SugenoRule:
            consequent = _EncodeSugenoConsequent(rule.consequent, names, consequentPath)

        else:
            raise ConfigExportError(rulePath, "Choose an explicit built-in inference rule.")

        rules.append({
            "id": ruleId, "name": rule.name, "weight": _Binary64(rule.weight, (*rulePath, "weight")),
            "antecedent": _EncodeAntecedent(rule.antecedent, names, terms, (*rulePath, "antecedent")),
            "consequent": consequent,
        })

    inference["rules"] = rules

    return inference


def _JsonText(wire: _Wire) -> str:
    """Emit canonical key order, Unicode text and round-trip binary64 decimals."""

    return dumps(wire, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def _CheckUnicode(wire: _Wire, path: ConfigPath) -> None:
    """Locate an unpaired Unicode surrogate in a rejected export value."""

    if isinstance(wire, str) and _SURROGATE.search(wire):
        raise ConfigExportError(path, "Replace unpaired Unicode surrogates in source text.")

    if isinstance(wire, dict):
        for key, value in sorted(wire.items()):
            _CheckUnicode(key, (*path, key))
            _CheckUnicode(value, (*path, key))

    if isinstance(wire, list):
        for index, value in enumerate(wire):
            _CheckUnicode(value, (*path, index))


def _EncodeModelBytes(model: _Model) -> bytes:
    """Encode canonical bytes for validation against the v1 model contract."""

    definitions = model if isinstance(model, _ScaleModel) else model.definitions
    wire = _EncodeDefinitions(definitions)

    if not isinstance(model, _ScaleModel):
        wire["inference"] = _EncodeInference(model)

    try:
        return (_JsonText(wire) + "\n").encode("utf-8")

    except UnicodeEncodeError as error:
        _CheckUnicode(wire, ())

        raise ConfigExportError((), "Replace unpaired Unicode surrogates in source text.") from error


def EncodeModel(model: _Model) -> bytes:
    """Encode one configured scale, Mamdani or Sugeno model without evaluation.

    Args:
        model: Immutable runtime definitions with their explicit wire bindings.

    Returns:
        Validated, deterministic UTF-8 v1 model bytes with a final LF.

    Raises:
        ValueError: A source value has no supported v1 representation, or the
            generated document violates the v1 parser, shape or semantic limits.
    """

    encoded = _EncodeModelBytes(model)

    if isinstance(model, _ConfiguredMamdani):
        DecodeMamdaniModel(encoded)

    elif isinstance(model, _ConfiguredSugeno):
        DecodeSugenoModel(encoded)

    else:
        DecodeScaleModel(encoded)

    return encoded
