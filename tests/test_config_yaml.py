# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Wire-level tests for the optional bounded YAML event reader."""

from importlib.util import find_spec
from math import copysign
from unittest import SkipTest

from fuzzyroutines._config_json import DecodeConfigJson, JsonConfigParseError, JsonNumber, JsonValue


def _DecodeYaml(encoded: bytes) -> JsonValue:
    """Use the optional backend when the test environment supplies it."""

    if find_spec("yaml") is None:
        raise SkipTest("The YAML parser checkpoint requires PyYAML.")

    from fuzzyroutines._config_yaml import DecodeConfigYaml

    return DecodeConfigYaml(encoded)


def test_DecodesJsonSemanticsAndExactNumericTokens():
    """Keep JSON-compatible values, Unicode keys, and exact number spellings."""

    yaml = '"шкала": [-0, 9007199254740993, "🚀", true, null, "on", "${HOME}"]'.encode()
    json = '{"шкала":[-0,9007199254740993,"🚀",true,null,"on","${HOME}"]}'.encode()

    assert _DecodeYaml(yaml) == DecodeConfigJson(json), "YAML and JSON must produce equivalent wire trees."
    negativeZero = _DecodeYaml(b"-0")
    assert isinstance(negativeZero, JsonNumber) and copysign(1, negativeZero.binary64) == -1, (
        "YAML must preserve negative zero."
    )


def _Reject(encoded: bytes, pointer: str, message: str) -> None:
    """Require a stable wire diagnostic for one malformed YAML input."""

    try:
        _DecodeYaml(encoded)

    except JsonConfigParseError as failure:
        assert failure.pointer == pointer, f"Expected {pointer!r} for {encoded[:60]!r}, got {failure.pointer!r}."
        assert failure.category == "malformed-document", "YAML syntax failures must use the JSON wire category."
        assert message in str(failure), "YAML diagnostics must identify the failed guard."

    else:
        raise AssertionError(f"Unsafe YAML was accepted: {encoded[:60]!r}.")


def test_RejectsConstructionAndAmbiguousScalarsAtTheirPath():
    """Reject unsafe YAML features, duplicate keys, and non-JSON values."""

    cases = (
        (b'"a/b~c": [{same: 1, "same": 2}]', "/a~1b~0c/0/same", "Duplicate"),
        (b"entry: !!python/name:os.system ''", "/entry", "tags"),
        (b"entry: !include elsewhere.yml", "/entry", "tags"),
        (b"entry: &anchor [1]", "/entry", "anchors"),
        (b"entry: *anchor", "/entry", "aliases"),
        (b"entry: {<<: {sample: 1}}", "/entry/<<", "merge keys"),
        (b"entry: {1: a}", "/entry", "keys"),
        (b"entry: {[1, 2]: a}", "/entry", "keys"),
        (b"entry: .Inf", "/entry", "non-JSON"),
        (b"entry: 2026-11-06", "/entry", "non-JSON"),
        (b"entry: 012", "/entry", "non-JSON"),
        (b"entry: true\n---\nentry: false", "", "only one"),
        (b"%YAML 1.1\n---\nentry: false", "", "directives"),
        (b"entry: 1e309", "/entry", "overflows"),
        (b"entry: -1e-999", "/entry", "rounds to zero"),
        (b'entry: "\\uD800"', "/entry", "surrogate"),
        (b"entry: \xff", "", "UTF-8"),
        (b"\xef\xbb\xbf{}", "", "byte-order mark"),
    )

    for encoded, pointer, message in cases:
        _Reject(encoded, pointer, message)


def test_EnforcesExactStructuralBoundaries():
    """Reject input before a recursive or oversized tree can be created."""

    boundary = b" " * (1_048_576 - 2) + b"{}"
    assert _DecodeYaml(boundary) == {}, "Exactly 1,048,576 encoded bytes must be accepted."
    _Reject(boundary + b" ", "", "byte limit")
    depthBoundary = b"[" * 96 + b"]" * 96
    assert _DecodeYaml(depthBoundary) == DecodeConfigJson(depthBoundary), "Exactly 96 containers must be accepted."
    _Reject(b"[" + depthBoundary + b"]", "/0" * 96, "nesting limit")
    nodeBoundary = b"[" + b"null," * 65_534 + b"null"
    assert _DecodeYaml(nodeBoundary + b"]") == [None] * 65_535, "A list and its elements count against one budget."
    _Reject(nodeBoundary + b",null]", "/65535", "node limit")


def test_ReadsBlockCollectionsAndRejectsDeepAntecedents():
    """Handle readable block collections and keep the rule-depth boundary."""

    block = b"models:\n  sample:\n    values:\n      - 1.0\n      - false\n"
    assert _DecodeYaml(block) == DecodeConfigJson(b'{"models":{"sample":{"values":[1.0,false]}}}'), (
        "Block YAML must preserve the same shape and scalar types as JSON."
    )
    root = b"{inference: {rules: [{antecedent: "
    condition = b"{operand: " * 63 + b"{kind: term}" + b"}" * 63
    tail = b"}]}}"
    _DecodeYaml(root + condition + tail)
    _Reject(root + b"{operand: " + condition + b"}" + tail, "/inference/rules/0/antecedent" + "/operand" * 64, "64-node")
