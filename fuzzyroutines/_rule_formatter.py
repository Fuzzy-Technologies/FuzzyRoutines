# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Canonical UTF-8 formatting of bounded, unbound readable rule drafts."""

from decimal import Decimal
from json import dumps
from math import copysign
from typing import Literal

from fuzzyroutines._rule_lexer import _MAX_BYTES, _MAX_TOKENS
from fuzzyroutines._rule_parser import (
    _MAX_DEPTH,
    _AffineDraft,
    _AntecedentDraft,
    _ConstantDraft,
    _JunctionDraft,
    _NegationDraft,
    _PredicateDraft,
    _RuleDraft,
)

type _Operator = Literal["OR", "AND", "NOT"]
_PRECEDENCE: dict[_Operator | None, int] = {"OR": 1, "AND": 2, "NOT": 3, None: 0}


class _RuleFormatError(ValueError):
    """Canonical size or depth overflow, with an offset when source exists."""

    category = "exceeded-limit"

    def __init__(self, offset: int | None, limit: str) -> None:
        """Keep the original end offset and name the exceeded output limit."""

        super().__init__(f"Canonical rule exceeds the {limit} limit.")
        self.offset = offset


class _RuleWriter:
    """An incremental UTF-8 and token budget for canonical output."""

    def __init__(self, sourceEnd: int | None) -> None:
        """Start an empty output buffer associated with the original source."""

        self.sourceEnd = sourceEnd
        self.data = bytearray()
        self.tokens = 0

    def Write(self, text: str, tokens: int = 1) -> None:
        """Append one bounded fragment after reserving bytes and tokens."""

        encoded = text.encode("utf-8")

        if len(self.data) + len(encoded) > _MAX_BYTES:
            raise _RuleFormatError(self.sourceEnd, "65,536-byte")

        if self.tokens + tokens > _MAX_TOKENS:
            raise _RuleFormatError(self.sourceEnd, "4,096-token")

        self.data.extend(encoded)
        self.tokens += tokens


def _QuoteRuleName(value: str) -> str:
    """Escape controls and JSON syntax while retaining printable Unicode."""

    quoted = dumps(value, ensure_ascii=False)

    return "".join(character if character.isprintable() else dumps(character)[1:-1] for character in quoted)


def _RuleNumber(value: float) -> str:
    """Choose a short exact binary64 round-trip token and preserve signed zero."""

    if value == 0.0:
        return "-0" if copysign(1.0, value) < 0.0 else "0"

    sign, digits, exponent = Decimal(repr(value)).as_tuple()
    assert isinstance(exponent, int), "Parsed numbers are finite binary64 values."
    coefficient = "".join(map(str, digits))
    significant = coefficient.rstrip("0")
    exponent += len(coefficient) - len(significant)
    point = len(significant) + exponent

    if exponent >= 0:
        fixed = significant + "0" * exponent

    elif point <= 0:
        fixed = "0." + "0" * -point + significant

    else:
        fixed = significant[:point] + "." + significant[point:]

    # The decimal point in scientific notation costs a character. With at
    # most 17 significant digits its shift can save at most one exponent
    # character unless the exponent disappears, which is the fixed candidate.
    scientific = f"{significant}e{exponent}"
    shortest = fixed if len(fixed) <= len(scientific) else scientific

    return ("-" if sign else "") + shortest


def _WriteAntecedent(
    writer: _RuleWriter, node: _AntecedentDraft, parent: _Operator | None, depth: int, pending: int,
) -> None:
    """Preserve ordered n-ary boundaries and reject canonical depth overflow."""

    if depth > _MAX_DEPTH:
        raise _RuleFormatError(writer.sourceEnd, "64-node antecedent path")

    if isinstance(node, _PredicateDraft):
        writer.Write(_QuoteRuleName(node.inputName.value))
        writer.Write(" IS ")
        writer.Write(_QuoteRuleName(node.termName.value))

        return

    operator: _Operator = "NOT" if isinstance(node, _NegationDraft) else node.operator
    grouped = _PRECEDENCE[operator] < _PRECEDENCE[parent] or (isinstance(node, _JunctionDraft) and operator == parent)
    pending += int(grouped) + int(operator == "NOT")

    if pending > _MAX_DEPTH:
        raise _RuleFormatError(writer.sourceEnd, "64-level nesting")

    if grouped:
        writer.Write("(")

    if isinstance(node, _NegationDraft):
        writer.Write("NOT ")
        _WriteAntecedent(writer, node.operand, operator, depth + 1, pending)

    else:
        for index, operand in enumerate(node.operands):
            if index:
                writer.Write(f" {operator} ")

            _WriteAntecedent(writer, operand, operator, depth + 1, pending)

    if grouped:
        writer.Write(")")


def _FormatRule(draft: _RuleDraft) -> bytes:
    """Return the canonical representation after all output limits pass.

    The draft must have been parsed from a valid source or supplied by the
    future binding stage with the same invariants. No partial bytes escape.
    """

    writer = _RuleWriter(draft.sourceEnd)
    writer.Write("RULE ")
    writer.Write(draft.identifier.value)
    writer.Write(" ", 0)
    writer.Write(_QuoteRuleName(draft.name.value))
    writer.Write(" IF ")
    _WriteAntecedent(writer, draft.antecedent, None, 1, 0)
    writer.Write(" THEN ")
    consequent = draft.consequent

    if isinstance(consequent, _AffineDraft):
        writer.Write("AFFINE(", 2)
        writer.Write(_RuleNumber(consequent.intercept.value))

        for name, value in consequent.coefficients:
            writer.Write(", ")
            writer.Write(_QuoteRuleName(name.value))
            writer.Write(": ")
            writer.Write(_RuleNumber(value.value))

        writer.Write(")")

    elif isinstance(consequent, _ConstantDraft):
        writer.Write("CONSTANT ")
        writer.Write(_RuleNumber(consequent.output.value))

    else:
        writer.Write("TERM ")
        writer.Write(_QuoteRuleName(consequent.termName.value))

    writer.Write(" WEIGHT ")
    writer.Write(_RuleNumber(draft.weight.value))
    writer.Write("\n", 0)

    return bytes(writer.data)
