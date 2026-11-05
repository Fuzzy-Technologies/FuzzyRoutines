# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Bounded JSON decoding for the versioned configuration wire format.

This private parsing stage constructs data only. Envelope validation and
runtime object construction are separate stages.
"""

from dataclasses import dataclass
from json import JSONDecodeError, JSONDecoder
from math import isfinite
from re import compile

_MAX_BYTES = 1_048_576
_MAX_DEPTH = 96
_MAX_NODES = 65_536
_WHITESPACE = compile(r"[ \t\r\n]*")
_NUMBER = compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
_SURROGATE = compile(r"[\ud800-\udfff]")
_STRING_DECODER = JSONDecoder()


@dataclass(frozen=True, slots=True)
class JsonNumber:
    """A JSON number with its exact spelling and checked binary64 value.

    Schema-aware validation can use the exact spelling to validate integral
    fields without first rounding them to binary64.
    """

    token: str
    binary64: float


type JsonValue = None | bool | str | JsonNumber | list[JsonValue] | dict[str, JsonValue]
type _Path = tuple[str | int, ...]


class JsonConfigParseError(ValueError):
    """Malformed or unsafe wire data with an RFC 6901 diagnostic pointer."""

    category = "malformed-document"

    def __init__(self, message: str, pointer: str = "") -> None:
        """Retain the parser diagnostic and its source location."""

        super().__init__(message)
        self.pointer = pointer


class _JsonReader:
    """Cursor over one UTF-8 document with bounded structural allocations."""

    def __init__(self, source: str) -> None:
        """Initialize the cursor and the shared structural node budget."""

        self.source = source
        self.position = 0
        self.nodes = 0

    def Error(self, message: str, path: _Path) -> JsonConfigParseError:
        """Attach an escaped pointer to the current diagnostic."""

        pointer = "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in path)

        return JsonConfigParseError(message, pointer)

    def CountNode(self, path: _Path) -> None:
        """Reserve capacity for a JSON value or an object key."""

        self.nodes += 1

        if self.nodes > _MAX_NODES:
            raise self.Error("JSON exceeds the 65,536-node limit.", path)

    def Peek(self) -> str:
        """Skip only JSON whitespace and inspect the next character."""

        whitespace = _WHITESPACE.match(self.source, self.position)
        assert whitespace is not None, "The whitespace pattern must match empty input."
        self.position = whitespace.end()

        return self.source[self.position:self.position + 1]

    def ReadString(self, path: _Path) -> str:
        """Decode one quoted string and reject unpaired surrogate escapes."""

        try:
            value, self.position = _STRING_DECODER.raw_decode(self.source, self.position)

        except (JSONDecodeError, UnicodeDecodeError) as error:
            raise self.Error("Invalid JSON string.", path) from error

        assert isinstance(value, str), "A quoted JSON token must decode to a string."

        if _SURROGATE.search(value):
            raise self.Error("Unpaired Unicode surrogate in JSON string.", path)

        return value

    def ReadValue(self, path: _Path, depth: int) -> JsonValue:
        """Decode one value after reserving its node and container depth."""

        self.CountNode(path)
        character = self.Peek()

        if character in ("{", "["):
            if depth >= _MAX_DEPTH:
                raise self.Error("JSON exceeds the 96-container nesting limit.", path)

            self.position += 1

            if character == "{":
                return self.ReadObject(path, depth + 1)

            return self.ReadArray(path, depth + 1)

        if character == '"':
            return self.ReadString(path)

        for token, value in (("true", True), ("false", False), ("null", None)):
            if self.source.startswith(token, self.position):
                self.position += len(token)
                return value

        number = _NUMBER.match(self.source, self.position)

        if number is None:
            raise self.Error("Expected a JSON value.", path)

        self.position = number.end()
        token = number[0]
        binary64 = float(token)

        if not isfinite(binary64):
            raise self.Error("JSON number overflows binary64.", path)

        if binary64 == 0.0:
            significand = token.lower().partition("e")[0]

            if any("1" <= digit <= "9" for digit in significand):
                raise self.Error("Nonzero JSON number rounds to zero.", path)

        return JsonNumber(token, binary64)

    def ReadObject(self, path: _Path, depth: int) -> dict[str, JsonValue]:
        """Decode unique string keys and their values within the node budget."""

        members: dict[str, JsonValue] = {}

        if self.Peek() == "}":
            self.position += 1
            return members

        while True:
            if self.Peek() != '"':
                raise self.Error("Expected a quoted JSON object key.", path)

            self.CountNode(path)
            key = self.ReadString(path)
            memberPath = (*path, key)

            if key in members:
                raise self.Error("Duplicate JSON object key.", memberPath)

            if self.Peek() != ":":
                raise self.Error("Expected ':' after JSON object key.", memberPath)

            self.position += 1
            members[key] = self.ReadValue(memberPath, depth)
            separator = self.Peek()

            if separator == "}":
                self.position += 1
                return members

            if separator != ",":
                raise self.Error("Expected ',' or '}' after JSON object member.", path)

            self.position += 1

    def ReadArray(self, path: _Path, depth: int) -> list[JsonValue]:
        """Decode an ordered array without accepting a trailing comma."""

        values: list[JsonValue] = []

        if self.Peek() == "]":
            self.position += 1
            return values

        while True:
            values.append(self.ReadValue((*path, len(values)), depth))
            separator = self.Peek()

            if separator == "]":
                self.position += 1
                return values

            if separator != ",":
                raise self.Error("Expected ',' or ']' after JSON array element.", path)

            self.position += 1


def DecodeConfigJson(encoded: bytes) -> JsonValue:
    """Decode a bounded UTF-8 JSON document into private wire values.

    Args:
        encoded: At most 1,048,576 bytes of JSON encoded as UTF-8.

    Returns:
        One complete JSON value with number spellings preserved for validation.

    Raises:
        JsonConfigParseError: The document is malformed or exceeds a wire limit.
    """

    if len(encoded) > _MAX_BYTES:
        raise JsonConfigParseError("JSON exceeds the 1,048,576-byte limit.")

    try:
        source = encoded.decode("utf-8")

    except UnicodeDecodeError as error:
        raise JsonConfigParseError("Configuration JSON must be UTF-8.") from error

    reader = _JsonReader(source)
    value = reader.ReadValue((), 0)

    if reader.Peek():
        raise JsonConfigParseError("Unexpected data after the JSON value.")

    return value
