# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Readable rule precedence, structure, source diagnostics and nesting limits."""

from math import copysign
from random import Random

from fuzzyroutines._rule_parser import (
    _AffineDraft,
    _ConstantDraft,
    _JunctionDraft,
    _NegationDraft,
    _ParseRule,
    _PredicateDraft,
    _RuleParseError,
    _TermDraft,
)

_PREFIX = b'RULE NOT "Alert" IF '
_PREDICATE = b'"risk" IS "High"'
_SUFFIX = b' THEN TERM "Urgent" WEIGHT 1'


def _AssertFailure(source: bytes, category: str, offset: int) -> None:
    """Require a normalized diagnostic without returning a partial draft."""

    try:
        _ParseRule(source)

    except _RuleParseError as error:
        assert (error.category, error.offset) == (category, offset)
        return

    raise AssertionError("Expected parsing to fail.")


def test_PrecedenceAndOrderedAffineCoefficients() -> None:
    """Bind NOT before AND before OR and retain the coefficient order."""

    source = (
        _PREFIX + b'NOT "risk" IS "Low" AND "sensor" IS "Stable" OR "load" IS "High"'
        b' THEN AFFINE(0.25, "load": -0, "risk": 0.75) WEIGHT 0.8'
    )
    draft = _ParseRule(source)
    assert draft.identifier.value == "NOT"
    assert draft.name.value == "Alert" and draft.weight.value == 0.8
    assert isinstance(draft.antecedent, _JunctionDraft) and draft.antecedent.operator == "OR"
    left, right = draft.antecedent.operands
    assert isinstance(left, _JunctionDraft) and left.operator == "AND"
    negative, middle = left.operands
    assert isinstance(negative, _NegationDraft) and isinstance(negative.operand, _PredicateDraft)
    assert negative.operand.termName.value == "Low"
    assert isinstance(middle, _PredicateDraft) and middle.inputName.value == "sensor"
    assert isinstance(right, _PredicateDraft) and right.inputName.value == "load"
    assert isinstance(draft.consequent, _AffineDraft)
    assert draft.consequent.intercept.value == 0.25
    assert [(name.value, value.value) for name, value in draft.consequent.coefficients] == [
        ("load", -0.0), ("risk", 0.75),
    ]
    assert copysign(1.0, draft.consequent.coefficients[0][1].value) == -1.0


def test_GroupedSameOperatorIsNotFlattened() -> None:
    """Retain a nested junction while flattening a plain chain in order."""

    plain = _ParseRule(_PREFIX + b" AND ".join([_PREDICATE] * 3) + _SUFFIX)
    grouped = _ParseRule(_PREFIX + _PREDICATE + b" AND (" + b" AND ".join([_PREDICATE] * 2) + b")" + _SUFFIX)
    assert isinstance(plain.antecedent, _JunctionDraft) and len(plain.antecedent.operands) == 3
    assert isinstance(grouped.antecedent, _JunctionDraft) and len(grouped.antecedent.operands) == 2
    child = grouped.antecedent.operands[1]
    assert isinstance(child, _JunctionDraft) and len(child.operands) == 2
    assert isinstance(grouped.consequent, _TermDraft)
    assert grouped.consequent.termName.value == "Urgent"


def test_ConstantAndEmptyAffineRemainDistinct() -> None:
    """Keep AFFINE(0) affine, including when its intercept is signed zero."""

    constant = _ParseRule(_PREFIX + _PREDICATE + b" THEN CONSTANT 0 WEIGHT 1")
    affine = _ParseRule(_PREFIX + _PREDICATE + b" THEN AFFINE(-0) WEIGHT -0")
    assert isinstance(constant.consequent, _ConstantDraft) and constant.consequent.output.value == 0.0
    assert isinstance(affine.consequent, _AffineDraft) and not affine.consequent.coefficients
    assert copysign(1.0, affine.consequent.intercept.value) == -1.0
    assert copysign(1.0, affine.weight.value) == -1.0


def test_DiagnosticsUseUtf8OffsetsIncludingEof() -> None:
    """Identify the offending token after multibyte names or at input end."""

    prefix = 'RULE R "温度" IF "环境" IS "高" THEN '.encode()
    source = prefix + b'TERM "Alarm" WEIGHT'
    _AssertFailure(source, "malformed-input", len(source))
    source = prefix + b'TERM "Alarm" WEIGHT 1 EXTRA'
    _AssertFailure(source, "malformed-input", source.index(b"EXTRA"))
    source = prefix + b'TERM "Alarm" WEIGHT 1.01'
    _AssertFailure(source, "invalid-rule-semantics", source.index(b"1.01"))
    source = prefix + b'AFFINE(0, "risk": 1, "risk": 2) WEIGHT 1'
    _AssertFailure(source, "invalid-rule-semantics", source.rindex(b'"risk"'))
    source = prefix + b'TERM "Alarm" WEIGHT 1e-999'
    _AssertFailure(source, "malformed-input", source.index(b"1e-999"))


def test_PendingAndEmittedDepthHaveSeparateLimits() -> None:
    """Accept exactly 64 groups or path nodes and reject the first excess."""

    _ParseRule(_PREFIX + b"(" * 64 + _PREDICATE + b")" * 64 + _SUFFIX)
    _AssertFailure(_PREFIX + b"(" * 65 + _PREDICATE + b")" * 65 + _SUFFIX, "exceeded-limit", len(_PREFIX) + 64)
    _ParseRule(_PREFIX + b"NOT " * 63 + _PREDICATE + _SUFFIX)
    source = _PREFIX + b"NOT " * 64 + _PREDICATE + _SUFFIX
    _AssertFailure(source, "exceeded-limit", len(_PREFIX) + 64 * len(b"NOT "))


def test_SeededUnsupportedOperatorsAndTrailingTokens() -> None:
    """Reject operator substitutions and trailing word tokens deterministically."""

    generator = Random(415)
    operators = (b"XOR", b"NOR", b"NOTHING", b"ORWARD", b"&&", b"+", b"__import__")
    leading = _PREFIX + _PREDICATE + b" "

    for _ in range(100):
        word = generator.choice(operators)
        _AssertFailure(leading + word + b" " + _PREDICATE + _SUFFIX, "malformed-input", len(leading))

    complete = _PREFIX + _PREDICATE + _SUFFIX + b" "
    _AssertFailure(complete + b"RULE", "malformed-input", len(complete))
