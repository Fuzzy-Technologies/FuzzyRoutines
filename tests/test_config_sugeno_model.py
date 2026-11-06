# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Golden Sugeno fixture decoding and exact scoped inference diagnostics."""

import json
from pathlib import Path

import pytest

from fuzzyroutines._config_scale_model import ScaleModelDecodeError
from fuzzyroutines._config_sugeno_model import DecodeSugenoModel
from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.inference import (
    AffineConsequent,
    AllOf,
    AnyOf,
    ConstantConsequent,
    FuzzyVariable,
    InferencePolicy,
    NotCondition,
    SugenoModel,
    SugenoRule,
    TermCondition,
)
from fuzzyroutines.linguistic import LinguisticTerm
from fuzzyroutines.membership import MembershipFunction, SShoulder
from fuzzyroutines.operators import NegationPolicy, SNormPolicy, TNormPolicy

pytest.importorskip("jsonschema")

_PROJECT_FIXTURE = (
    Path(__file__).resolve().parents[1] / "docs" / "schemas" / "config-v1" / "fixtures" / "valid-project.json"
)


def _ReadGoldenModel():
    """Return the standalone Sugeno envelope from the canonical project fixture."""

    return json.loads(_PROJECT_FIXTURE.read_bytes())["models"]["weighted"]


def test_ReconstructsTheGoldenSugenoOutputsAndTraces():
    """Match independent scalar construction and exact ordered trace anchors."""

    configured = DecodeSugenoModel(json.dumps(_ReadGoldenModel()).encode())
    universe = ContinuousUniverse(0, 1, True, True)
    variable = FuzzyVariable("Risk", (LinguisticTerm("High", ScalarFuzzySet(universe, SShoulder(0, 1))),))
    high = TermCondition("Risk", "High")
    low = NotCondition(high)
    reference = SugenoModel(
        (variable,),
        (
            SugenoRule("Base", low, ConstantConsequent(0.25)),
            SugenoRule("Increase", AllOf((high, AnyOf((high, low)))), AffineConsequent(0.5, (("Risk", 0.5),))),
        ),
        InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard")),
        universe,
    )

    assert configured.inputIds == ("risk",) and configured.inputScaleIds == ("risk",), "Keep the wire input bindings."
    assert configured.ruleIds == ("base", "increase"), "Rule IDs must retain the declared order."
    assert configured.outputUniverseId == "normalized", "Keep the declared output universe ID."
    assert tuple(rule.antecedent for rule in configured.model.rules) == (low, AllOf((high, AnyOf((high, low))))), (
        "Nested terms must use runtime names and retain operand order."
    )

    for coordinate in (0.0, 0.25, 0.5, 0.75, 1.0):
        inputs = {"Risk": coordinate}
        assert configured.model.Evaluate(inputs) == reference.Evaluate(inputs), (
            "The decoded model must match the independent scalar result and full trace."
        )

    quarter = configured.model.Evaluate({"Risk": 0.25})
    assert quarter.value == 0.296875, "The published fixture's weighted average must be exact."
    assert tuple(rule.firingStrength for rule in quarter.rules) == (0.875, 0.125), "Preserve both firing strengths."
    assert tuple(rule.consequentValue for rule in quarter.rules) == (0.25, 0.625), "Preserve constant and affine outputs."


def test_DoesNotExecuteTermsOrModelsDuringLoad(monkeypatch):
    """Construct a complete model while both evaluator entry points are disabled."""

    def RejectEvaluation(self, value):
        """Fail if the decoder runs any evaluator."""

        raise AssertionError("Decoding is data-only.")

    monkeypatch.setattr(SugenoModel, "Evaluate", RejectEvaluation)
    monkeypatch.setattr(MembershipFunction, "Evaluate", RejectEvaluation)

    assert len(DecodeSugenoModel(json.dumps(_ReadGoldenModel()).encode()).model.rules) == 2, (
        "Data-only loading must reconstruct both rules."
    )


def test_PreservesAffineCoefficientOrderIndependentlyOfInputOrder():
    """Bind multiple affine coefficients by ID and retain the declared coefficient sequence."""

    document = _ReadGoldenModel()
    inference = document["inference"]
    inference["inputs"].append({"id": "second", "name": "Secondary", "scale": "risk"})
    consequent = inference["rules"][1]["consequent"]
    consequent["coefficients"].insert(0, {"input": "second", "value": 0.125})

    decoded = DecodeSugenoModel(json.dumps(document).encode())
    affine = decoded.model.rules[1].consequent

    assert decoded.inputIds == ("risk", "second"), "Input order must remain independent of coefficient order."
    assert isinstance(affine, AffineConsequent), "The second rule must remain affine."
    assert affine.coefficients == (("Secondary", 0.125), ("Risk", 0.5)), "Bind names without sorting coefficients."


@pytest.mark.parametrize(
    ("mutation", "category", "pointer"),
    [
        ("unknown-input", "unresolved-reference", "/inference/rules/0/antecedent/operand/input"),
        ("unknown-term", "unresolved-reference", "/inference/rules/0/antecedent/operand/term"),
        ("nested-term", "unresolved-reference", "/inference/rules/1/antecedent/operands/1/operands/1/operand/term"),
        ("unknown-scale", "unresolved-reference", "/inference/inputs/0/scale"),
        ("unknown-output", "unresolved-reference", "/inference/outputUniverse"),
        ("discrete-output", "invalid-value", "/inference/outputUniverse"),
        ("outside-constant", "invalid-value", "/inference/rules/0/consequent/value"),
        ("unknown-coefficient", "unresolved-reference", "/inference/rules/1/consequent/coefficients/0/input"),
        ("duplicate-coefficient", "duplicate-id", "/inference/rules/1/consequent/coefficients/1/input"),
        ("duplicate-input-id", "duplicate-id", "/inference/inputs/1/id"),
        ("duplicate-input-name", "duplicate-name", "/inference/inputs/1/name"),
        ("duplicate-rule-id", "duplicate-id", "/inference/rules/1/id"),
        ("duplicate-rule-name", "duplicate-name", "/inference/rules/1/name"),
    ],
)
def test_ReportsExactSourcePointersForInvalidInference(mutation, category, pointer):
    """Report the offending reference, duplicate, or value with its source pointer."""

    document = _ReadGoldenModel()
    inference = document["inference"]
    inputs = inference["inputs"]
    rules = inference["rules"]
    firstLeaf = rules[0]["antecedent"]["operand"]
    coefficients = rules[1]["consequent"]["coefficients"]

    match mutation:
        case "unknown-input":
            firstLeaf["input"] = "Risk"
        case "unknown-term":
            firstLeaf["term"] = "High"
        case "nested-term":
            rules[1]["antecedent"]["operands"][1]["operands"][1]["operand"]["term"] = "High"
        case "unknown-scale":
            inputs[0]["scale"] = "absent"
        case "unknown-output":
            inference["outputUniverse"] = "absent"
        case "discrete-output":
            document["universes"]["normalized"] = {"kind": "discrete", "points": [0, 1]}
        case "outside-constant":
            rules[0]["consequent"]["value"] = 2
        case "unknown-coefficient":
            coefficients[0]["input"] = "Risk"
        case "duplicate-coefficient":
            coefficients.append(dict(coefficients[0]))
        case "duplicate-input-id":
            inputs.append(dict(inputs[0], name="Second"))
        case "duplicate-input-name":
            inputs.append(dict(inputs[0], id="second"))
        case "duplicate-rule-id":
            rules[1]["id"] = rules[0]["id"]
        case "duplicate-rule-name":
            rules[1]["name"] = rules[0]["name"]

    with pytest.raises(ScaleModelDecodeError) as failure:
        DecodeSugenoModel(json.dumps(document).encode())

    assert failure.value.category == category, "Preserve the actionable semantic failure category."
    assert failure.value.pointer == pointer, "Locate the exact offending inference field."
