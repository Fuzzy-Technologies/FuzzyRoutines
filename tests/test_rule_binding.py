# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Readable rule binding to exact configured names and v1 IDs."""

from dataclasses import replace
from math import copysign

import pytest

from fuzzyroutines._rule_binding import _BindRule
from fuzzyroutines._rule_parser import _RuleParseError
from fuzzyroutines.configuration import AssembleModel, MamdaniBinding, ModelConfiguration, ScaleDefinition, SugenoBinding
from fuzzyroutines.domain import ContinuousUniverse, IntegrationDomain
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.inference import (
    AffineConsequent,
    AllOf,
    AnyOf,
    ConstantConsequent,
    FuzzyVariable,
    InferencePolicy,
    MamdaniModel,
    MamdaniRule,
    NotCondition,
    SugenoModel,
    SugenoRule,
    TermCondition,
)
from fuzzyroutines.linguistic import LinguisticScale, LinguisticTerm
from fuzzyroutines.membership import Triangle
from fuzzyroutines.operators import NegationPolicy, SNormPolicy, TNormPolicy


def _Configuration(mamdani: bool) -> ModelConfiguration:
    """Build a validated context with separate input and output namespaces."""

    pytest.importorskip("jsonschema")
    universe = ContinuousUniverse(0, 1, True, True)
    triangle = Triangle(0, 0.5, 1)
    fuzzySet = ScalarFuzzySet(universe, triangle)
    low = LinguisticTerm("Low", fuzzySet)
    stable = LinguisticTerm("Stable", fuzzySet)
    urgent = LinguisticTerm("Urgent", fuzzySet)
    scopes = {
        "risk-scale": ScaleDefinition(LinguisticScale((low,)), "u", ("low-id",), ("triangle",)),
        "sensor-scale": ScaleDefinition(LinguisticScale((stable,)), "u", ("stable-id",), ("triangle",)),
        "out-scale": ScaleDefinition(LinguisticScale((urgent,)), "u", ("urgent-id",), ("triangle",)),
    }
    inputs = (FuzzyVariable("risk", (low,)), FuzzyVariable("sensor", (stable,)))
    pairs = (("risk-id", "risk-scale"), ("sensor-id", "sensor-scale"))
    policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))
    condition = TermCondition("risk", "Low")
    binding: MamdaniBinding | SugenoBinding

    if mamdani:
        output = FuzzyVariable("result", (urgent,))
        model = MamdaniModel(
            inputs, output, (MamdaniRule("Existing", condition, "Urgent"),),
            policy, TNormPolicy("logic"), SNormPolicy("logic"),
        )
        binding = MamdaniBinding(model, pairs, ("existing-id",), "out-id", "out-scale")

    else:
        sugeno = SugenoModel(inputs, (SugenoRule("Existing", condition, ConstantConsequent(0.25)),), policy, universe)
        binding = SugenoBinding(sugeno, pairs, ("existing-id",), "u")

    return AssembleModel({"u": universe}, {"triangle": triangle}, scopes, inference=binding)


def test_MamdaniWireIdsAndHandBuiltInferenceAgree() -> None:
    """Bind ordered conditions and the output term without changing the model."""

    configuration = _Configuration(True)
    binding = configuration.inference
    assert isinstance(binding, MamdaniBinding)
    source = b'RULE first "First" IF NOT "risk" IS "Low" AND "sensor" IS "Stable" THEN TERM "Urgent" WEIGHT 0.5'
    bound = _BindRule(source, configuration)
    expected = MamdaniRule(
        "First", AllOf((NotCondition(TermCondition("risk", "Low")), TermCondition("sensor", "Stable"))),
        "Urgent", 0.5,
    )
    assert isinstance(bound.rule, MamdaniRule) and bound.rule == expected
    assert bound.wire == {
        "id": "first", "name": "First", "weight": 0.5, "consequent": "urgent-id",
        "antecedent": {"kind": "all", "operands": [
            {"kind": "not", "operand": {"kind": "term", "input": "risk-id", "term": "low-id"}},
            {"kind": "term", "input": "sensor-id", "term": "stable-id"},
        ]},
    }
    coordinates = {"risk": 0.25, "sensor": 0.25}
    domain = IntegrationDomain(0, 1)
    actual = replace(binding.model, rules=(bound.rule,)).Evaluate(coordinates, domain)
    reference = replace(binding.model, rules=(expected,)).Evaluate(coordinates, domain)
    actualTrace, = actual.rules
    referenceTrace, = reference.rules
    assert actual.inputGrades == reference.inputGrades
    assert (actualTrace.name, actualTrace.antecedentGrade, actualTrace.weight, actualTrace.firingStrength) == (
        referenceTrace.name, referenceTrace.antecedentGrade, referenceTrace.weight, referenceTrace.firingStrength,
    )
    assert actualTrace.firingStrength == 0.25 and actual.value == reference.value

    for coordinate in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert actualTrace.activatedSet.Membership(coordinate) == referenceTrace.activatedSet.Membership(coordinate)
        assert actual.outputSet.Membership(coordinate) == reference.outputSet.Membership(coordinate)

    assert len(binding.model.rules) == 1 and binding.model.rules[0].name == "Existing"


def test_SugenoAffineOrderAndHandBuiltInferenceAgree() -> None:
    """Bind affine coefficients by explicit IDs and preserve signed zero."""

    configuration = _Configuration(False)
    binding = configuration.inference
    assert isinstance(binding, SugenoBinding)
    source = (
        b'RULE next "Next" IF "risk" IS "Low" OR "sensor" IS "Stable" '
        b'THEN AFFINE(0.25,"sensor":-0,"risk":0.5) WEIGHT 0.5'
    )
    bound = _BindRule(source, configuration)
    expected = SugenoRule(
        "Next", AnyOf((TermCondition("risk", "Low"), TermCondition("sensor", "Stable"))),
        AffineConsequent(0.25, (("sensor", -0.0), ("risk", 0.5))), 0.5,
    )
    assert isinstance(bound.rule, SugenoRule) and bound.rule == expected
    assert isinstance(bound.rule.consequent, AffineConsequent)
    assert copysign(1.0, bound.rule.consequent.coefficients[0][1]) == -1.0
    assert bound.wire["consequent"] == {
        "kind": "affine", "intercept": 0.25,
        "coefficients": [{"input": "sensor-id", "value": -0.0}, {"input": "risk-id", "value": 0.5}],
    }
    coordinates = {"risk": 0.25, "sensor": 0.5}
    actual = replace(binding.model, rules=(bound.rule,)).Evaluate(coordinates)
    reference = replace(binding.model, rules=(expected,)).Evaluate(coordinates)
    assert actual == reference and actual.value == 0.375


def test_ExactReferenceAndSemanticErrorsUseSourceOffsets() -> None:
    """Point to the offending token after multibyte text and across scopes."""

    configuration = _Configuration(False)
    prefix = 'RULE next "温度" IF '.encode()
    condition = b'"risk" IS "Low" THEN '
    cases = (
        (b'"risk-id" IS "Low" THEN CONSTANT 0 WEIGHT 1', b'"risk-id"', "unresolved-binding"),
        (b'"risk" IS "Stable" THEN CONSTANT 0 WEIGHT 1', b'"Stable"', "unresolved-binding"),
        (condition + b'AFFINE(0,"Sensor":1) WEIGHT 1', b'"Sensor"', "unresolved-binding"),
        (condition + b'TERM "Urgent" WEIGHT 1', b"TERM", "invalid-rule-semantics"),
        (condition + b"CONSTANT 1.5 WEIGHT 1", b"1.5", "invalid-rule-semantics"),
    )

    for tail, token, category in cases:
        source = prefix + tail

        with pytest.raises(_RuleParseError) as failure:
            _BindRule(source, configuration)

        assert (failure.value.category, failure.value.offset) == (category, source.index(token))


def test_DuplicateRuleIdentityIsRejectedWithoutMutation() -> None:
    """Preserve both unique rule namespaces in the original model."""

    configuration = _Configuration(True)
    suffix = b' IF "risk" IS "Low" THEN TERM "Urgent" WEIGHT 1'

    for prefix, token in ((b'RULE existing-id "Other"', b"existing-id"), (b'RULE other "Existing"', b'"Existing"')):
        source = prefix + suffix

        with pytest.raises(_RuleParseError) as failure:
            _BindRule(source, configuration)

        assert failure.value.category == "invalid-rule-semantics"
        assert failure.value.offset == source.index(token)

    binding = configuration.inference
    assert isinstance(binding, MamdaniBinding)
    assert binding.ruleIds == ("existing-id",) and len(binding.model.rules) == 1


def test_CanonicalOverflowPrecedesModelResolution() -> None:
    """Reject a compact input at its EOF before building a partial bound rule."""

    configuration = _Configuration(False)
    pairs = b"".join(f',"x{index:03d}{"a" * 246}":0'.encode() for index in range(255))
    source = b'RULE r "R" IF "risk" IS "Low" THEN AFFINE(0' + pairs + b") WEIGHT 1"

    with pytest.raises(_RuleParseError) as failure:
        _BindRule(source, configuration)

    assert failure.value.category == "exceeded-limit"
    assert failure.value.offset == len(source) and "Canonical rule" in str(failure.value)
