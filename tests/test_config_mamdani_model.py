# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Golden Mamdani decoding and exact source diagnostics for v1 model policy."""

import json
from pathlib import Path

import pytest

from fuzzyroutines._config_mamdani_model import DecodeMamdaniModel
from fuzzyroutines._config_scale_model import ScaleModelDecodeError
from fuzzyroutines.defuzzification import CentroidPolicy
from fuzzyroutines.domain import ContinuousUniverse, IntegrationDomain
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.inference import (
    FuzzyVariable,
    InferencePolicy,
    MamdaniModel,
    MamdaniRule,
    NotCondition,
    TermCondition,
)
from fuzzyroutines.linguistic import LinguisticTerm
from fuzzyroutines.membership import MembershipFunction, SShoulder, Triangle
from fuzzyroutines.operators import NegationPolicy, SNormPolicy, TNormPolicy

pytest.importorskip("jsonschema")

_PROJECT_FIXTURE = (
    Path(__file__).resolve().parents[1] / "docs" / "schemas" / "config-v1" / "fixtures" / "valid-project.json"
)


def _ReadGoldenModel():
    """Return the Mamdani model from the canonical project fixture."""

    return json.loads(_PROJECT_FIXTURE.read_bytes())["models"]["centroid"]


def test_MamdaniMatchesReferenceOutputsAndOrderedTraces():
    """Preserve ordered rules and independent operators through centroid evaluation."""

    document = _ReadGoldenModel()
    inference = document["inference"]
    inference["activation"] = "algebraic"
    inference["rules"].append({
        "id": "reverse", "name": "Reverse",
        "antecedent": {"input": "risk", "kind": "term", "term": "high"},
        "consequent": "central", "weight": 0.5,
    })
    decoded = DecodeMamdaniModel(json.dumps(document).encode())
    universe = ContinuousUniverse(0, 1, True, True)
    variable = FuzzyVariable("Risk", (LinguisticTerm("High", ScalarFuzzySet(universe, SShoulder(0, 1))),))
    output = FuzzyVariable("Response", (LinguisticTerm("Central", ScalarFuzzySet(universe, Triangle(0, 0.5, 1))),))
    condition = TermCondition("Risk", "High")
    reference = MamdaniModel(
        (variable,), output, (
            MamdaniRule("Respond", NotCondition(condition), "Central"),
            MamdaniRule("Reverse", condition, "Central", 0.5),
        ),
        InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard")),
        TNormPolicy("algebraic"), SNormPolicy("logic"),
    )

    assert decoded.centroid is not None, "Retain explicit centroid settings."
    assert decoded.centroid.domain == IntegrationDomain(0, 1), "Keep the declared closed domain."
    assert decoded.centroid.policy == CentroidPolicy(1e-12, 1e-10, 20), "Keep every explicit numerical setting."
    assert decoded.inputIds == ("risk",) and decoded.inputScaleIds == ("risk",), "Keep ordered input bindings."
    assert (decoded.outputId, decoded.outputScaleId) == ("response", "response"), "Keep the exact output bindings."
    assert decoded.ruleIds == ("respond", "reverse"), "Keep rules in declaration order."

    for coordinate in (0, 0.25, 0.5, 0.75, 1):
        inputs = {"Risk": coordinate}
        actual = decoded.model.Evaluate(inputs, decoded.centroid.domain, decoded.centroid.policy)
        expected = reference.Evaluate(inputs, IntegrationDomain(0, 1), CentroidPolicy(1e-12, 1e-10, 20))
        assert actual.value == expected.value == pytest.approx(0.5, rel=0, abs=1e-12), "Keep the symmetric centroid."
        assert actual.method == expected.method == "adaptive-simpson", "Keep the declared numerical result method."
        assert actual.inputGrades == expected.inputGrades, "Keep the ordered input-grade trace."
        assert tuple((trace.name, trace.antecedentGrade, trace.weight, trace.firingStrength) for trace in actual.rules) == tuple(
            (trace.name, trace.antecedentGrade, trace.weight, trace.firingStrength) for trace in expected.rules
        ), "Keep rule order and firing strengths."

        for point in (0, 0.25, 0.5, 0.75, 1):
            assert actual.outputSet.Membership(point) == expected.outputSet.Membership(point), "Keep the aggregate."
            assert tuple(trace.activatedSet.Membership(point) for trace in actual.rules) == tuple(
                trace.activatedSet.Membership(point) for trace in expected.rules
            ), "Keep individual activation traces."


def test_OmittedCentroidAndNoEvaluationDuringLoad(monkeypatch):
    """Keep centroid optional and construct both variants without running evaluators."""

    def RejectEvaluation(*arguments, **options):
        """Fail if reconstruction runs membership or model evaluation."""

        raise AssertionError("Loading must be data-only.")

    document = _ReadGoldenModel()

    with monkeypatch.context() as patched:
        patched.setattr(MembershipFunction, "Evaluate", RejectEvaluation)
        patched.setattr(MamdaniModel, "Evaluate", RejectEvaluation)
        explicit = DecodeMamdaniModel(json.dumps(document).encode())
        del document["inference"]["centroid"]
        fuzzyOnly = DecodeMamdaniModel(json.dumps(document).encode())

    assert explicit.centroid is not None, "Read an explicit centroid without executing it."
    assert fuzzyOnly.centroid is None, "Never add an implicit centroid policy."
    result = fuzzyOnly.model.Evaluate({"Risk": 0.25})
    assert result.value is None and result.method == "fuzzy-set", "An omitted centroid leaves a fuzzy result only."


def test_NondefaultCentroidSettingsAreRetained():
    """Keep a closed interior window and the greatest allowed exact depth."""

    document = _ReadGoldenModel()
    document["inference"]["centroid"] = {
        "domain": {"left": 0.125, "right": 0.75},
        "policy": {"absoluteTolerance": 1e-7, "relativeTolerance": 1e-8, "maximumDepth": 9007199254740991},
    }
    decoded = DecodeMamdaniModel(json.dumps(document).encode())

    assert decoded.centroid is not None, "Retain the declared numerical settings."
    assert decoded.centroid.domain == IntegrationDomain(0.125, 0.75), "Use the exact interior window."
    assert decoded.centroid.policy == CentroidPolicy(1e-7, 1e-8, 9007199254740991), "Use explicit tolerances and depth."


@pytest.mark.parametrize(
    ("mutation", "category", "pointer"),
    [
        ("duplicate-output-id", "duplicate-id", "/inference/output/id"),
        ("unknown-output-scale", "unresolved-reference", "/inference/output/scale"),
        ("discrete-output-scale", "invalid-value", "/inference/output/scale"),
        ("blank-output-name", "invalid-value", "/inference/output/name"),
        ("wrong-scope-term", "unresolved-reference", "/inference/rules/0/consequent"),
        ("case-mismatched-term", "unresolved-reference", "/inference/rules/0/consequent"),
        ("left-outside-open", "invalid-value", "/inference/centroid/domain/left"),
        ("right-outside-open", "invalid-value", "/inference/centroid/domain/right"),
        ("inverted-window", "invalid-value", "/inference/centroid/domain/right"),
        ("depth-too-large", "invalid-shape", "/inference/centroid/policy/maximumDepth"),
    ],
)
def test_MamdaniReportsSourcePointers(mutation, category, pointer):
    """Locate invalid Mamdani references, integration endpoints or policies."""

    document = _ReadGoldenModel()
    inference = document["inference"]
    universe = document["universes"]["normalized"]
    domain = inference["centroid"]["domain"]

    match mutation:
        case "duplicate-output-id":
            inference["output"]["id"] = "risk"
        case "unknown-output-scale":
            inference["output"]["scale"] = "Response"
        case "discrete-output-scale":
            document["universes"]["normalized"] = {"kind": "discrete", "points": [0, 1]}
        case "blank-output-name":
            inference["output"]["name"] = "  "
        case "wrong-scope-term":
            inference["rules"][0]["consequent"] = "high"
        case "case-mismatched-term":
            inference["rules"][0]["consequent"] = "Central"
        case "left-outside-open":
            universe["leftClosed"] = False
        case "right-outside-open":
            universe["rightClosed"] = False
        case "inverted-window":
            domain["left"] = 1
        case "depth-too-large":
            inference["centroid"]["policy"]["maximumDepth"] = 9007199254740992

    with pytest.raises(ValueError) as failure:
        DecodeMamdaniModel(json.dumps(document).encode())

    assert failure.value.category == category, "Return the correct diagnostic category."
    assert failure.value.pointer == pointer, "Return the precise pointer in the original wire data."

    if mutation != "depth-too-large":
        assert isinstance(failure.value, ScaleModelDecodeError), "Keep semantic failures distinct from structural failures."
