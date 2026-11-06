# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic v1 model round trips and lossless export boundaries."""

import json
import math
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from fuzzyroutines._config_export import ConfigExportError, EncodeModel
from fuzzyroutines._config_mamdani_model import DecodeMamdaniModel
from fuzzyroutines._config_scale_model import DecodeScaleModel
from fuzzyroutines._config_sugeno_model import DecodeSugenoModel
from fuzzyroutines.defuzzification import CentroidPolicy
from fuzzyroutines.domain import DiscreteUniverse
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.inference import AffineConsequent, MamdaniModel, SugenoModel
from fuzzyroutines.linguistic import LinguisticScale
from fuzzyroutines.membership import MembershipFunction

pytest.importorskip("jsonschema")

_FIXTURES = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "config-v1" / "fixtures"


def _InlineFixture(modelId):
    """Read the original standalone inference envelope from the golden project."""

    return json.loads((_FIXTURES / "valid-project.json").read_bytes())["models"][modelId]


@pytest.mark.parametrize("fileName", ("valid-historical-scale.json", "valid-discrete-scale.json"))
def test_ScaleRoundTripRetainsExactDefinitionsAndPolicies(fileName):
    """Preserve normative coefficients, ordered windows and policies on export."""

    original = (_FIXTURES / fileName).read_bytes()
    model = DecodeScaleModel(original)
    encoded = EncodeModel(model)
    decoded = DecodeScaleModel(encoded)

    assert json.loads(encoded) == json.loads(original), "Keep every explicit definition and policy."
    assert EncodeModel(decoded) == encoded, "Re-export produces identical bytes."
    assert encoded.endswith(b"\n") and b"\r" not in encoded, "Emit UTF-8 JSON with a final LF."
    assert all(
        first.parameters == decoded.memberships[key].parameters for key, first in model.memberships.items()
    ), "Retain built-in family parameters."
    assert all(
        first.representatives == decoded.scales[key].representatives for key, first in model.scales.items()
    ), "Retain representative windows and exact numerical policies."


def test_SugenoRoundTripPreservesAffineOrderAndFullTraces():
    """Keep ordered inputs, coefficients, consequents and exact weighted outputs."""

    original = _InlineFixture("weighted")
    inference = original["inference"]
    inference["inputs"].append({"id": "second", "name": "Second", "scale": "risk"})
    inference["rules"][1]["consequent"]["coefficients"].insert(0, {"input": "second", "value": -0.125})
    model = DecodeSugenoModel(json.dumps(original).encode())
    encoded = EncodeModel(model)
    decoded = DecodeSugenoModel(encoded)
    assert json.loads(encoded) == original, "Preserve wire ID bindings and ordered expressions."
    assert EncodeModel(decoded) == encoded, "Canonical export must be byte-identical after reconstruction."

    for coordinate in (0, 0.25, 0.5, 0.75, 1):
        inputs = {"Risk": coordinate, "Second": 0.25}
        assert decoded.model.Evaluate(inputs) == model.model.Evaluate(inputs), "Preserve every Sugeno trace field."


def test_MamdaniRoundTripPreservesWindowOperatorsAndTraces():
    """Keep the configured centroid, weighted firing trace and aggregate grades."""

    original = _InlineFixture("centroid")
    model = DecodeMamdaniModel(json.dumps(original).encode())
    encoded = EncodeModel(model)
    decoded = DecodeMamdaniModel(encoded)
    assert json.loads(encoded) == original, "Keep explicit operators and optional centroid settings."
    assert EncodeModel(decoded) == encoded, "Canonical export must be byte-identical after reconstruction."
    assert model.centroid is not None and decoded.centroid == model.centroid, "Keep exact numerical settings."

    for coordinate in (0, 0.25, 0.5, 0.75):
        first = model.model.Evaluate({"Risk": coordinate}, model.centroid.domain, model.centroid.policy)
        second = decoded.model.Evaluate({"Risk": coordinate}, decoded.centroid.domain, decoded.centroid.policy)
        assert second.value == first.value, "Keep the numeric centroid."
        assert second.inputGrades == first.inputGrades, "Keep the ordered grade trace."
        assert [trace.firingStrength for trace in second.rules] == [trace.firingStrength for trace in first.rules], (
            "Keep the ordered weighted firing trace."
        )

        for point in (0, 0.25, 0.5, 0.75, 1):
            assert second.outputSet.Membership(point) == first.outputSet.Membership(point), "Keep aggregate grades."


def test_SerializesUnicodeAndSignedZeroWithoutCallingEvaluators(monkeypatch):
    """Emit exact text and signed-zero tokens without model or membership evaluation."""

    def RejectEvaluation(*arguments, **options):
        """Fail if export or its validation runs an evaluator."""

        raise AssertionError("Export must not execute mathematical models.")

    original = _InlineFixture("weighted")
    original["inference"]["rules"][0]["name"] = "База / 基准"
    original["inference"]["rules"][1]["consequent"]["intercept"] = -0.0
    model = DecodeSugenoModel(json.dumps(original).encode())
    monkeypatch.setattr(MembershipFunction, "Evaluate", RejectEvaluation)
    monkeypatch.setattr(SugenoModel, "Evaluate", RejectEvaluation)
    monkeypatch.setattr(MamdaniModel, "Evaluate", RejectEvaluation)
    encoded = EncodeModel(model)
    decoded = DecodeSugenoModel(encoded)
    affine = decoded.model.rules[1].consequent

    assert "База / 基准".encode() in encoded, "Emit preserved Unicode as UTF-8."
    assert b'"intercept":-0.0' in encoded, "Keep signed zero as a JSON number."
    assert isinstance(affine, AffineConsequent) and math.copysign(1.0, affine.intercept) < 0, "Restore negative zero."


@pytest.mark.parametrize("number", (Fraction(1, 10), Fraction(1, 1 << 1100), 2**53 + 1))
def test_RejectsRealValuesRequiringRounding(number):
    """Reject rounded, underflowed and nonrepresentable integer coefficients."""

    model = DecodeSugenoModel(json.dumps(_InlineFixture("weighted")).encode())
    rule = model.model.rules[1]
    consequent = AffineConsequent(0.5, (("Risk", number),))
    modified = replace(model, model=replace(model.model, rules=(model.model.rules[0], replace(rule, consequent=consequent))))

    with pytest.raises(ConfigExportError) as failure:
        EncodeModel(modified)

    assert failure.value.category == "unsupported-source", "Use the explicit source-value category."
    assert failure.value.pointer == "/inference/rules/1/consequent/coefficients/0/value", "Locate the exact coefficient."


def test_AcceptsExactlyRepresentableFractionAndRejectsOversizedIntegerDepth():
    """Keep exact finite rational values and enforce the distinct depth field limit."""

    model = DecodeSugenoModel(json.dumps(_InlineFixture("weighted")).encode())
    rule = model.model.rules[1]
    consequent = AffineConsequent(Fraction(1, 2), (("Risk", Fraction(1, 4)),))
    modified = replace(model, model=replace(model.model, rules=(model.model.rules[0], replace(rule, consequent=consequent))))
    exported = json.loads(EncodeModel(modified))["inference"]["rules"][1]["consequent"]
    assert exported["intercept"] == 0.5 and exported["coefficients"] == [{"input": "risk", "value": 0.25}], (
        "Encode exact binary fractions without loss."
    )

    mamdani = DecodeMamdaniModel(json.dumps(_InlineFixture("centroid")).encode())
    assert mamdani.centroid is not None, "The reference model declares a centroid."
    centroid = replace(mamdani.centroid, policy=CentroidPolicy(maximumDepth=2**53))

    with pytest.raises(ConfigExportError) as failure:
        EncodeModel(replace(mamdani, centroid=centroid))

    assert failure.value.pointer == "/inference/centroid/policy/maximumDepth", "Locate the nonportable depth."


def test_RejectsCallbacksAndMembershipSubclassesWithoutExecution():
    """Fail at the actual fuzzy-set source and never approximate the callable."""

    class CustomMembership(MembershipFunction):
        """An unsupported membership subclass with its own evaluator."""

        def Evaluate(self, coordinate):
            """Fail if a custom evaluator is called during export."""

            raise AssertionError("Membership subclasses must not be evaluated.")

    def Callback(coordinate):
        """Fail if an arbitrary fuzzy-set callback is sampled."""

        raise AssertionError("A callback must not be sampled.")

    model = DecodeScaleModel((_FIXTURES / "valid-historical-scale.json").read_bytes())
    scaleId, configured = next(iter(model.scales.items()))
    term = configured.scale.terms[0]

    for source in (Callback, CustomMembership("s_shoulder", left=0, right=1)):
        modifiedTerm = replace(term, fuzzySet=ScalarFuzzySet(term.fuzzySet.universe, source))
        modifiedScale = replace(configured, scale=LinguisticScale((modifiedTerm, *configured.scale.terms[1:])))
        modified = replace(model, scales={scaleId: modifiedScale})

        with pytest.raises(ConfigExportError) as failure:
            EncodeModel(modified)

        assert failure.value.pointer == f"/scales/{scaleId}/terms/0/membership", "Identify the unsupported term source."
        assert "built-in membership family" in str(failure.value), "Tell callers how to represent a supported source."


def test_RejectsNonfiniteSourceScalarsAndEscapesMapPointers():
    """Report the original key and field even for a malformed export source."""

    model = DecodeScaleModel((_FIXTURES / "valid-discrete-scale.json").read_bytes())
    universe = DiscreteUniverse((0.0, 1.0))
    object.__setattr__(universe, "points", (math.inf,))
    modified = replace(model, universes={"a/~b": universe})

    with pytest.raises(ConfigExportError) as failure:
        EncodeModel(modified)

    assert failure.value.pointer == "/universes/a~1~0b/points/0", "Escape exact map keys in source pointers."


def test_RejectsUnpairedUnicodeAtItsSourceField():
    """Locate an invalid source label before emitting invalid UTF-8."""

    model = DecodeSugenoModel(json.dumps(_InlineFixture("weighted")).encode())
    first, second = model.model.rules
    modified = replace(model, model=replace(model.model, rules=(replace(first, name="\ud800"), second)))

    with pytest.raises(ConfigExportError) as failure:
        EncodeModel(modified)

    assert failure.value.pointer == "/inference/rules/0/name", "Report the field with the invalid Unicode label."
