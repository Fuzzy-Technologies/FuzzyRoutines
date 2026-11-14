# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Independent structural examples for Mamdani and Sugeno rule drafts."""

import pytest

from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.exceptions import InvalidParameterError, InvalidParameterTypeError
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.inference import (
    AffineConsequent,
    AllOf,
    AnyOf,
    ConstantConsequent,
    FuzzyVariable,
    MamdaniRule,
    NotCondition,
    SugenoRule,
    TermCondition,
)
from fuzzyroutines.linguistic import LinguisticTerm
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.rule_diagnostics import InspectRules


def _UnexpectedMembership(coordinate: MembershipScalar) -> MembershipScalar:
    """Fail if structural inspection ever evaluates a membership callback."""

    raise AssertionError(f"Structural inspection evaluated membership at {coordinate!r}")


def _Variable(name: str) -> FuzzyVariable:
    """Make a declaration whose callbacks must stay unevaluated."""

    universe = ContinuousUniverse(0, 1, True, True)
    fuzzy_set = ScalarFuzzySet(universe, _UnexpectedMembership)

    return FuzzyVariable(name, (LinguisticTerm("low", fuzzy_set), LinguisticTerm("high", fuzzy_set)))


def test_MamdaniReferencesAreReportedInTreeOrderForDisabledRule() -> None:
    """Find every distinct missing binding without treating zero weight as a waiver."""

    draft = MamdaniRule(
        "draft",
        AllOf((
            TermCondition("risk", "missing"),
            NotCondition(AnyOf((
                TermCondition("typo", "high"),
                TermCondition("risk", "missing"),
            ))),
        )),
        "undefined",
        weight=0,
    )
    findings = InspectRules((_Variable("risk"),), (draft,), output=_Variable("action"))

    assert [(item.code, item.severity, item.rule_index) for item in findings] == [
        ("unknown_input_term", "error", 0),
        ("unknown_input", "error", 0),
        ("unknown_output_term", "error", 0),
        ("zero_weight", "warning", 0),
    ], "Inspection must visit nested leaves before checking the consequence and weight"
    assert "'missing'" in findings[0].message and "'risk'" in findings[0].message, (
        "The explanation must name the missing term and its declared variable"
    )


def test_DuplicatesAndConflictsUseExactAntecedentsAndEarliestRule() -> None:
    """Distinguish exact repeats, different outputs, partial overlap and different weights."""

    high = TermCondition("risk", "high")
    low = TermCondition("risk", "low")
    rules = (
        MamdaniRule("base", high, "high"),
        MamdaniRule("weighted", high, "high", weight=0.5),
        MamdaniRule("repeat", high, "high"),
        MamdaniRule("different", high, "low"),
        MamdaniRule("overlap", AllOf((high, low)), "low"),
        MamdaniRule("reordered", AllOf((low, high)), "high"),
        MamdaniRule("off", high, "low", weight=0),
    )
    findings = InspectRules((_Variable("risk"),), rules, output=_Variable("action"))

    assert [(item.code, item.rule_index, item.related_rule_index) for item in findings] == [
        ("duplicate_rule", 2, 0),
        ("potential_conflict", 3, 0),
        ("zero_weight", 6, None),
    ], "Only exact active antecedents may form pairs, and each pair must point to the first earlier match"


def test_SugenoResolvesAffineInputsAndComparesDeclaredMaps() -> None:
    """Avoid warnings for explicit zero coefficients and locate unknown affine inputs."""

    antecedent = TermCondition("risk", "high")
    rules = (
        SugenoRule("constant", antecedent, ConstantConsequent(0.25)),
        SugenoRule("equivalent", antecedent, AffineConsequent(0.25, (("risk", 0),))),
        SugenoRule("different", antecedent, AffineConsequent(0.25, (("risk", 0.5),))),
        SugenoRule("constant", antecedent, AffineConsequent(0.25, (("typo", 0.5),))),
        SugenoRule("repeat", antecedent, AffineConsequent(0.25, (("risk", 0.5),))),
    )
    findings = InspectRules((_Variable("risk"),), rules)

    assert [(item.code, item.rule_index, item.related_rule_index) for item in findings] == [
        ("potential_conflict", 2, 0),
        ("duplicate_name", 3, 0),
        ("unknown_affine_input", 3, None),
        ("duplicate_rule", 4, 2),
        ("potential_conflict", 4, 0),
    ], "A bad affine binding must not produce a comparison warning, and distinct valid pairs must remain visible"


def test_EmptyDraftAndAmbiguousDeclarations() -> None:
    """Allow empty drafts while failing closed for ambiguous input names or rule kinds."""

    variable = _Variable("risk")
    rule = MamdaniRule("mamdani", TermCondition("risk", "high"), "high")

    assert InspectRules((variable,), ()) == (), "An empty draft must not invent diagnostics"

    with pytest.raises(InvalidParameterError, match="input names must be unique"):
        InspectRules((variable, variable), ())

    with pytest.raises(InvalidParameterTypeError, match="SugenoRule"):
        InspectRules((variable,), (rule,))
