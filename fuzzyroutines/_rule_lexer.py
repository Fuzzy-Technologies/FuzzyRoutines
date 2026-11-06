# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Bounded UTF-8 lexing for the readable rule grammar.

Tokens carry half-open byte spans and inert values. A parser must enforce
keyword positions, nesting limits, model bindings and canonical output size.
"""

from dataclasses import dataclass
from json import JSONDecodeError, JSONDecoder
from math import isfinite
from re import compile
from typing import Literal

_MAX_BYTES = 65_536
_MAX_TOKENS = 4_096
_WHITESPACE = " \t\r\n"
_PUNCTUATION = "(),:"
_ATOM = compile(r'[^ \t\r\n"(),:]+')
_WORD = compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}")
_NUMBER = compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
_SURROGATE = compile(r"[\ud800-\udfff]")
_STRING_DECODER = JSONDecoder()

type _TokenKind = Literal["word", "number", "string", "punctuation", "end"]
type _ErrorCategory = Literal["malformed-input", "exceeded-limit"]


class _RuleLexError(ValueError):
    """A lexical failure at a zero-based UTF-8 byte offset.

    Attributes:
        category: Stable diagnostic category.
        offset: Start of the offending token, invalid UTF-8 byte, or byte limit.
    """

    def __init__(self, category: _ErrorCategory, offset: int, message: str) -> None:
        """Store the category and source position independently of the wording."""

        super().__init__(message)
        self.category = category
        self.offset = offset


@dataclass(frozen=True, slots=True)
class _RuleToken:
    """An immutable lexical value and its half-open UTF-8 source span.

    A word remains a word even when it spells a keyword. The parser decides
    whether its grammatical position requires an ID or a keyword.
    """

    kind: _TokenKind
    value: str | float | None
    start: int
    end: int


def _ReadString(source: str, position: int, offset: int) -> tuple[str, int]:
    """Decode one JSON string and validate its name constraints."""

    try:
        value, end = _STRING_DECODER.raw_decode(source, position)

    except JSONDecodeError as error:
        raise _RuleLexError("malformed-input", offset, "Invalid JSON string.") from error

    assert isinstance(value, str), "A quoted JSON token must decode to a string."

    if _SURROGATE.search(value) or not value.strip():
        raise _RuleLexError("malformed-input", offset, "Expected a nonblank Unicode scalar string.")

    if len(value) > 256:
        raise _RuleLexError("exceeded-limit", offset, "Rule name exceeds 256 code points.")

    return value, end


def _ReadAtom(atom: str, offset: int) -> tuple[_TokenKind, str | float]:
    """Classify a complete word or round a JSON number to finite binary64."""

    if _WORD.fullmatch(atom):
        return "word", atom

    if not _NUMBER.fullmatch(atom):
        raise _RuleLexError("malformed-input", offset, "Expected a rule ID, keyword, or JSON number.")

    value = float(atom)

    if not isfinite(value):
        raise _RuleLexError("malformed-input", offset, "Rule number overflows binary64.")

    if value == 0.0:
        significand = atom.lower().partition("e")[0]

        if any("1" <= digit <= "9" for digit in significand):
            raise _RuleLexError("malformed-input", offset, "Nonzero rule number rounds to zero.")

    return "number", value


def _LexRule(source: bytes) -> tuple[_RuleToken, ...]:
    """Return complete inert tokens followed by a zero-width end token.

    Args:
        source: UTF-8 rule text, at most 65,536 encoded bytes.

    Returns:
        At most 4,096 lexical tokens plus the end token, in source order.

    Raises:
        _RuleLexError: Invalid UTF-8, a malformed token, or a lexical limit.
    """

    if len(source) > _MAX_BYTES:
        raise _RuleLexError("exceeded-limit", _MAX_BYTES, "Rule exceeds the 65,536-byte limit.")

    try:
        text = source.decode("utf-8")

    except UnicodeDecodeError as error:
        raise _RuleLexError("malformed-input", error.start, "Invalid UTF-8 in rule.") from error

    tokens: list[_RuleToken] = []
    position = 0
    offset = 0

    while position < len(text):
        character = text[position]

        if character in _WHITESPACE:
            position += 1
            offset += 1
            continue

        if len(tokens) == _MAX_TOKENS:
            raise _RuleLexError("exceeded-limit", offset, "Rule exceeds the 4,096-token limit.")

        kind: _TokenKind
        value: str | float

        if character == '"':
            kind = "string"
            value, end = _ReadString(text, position, offset)

        elif character in _PUNCTUATION:
            kind, value, end = "punctuation", character, position + 1

        else:
            atom = _ATOM.match(text, position)
            assert atom is not None, "A nonseparator starts an atom."
            kind, value = _ReadAtom(atom[0], offset)
            end = atom.end()

        byteEnd = offset + len(text[position:end].encode("utf-8"))
        tokens.append(_RuleToken(kind, value, offset, byteEnd))
        position = end
        offset = byteEnd

    tokens.append(_RuleToken("end", None, offset, offset))

    return tuple(tokens)
