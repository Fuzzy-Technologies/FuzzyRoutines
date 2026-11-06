# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Strict JSON wire parsing, binary64 conversion and allocation limits."""

from math import copysign

import pytest

from fuzzyroutines._config_json import (
    DecodeConfigJson,
    JsonConfigParseError,
    JsonNumber,
)


def test_DecodesUtf8AndPreservesExactNumberSpelling():
    """Preserve names, array order, signed zero and exact numeric source tokens."""

    decoded = DecodeConfigJson('{"шкала": [-0, 9007199254740993, "\\ud83d\\ude80", true, null]}'.encode())

    assert decoded == {
        "шкала": [JsonNumber("-0", -0.0), JsonNumber("9007199254740993", 9007199254740992.0), "🚀", True, None],
    }, "The wire tree must retain exact numeric tokens and decoded Unicode."
    negativeZero = DecodeConfigJson(b"-0")
    assert isinstance(negativeZero, JsonNumber) and copysign(1.0, negativeZero.binary64) < 0, (
        "Binary64 conversion must preserve negative zero."
    )


@pytest.mark.parametrize(
    ("encoded", "pointer"),
    [
        (b'{"a/b~c": [{"same": 1, "\\u0073ame": 2}]}', "/a~1b~0c/0/same"),
        (b'{"member":"\\ud800"}', "/member"),
        (b'{"\\udc00":0}', ""),
        (b'{"member":"\xff"}', ""),
        (b"\xef\xbb\xbf{}", ""),
        (b'{"value":NaN}', "/value"),
        (b'{"value":Infinity}', "/value"),
        (b'{"value":-Infinity}', "/value"),
        (b'{"value":1e309}', "/value"),
        (b'{"value":-1e-999}', "/value"),
        (b"[1,]", "/1"),
        (b'{"value":1,}', ""),
        (b"01", ""),
        (b"{} {}", ""),
        (b"\x0b{}", ""),
        (b"{1:null}", ""),
    ],
)
def test_RejectsMalformedDataWithEscapedPointer(encoded, pointer):
    """Reject unsafe syntax and numbers at the precise known wire location."""

    with pytest.raises(JsonConfigParseError) as failure:
        DecodeConfigJson(encoded)

    assert failure.value.pointer == pointer, "The diagnostic must identify the malformed input."
    assert failure.value.category == "malformed-document", "Syntax errors belong to the parsing phase."


def test_AcceptsMinimumSubnormalAndExactZeroWithAnExponent():
    """Distinguish binary64 subnormals and true zero from rounded-away numbers."""

    assert DecodeConfigJson(b"[5e-324, -0.0e-999]") == [
        JsonNumber("5e-324", 5e-324), JsonNumber("-0.0e-999", -0.0),
    ], "Representable subnormals and exact zero must survive the numeric guard."


def test_EnforcesExactEncodedByteBoundary():
    """Accept one MiB exactly and reject one additional encoded byte."""

    boundary = b" " * (1_048_576 - 2) + b"{}"
    assert DecodeConfigJson(boundary) == {}, "Exactly 1,048,576 bytes must be accepted."

    with pytest.raises(JsonConfigParseError, match="byte limit"):
        DecodeConfigJson(boundary + b" ")


def test_EnforcesDepthBeforeDescending():
    """Accept 96 containers and reject the 97th at its wire path."""

    boundary = b"[" * 96 + b"]" * 96
    DecodeConfigJson(boundary)

    with pytest.raises(JsonConfigParseError, match="nesting limit") as failure:
        DecodeConfigJson(b"[" + boundary + b"]")

    assert failure.value.pointer == "/0" * 96, "The 97th container must be rejected before parsing its children."


def test_EnforcesNodeBudgetIncludingObjectKeys():
    """Count object keys, scalar values, and containers against the same limit."""

    values = b"null," * 65_531 + b"null"
    boundary = b'{"key":[[], ' + values + b"]}"
    DecodeConfigJson(boundary)

    with pytest.raises(JsonConfigParseError, match="node limit") as failure:
        DecodeConfigJson(b'{"key":[[], ' + values + b",null]}")

    assert failure.value.pointer == "/key/65533", "The node budget must count the object key and all containers."


@pytest.mark.parametrize("inline", (False, True))
def test_BoundsAntecedentDepthBeforeBuildingItsObject(inline):
    """Count condition nodes through unary and array edges in both envelope paths."""

    from json import dumps

    expression = {"kind": "term", "input": "risk", "term": "high"}
    current = expression

    for _ in range(62):
        current = {"kind": "not", "operand": current}

    antecedent = {"kind": "all", "operands": [current, expression]}
    model = {"inference": {"rules": [{"antecedent": antecedent}]}}
    document = {"models": {"sample": model}} if inline else model
    DecodeConfigJson(dumps(document).encode())

    antecedent["operands"][0] = {"kind": "not", "operand": current}

    with pytest.raises(JsonConfigParseError, match="64-node antecedent") as failure:
        DecodeConfigJson(dumps(document).encode())

    prefix = "/models/sample" if inline else ""
    assert failure.value.pointer == prefix + "/inference/rules/0/antecedent/operands/0" + "/operand" * 63, (
        "The parser must stop at the first condition deeper than 64 nodes."
    )
