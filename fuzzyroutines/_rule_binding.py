# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Exact binding of readable rule drafts to one validated inference context."""

from collections.abc import Mapping
from dataclasses import dataclass

from ._config_export import _EncodeAntecedent, _EncodeSugenoConsequent, _Object, _Wire
from ._rule_formatter import _FormatRule, _RuleFormatError
from ._rule_parser import (
    _AntecedentDraft,
    _ConstantDraft,
    _LocatedValue,
    _NegationDraft,
    _ParseRule,
    _PredicateDraft,
    _RuleParseError,
    _TermDraft,
)
from .configuration import MamdaniBinding, ModelConfiguration, ScaleDefinition, SugenoBinding
from .inference import (
    AffineConsequent,
    AllOf,
    Antecedent,
    AnyOf,
    ConstantConsequent,
    MamdaniRule,
    NotCondition,
    SugenoRule,
    TermCondition,
)


@dataclass(frozen=True, slots=True)
class _BoundRule:
    """One scalar rule and its separately owned v1 rule object."""

    rule: MamdaniRule | SugenoRule
    wire: _Object


def _TermIds(scale: ScaleDefinition) -> dict[str, str]:
    """Index exact term names by the IDs from their own declared scale."""

    return {term.name: termId for term, termId in zip(scale.scale.terms, scale.termIds, strict=True)}


def _InputMaps(
    binding: MamdaniBinding | SugenoBinding, scales: Mapping[str, ScaleDefinition],
) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    """Index configured names and IDs without evaluating the model."""

    inputIds = {}
    termsByInput = {}
    termsByScale = {}

    for variable, (inputId, scaleId) in zip(binding.model.inputs, binding.inputs, strict=True):
        if scaleId not in termsByScale:
            termsByScale[scaleId] = _TermIds(scales[scaleId])

        inputIds[variable.name] = inputId
        termsByInput[variable.name] = termsByScale[scaleId]

    return inputIds, termsByInput


def _RequireReference(name: _LocatedValue[str], names: Mapping[str, object], namespace: str) -> str:
    """Resolve an exact runtime spelling or report its source token."""

    if name.value not in names:
        raise _RuleParseError("unresolved-binding", name.start, f"Unknown {namespace} name {name.value!r}.")

    return name.value


def _BindAntecedent(
    draft: _AntecedentDraft, termsByInput: Mapping[str, dict[str, str]],
) -> Antecedent:
    """Resolve terms in their own scope and preserve ordered connectives."""

    if isinstance(draft, _PredicateDraft):
        inputName = _RequireReference(draft.inputName, termsByInput, "input")
        termName = _RequireReference(draft.termName, termsByInput[inputName], f"term for input {inputName!r}")

        return TermCondition(inputName, termName)

    if isinstance(draft, _NegationDraft):
        return NotCondition(_BindAntecedent(draft.operand, termsByInput))

    operands = tuple(_BindAntecedent(child, termsByInput) for child in draft.operands)

    return AllOf(operands) if draft.operator == "AND" else AnyOf(operands)


def _BindRule(source: bytes, configuration: ModelConfiguration) -> _BoundRule:
    """Parse and bind one rule without changing or evaluating its model.

    Args:
        source: One complete UTF-8 rule under the ADR-0027 limits.
        configuration: Validated v1 model with explicit inference IDs.

    Returns:
        A scalar rule ready for insertion and its independently owned v1
        rule object. Output fields use the configured IDs.

    Raises:
        _RuleParseError: Syntax, canonical limits, bindings or rule semantics
            prevent the rule from being inserted into the selected model.
    """

    draft = _ParseRule(source)

    try:
        _FormatRule(draft)

    except _RuleFormatError as error:
        raise _RuleParseError("exceeded-limit", len(source), str(error)) from error

    binding = configuration.inference

    if binding is None:
        raise _RuleParseError("invalid-rule-semantics", 0, "A rule requires an inference model.")

    if draft.identifier.value in binding.ruleIds:
        raise _RuleParseError("invalid-rule-semantics", draft.identifier.start, "Repeated rule ID.")

    if any(rule.name == draft.name.value for rule in binding.model.rules):
        raise _RuleParseError("invalid-rule-semantics", draft.name.start, "Repeated rule name.")

    inputIds, termsByInput = _InputMaps(binding, configuration.scales)
    antecedent = _BindAntecedent(draft.antecedent, termsByInput)
    consequent = draft.consequent
    weight = draft.weight.value
    rule: MamdaniRule | SugenoRule
    wireConsequent: _Wire

    if isinstance(binding, MamdaniBinding):
        if not isinstance(consequent, _TermDraft):
            raise _RuleParseError("invalid-rule-semantics", consequent.start, "A Mamdani rule requires TERM.")

        outputTerms = _TermIds(configuration.scales[binding.outputScaleId])
        outputTerm = _RequireReference(consequent.termName, outputTerms, "output term")
        rule = MamdaniRule(draft.name.value, antecedent, outputTerm, weight)
        wireConsequent = outputTerms[outputTerm]

    else:
        if isinstance(consequent, _TermDraft):
            raise _RuleParseError(
                "invalid-rule-semantics", consequent.start, "A Sugeno rule requires CONSTANT or AFFINE.",
            )

        scalar: ConstantConsequent | AffineConsequent

        if isinstance(consequent, _ConstantDraft):
            output = consequent.output

            if not binding.model.outputUniverse.Contains(output.value):
                raise _RuleParseError("invalid-rule-semantics", output.start, "Constant lies outside the output universe.")

            scalar = ConstantConsequent(output.value)

        else:
            coefficients = tuple(
                (_RequireReference(name, inputIds, "affine input"), value.value)
                for name, value in consequent.coefficients
            )
            scalar = AffineConsequent(consequent.intercept.value, coefficients)

        rule = SugenoRule(draft.name.value, antecedent, scalar, weight)
        wireConsequent = _EncodeSugenoConsequent(scalar, inputIds, ("consequent",))

    return _BoundRule(rule, {
        "id": draft.identifier.value,
        "name": draft.name.value,
        "weight": weight,
        "antecedent": _EncodeAntecedent(antecedent, inputIds, termsByInput, ("antecedent",)),
        "consequent": wireConsequent,
    })
