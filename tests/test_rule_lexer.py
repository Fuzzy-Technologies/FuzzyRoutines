# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Lexical rule diagnostics, exact token spans and input limits."""

from math import copysign
from random import Random

from fuzzyroutines._rule_lexer import _LexRule, _RuleLexError


def _AssertFailure(source: bytes, category: str, offset: int) -> None:
    """Check the diagnostic without accepting partial tokens."""

    try:
        _LexRule(source)

    except _RuleLexError as error:
        assert (error.category, error.offset) == (category, offset)
        return

    raise AssertionError("Expected lexing to fail.")


def test_CompleteWordsAndExactUtf8Spans() -> None:
    """Keep keyword-like words intact and preserve quoted Unicode values."""

    source = 'RULE NOT "风险\\uD83D\\uDE00" IF NOTHING("量": -0)\r\n'.encode()
    tokens = _LexRule(source)
    assert [(token.kind, token.value) for token in tokens[:-1]] == [
        ("word", "RULE"),
        ("word", "NOT"),
        ("string", "风险😀"),
        ("word", "IF"),
        ("word", "NOTHING"),
        ("punctuation", "("),
        ("string", "量"),
        ("punctuation", ":"),
        ("number", -0.0),
        ("punctuation", ")"),
    ]
    assert source[tokens[6].start:tokens[6].end] == '"量"'.encode()
    value = tokens[8].value
    assert isinstance(value, float) and copysign(1.0, value) == -1.0
    assert tokens[-1].kind == "end" and tokens[-1].start == tokens[-1].end == len(source)


def test_MalformedInputReportsTheStartOfTheToken() -> None:
    """Reject incomplete numbers, unsafe text, comments and bad string data."""

    prefix = '"温度" '.encode()

    for token in (
        b"01", b"1.2e", b"1-2", b"1IF", b"1e309", b"1e-999", b"1+2",
        b"//comment", b"#comment", b'""', b'"  "', b'"\\ud800"', b'"\\x00"', b'"\x00"',
        b"__import__", b"pkg.module", b"[1]", "\u00a0".encode(),
    ):
        _AssertFailure(prefix + token, "malformed-input", len(prefix))

    _AssertFailure(prefix + b"\xff", "malformed-input", len(prefix))


def test_LexicalLimitsAcceptTheBoundaryAndRejectTheFirstExcess() -> None:
    """Count encoded bytes, real tokens, and decoded code points separately."""

    assert _LexRule(b" " * 65_536)[-1].start == 65_536
    _AssertFailure(b" " * 65_537, "exceeded-limit", 65_536)
    assert len(_LexRule(b"()" * 2_048)) == 4_097
    _AssertFailure(b"()" * 2_048 + b" (", "exceeded-limit", 4_097)
    assert _LexRule(('"' + "😀" * 256 + '"').encode())[0].value == "😀" * 256
    _AssertFailure(('"' + "😀" * 257 + '"').encode(), "exceeded-limit", 0)


def test_SeededIllegalTokensNeverBecomeLegalPrefixes() -> None:
    """Reject complete corrupted atoms at their true position."""

    generator = Random(415)

    for _ in range(100):
        number = str(generator.randrange(100_000)).encode()
        prefix = ('"é" ' + " " * generator.randrange(10)).encode()
        suffix = generator.choice((b"AND", b"_", b"#", b".", b"+", b"/"))
        _AssertFailure(prefix + number + suffix, "malformed-input", len(prefix))
