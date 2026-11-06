# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Bounded readable rule text for explicitly selected fuzzy inference models."""

from copy import deepcopy
from dataclasses import dataclass

from ._config_export import _Object
from ._rule_binding import _BindRuleDraft
from ._rule_formatter import _FormatRule, _RuleFormatError
from ._rule_parser import _ParseRule, _RuleDraft, _RuleParseError
from .configuration import ModelConfiguration
from .exceptions import InvalidParameterTypeError
from .inference import MamdaniRule, SugenoRule

__all__ = ["BindRule", "BoundRule", "FormatRule", "ParseRule", "RuleDraft", "RuleTextError"]


class RuleTextError(ValueError):
    """A readable-rule diagnostic independent of the human-facing message.

    Attributes:
        category: One of `malformed-input`, `exceeded-limit`,
            `unresolved-binding` or `invalid-rule-semantics`.
        offset: Zero-based UTF-8 byte offset in the original input, or
            its byte length for an end-of-input diagnostic.
    """

    def __init__(self, category: str, offset: int, message: str) -> None:
        """Create a diagnostic with its category, offset and explanation."""

        super().__init__(message)
        self.category = category
        self.offset = offset


@dataclass(frozen=True, slots=True)
class RuleDraft:
    """An inert, immutable rule draft returned by `ParseRule`."""

    _draft: _RuleDraft

    @property
    def identifier(self) -> str:
        """The exact v1 identifier declared by the source."""

        return self._draft.identifier.value

    @property
    def name(self) -> str:
        """The decoded display name with its original spelling."""

        return self._draft.name.value

    @property
    def identifierSpan(self) -> tuple[int, int]:
        """The identifier's half-open UTF-8 byte span in the original source."""

        return self._draft.identifier.start, self._draft.identifier.end

    @property
    def nameSpan(self) -> tuple[int, int]:
        """The quoted name's half-open byte span, including its delimiters."""

        return self._draft.name.start, self._draft.name.end


@dataclass(frozen=True, slots=True)
class BoundRule:
    """A scalar rule bound to one model and its corresponding v1 object.

    Attributes:
        rule: The Mamdani or Sugeno rule for insertion into the selected model.
    """

    rule: MamdaniRule | SugenoRule
    _wire: _Object

    def ToWire(self) -> dict[str, object]:
        """Return a separate mutable JSON object with the selected model's IDs."""

        return dict(deepcopy(self._wire))


def ParseRule(source: bytes) -> RuleDraft:
    """Parse one complete UTF-8 rule into an inert syntax draft.

    Args:
        source: Rule bytes under the grammar's byte, token and depth limits.

    Returns:
        A syntax draft with exact source spans and no model bindings.

    Raises:
        InvalidParameterTypeError: The source is not bytes.
        RuleTextError: The source fails a grammar or draft validation rule.
    """

    if not isinstance(source, bytes):
        raise InvalidParameterTypeError("source must be UTF-8 bytes")

    try:
        return RuleDraft(_ParseRule(source))

    except _RuleParseError as error:
        raise RuleTextError(error.category, error.offset, str(error)) from error


def FormatRule(draft: RuleDraft) -> bytes:
    """Emit canonical UTF-8 for a parsed draft, including its final LF.

    Args:
        draft: An inert draft produced by `ParseRule`.

    Returns:
        A complete bounded rule preserving ordered grouping and binary64 values.

    Raises:
        InvalidParameterTypeError: The argument is not a rule draft.
        RuleTextError: Canonical output exceeds a limit.
    """

    if not isinstance(draft, RuleDraft):
        raise InvalidParameterTypeError("draft must come from ParseRule")

    try:
        return _FormatRule(draft._draft)

    except _RuleFormatError as error:
        assert error.offset is not None, "A parsed draft has an original source length."
        raise RuleTextError(error.category, error.offset, str(error)) from error


def BindRule(draft: RuleDraft, configuration: ModelConfiguration) -> BoundRule:
    """Resolve a parsed rule against one explicitly selected model configuration.

    Args:
        draft: An inert draft produced by `ParseRule`.
        configuration: Validated standalone v1 snapshot for Mamdani or Sugeno.

    Returns:
        A scalar rule and its corresponding wire data. The selected model stays
        unchanged and no membership function or rule is evaluated.

    Raises:
        InvalidParameterTypeError: An argument has the wrong object type.
        RuleTextError: The rule fails a canonical limit, binding or model rule.
    """

    if not isinstance(draft, RuleDraft):
        raise InvalidParameterTypeError("draft must come from ParseRule")

    if not isinstance(configuration, ModelConfiguration):
        raise InvalidParameterTypeError("configuration must be a validated standalone model snapshot")

    try:
        result = _BindRuleDraft(draft._draft, configuration)

    except _RuleParseError as error:
        raise RuleTextError(error.category, error.offset, str(error)) from error

    return BoundRule(result.rule, result.wire)
