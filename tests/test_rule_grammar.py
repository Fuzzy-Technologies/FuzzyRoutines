# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Public readable-rule parsing, formatting and standalone model binding."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from fuzzyroutines.configuration import LoadModel, SugenoBinding
from fuzzyroutines.inference import AffineConsequent, SugenoRule, TermCondition
from fuzzyroutines.rule_grammar import BindRule, FormatRule, ParseRule, RuleTextError

_FIXTURE = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "config-v1" / "fixtures" / "valid-project.json"


def test_PublicRoundTripPreservesSpansAndCanonicalBytes() -> None:
    """Retain the exact half-open byte spans, signed zero and original spelling."""

    source = 'RULE next "温度" IF "Risk" IS "High" THEN AFFINE(0,"Risk":-0) WEIGHT 1'.encode()
    draft = ParseRule(source)
    assert draft.identifier == "next" and draft.name == "温度"
    start, end = draft.identifierSpan
    assert source[start:end] == b"next"
    start, end = draft.nameSpan
    assert source[start:end] == '"温度"'.encode()
    canonical = FormatRule(draft)
    assert canonical == source.replace(b',"Risk":-0', b', "Risk": -0') + b"\n"
    assert FormatRule(ParseRule(canonical)) == canonical


def test_PublicMalformedAndCanonicalErrorsRetainOriginalOffsets() -> None:
    """Report hostile tokens and expanded-output overflow at their source bytes."""

    prefix = 'RULE next "温度" IF "Risk" IS "High" '.encode()
    source = prefix + b'+ "More" THEN CONSTANT 0 WEIGHT 1'

    with pytest.raises(RuleTextError) as malformed:
        ParseRule(source)

    assert (malformed.value.category, malformed.value.offset) == ("malformed-input", len(prefix))
    pairs = b"".join(f',"x{index:03d}{"a" * 246}":0'.encode() for index in range(255))
    compact = b'RULE r "R" IF "Risk" IS "High" THEN AFFINE(0' + pairs + b") WEIGHT 1"
    draft = ParseRule(compact)

    with pytest.raises(RuleTextError) as overflow:
        FormatRule(draft)

    assert (overflow.value.category, overflow.value.offset) == ("exceeded-limit", len(compact))


def test_PublicBindingPreservesConfiguredIdsAndScalarParity() -> None:
    """Resolve exact names, preserve the model and return independently owned wire data."""

    pytest.importorskip("jsonschema")
    document = json.loads(_FIXTURE.read_bytes())["models"]["weighted"]
    configuration = LoadModel(json.dumps(document).encode())
    inference = configuration.inference
    assert isinstance(inference, SugenoBinding)
    source = 'RULE next "温度" IF "Risk" IS "High" THEN AFFINE(0.25,"Risk":0.5) WEIGHT 1'.encode()
    bound = BindRule(ParseRule(source), configuration)
    assert isinstance(bound.rule, SugenoRule)
    reference = SugenoRule("温度", TermCondition("Risk", "High"), AffineConsequent(0.25, (("Risk", 0.5),)), 1)
    assert bound.rule == reference
    assert bound.ToWire() == {
        "id": "next", "name": "温度", "weight": 1.0,
        "antecedent": {"kind": "term", "input": "risk", "term": "high"},
        "consequent": {"kind": "affine", "intercept": 0.25, "coefficients": [{"input": "risk", "value": 0.5}]},
    }
    wire = bound.ToWire()
    antecedent = wire["antecedent"]
    assert isinstance(antecedent, dict)
    antecedent["term"] = "different"
    assert bound.ToWire()["antecedent"] == {"kind": "term", "input": "risk", "term": "high"}
    actual = replace(inference.model, rules=(bound.rule,)).Evaluate({"Risk": 0.25})
    expected = replace(inference.model, rules=(reference,)).Evaluate({"Risk": 0.25})
    assert actual == expected and actual.value == 0.375
    assert inference.ruleIds == ("base", "increase")
    unknown = source.replace(b'"Risk" IS', b'"risk" IS')

    with pytest.raises(RuleTextError) as unresolved:
        BindRule(ParseRule(unknown), configuration)

    assert unresolved.value.category == "unresolved-binding"
    assert unresolved.value.offset == unknown.index(b'"risk"')
