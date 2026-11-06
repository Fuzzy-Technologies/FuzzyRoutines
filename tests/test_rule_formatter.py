# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Canonical rule round trips and output limits."""

from dataclasses import replace
from math import isfinite
from random import Random
from struct import pack, unpack

from fuzzyroutines._rule_formatter import _FormatRule, _RuleFormatError, _RuleNumber
from fuzzyroutines._rule_parser import _JunctionDraft, _ParseRule

_PREFIX = b'RULE r "R" IF "risk" IS "High" THEN AFFINE(0'
_SUFFIX = b') WEIGHT 1'


def _AssertCanonicalLimit(source: bytes, offset: int | None) -> None:
    """Require the canonical limit diagnostic without returning partial text."""

    draft = _ParseRule(source)

    if offset is None:
        draft = replace(draft, sourceEnd=None)

    try:
        _FormatRule(draft)

    except _RuleFormatError as error:
        assert error.category == "exceeded-limit"
        assert error.offset == offset
        assert "Canonical rule" in str(error)
        return

    raise AssertionError("Expected the canonical representation to exceed a limit.")


def _CompactAffine(trim: int) -> bytes:
    """Construct the ADR byte witness with a controlled first-name length."""

    pairs = [
        f',"x{index:03d}{"a" * (246 - (trim if index == 0 else 0))}":0'.encode()
        for index in range(255)
    ]

    return _PREFIX + b"".join(pairs) + _SUFFIX


def test_CanonicalByteLimitIncludesSpacesAndFinalLf() -> None:
    """Accept 65,536 bytes and reject 65,537 or the original 65,590."""

    original = _CompactAffine(0)
    assert len(original) == 65_079
    _AssertCanonicalLimit(original, len(original))
    oneOver = _CompactAffine(53)
    _AssertCanonicalLimit(oneOver, len(oneOver))
    _AssertCanonicalLimit(oneOver, None)
    canonical = _FormatRule(_ParseRule(_CompactAffine(54)))
    assert len(canonical) == 65_536 and canonical.endswith(b"\n")
    assert _FormatRule(_ParseRule(canonical)) == canonical


def test_CanonicalGroupingAndAffineOrderRoundTrip() -> None:
    """Retain both required precedence and explicit same-operator grouping."""

    source = (
        ' RULE\tNOT "温度" IF NOT ("z" IS "Low" OR "a" IS "High") AND '
        '("b" IS "High" AND "c" IS "Low") THEN AFFINE(0.0,"z":-0.0,"a":0.25) WEIGHT 1.0 '
    )
    expected = (
        'RULE NOT "温度" IF NOT ("z" IS "Low" OR "a" IS "High") AND '
        '("b" IS "High" AND "c" IS "Low") THEN AFFINE(0, "z": -0, "a": 0.25) WEIGHT 1\n'
    )
    canonical = _FormatRule(_ParseRule(source.encode()))
    assert canonical == expected.encode()
    reparsed = _ParseRule(canonical)
    assert isinstance(reparsed.antecedent, _JunctionDraft)
    assert isinstance(reparsed.antecedent.operands[1], _JunctionDraft)
    assert _FormatRule(reparsed) == canonical


def test_PrintableUnicodeAndJsonEscapesAreCanonical() -> None:
    """Keep printable names literal and escape quotes and control characters."""

    source = r'RULE r "\u6e29\u5ea6\"\\\t\u0085\udb40\udc01" IF "x" IS "Low" THEN TERM "A" WEIGHT 1'.encode()
    canonical = _FormatRule(_ParseRule(source))
    expected = 'RULE r "温度' + r'\"\\\t\u0085\udb40\udc01" IF "x" IS "Low" THEN TERM "A" WEIGHT 1' + "\n"
    assert canonical == expected.encode()
    assert _ParseRule(canonical).name.value == _ParseRule(source).name.value


def test_CanonicalNumbersRoundTripBinary64BitPatterns() -> None:
    """Preserve binary64 bit patterns and prefer the shorter decimal spelling."""

    assert _RuleNumber(0.0) == "0"
    assert _RuleNumber(-0.0) == "-0"
    assert _RuleNumber(100.0) == "100"
    assert _RuleNumber(0.0001) == "1e-4"
    assert _RuleNumber(1.234e16) == "1234e13"
    generator = Random(415)

    for _ in range(500):
        bits = generator.getrandbits(64).to_bytes(8, "big")
        value, = unpack(">d", bits)

        if isfinite(value):
            token = _RuleNumber(value)
            assert pack(">d", float(token)) == bits
            source = _PREFIX + b',"x":' + token.encode() + _SUFFIX
            canonical = _FormatRule(_ParseRule(source))
            assert _FormatRule(_ParseRule(canonical)) == canonical


def test_CanonicalTokenLimitCountsGrammarTokensOnly() -> None:
    """Exclude whitespace from the token budget and reject a longer chain."""

    source = b'RULE r "R" IF "risk" IS "High" THEN TERM "A" WEIGHT 1'
    draft = _ParseRule(source)
    predicate = draft.antecedent
    junction = _JunctionDraft("AND", (predicate,) * 1_022, predicate.start)
    bounded = replace(draft, antecedent=junction, sourceEnd=None)
    canonical = _FormatRule(bounded)
    assert _FormatRule(_ParseRule(canonical)) == canonical
    tooMany = replace(bounded, antecedent=replace(junction, operands=(*junction.operands, predicate)))

    try:
        _FormatRule(tooMany)

    except _RuleFormatError as error:
        assert error.offset is None and "4,096-token" in str(error)
        return

    raise AssertionError("Expected canonical token overflow.")
