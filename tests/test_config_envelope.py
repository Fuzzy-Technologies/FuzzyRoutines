# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Exact v1 envelope dispatch and offline structural preflight."""

from math import copysign
from pathlib import Path

import pytest

from fuzzyroutines._config_envelope import CheckConfigEnvelope, ConfigEnvelopeError
from fuzzyroutines._config_json import DecodeConfigJson, JsonNumber
from fuzzyroutines._config_schema import ReadConfigV1Schema

_SCHEMA_DIRECTORY = Path(__file__).resolve().parents[1] / "docs" / "schemas"
_SCHEMA = ReadConfigV1Schema()
_FIXTURES = _SCHEMA_DIRECTORY / "config-v1" / "fixtures"


@pytest.mark.parametrize(
    ("name", "kind"),
    [
        ("valid-historical-scale.json", "model"),
        ("valid-discrete-scale.json", "model"),
        ("valid-project.json", "project"),
    ],
)
def test_DispatchesTheLocalSchemaFixtures(name, kind):
    """Select the appropriate v1 schema definition for each valid fixture."""

    wire = DecodeConfigJson((_FIXTURES / name).read_bytes())

    assert CheckConfigEnvelope(wire, _SCHEMA) == kind, "Each fixture must select its own envelope kind."


@pytest.mark.parametrize(
    ("encoded", "category", "pointer"),
    [
        (b"[]", "invalid-shape", ""),
        (b"{}", "invalid-shape", "/kind"),
        (b'{"kind": "MODEL", "schemaVersion": 1}', "unsupported-kind", "/kind"),
        (b'{"kind": "model", "schemaVersion": true}', "invalid-shape", "/schemaVersion"),
        (b'{"kind": "model", "schemaVersion": "1"}', "invalid-shape", "/schemaVersion"),
        (b'{"kind": "model", "schemaVersion": 1.0000000000000000001}', "invalid-shape", "/schemaVersion"),
        (b'{"kind": "model", "schemaVersion": 2}', "unsupported-version", "/schemaVersion"),
        (b'{"kind": "model", "schemaVersion": -0e999999999999999999999999}', "unsupported-version", "/schemaVersion"),
        (b'{"kind": "model", "schemaVersion": 1}', "invalid-shape", "/universes"),
        (b'{"kind": "project", "schemaVersion": 1, "models": []}', "invalid-shape", "/models"),
        (b'{"kind": "project", "schemaVersion": 1, "models": {}}', "invalid-shape", "/models"),
        (b'{"kind": "project", "schemaVersion": 1, "models": {"a/~": []}}', "invalid-shape", "/models/a~1~0"),
        (
            b'{"kind": "project", "schemaVersion": 1, "models": {"x": {"kind": "project", "schemaVersion": 1}}}',
            "unsupported-kind", "/models/x/kind",
        ),
        (
            b'{"kind": "project", "schemaVersion": 1, "models": {"x": {"kind": "model", "schemaVersion": 2}}}',
            "unsupported-version", "/models/x/schemaVersion",
        ),
        (
            b'{"kind": "project", "schemaVersion": 1, "models": {"x": {"kind": "model", "schemaVersion": 1}}}',
            "invalid-shape", "/models/x/universes",
        ),
    ],
)
def test_RejectsInvalidEnvelopeWithStableDiagnostic(encoded, category, pointer):
    """Report dispatch or structure failure at the original wire location."""

    with pytest.raises(ConfigEnvelopeError) as failure:
        CheckConfigEnvelope(DecodeConfigJson(encoded), _SCHEMA)

    assert failure.value.category == category, "The diagnostic must identify the failing validation phase."
    assert failure.value.pointer == pointer, "The diagnostic must point to the rejected envelope field."


def test_RejectsDocumentSchemaSelection():
    """Reject a wire field that attempts to select an external schema."""

    wire = DecodeConfigJson((_FIXTURES / "valid-historical-scale.json").read_bytes())
    assert isinstance(wire, dict), "The historical fixture must contain a model object."
    wire["$schema"] = "https://example.invalid/config.schema.json"

    with pytest.raises(ConfigEnvelopeError) as failure:
        CheckConfigEnvelope(wire, _SCHEMA)

    assert failure.value.pointer == "/$schema", "The supplied schema identifier must be treated as an unknown field."


def test_PreservesNumberTokensAndSignedZero():
    """Accept exact integral spelling without normalizing any wire value."""

    encoded = (
        b'{"kind":"model","schemaVersion":100e-2,"universes":{"u":{"left":-0}},'
        b'"memberships":{"m":{}},"scales":{"s":{}}}'
    )
    wire = DecodeConfigJson(encoded)

    assert CheckConfigEnvelope(wire, _SCHEMA) == "model", "The exact decimal version is mathematically one."
    assert isinstance(wire, dict), "The model envelope must remain a mapping."
    assert wire["schemaVersion"] == JsonNumber("100e-2", 1.0), "Dispatch must keep the original version token."
    universes = wire["universes"]
    assert isinstance(universes, dict), "The universe map must remain accessible."
    universe = universes["u"]
    assert isinstance(universe, dict), "The nested universe must remain accessible."
    coordinate = universe["left"]
    assert isinstance(coordinate, JsonNumber) and copysign(1.0, coordinate.binary64) < 0, (
        "Dispatch must preserve signed zero for downstream validation."
    )


def test_LoadsPackagedSchemaOutsideTheWorkingTree(tmpPath, monkeypatch):
    """Load fresh canonical schema data independently of the current directory."""

    monkeypatch.chdir(tmpPath)
    schema = ReadConfigV1Schema()

    assert schema == _SCHEMA, "Schema resource selection must be independent of the working directory."
    schema["$id"] = "unexpected"
    assert ReadConfigV1Schema() == _SCHEMA, "Callers must not share mutable schema data."
