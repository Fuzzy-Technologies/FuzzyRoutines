# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private reconstruction of v1 scale-only model envelopes."""

from collections.abc import Mapping
from dataclasses import dataclass
from itertools import pairwise
from types import MappingProxyType
from typing import Literal, cast

from ._config_json import (
    ConfigPath,
    ConfigPointer,
    DecodeConfigJson,
    JsonNumber,
    JsonValue,
)
from ._config_schema import ReadConfigV1Schema
from ._config_structure import CheckConfigStructure
from .defuzzification import CentroidPolicy
from .domain import ContinuousUniverse, DiscreteUniverse, IntegrationDomain
from .exceptions import InvalidDomainError, InvalidParameterError
from .fuzzysets import ScalarFuzzySet
from .linguistic import FuzzificationPolicy, LinguisticScale, LinguisticTerm
from .membership import MembershipFunction

type _Universe = ContinuousUniverse | DiscreteUniverse
type _Object = dict[str, JsonValue]
type _Category = Literal[
    "duplicate-id", "duplicate-name", "invalid-value", "unresolved-reference", "unsupported-model",
]


class ScaleModelDecodeError(ValueError):
    """Semantic failure with a category and its original wire field pointer."""

    def __init__(self, category: _Category, path: ConfigPath, message: str) -> None:
        """Record actionable scale model diagnostics."""

        super().__init__(message)
        self.category = category
        self.pointer = ConfigPointer(path)


@dataclass(frozen=True, slots=True)
class _Representatives:
    """Explicit closed windows in term order and their numerical policy."""

    domains: tuple[IntegrationDomain, ...]
    policy: CentroidPolicy


@dataclass(frozen=True, slots=True)
class _ConfiguredScale:
    """One scale with wire IDs and independently optional policies."""

    scale: LinguisticScale
    universeId: str
    termIds: tuple[str, ...]
    membershipIds: tuple[str, ...]
    fuzzification: FuzzificationPolicy | None
    representatives: _Representatives | None


@dataclass(frozen=True, slots=True)
class _ScaleModel:
    """Immutable reconstruction of the named definitions in a scale model."""

    universes: Mapping[str, _Universe]
    memberships: Mapping[str, MembershipFunction]
    scales: Mapping[str, _ConfiguredScale]


def _Real(value: JsonValue) -> float:
    """Read a binary64 value after successful structural validation."""

    return cast(JsonNumber, value).binary64


def _DecodeUniverse(definition: _Object, path: ConfigPath) -> _Universe:
    """Reconstruct a discrete or continuous universe with local diagnostics."""

    if definition["kind"] == "discrete":
        points = tuple(_Real(value) for value in cast(list[JsonValue], definition["points"]))

        for index, (leftPoint, rightPoint) in enumerate(pairwise(points), 1):
            if leftPoint >= rightPoint:
                raise ScaleModelDecodeError(
                    "invalid-value", (*path, "points", index), "Universe points must increase strictly.",
                )

        return DiscreteUniverse(points)

    left = definition["left"]
    right = definition["right"]

    try:
        return ContinuousUniverse(
            None if left is None else _Real(left),
            None if right is None else _Real(right),
            leftClosed=cast(bool, definition["leftClosed"]),
            rightClosed=cast(bool, definition["rightClosed"]),
        )

    except InvalidDomainError as error:
        raise ScaleModelDecodeError("invalid-value", (*path, "right"), str(error)) from error


def _DecodeMembership(definition: _Object, path: ConfigPath) -> MembershipFunction:
    """Construct a built-in family with validated canonical parameter names."""

    parameters = {
        name: _Real(value)
        for name, value in cast(_Object, definition["parameters"]).items()
    }

    try:
        return MembershipFunction(cast(str, definition["family"]), **parameters)

    except InvalidParameterError as error:
        raise ScaleModelDecodeError("invalid-value", (*path, "parameters"), str(error)) from error


def _DecodeWindow(definition: _Object, universe: ContinuousUniverse, path: ConfigPath) -> IntegrationDomain:
    """Require a closed ordered window entirely within its declared universe."""

    left = _Real(definition["left"])
    right = _Real(definition["right"])

    if left >= right:
        raise ScaleModelDecodeError("invalid-value", (*path, "right"), "The right bound must exceed the left bound.")

    for field, coordinate in (("left", left), ("right", right)):
        if not universe.Contains(coordinate):
            raise ScaleModelDecodeError("invalid-value", (*path, field), "Window bound is outside the scale universe.")

    return IntegrationDomain(left, right)


def _DecodeRepresentatives(
    definition: _Object, universe: _Universe, termIds: tuple[str, ...], path: ConfigPath,
) -> _Representatives:
    """Bind exactly one integration window to every term ID in declared order."""

    if not isinstance(universe, ContinuousUniverse):
        raise ScaleModelDecodeError("invalid-value", path, "Representatives require a continuous universe.")

    windows = cast(_Object, definition["windows"])
    unknown = sorted(windows.keys() - set(termIds))

    if unknown:
        raise ScaleModelDecodeError(
            "unresolved-reference", (*path, "windows", unknown[0]), f"Unknown scale term ID {unknown[0]!r}.",
        )

    domains = []

    for termId in termIds:
        windowPath = (*path, "windows", termId)

        if termId not in windows:
            raise ScaleModelDecodeError(
                "invalid-value", windowPath, f"Missing integration window for scale term ID {termId!r}.",
            )

        domains.append(_DecodeWindow(cast(_Object, windows[termId]), universe, windowPath))

    policy = cast(_Object, definition["policy"])
    centroidPolicy = CentroidPolicy(
        absoluteTolerance=_Real(policy["absoluteTolerance"]),
        relativeTolerance=_Real(policy["relativeTolerance"]),
        maximumDepth=int(cast(JsonNumber, policy["maximumDepth"]).ExactDecimal()),
    )

    return _Representatives(tuple(domains), centroidPolicy)


def _DecodeScale(
    definition: _Object,
    universes: Mapping[str, _Universe],
    memberships: Mapping[str, MembershipFunction],
    path: ConfigPath,
) -> _ConfiguredScale:
    """Resolve one scale's terms and preserve its explicit optional policies."""

    universeId = cast(str, definition["universe"])

    if universeId not in universes:
        raise ScaleModelDecodeError(
            "unresolved-reference", (*path, "universe"), f"Unknown model universe ID {universeId!r}.",
        )

    universe = universes[universeId]
    terms = []
    termIds: dict[str, None] = {}
    names: set[str] = set()
    membershipIds = []

    for index, term in enumerate(cast(list[_Object], definition["terms"])):
        termPath = (*path, "terms", index)
        termId = cast(str, term["id"])
        membershipId = cast(str, term["membership"])
        name = cast(str, term["name"])
        lookupName = name.casefold()

        if termId in termIds:
            raise ScaleModelDecodeError("duplicate-id", (*termPath, "id"), f"Repeated scale term ID {termId!r}.")

        if membershipId not in memberships:
            raise ScaleModelDecodeError(
                "unresolved-reference", (*termPath, "membership"), f"Unknown model membership ID {membershipId!r}.",
            )

        if not name.strip():
            raise ScaleModelDecodeError("invalid-value", (*termPath, "name"), "The term name must be nonblank.")

        if lookupName in names:
            raise ScaleModelDecodeError("duplicate-name", (*termPath, "name"), f"Repeated scale term name {name!r}.")

        termIds[termId] = None
        names.add(lookupName)
        membershipIds.append(membershipId)
        terms.append(LinguisticTerm(name, ScalarFuzzySet(universe, memberships[membershipId])))

    fuzzification = None

    if "fuzzification" in definition:
        policy = cast(_Object, definition["fuzzification"])
        fuzzification = FuzzificationPolicy(
            tiePolicy=cast(str, policy["tiePolicy"]),
            minimumConfidence=_Real(policy["minimumConfidence"]),
            tieTolerance=_Real(policy["tieTolerance"]),
        )

    representatives = None

    if "representatives" in definition:
        representatives = _DecodeRepresentatives(
            cast(_Object, definition["representatives"]), universe, tuple(termIds), (*path, "representatives"),
        )

    return _ConfiguredScale(
        LinguisticScale(tuple(terms)), universeId, tuple(termIds), tuple(membershipIds), fuzzification, representatives,
    )


def DecodeScaleModel(encoded: bytes) -> _ScaleModel:
    """Decode one scale-only v1 model without invoking membership evaluators.

    Args:
        encoded: One bounded UTF-8 configuration document.

    Returns:
        Immutable universes, memberships and scales with their declared IDs.

    Raises:
        ValueError: The document fails parsing, structure, or scale semantics,
            or contains a project envelope or an inference definition.
    """

    wire = DecodeConfigJson(encoded)
    CheckConfigStructure(wire, ReadConfigV1Schema())
    document = cast(_Object, wire)

    if document["kind"] != "model":
        raise ScaleModelDecodeError("unsupported-model", ("kind",), "Expected a standalone scale model.")

    if "inference" in document:
        raise ScaleModelDecodeError("unsupported-model", ("inference",), "A scale model cannot contain inference.")

    memberships = {
        key: _DecodeMembership(cast(_Object, value), ("memberships", key))
        for key, value in sorted(cast(_Object, document["memberships"]).items())
    }
    universes = {
        key: _DecodeUniverse(cast(_Object, value), ("universes", key))
        for key, value in sorted(cast(_Object, document["universes"]).items())
    }
    scales = {
        key: _DecodeScale(cast(_Object, value), universes, memberships, ("scales", key))
        for key, value in sorted(cast(_Object, document["scales"]).items())
    }

    return _ScaleModel(MappingProxyType(universes), MappingProxyType(memberships), MappingProxyType(scales))
