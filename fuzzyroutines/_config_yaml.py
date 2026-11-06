# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Decode a bounded YAML document into the private JSON wire representation.

The optional YAML backend supplies parsing events. No YAML objects are
constructed and project semantics are validated separately.
"""

from collections.abc import Iterator

from yaml import BaseLoader, YAMLError, parse
from yaml.events import (
    AliasEvent,
    CollectionStartEvent,
    DocumentEndEvent,
    DocumentStartEvent,
    Event,
    MappingEndEvent,
    MappingStartEvent,
    ScalarEvent,
    SequenceEndEvent,
    SequenceStartEvent,
    StreamEndEvent,
    StreamStartEvent,
)
from yaml.nodes import ScalarNode
from yaml.resolver import Resolver

from ._config_json import (
    _AntecedentDepth,
    _MAX_ANTECEDENT_DEPTH,
    _MAX_BYTES,
    _MAX_DEPTH,
    _MAX_NODES,
    _NUMBER,
    _SURROGATE,
    ConfigPath,
    ConfigPointer,
    DecodeConfigJson,
    JsonConfigParseError,
    JsonValue,
)

_JSON_LITERALS = {"null": None, "false": False, "true": True}
_STRING_TAG = "tag:yaml.org,2002:str"


def _Error(message: str, path: ConfigPath) -> JsonConfigParseError:
    """Report malformed YAML with the same wire diagnostic as JSON."""

    return JsonConfigParseError(message, ConfigPointer(path))


class _YamlReader:
    """Consume parsing events while bounding the JSON-shaped data tree."""

    def __init__(self, events: Iterator[Event]) -> None:
        """Initialize the event source and the node budget."""

        self.events = events
        self.nodes = 0
        self.resolver = Resolver()

    def Next(self, path: ConfigPath) -> Event:
        """Read the next event and translate syntax errors."""

        try:
            return next(self.events)

        except (YAMLError, StopIteration) as error:
            raise _Error("Invalid YAML syntax.", path) from error

    def CountNode(self, path: ConfigPath) -> None:
        """Reserve capacity for a JSON value or mapping key."""

        self.nodes += 1

        if self.nodes > _MAX_NODES:
            raise _Error("YAML exceeds the 65,536-node limit.", path)

    def Scalar(self, event: ScalarEvent, path: ConfigPath) -> JsonValue:
        """Interpret only JSON plain literals and preserve quoted strings."""

        token = event.value

        if _SURROGATE.search(token):
            raise _Error("Unpaired Unicode surrogate in YAML scalar.", path)

        if event.style is not None:
            return token

        if token in _JSON_LITERALS:
            return _JSON_LITERALS[token]

        if _NUMBER.fullmatch(token):
            try:
                return DecodeConfigJson(token.encode("ascii"))

            except JsonConfigParseError as error:
                raise _Error(str(error), path) from error

        # The backend resolver is used only to reject ambiguous plain
        # spellings. It never selects a constructor or converts a value.
        if self.resolver.resolve(ScalarNode, token, (True, False)) != _STRING_TAG:
            raise _Error("Quote non-JSON YAML scalars to use them as strings.", path)

        return token

    def CheckProperties(self, event: Event, path: ConfigPath) -> None:
        """Reject alias references, anchors, and explicit tags."""

        if isinstance(event, AliasEvent):
            raise _Error("YAML aliases are not supported.", path)

        if isinstance(event, (ScalarEvent, CollectionStartEvent)) and (event.anchor or event.tag):
            raise _Error("YAML anchors and tags are not supported.", path)

    def ReadMapping(self, path: ConfigPath, depth: int) -> dict[str, JsonValue]:
        """Read unique string keys and ordered values without merge keys."""

        result: dict[str, JsonValue] = {}
        keyEvent = self.Next(path)

        while not isinstance(keyEvent, MappingEndEvent):
            self.CountNode(path)
            self.CheckProperties(keyEvent, path)

            if not isinstance(keyEvent, ScalarEvent):
                raise _Error("YAML object keys must be strings.", path)

            keyPath = (*path, keyEvent.value)

            if keyEvent.value == "<<":
                raise _Error("YAML merge keys are not supported.", keyPath)

            key = self.Scalar(keyEvent, path)

            if not isinstance(key, str):
                raise _Error("YAML object keys must be strings.", path)

            if key in result:
                raise _Error("Duplicate YAML object key.", keyPath)

            result[key] = self.ReadValue(self.Next(keyPath), keyPath, depth)
            keyEvent = self.Next(path)

        return result

    def ReadSequence(self, path: ConfigPath, depth: int) -> list[JsonValue]:
        """Read the sequence in source order within the shared node budget."""

        result: list[JsonValue] = []
        itemPath = (*path, 0)
        event = self.Next(itemPath)

        while not isinstance(event, SequenceEndEvent):
            result.append(self.ReadValue(event, itemPath, depth))
            itemPath = (*path, len(result))
            event = self.Next(itemPath)

        return result

    def ReadValue(self, event: Event, path: ConfigPath, depth: int) -> JsonValue:
        """Read a scalar or descend into a container within the wire limits."""

        self.CountNode(path)
        self.CheckProperties(event, path)

        if isinstance(event, ScalarEvent):
            return self.Scalar(event, path)

        if depth >= _MAX_DEPTH:
            raise _Error("YAML exceeds the 96-container nesting limit.", path)

        if isinstance(event, MappingStartEvent):
            if len(path) > _MAX_ANTECEDENT_DEPTH and _AntecedentDepth(path) > _MAX_ANTECEDENT_DEPTH:
                raise _Error("YAML exceeds the 64-node antecedent depth limit.", path)

            return self.ReadMapping(path, depth + 1)

        if isinstance(event, SequenceStartEvent):
            return self.ReadSequence(path, depth + 1)

        raise _Error("Expected one YAML data value.", path)

    def ReadDocument(self) -> JsonValue:
        """Read exactly one document and reject YAML directives."""

        start = self.Next(())
        assert isinstance(start, StreamStartEvent), "The YAML parser must start with a stream."
        document = self.Next(())

        if not isinstance(document, DocumentStartEvent):
            raise _Error("Expected one YAML document.", ())

        if document.version or document.tags:
            raise _Error("YAML directives are not supported.", ())

        result = self.ReadValue(self.Next(()), (), 0)
        end = self.Next(())
        assert isinstance(end, DocumentEndEvent), "A complete YAML value must end its document."

        if not isinstance(self.Next(()), StreamEndEvent):
            raise _Error("Expected only one YAML document.", ())

        return result


def DecodeConfigYaml(encoded: bytes) -> JsonValue:
    """Decode one UTF-8 YAML document into the JSON-shaped v1 wire tree.

    Args:
        encoded: At most 1,048,576 bytes of UTF-8 YAML.

    Returns:
        One value with exact JSON number tokens and source sequence order.

    Raises:
        JsonConfigParseError: The document uses unsafe syntax or violates a wire limit.
    """

    if len(encoded) > _MAX_BYTES:
        raise _Error("YAML exceeds the 1,048,576-byte limit.", ())

    try:
        source = encoded.decode("utf-8")

    except UnicodeDecodeError as error:
        raise _Error("Configuration YAML must be UTF-8.", ()) from error

    if source.startswith("\ufeff"):
        raise _Error("Configuration YAML must not start with a byte-order mark.", ())

    events = parse(source, Loader=BaseLoader)

    try:
        return _YamlReader(events).ReadDocument()

    finally:
        events.close()
