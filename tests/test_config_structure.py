# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Exact numeric and descendant checks with the offline design validator."""

from json import dumps, loads
from math import copysign
from pathlib import Path

import pytest

from fuzzyroutines._config_envelope import ConfigEnvelopeError
from fuzzyroutines._config_json import DecodeConfigJson, JsonNumber
from fuzzyroutines._config_schema import ReadConfigV1Schema
from fuzzyroutines._config_structure import CheckConfigStructure

pytest.importorskip("jsonschema")

_SCHEMA_DIRECTORY = Path(__file__).resolve().parents[1] / "docs" / "schemas"
_SCHEMA = ReadConfigV1Schema()
_FIXTURES = _SCHEMA_DIRECTORY / "config-v1" / "fixtures"


@pytest.mark.parametrize(
    "name",
    [
        "valid-historical-scale.json",
        "valid-discrete-scale.json",
        "valid-project.json",
        "invalid-semantic-reference.json",
    ],
)
def test_ValidatesDescendantsWithoutResolvingSemanticReferences(name):
    """Accept structurally valid fixtures regardless of reference targets."""

    CheckConfigStructure(DecodeConfigJson((_FIXTURES / name).read_bytes()), _SCHEMA)


def test_UnknownFamilyPointsToDiscriminator():
    """Reject an unlisted evaluator family at its discriminator."""

    wire = DecodeConfigJson((_FIXTURES / "invalid-schema-callable.json").read_bytes())

    with pytest.raises(ConfigEnvelopeError) as failure:
        CheckConfigStructure(wire, _SCHEMA)

    assert failure.value.category == "invalid-shape", "An unlisted evaluator family is a structural error."
    assert failure.value.pointer == "/memberships/desirability/family", (
        "The invalid family must be reported before unrelated branch errors."
    )


@pytest.mark.parametrize(
    ("mutation", "pointer"),
    [
        ("extra", "/memberships/high/parameters/~1extra~0"),
        ("required", "/memberships/high/parameters/left"),
        ("key", "/memberships/bad~1key"),
        ("fraction", "/scales/universal/representatives/policy/maximumDepth"),
        ("boolean", "/scales/universal/representatives/policy/maximumDepth"),
        ("range", "/scales/universal/representatives/policy/maximumDepth"),
    ],
)
def test_DiagnosesNestedShapeAndExactIntegerConstraints(mutation, pointer):
    """Report selected branch errors using the original escaped wire path."""

    model = loads((_FIXTURES / "valid-historical-scale.json").read_bytes())
    parameters = model["memberships"]["high"]["parameters"]
    policy = model["scales"]["universal"]["representatives"]["policy"]

    if mutation == "extra":
        parameters["/extra~"] = 1

    elif mutation == "required":
        del parameters["left"]

    elif mutation == "key":
        model["memberships"]["bad/key"] = model["memberships"].pop("high")

    else:
        policy["maximumDepth"] = "REPLACE"

    replacements = {"fraction": b"1.0000000000000000001", "boolean": b"true", "range": b"9007199254740992"}
    encoded = dumps(model).encode()

    if mutation in replacements:
        encoded = encoded.replace(b'"REPLACE"', replacements[mutation])

    with pytest.raises(ConfigEnvelopeError) as failure:
        CheckConfigStructure(DecodeConfigJson(encoded), _SCHEMA)

    assert failure.value.pointer == pointer, "The diagnostic must identify the offending nested field or key."


def test_ValidatesBinary64WithoutRewritingSourceNumber():
    """Keep the signed real zero and the exact version spelling in the wire tree."""

    encoded = (_FIXTURES / "valid-historical-scale.json").read_bytes().replace(
        b'"schemaVersion": 1', b'"schemaVersion": 100e-2',
    ).replace(b'"cutoff": 0', b'"cutoff": -0')
    wire = DecodeConfigJson(encoded)
    CheckConfigStructure(wire, _SCHEMA)

    assert isinstance(wire, dict), "The wire tree must retain its original mapping."
    assert wire["schemaVersion"] == JsonNumber("100e-2", 1.0), "Schema validation must preserve the version token."
    memberships = wire["memberships"]
    assert isinstance(memberships, dict), "The membership map must remain accessible."
    minimum = memberships["min"]
    assert isinstance(minimum, dict), "The minimum membership must remain accessible."
    parameters = minimum["parameters"]
    assert isinstance(parameters, dict), "The membership parameters must remain accessible."
    cutoff = parameters["cutoff"]
    assert isinstance(cutoff, JsonNumber) and cutoff.token == "-0" and copysign(1.0, cutoff.binary64) < 0, (
        "Schema validation must preserve the signed-zero spelling and binary64 value."
    )


def test_OfflineRegistryRejectsAnExternalReference():
    """A broken local schema cannot initiate a remote reference lookup."""

    schema = ReadConfigV1Schema()
    uri = "https://example.invalid/external-schema"
    schema["$defs"]["membership"] = {"$ref": uri}
    wire = DecodeConfigJson((_FIXTURES / "valid-historical-scale.json").read_bytes())
    exceptions = pytest.importorskip("referencing.exceptions")

    with pytest.raises(exceptions.Unresolvable, match=uri):
        CheckConfigStructure(wire, schema)
