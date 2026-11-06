# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Bounded parsing of a single readable rule into immutable draft data.

The parser does not resolve model names, evaluate expressions or construct
runtime rules. Canonical output limits are checked by the later binding stage.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from fuzzyroutines._rule_lexer import _LexRule, _RuleLexError, _RuleToken, _TokenKind

_MAX_DEPTH = 64

type _RuleErrorCategory = Literal["malformed-input", "exceeded-limit", "invalid-rule-semantics"]
type _AntecedentDraft = _PredicateDraft | _NegationDraft | _JunctionDraft
type _ConsequentDraft = _TermDraft | _ConstantDraft | _AffineDraft


class _RuleParseError(ValueError):
    """A draft parsing failure with a category and zero-based UTF-8 offset."""

    def __init__(self, category: _RuleErrorCategory, offset: int, message: str) -> None:
        """Store the category and offset independently of the wording."""

        super().__init__(message)
        self.category = category
        self.offset = offset


@dataclass(frozen=True, slots=True)
class _LocatedValue[Value]:
    """An inert value and the half-open UTF-8 byte span of its source token."""

    value: Value
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class _PredicateDraft:
    """An exact input name and term name, before model resolution."""

    inputName: _LocatedValue[str]
    termName: _LocatedValue[str]
    start: int


@dataclass(frozen=True, slots=True)
class _NegationDraft:
    """One explicit NOT and its operand, with the operator's byte offset."""

    operand: _AntecedentDraft
    start: int


@dataclass(frozen=True, slots=True)
class _JunctionDraft:
    """Ordered AND or OR operands with explicitly grouped subtrees intact."""

    operator: Literal["AND", "OR"]
    operands: tuple[_AntecedentDraft, ...]
    start: int


@dataclass(frozen=True, slots=True)
class _TermDraft:
    """The exact name of a Mamdani output term."""

    termName: _LocatedValue[str]


@dataclass(frozen=True, slots=True)
class _ConstantDraft:
    """A finite binary64 Sugeno constant with its source span."""

    output: _LocatedValue[float]


@dataclass(frozen=True, slots=True)
class _AffineDraft:
    """A finite binary64 intercept and ordered, uniquely named coefficients."""

    intercept: _LocatedValue[float]
    coefficients: tuple[tuple[_LocatedValue[str], _LocatedValue[float]], ...]


@dataclass(frozen=True, slots=True)
class _RuleDraft:
    """A complete but unbound rule preserving its ordered source structure."""

    identifier: _LocatedValue[str]
    name: _LocatedValue[str]
    antecedent: _AntecedentDraft
    consequent: _ConsequentDraft
    weight: _LocatedValue[float]
    sourceEnd: int | None


def _ValidateAntecedentDepth(root: _AntecedentDraft) -> None:
    """Reject the first node on an emitted path longer than 64 nodes."""

    pending = [(root, 1)]

    while pending:
        node, depth = pending.pop()

        if depth > _MAX_DEPTH:
            raise _RuleParseError("exceeded-limit", node.start, "Antecedent exceeds the 64-node path limit.")

        if isinstance(node, _NegationDraft):
            pending.append((node.operand, depth + 1))

        elif isinstance(node, _JunctionDraft):
            pending.extend((child, depth + 1) for child in reversed(node.operands))


class _RuleParser:
    """A cursor over the bounded token stream of one source."""

    def __init__(self, tokens: tuple[_RuleToken, ...]) -> None:
        """Initialize the cursor at the first source token."""

        self.tokens = tokens
        self.position = 0

    def Peek(self) -> _RuleToken:
        """Return the next token, including the end sentinel."""

        return self.tokens[self.position]

    def Take(self, kind: _TokenKind, expected: str | None = None) -> _RuleToken:
        """Require and consume a token or fail at its starting byte."""

        token = self.Peek()

        if token.kind != kind or (expected is not None and token.value != expected):
            label = kind if expected is None else repr(expected)
            raise _RuleParseError("malformed-input", token.start, f"Expected {label}.")

        self.position += 1

        return token

    def Text(self, kind: Literal["word", "string"]) -> _LocatedValue[str]:
        """Read an exact word or quoted name with its token span."""

        token = self.Take(kind)
        assert isinstance(token.value, str), "The lexer assigns text to word and string tokens."

        return _LocatedValue(token.value, token.start, token.end)

    def Number(self) -> _LocatedValue[float]:
        """Read a finite binary64 value with its token span."""

        token = self.Take("number")
        assert isinstance(token.value, float), "The lexer assigns binary64 values to number tokens."

        return _LocatedValue(token.value, token.start, token.end)

    def Chain(
        self, pending: int, operator: Literal["AND", "OR"], operand: Callable[[int], _AntecedentDraft],
    ) -> _AntecedentDraft:
        """Collect one unparenthesized chain without flattening child nodes."""

        first = operand(pending)

        if self.Peek().value != operator or self.Peek().kind != "word":
            return first

        operands = [first]

        while self.Peek().kind == "word" and self.Peek().value == operator:
            self.Take("word", operator)
            operands.append(operand(pending))

        return _JunctionDraft(operator, tuple(operands), first.start)

    def Disjunction(self, pending: int) -> _AntecedentDraft:
        """Read OR operands after their tighter-binding conjunctions."""

        return self.Chain(pending, "OR", self.Conjunction)

    def Conjunction(self, pending: int) -> _AntecedentDraft:
        """Read AND operands after their tighter-binding negations."""

        return self.Chain(pending, "AND", self.Negation)

    def Negation(self, pending: int) -> _AntecedentDraft:
        """Read a predicate, grouped expression or prefix NOT."""

        token = self.Peek()
        negated = token.kind == "word" and token.value == "NOT"
        grouped = token.kind == "punctuation" and token.value == "("

        if negated or grouped:
            if pending == _MAX_DEPTH:
                raise _RuleParseError("exceeded-limit", token.start, "Rule exceeds the 64-level nesting limit.")

            self.position += 1

            if negated:
                return _NegationDraft(self.Negation(pending + 1), token.start)

            operand = self.Disjunction(pending + 1)
            self.Take("punctuation", ")")

            return operand

        inputName = self.Text("string")
        self.Take("word", "IS")

        return _PredicateDraft(inputName, self.Text("string"), inputName.start)

    def Consequent(self) -> _ConsequentDraft:
        """Read a TERM, CONSTANT or AFFINE without resolving its model."""

        token = self.Take("word")

        match token.value:
            case "TERM":
                return _TermDraft(self.Text("string"))
            case "CONSTANT":
                return _ConstantDraft(self.Number())
            case "AFFINE":
                return self.Affine()
            case _:
                raise _RuleParseError("malformed-input", token.start, "Expected TERM, CONSTANT, or AFFINE.")

    def Affine(self) -> _AffineDraft:
        """Read an intercept and unique, ordered name-coefficient pairs."""

        self.Take("punctuation", "(")
        intercept = self.Number()
        coefficients = []
        names = set()

        while self.Peek().value == "," and self.Peek().kind == "punctuation":
            self.Take("punctuation", ",")
            name = self.Text("string")
            self.Take("punctuation", ":")
            coefficient = self.Number()

            if name.value in names:
                raise _RuleParseError("invalid-rule-semantics", name.start, "Repeated affine coefficient name.")

            names.add(name.value)
            coefficients.append((name, coefficient))

        self.Take("punctuation", ")")

        return _AffineDraft(intercept, tuple(coefficients))

    def Rule(self) -> _RuleDraft:
        """Require one complete rule with an explicit weight in [0, 1]."""

        self.Take("word", "RULE")
        identifier = self.Text("word")
        name = self.Text("string")
        self.Take("word", "IF")
        antecedent = self.Disjunction(0)
        _ValidateAntecedentDepth(antecedent)
        self.Take("word", "THEN")
        consequent = self.Consequent()
        self.Take("word", "WEIGHT")
        weight = self.Number()
        sourceEnd = self.Take("end").start

        if not 0.0 <= weight.value <= 1.0:
            raise _RuleParseError("invalid-rule-semantics", weight.start, "Rule weight must be in [0, 1].")

        return _RuleDraft(identifier, name, antecedent, consequent, weight, sourceEnd)


def _ParseRule(source: bytes) -> _RuleDraft:
    """Return one immutable rule draft or a byte-addressed diagnostic."""

    try:
        tokens = _LexRule(source)

    except _RuleLexError as error:
        raise _RuleParseError(error.category, error.offset, str(error)) from error

    return _RuleParser(tokens).Rule()
