# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Inspect typed scalar rule drafts without evaluating membership or inference."""

from dataclasses import dataclass
from typing import Literal

from fuzzyroutines.exceptions import InvalidParameterError, InvalidParameterTypeError
from fuzzyroutines.inference import (
    AffineConsequent,
    Antecedent,
    ConstantConsequent,
    FuzzyVariable,
    MamdaniRule,
    SugenoRule,
    _References,
)
from fuzzyroutines.membership import MembershipScalar

__all__ = ["InspectRules", "RuleDiagnostic"]

type _Rule = MamdaniRule | SugenoRule
type _Code = Literal[
    "unknown_input",
    "unknown_input_term",
    "unknown_output_term",
    "unknown_affine_input",
    "duplicate_name",
    "zero_weight",
    "duplicate_rule",
    "potential_conflict",
]


@dataclass(frozen=True, slots=True)
class RuleDiagnostic:
    """One structural finding, with an earlier rule index for paired findings.

    Attributes:
        code: Stable machine-readable finding identifier.
        severity: Error for unresolved references or repeated names; otherwise
            warning.
        rule_index: Zero-based index of the rule that produced the finding.
        message: Human-readable explanation, including the unresolved name
            where applicable.
        related_rule_index: First matching earlier rule index, if applicable.
    """

    code: _Code
    severity: Literal["error", "warning"]
    rule_index: int
    message: str
    related_rule_index: int | None = None


def _ReferenceErrors(
    rule: _Rule,
    index: int,
    inputs: dict[str, set[str]],
    output_terms: set[str],
) -> tuple[RuleDiagnostic, ...]:
    """Find each distinct unresolved reference in traversal order."""

    diagnostics: dict[tuple[_Code, str, str | None], RuleDiagnostic] = {}
    key: tuple[_Code, str, str | None]

    for leaf in _References(rule.antecedent):
        if leaf.variable not in inputs:
            key = ("unknown_input", leaf.variable, None)
            diagnostics[key] = RuleDiagnostic(key[0], "error", index, f"Unknown input {leaf.variable!r}")

        elif leaf.term not in inputs[leaf.variable]:
            key = ("unknown_input_term", leaf.variable, leaf.term)
            diagnostics[key] = RuleDiagnostic(
                key[0], "error", index, f"Unknown term {leaf.term!r} for input {leaf.variable!r}"
            )

    if isinstance(rule, MamdaniRule) and rule.consequent not in output_terms:
        key = ("unknown_output_term", rule.consequent, None)
        diagnostics[key] = RuleDiagnostic(key[0], "error", index, f"Unknown output term {rule.consequent!r}")

    if isinstance(rule, SugenoRule) and isinstance(rule.consequent, AffineConsequent):
        for name, _ in rule.consequent.coefficients:
            if name not in inputs:
                key = ("unknown_affine_input", name, None)
                diagnostics[key] = RuleDiagnostic(key[0], "error", index, f"Unknown affine input {name!r}")

    return tuple(diagnostics.values())


def _OutputSignature(
    consequent: str | ConstantConsequent | AffineConsequent,
) -> str | tuple[MembershipScalar, dict[str, MembershipScalar]]:
    """Compare declared output terms or affine maps, treating omitted coefficients as zero."""

    if isinstance(consequent, str):
        return consequent

    if isinstance(consequent, ConstantConsequent):
        return consequent.value, {}

    return consequent.intercept, {
        name: coefficient for name, coefficient in consequent.coefficients if coefficient != 0
    }


def InspectRules(
    inputs: tuple[FuzzyVariable, ...],
    rules: tuple[_Rule, ...],
    *,
    output: FuzzyVariable | None = None,
) -> tuple[RuleDiagnostic, ...]:
    """Report unresolved bindings and exact structural patterns in an ordered draft.

    Pass the output variable for Mamdani rules and omit it for Sugeno rules.
    All references are checked, including those in rules with zero weight.
    Comparisons use the ordered antecedent AST and consider only active rules
    with resolvable references. Different antecedents can overlap without a
    structural warning. Different declared outputs with identical antecedents
    may blend intentionally; inspect such warnings in the model's context.

    Args:
        inputs: Declared input variables with unique names.
        rules: Ordered rules of the selected model kind. An empty draft is
            accepted.
        output: Mamdani output variable. For Sugeno, structural inspection
            needs only the input bindings.

    Returns:
        Diagnostics in rule order. In a paired finding, the later rule
        points to the first earlier matching rule.

    Raises:
        InvalidParameterTypeError: A declaration has the wrong type.
        InvalidParameterError: Two input declarations have the same name.
    """

    if not isinstance(inputs, tuple) or not all(isinstance(variable, FuzzyVariable) for variable in inputs):
        raise InvalidParameterTypeError("inputs must be a tuple of fuzzy variables")

    if output is not None and not isinstance(output, FuzzyVariable):
        raise InvalidParameterTypeError("output must be a fuzzy variable or None")

    rule_type = MamdaniRule if output is not None else SugenoRule

    if not isinstance(rules, tuple) or not all(isinstance(rule, rule_type) for rule in rules):
        raise InvalidParameterTypeError(f"rules must be a tuple of {rule_type.__name__} objects")

    bindings = {variable.name: {term.name for term in variable.terms} for variable in inputs}

    if len(bindings) != len(inputs):
        raise InvalidParameterError("input names must be unique")

    output_terms = {term.name for term in output.terms} if output is not None else set()
    diagnostics: list[RuleDiagnostic] = []
    first_by_name: dict[str, int] = {}
    active_rules: dict[Antecedent, list[tuple[int, _Rule]]] = {}

    for index, rule in enumerate(rules):
        earlier_name = first_by_name.setdefault(rule.name, index)

        if earlier_name != index:
            diagnostics.append(
                RuleDiagnostic("duplicate_name", "error", index, f"Repeated rule name {rule.name!r}", earlier_name)
            )

        errors = _ReferenceErrors(rule, index, bindings, output_terms)
        diagnostics.extend(errors)

        if rule.weight == 0:
            diagnostics.append(RuleDiagnostic("zero_weight", "warning", index, "A zero-weight rule cannot fire"))
            continue

        if errors:
            continue

        peers = active_rules.setdefault(rule.antecedent, [])
        earlier_duplicate = next(
            (
                peer_index for peer_index, peer in peers
                if rule.consequent == peer.consequent and rule.weight == peer.weight
            ),
            None,
        )
        output_signature = _OutputSignature(rule.consequent)
        earlier_conflict = next(
            (
                peer_index for peer_index, peer in peers
                if output_signature != _OutputSignature(peer.consequent)
            ),
            None,
        )

        if earlier_duplicate is not None:
            diagnostics.append(
                RuleDiagnostic("duplicate_rule", "warning", index, "Repeated active rule", earlier_duplicate)
            )

        if earlier_conflict is not None:
            diagnostics.append(
                RuleDiagnostic(
                    "potential_conflict", "warning", index,
                    "Identical antecedent has a different declared output", earlier_conflict,
                )
            )

        peers.append((index, rule))

    return tuple(diagnostics)
