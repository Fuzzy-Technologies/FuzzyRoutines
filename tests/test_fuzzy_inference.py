# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Independent integral references and failure boundaries for scalar inference."""

import math
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction

import pytest

from fuzzyroutines import (
    CentroidConvergenceError,
    CentroidPolicy,
    ContinuousUniverse,
    DiscreteUniverse,
    IntegrationDomain,
    LinguisticTerm,
    NegationPolicy,
    ScalarFuzzySet,
    SNormPolicy,
    TNormPolicy,
)
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
    NumericalError,
    UndefinedResultError,
)
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

UNIT = ContinuousUniverse(0, 1, True, True)
POLICY = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))
DOMAIN = IntegrationDomain(0, 1)


def Low(coordinate):
    """Return the analytical decreasing unit ramp."""

    return 1 - coordinate


def High(coordinate):
    """Return the analytical increasing unit ramp."""

    return coordinate


def Variable(name="risk"):
    """Create a two-ramp linguistic variable without inference dependencies."""

    return FuzzyVariable(name, (
        LinguisticTerm("low", ScalarFuzzySet(UNIT, Low)),
        LinguisticTerm("high", ScalarFuzzySet(UNIT, High)),
    ))


def Mamdani():
    """Create the hand-integrable reference model from ADR-0017."""

    return MamdaniModel((Variable(),), Variable("response"), (
        MamdaniRule("low rule", TermCondition("risk", "low"), "low"),
        MamdaniRule("high rule", TermCondition("risk", "high"), "high"),
    ), POLICY, TNormPolicy("logic"), SNormPolicy("logic"))


def Sugeno(affine=False):
    """Create independently computable zero/first-order reference models."""

    consequents = (
        (AffineConsequent(0, (("risk", 0.5),)), AffineConsequent(0.5, (("risk", 0.5),)))
        if affine else (ConstantConsequent(0.2), ConstantConsequent(0.8))
    )

    return SugenoModel((Variable(),), (
        SugenoRule("low rule", TermCondition("risk", "low"), consequents[0]),
        SugenoRule("high rule", TermCondition("risk", "high"), consequents[1]),
    ), POLICY, UNIT)


def test_MamdaniMatchesPiecewiseIntegralAndTrace():
    """Integrate the three known segments by hand, independently of the engine."""

    result = Mamdani().Evaluate({"risk": 0.25}, DOMAIN)
    area = Fraction(3, 4) * Fraction(1, 4) + Fraction(1, 4) + Fraction(1, 4) * Fraction(1, 4)
    moment = Fraction(3, 4) * Fraction(1, 32) + Fraction(11, 96) + Fraction(1, 4) * Fraction(7, 32)
    assert area == Fraction(1, 2), "Analytical aggregate area must be 1/2"
    assert moment == Fraction(37, 192), "Analytical aggregate moment must be 37/192"
    assert result.value == pytest.approx(float(moment / area), rel=0, abs=1e-12), "Adaptive centroid disagrees with exact piecewise integration"
    assert result.method == "adaptive-simpson", "Composition must not claim analytical certification"
    assert tuple(trace.firingStrength for trace in result.rules) == (0.75, 0.25), "Firing order must follow rule declaration"
    assert tuple(grade.grade for grade in result.inputGrades) == (0.75, 0.25), "All input terms must be exposed"

    for coordinate, expected in ((0, 0.75), (0.25, 0.75), (0.5, 0.5), (0.75, 0.25), (1, 0.25)):
        assert result.outputSet.Membership(coordinate) == expected, "Max-min aggregate differs from its analytical envelope"


def test_SugenoIndependentConstantAndAffineReferences():
    """Check normalized weighted scalar consequences, not an area centroid."""

    zero = Sugeno().Evaluate({"risk": 0.25})
    first = Sugeno(True).Evaluate({"risk": 0.25})
    assert zero.value == pytest.approx(0.35, rel=0, abs=1e-15), "Zero-order reference is 3/4*1/5 + 1/4*4/5"
    assert first.value == pytest.approx(0.25, rel=0, abs=1e-15), "First-order reference is 3/4*1/8 + 1/4*5/8"
    assert tuple(trace.consequentValue for trace in first.rules) == (0.125, 0.625), "Affine values must use the current input"
    assert sum(trace.contribution for trace in zero.rules) == zero.value, "Trace contributions must reconstruct the output"
    assert sum(trace.normalizedStrength for trace in zero.rules) == 1, "Normalized strengths must sum to one"
    assert zero.method == "normalized-weighted-average", "Sugeno must identify its own output method"


@pytest.mark.parametrize("coordinate, expected", ((0, 0.2), (1, 0.8), (0.5, 0.5)))
def test_SugenoBoundaries(coordinate, expected):
    """Retain endpoint ownership, inactive rule traces and midpoint symmetry."""

    result = Sugeno().Evaluate({"risk": coordinate})
    assert result.value == pytest.approx(expected, rel=0, abs=1e-15), "Boundary weighted mean is incorrect"
    assert len(result.rules) == 2, "Inactive rules must remain visible in the trace"


def test_CompositionWeightsAndDifferentActivationAreIndependent():
    """Verify multiple inputs with OR/NOT and product conjunction/weighting."""

    condition = AllOf((TermCondition("risk", "high"), AnyOf((
        TermCondition("load", "high"), NotCondition(TermCondition("load", "low")),
    ))))
    model = replace(Mamdani(), inputs=(Variable(), Variable("load")), rules=(
        MamdaniRule("combined", condition, "high", 0.5),
    ), policy=replace(POLICY, conjunction=TNormPolicy("algebraic")), activation=TNormPolicy("algebraic"))
    result = model.Evaluate({"risk": 0.5, "load": 0.25}, DOMAIN)
    assert result.rules[0].antecedentGrade == 0.125, "AND must use the explicitly chosen product"
    assert result.rules[0].firingStrength == 0.0625, "Rule weight is multiplicative, independent from conjunction"
    assert result.outputSet.Membership(0.5) == 0.03125, "Output activation must use its own operator"
    assert result.value == pytest.approx(2 / 3, rel=0, abs=1e-12), "Scaling a unit increasing ramp preserves its 2/3 centroid"


def test_OverlappingContradictoryRulesAndAggregationChoice():
    """Expose contradictory consequences and the effect of duplicate rules."""

    model = Mamdani()
    symmetric = model.Evaluate({"risk": 0.5}, DOMAIN)
    assert symmetric.value == pytest.approx(0.5, rel=0, abs=1e-12), "Symmetric contradictory rules must have a centered centroid"
    duplicated = replace(model, rules=model.rules + (replace(model.rules[0], name="duplicate"),))
    maximum = duplicated.Evaluate({"risk": 0.5})
    summed = replace(duplicated, aggregation=SNormPolicy("boundary")).Evaluate({"risk": 0.5})
    assert maximum.outputSet.Membership(0.5) == 0.5, "Maximum aggregation is idempotent"
    assert summed.outputSet.Membership(0.5) == 1, "Bounded-sum aggregation must saturate explicitly"


def test_SugenoWeightScalingAndConvexHull():
    """Scale normalization must preserve tiny common weights and convexity."""

    model = Sugeno()
    tiny = replace(model, rules=tuple(replace(rule, weight=1e-310) for rule in model.rules))
    result = tiny.Evaluate({"risk": 0.25})
    assert result.value == pytest.approx(0.35, rel=0, abs=1e-12), "Common tiny weights must not create a false zero denominator"
    assert 0.2 <= result.value <= 0.8, "Non-negative normalized weights preserve the consequent convex hull"
    reordered = replace(model, rules=tuple(reversed(model.rules))).Evaluate({"risk": 0.25})
    assert reordered.value == pytest.approx(result.value, rel=0, abs=1e-12), "Reordering independent rules must preserve weighted output"


def test_ResultsOwnSnapshotsWithoutRetainingMutableInputs():
    """Later evaluations and input mutations must not alter prior traces/sets."""

    inputs = {"risk": 0.25}
    model = Mamdani()
    result = model.Evaluate(inputs)
    inputs["risk"] = 0.75
    model.Evaluate(inputs)
    assert result.outputSet.Membership(0) == 0.75, "Prior aggregate must retain its own firing snapshot"
    assert result.value is None and result.method == "fuzzy-set", "No implicit defuzzification is permitted"

    with pytest.raises(FrozenInstanceError):
        result.value = 0

    with pytest.raises(FrozenInstanceError):
        model.rules = ()

    with pytest.raises(InvalidParameterTypeError):
        replace(result, rules=list(result.rules))


@pytest.mark.parametrize("values", ({}, {"risk": 0.2, "extra": 0.1}, {"Risk": 0.2}))
def test_RejectMissingExtraAndWrongCaseInputs(values):
    """Input key mismatch must not fall back to an inferred coordinate."""

    for model in (Mamdani(), Sugeno()):
        with pytest.raises(InvalidParameterError, match="exactly"):
            model.Evaluate(values)


@pytest.mark.parametrize("value, error", ((True, InvalidParameterTypeError), ("0.2", InvalidParameterTypeError), (math.nan, InvalidParameterError), (math.inf, InvalidParameterError), (-0.1, InvalidDomainError), (1.1, InvalidDomainError)))
def test_RejectInvalidInputValues(value, error):
    """Both engines reject malformed coordinates before producing predictions."""

    for model in (Mamdani(), Sugeno()):
        with pytest.raises(error):
            model.Evaluate({"risk": value})


def test_NoFireAndZeroAreaAreDifferentFailures():
    """Positive firing alone does not establish nonzero integrated output area."""

    model = Mamdani()
    noFire = replace(model, rules=tuple(replace(rule, weight=0) for rule in model.rules))

    with pytest.raises(UndefinedResultError, match="no rule fires"):
        noFire.Evaluate({"risk": 0.25})

    sugeno = Sugeno()

    with pytest.raises(UndefinedResultError, match="no rule fires"):
        replace(sugeno, rules=tuple(replace(rule, weight=0) for rule in sugeno.rules)).Evaluate({"risk": 0.25})

    def Zero(coordinate):
        """Return a zero-area output set despite positive antecedent firing."""

        return 0

    empty = replace(model, output=FuzzyVariable("output", (LinguisticTerm("zero", ScalarFuzzySet(UNIT, Zero)),)), rules=(replace(model.rules[0], consequent="zero"),))
    assert empty.Evaluate({"risk": 0.25}).outputSet.Membership(0.5) == 0, "A fuzzy-only result may expose an empty output set"

    with pytest.raises(UndefinedResultError, match="zero membership area"):
        empty.Evaluate({"risk": 0.25}, DOMAIN)


def test_NumericalNonconvergencePropagates():
    """A coarse depth budget must not silently invent a Mamdani centroid."""

    def FourthPower(coordinate):
        """Use a smooth non-polynomial-for-Simpson integrand requiring refinement."""

        return coordinate**4

    model = Mamdani()
    output = FuzzyVariable("output", (LinguisticTerm("power", ScalarFuzzySet(UNIT, FourthPower)),))
    model = replace(model, output=output, rules=(MamdaniRule("power", TermCondition("risk", "high"), "power"),))

    with pytest.raises(CentroidConvergenceError):
        model.Evaluate({"risk": 1}, DOMAIN, CentroidPolicy(maximumDepth=0))

    assert model.Evaluate({"risk": 1}, DOMAIN).value == pytest.approx(5 / 6, rel=0, abs=1e-9), "Resolved x^4 density has centroid (1/6)/(1/5)"


def test_SugenoArithmeticAndUniverseFailuresAreExplicit():
    """Reject overflow, undefined sums and out-of-range affine consequences."""

    model = Sugeno(True)
    huge = replace(model.rules[0], consequent=AffineConsequent(1e308, (("risk", 1e308),)))

    with pytest.raises(NumericalError, match="overflow"):
        replace(model, rules=(huge,), outputUniverse=ContinuousUniverse()).Evaluate({"risk": 0.9})

    outside = replace(model.rules[0], consequent=AffineConsequent(0, (("risk", 2),)))

    with pytest.raises(InvalidDomainError, match="consequent"):
        replace(model, rules=(outside,)).Evaluate({"risk": 0.75})

    with pytest.raises(InvalidDomainError, match="constant"):
        replace(Sugeno(), rules=(replace(Sugeno().rules[0], consequent=ConstantConsequent(2)),))


def test_FailEvenForInvalidInactiveConsequent():
    """Inactive rules remain part of the model and cannot hide invalid values."""

    model = Sugeno(True)
    invalid = replace(model.rules[0], consequent=AffineConsequent(2, ()), weight=0)

    with pytest.raises(InvalidDomainError, match="consequent"):
        replace(model, rules=(invalid, model.rules[1])).Evaluate({"risk": 0.5})


@pytest.mark.parametrize("construct", (
    lambda: FuzzyVariable("", Variable().terms),
    lambda: FuzzyVariable("risk", (Variable().terms[0], Variable().terms[0])),
    lambda: FuzzyVariable("risk", list(Variable().terms)),
    lambda: AllOf((TermCondition("risk", "low"),)),
    lambda: NotCondition("risk is low"),
    lambda: MamdaniRule("bad", TermCondition("risk", "low"), "low", -1),
    lambda: ConstantConsequent(math.inf),
    lambda: AffineConsequent(0, (("risk", 1), ("risk", 2))),
    lambda: AffineConsequent(0, (("risk", math.nan),)),
    lambda: replace(Mamdani(), rules=()),
    lambda: replace(Mamdani(), inputs=(Variable(), Variable())),
    lambda: replace(Mamdani(), rules=(MamdaniRule("bad", TermCondition("missing", "low"), "low"),)),
    lambda: replace(Mamdani(), rules=(MamdaniRule("bad", TermCondition("risk", "low"), "missing"),)),
    lambda: replace(Sugeno(), rules=(SugenoRule("bad", TermCondition("risk", "low"), AffineConsequent(0, (("missing", 1),))),)),
    lambda: replace(Mamdani(), activation="minimum"),
    lambda: replace(Sugeno(), policy="default"),
))
def test_RejectMalformedModels(construct):
    """Typed construction validates unknown bindings, shapes and policy choices."""

    with pytest.raises((InvalidParameterError, InvalidParameterTypeError)):
        construct()


def test_ValidateIntegrationBeforeEvaluatingCallbacks():
    """A missing domain, invalid policy or out-of-universe interval is rejected."""

    model = Mamdani()

    with pytest.raises(InvalidParameterError, match="requires"):
        model.Evaluate({"risk": 0.5}, centroidPolicy=CentroidPolicy())

    with pytest.raises(InvalidDomainError):
        model.Evaluate({"risk": 0.5}, IntegrationDomain(-1, 1))

    with pytest.raises(InvalidParameterTypeError):
        model.Evaluate({"risk": 0.5}, DOMAIN, "automatic")


def test_DiscreteInputsAndMixedMembershipShapes():
    """Input universes may be discrete while the output remains continuous."""

    variable = FuzzyVariable("risk", (LinguisticTerm("high", ScalarFuzzySet(DiscreteUniverse((0, 0.5, 1)), High)),))
    model = replace(Sugeno(), inputs=(variable,), rules=(Sugeno().rules[1],))
    assert model.Evaluate({"risk": 0.5}).value == 0.8, "A valid discrete input must participate in scalar inference"

    with pytest.raises(InvalidDomainError):
        model.Evaluate({"risk": 0.25})


def test_EvaluateEachTermOnceAndPreserveCallbackExceptions():
    """Repeated references reuse a per-call snapshot without swallowing errors."""

    calls = []

    def Counting(coordinate):
        """Record one invocation and return a valid degree."""

        calls.append(coordinate)

        return coordinate

    variable = FuzzyVariable("risk", (LinguisticTerm("high", ScalarFuzzySet(UNIT, Counting)),))
    model = replace(Sugeno(), inputs=(variable,), rules=(replace(Sugeno().rules[1], antecedent=AllOf((TermCondition("risk", "high"), TermCondition("risk", "high")))),))
    model.Evaluate({"risk": 0.5})
    assert calls == [0.5], "A repeated term reference must be evaluated once per invocation"

    def Broken(coordinate):
        """Raise a custom evaluator failure that must remain visible."""

        raise RuntimeError("custom callback failed")

    broken = FuzzyVariable("risk", (LinguisticTerm("high", ScalarFuzzySet(UNIT, Broken)),))

    with pytest.raises(RuntimeError, match="custom callback failed"):
        replace(model, inputs=(broken,)).Evaluate({"risk": 0.5})


def test_ExampleRunsThroughTheCommandLine():
    """Exercise the user-facing JSON boundary, not only its helper functions."""

    import json
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, "-m", "examples.inference"], cwd=root, capture_output=True, text=True, timeout=30, check=False)
    assert result.returncode == 0, f"Inference example failed: {result.stderr}"
    payload = json.loads(result.stdout)
    assert payload["mamdani"]["value"] == pytest.approx(37 / 96, rel=0, abs=1e-12), "CLI evidence must expose the actual centroid"
    assert payload["firingStrengths"] == [0.75, 0.25], "CLI evidence must preserve fired-rule order"


def test_MixedMembershipFamiliesFeedTheSameRuleContract():
    """Combine a Gaussian peak and triangle slope without assuming a partition."""

    from fuzzyroutines import Gaussian, Triangle

    variable = FuzzyVariable("risk", (
        LinguisticTerm("peak", ScalarFuzzySet(UNIT, Gaussian(0.5, 0.2))),
        LinguisticTerm("ramp", ScalarFuzzySet(UNIT, Triangle(0, 1, 1))),
    ))
    model = SugenoModel((variable,), (
        SugenoRule("peak", TermCondition("risk", "peak"), ConstantConsequent(0.2)),
        SugenoRule("ramp", TermCondition("risk", "ramp"), ConstantConsequent(0.8)),
    ), POLICY, UNIT)
    result = model.Evaluate({"risk": 0.5})
    assert tuple(grade.grade for grade in result.inputGrades) == (1, 0.5), "Input grades need not sum to one"
    assert result.value == pytest.approx(0.4, rel=0, abs=1e-15), "Sugeno must normalize firing strengths independently of the membership family"


def test_AffineProductOverflowIsRejectedBeforeSummation():
    """Large finite coefficients/coordinates cannot silently generate infinity."""

    def Full(coordinate):
        """Return full membership for any finite real coordinate."""

        return 1

    variable = FuzzyVariable("large", (LinguisticTerm("valid", ScalarFuzzySet(ContinuousUniverse(), Full)),))
    model = SugenoModel((variable,), (
        SugenoRule("overflow", TermCondition("large", "valid"), AffineConsequent(0, (("large", 1e308),))),
    ), POLICY, ContinuousUniverse())

    with pytest.raises(NumericalError, match="intermediate arithmetic"):
        model.Evaluate({"large": 2})


@pytest.mark.parametrize("left,right,constant", ((0, 1, 1), (0, 1, 0), (-0.1, 0.2, 0.2), (0.1, 0.2, 0.1), (-1, -0.3, -0.3), (1e308, float.fromhex("0x1.fffffffffffffp+1023"), float.fromhex("0x1.fffffffffffffp+1023"))))
def test_SugenoConstantBoundarySurvivesWeightRounding(left, right, constant):
    """A convex combination of equal endpoint consequences is exactly that endpoint."""

    def Full(coordinate):
        """Return a full firing degree independently of the normalized weights."""

        return 1

    variable = FuzzyVariable("x", (LinguisticTerm("full", ScalarFuzzySet(UNIT, Full)),))
    model = SugenoModel((variable,), tuple(
        SugenoRule(f"rule {index}", TermCondition("x", "full"), ConstantConsequent(constant), weight)
        for index, weight in enumerate((0.01227824739797545, 0.11239886108023578))
    ), POLICY, ContinuousUniverse(left, right, True, True))
    result = model.Evaluate({"x": 0.5})
    assert result.value == constant, "A rounded trace sum must not reject or move an exact constant endpoint"
    assert sum(trace.normalizedStrength for trace in result.rules) == pytest.approx(1, rel=0, abs=1e-15), "Recorded normalized strengths must remain honest floating-point values"

    for trace in result.rules:
        assert trace.contribution == trace.normalizedStrength * constant, "Stabilizing the final mean must not falsify individual rule contributions"


def test_SugenoBoundaryFallbackPreservesTinyRationalWeights():
    """Exact rational degrees must not underflow through a binary64 conversion."""

    def Full(coordinate):
        """Return an exact full grade to preserve rational arithmetic upstream."""

        return 1

    weights = tuple(Fraction(value) / 10**1000 for value in (0.01227824739797545, 0.11239886108023578))
    variable = FuzzyVariable("x", (LinguisticTerm("full", ScalarFuzzySet(UNIT, Full)),))
    model = SugenoModel((variable,), tuple(
        SugenoRule(f"rule {index}", TermCondition("x", "full"), ConstantConsequent(1), weight)
        for index, weight in enumerate(weights)
    ), POLICY, UNIT)
    result = model.Evaluate({"x": 0.5})
    assert result.value == 1, "A rational firing denominator must not become zero through a fallback float cast"
    assert tuple(trace.firingStrength for trace in result.rules) == weights, "The trace must retain the original exact rational strengths"
