# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Strict source and installed-wheel consumers of scalar fuzzy inference.

Exact result/trace types and targeted negative probes prevent accidental Any
at model, antecedent, consequent, input and immutable-result boundaries.
"""

from typing import assert_type as assertType

from fuzzyroutines import (
    ContinuousUniverse,
    IntegrationDomain,
    LinguisticTerm,
    MembershipScalar,
    NegationPolicy,
    ScalarFuzzySet,
    SNormPolicy,
    TNormPolicy,
    Triangle,
)
from fuzzyroutines.inference import (
    AffineConsequent,
    AllOf,
    Antecedent,
    AnyOf,
    ConstantConsequent,
    FuzzyVariable,
    InferencePolicy,
    InputGrade,
    MamdaniModel,
    MamdaniResult,
    MamdaniRule,
    MamdaniRuleTrace,
    NotCondition,
    SugenoModel,
    SugenoResult,
    SugenoRule,
    SugenoRuleTrace,
    TermCondition,
)


def CheckInferenceConsumer() -> None:
    """Construct both models and inspect their complete typed result evidence."""

    universe = ContinuousUniverse(0, 1, True, True)
    terms = (LinguisticTerm("middle", ScalarFuzzySet(universe, Triangle(0, 0.5, 1))),)
    inputs = (FuzzyVariable("risk", terms),)
    leaf = TermCondition("risk", "middle")
    antecedent: Antecedent = AllOf((leaf, AnyOf((leaf, NotCondition(leaf)))))
    policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))
    mamdani = MamdaniModel(
        inputs, FuzzyVariable("response", terms),
        (MamdaniRule("response", antecedent, "middle"),),
        policy, TNormPolicy("logic"), SNormPolicy("logic"),
    )
    result = mamdani.Evaluate({"risk": 0.25}, IntegrationDomain(0, 1))
    assertType(result, MamdaniResult)
    assertType(result.inputGrades, tuple[InputGrade, ...])
    assertType(result.rules, tuple[MamdaniRuleTrace, ...])
    assertType(result.rules[0].activatedSet, ScalarFuzzySet)
    assertType(result.value, MembershipScalar | None)
    assertType(mamdani.Evaluate({"risk": 0.25}).outputSet, ScalarFuzzySet)

    sugeno = SugenoModel(inputs, (
        SugenoRule("constant", leaf, ConstantConsequent(0.2)),
        SugenoRule("affine", NotCondition(leaf), AffineConsequent(0.5, (("risk", 0.5),))),
    ), policy, universe)
    scalarResult = sugeno.Evaluate({"risk": 0.25})
    assertType(scalarResult, SugenoResult)
    assertType(scalarResult.inputGrades, tuple[InputGrade, ...])
    assertType(scalarResult.rules, tuple[SugenoRuleTrace, ...])
    assertType(scalarResult.rules[0].contribution, MembershipScalar)
    assertType(scalarResult.value, MembershipScalar)

    MamdaniRule("text", "risk is middle", "middle")  # type: ignore[arg-type]
    SugenoRule("numeric", leaf, 0.5)  # type: ignore[arg-type]
    AllOf((leaf, "condition"))  # type: ignore[arg-type]
    sugeno.Evaluate({"risk": "high"})  # type: ignore[dict-item]
    result.rules = ()  # type: ignore[misc]
