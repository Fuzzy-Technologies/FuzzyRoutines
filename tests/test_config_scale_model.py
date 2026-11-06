# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Golden scale model decoding and semantic diagnostics."""

import json
from pathlib import Path

import pytest

from fuzzyroutines._config_scale_model import DecodeScaleModel, ScaleModelDecodeError
from fuzzyroutines.defuzzification import CentroidPolicy
from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse
from fuzzyroutines.membership import MembershipFunction
from fuzzyroutines.presets import (
    CreateUniversalFuzzyScale,
    UniversalFuzzyScaleDomains,
    UniversalFuzzyScalePolicy,
)

pytest.importorskip("jsonschema")

_FIXTURES = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "config-v1" / "fixtures"


def test_DecodesGoldenHistoricalScaleWithoutChangingItsCoefficients():
    """Preserve all declared definitions, representative domains and historical winners."""

    model = DecodeScaleModel((_FIXTURES / "valid-historical-scale.json").read_bytes())
    definition = model.scales["universal"]
    expected = CreateUniversalFuzzyScale()
    expectedPolicy = UniversalFuzzyScalePolicy()

    assert model.universes["normalized"] == ContinuousUniverse(0, 1, True, True), "Keep the closed unit universe."
    assert definition.termIds == ("min", "low", "med", "high", "max"), "Term IDs must remain in declared order."
    assert definition.membershipIds == definition.termIds, "The historical model binds the original five definitions."
    assert definition.fuzzification == expectedPolicy, "The historical tie and no-match policy must survive decoding."
    assert definition.representatives is not None, "The fixture declares an explicit representative policy."
    assert definition.representatives.domains == UniversalFuzzyScaleDomains(), "Preserve all integration windows."
    assert definition.representatives.policy == CentroidPolicy(1e-12, 1e-10, 20), "Preserve centroid settings."

    for term, reference in zip(definition.scale.terms, expected.terms, strict=True):
        assert term.name == reference.name, "Keep the exact historical display name."
        assert term.fuzzySet.membershipFunction == reference.fuzzySet.membershipFunction, (
            "Decoded family and parameters must match the historical factory."
        )

    for coordinate in (0.0, 0.17, 0.25, 0.5, 0.75, 1.0):
        actual = definition.scale.Fuzzify(coordinate, definition.fuzzification)
        reference = expected.Fuzzify(coordinate, expectedPolicy)
        assert tuple(item.grade for item in actual.memberships) == tuple(item.grade for item in reference.memberships), (
            "Each membership grade must match the historical factory."
        )
        assert tuple(term.name for term in actual.selectedTerms) == tuple(term.name for term in reference.selectedTerms), (
            "Decoded policies must select the same winners, including weak coverage."
        )


def test_DecodesDiscreteScaleWithoutEvaluatingOrAddingPolicies(monkeypatch):
    """Keep a discrete universe and omitted optional policies without running formulas."""

    def RejectEvaluation(self, coordinate):
        """Fail if decoding attempts to evaluate a membership function."""

        raise AssertionError("Loading model definitions must not invoke membership evaluators.")

    monkeypatch.setattr(MembershipFunction, "Evaluate", RejectEvaluation)
    model = DecodeScaleModel((_FIXTURES / "valid-discrete-scale.json").read_bytes())
    definition = model.scales["score"]

    assert model.universes["scores"] == DiscreteUniverse((-2, 0, 2)), "Keep the exact discrete coordinates."
    assert definition.universeId == "scores", "Keep the original universe reference."
    assert definition.fuzzification is None and definition.representatives is None, (
        "Omitted policies must remain absent."
    )


def test_ReportsDanglingMembershipAtTheReferencingField():
    """Fail a structurally valid model if its term points outside its membership namespace."""

    with pytest.raises(ScaleModelDecodeError) as failure:
        DecodeScaleModel((_FIXTURES / "invalid-semantic-reference.json").read_bytes())

    assert failure.value.category == "unresolved-reference", "The dangling target is a semantic reference error."
    assert failure.value.pointer == "/scales/score/terms/0/membership", "The pointer must identify the referring field."
    assert "missing" in str(failure.value), "Report the actual missing membership ID."


@pytest.mark.parametrize(
    ("mutation", "category", "pointer"),
    [
        ("duplicate-id", "duplicate-id", "/scales/universal/terms/1/id"),
        ("duplicate-name", "duplicate-name", "/scales/universal/terms/1/name"),
        ("blank-name", "invalid-value", "/scales/universal/terms/1/name"),
        ("geometry", "invalid-value", "/memberships/high/parameters"),
        ("window-bound", "invalid-value", "/scales/universal/representatives/windows/min/left"),
        ("missing-window", "invalid-value", "/scales/universal/representatives/windows/low"),
        ("unknown-window", "unresolved-reference", "/scales/universal/representatives/windows/extra"),
        ("unknown-universe", "unresolved-reference", "/scales/universal/universe"),
    ],
)
def test_RejectsInvalidScaleGeometryAndIdentity(mutation, category, pointer):
    """Reject invalid declarations without losing the precise source field."""

    document = json.loads((_FIXTURES / "valid-historical-scale.json").read_bytes())
    scale = document["scales"]["universal"]
    terms = scale["terms"]
    windows = scale["representatives"]["windows"]

    match mutation:
        case "duplicate-id":
            terms[1]["id"] = terms[0]["id"]
        case "duplicate-name":
            terms[0]["name"] = "Straße"
            terms[1]["name"] = "STRASSE"
        case "blank-name":
            terms[1]["name"] = "  "
        case "geometry":
            document["memberships"]["high"]["parameters"]["left"] = 0.7
        case "window-bound":
            document["universes"]["normalized"]["leftClosed"] = False
        case "missing-window":
            del windows["low"]
        case "unknown-window":
            windows["extra"] = windows["min"]
        case "unknown-universe":
            scale["universe"] = "absent"

    with pytest.raises(ScaleModelDecodeError) as failure:
        DecodeScaleModel(json.dumps(document).encode())

    assert failure.value.category == category, "The diagnostic category must describe the failed semantic check."
    assert failure.value.pointer == pointer, "The diagnostic must locate the invalid wire field."


def test_ReportsTheFirstOutOfOrderDiscreteCoordinate():
    """Reject an unordered universe without sorting the declared points."""

    document = json.loads((_FIXTURES / "valid-discrete-scale.json").read_bytes())
    document["universes"]["scores"]["points"] = [0, 2, 1]

    with pytest.raises(ScaleModelDecodeError) as failure:
        DecodeScaleModel(json.dumps(document).encode())

    assert failure.value.pointer == "/universes/scores/points/2", "Locate the first descending coordinate."


@pytest.mark.parametrize("kind", ("project", "inference"))
def test_ScaleOnlyEntryRejectsUnimplementedEnvelopes(kind):
    """Fail explicitly before returning a scale-only view of an inference model or project."""

    project = (_FIXTURES / "valid-project.json").read_bytes()
    encoded = project if kind == "project" else json.dumps(json.loads(project)["models"]["weighted"]).encode()

    with pytest.raises(ScaleModelDecodeError) as failure:
        DecodeScaleModel(encoded)

    assert failure.value.category == "unsupported-model", "Unsupported inputs must not be partially decoded."
    expectedPointer = "/kind" if kind == "project" else "/inference"
    assert failure.value.pointer == expectedPointer, "Point to the source of the unsupported model."
