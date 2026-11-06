# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Ordering, analytical reuse and eligibility of prepared Sugeno models."""

from fractions import Fraction

import pytest

from fuzzyroutines._sugeno_antecedents import _EvaluateAntecedents
from fuzzyroutines._sugeno_batch import _ComputeFirings, _ReduceConsequents
from fuzzyroutines._sugeno_consequents import _EvaluateConsequents
from fuzzyroutines._sugeno_model import _PrepareModel, _PrepareTermSource
from fuzzyroutines.batches import _Evaluate
from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse
from fuzzyroutines.exceptions import InvalidParameterTypeError
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.inference import FuzzyVariable, SugenoModel
from fuzzyroutines.linguistic import LinguisticTerm
from fuzzyroutines.membership import MembershipFunction, Triangle

np = pytest.importorskip("numpy", reason="Sugeno rule batches use the optional NumPy extra")

from experiments.sugeno_batch_contract_probe import ScalarModel


def test_PreparedModelPreservesDeclaredFeaturesTermsAndRules():
    """Verify snapshot order and reuse existing numerical stages on one chunk."""

    model = ScalarModel("mixed")
    plan = _PrepareModel(model)
    rows = np.array([[0.25, 0.25], [0.5, 0.5]])
    reference = [
        model.Evaluate(dict(zip(plan.featureNames, row.tolist(), strict=True)))
        for row in rows
    ]
    termGrades = np.column_stack([_Evaluate(np, source, rows[:, index]) for index, source in plan.termSources])
    antecedents = _EvaluateAntecedents(plan.antecedents, termGrades)
    firings, firingStatus = _ComputeFirings(antecedents, np.array(plan.weights))
    consequents, consequentStatus, _ = _EvaluateConsequents(plan.consequents, rows)
    values, _ = _ReduceConsequents(firings, consequents, fullTrace=False)

    assert plan.featureNames == ("risk", "exposure"), "Feature binding must preserve model declaration order"
    assert plan.termNames == (("risk", "low"), ("risk", "high"), ("exposure", "gate"), ("exposure", "unused")), (
        "The prepared term matrix includes every declared term, even unused terms"
    )
    assert plan.ruleNames == ("low", "high"), "Prepared rules retain their declaration order"
    assert plan.weights == (0.5, 1.0), "Prepared rule weights must align with the rule axis"
    np.testing.assert_array_equal(termGrades, [[term.grade for term in result.inputGrades] for result in reference])
    np.testing.assert_array_equal(firingStatus, [0, 0])
    np.testing.assert_array_equal(consequentStatus, [0, 0])
    np.testing.assert_allclose(values, [result.value for result in reference], rtol=0, atol=1e-12)


def test_PreparationRejectsCallbackInUnreferencedTermWithoutExecutingIt():
    """Apply the eligibility gate to unused terms before invoking membership."""

    def RejectCallback(coordinate):
        """Raise if preparation evaluates a user-supplied term."""

        raise AssertionError(f"Unexpected callback evaluation at {coordinate}")

    base = ScalarModel("constant")
    risk = base.inputs[0]
    universe = risk.terms[0].fuzzySet.universe
    extra = LinguisticTerm("extra", ScalarFuzzySet(universe, RejectCallback))
    variable = FuzzyVariable(risk.name, (*risk.terms, extra))
    model = SugenoModel((variable, base.inputs[1]), base.rules, base.policy, base.outputUniverse)

    with pytest.raises(InvalidParameterTypeError, match="unchanged analytical"):
        _PrepareModel(model)


def test_MembershipSourceAcceptsUnchangedInheritanceButRejectsAttributeHooks():
    """Retain inherited built-in evaluation and avoid untrusted descriptor lookup."""

    class InheritedMembership(MembershipFunction):
        """Membership subclass that inherits all built-in evaluation methods."""

    class HookedMembership(MembershipFunction):
        """Membership subclass that would execute code on dynamic field access."""

        def __getattribute__(self, name):
            """Fail if preparation performs dynamic field access."""

            raise AssertionError(f"Unexpected field lookup for {name}")

    membership = InheritedMembership("triangle", left=0, peak=1, right=2)
    source = _PrepareTermSource(membership)

    assert source.parameterItems == (("a", 0), ("b", 2), ("c", 1)), "The analytical snapshot must retain the geometry"
    assert all(type(value) is int for _, value in source.parameterItems), "Array geometry must preserve integer arithmetic"

    with pytest.raises(InvalidParameterTypeError, match="unchanged analytical"):
        _PrepareTermSource(object.__new__(HookedMembership))


@pytest.mark.parametrize("universe", (ContinuousUniverse(Fraction(0), 1, True, True), DiscreteUniverse((0, 2**53 + 1))))
def test_PreparationRejectsRationalAndInexactInputUniverseValues(universe):
    """Fail on unsupported coordinates before preparing the first observation."""

    base = ScalarModel("constant")
    risk = base.inputs[0]
    terms = tuple(LinguisticTerm(term.name, ScalarFuzzySet(universe, Triangle(0, 1, 2))) for term in risk.terms)
    model = SugenoModel((FuzzyVariable(risk.name, terms), base.inputs[1]), base.rules, base.policy, base.outputUniverse)

    with pytest.raises(InvalidParameterTypeError, match="batch parameters"):
        _PrepareModel(model)


def test_PreparationSnapshotsExactDiscreteInputPoints():
    """Store eligible sorted points separately from the original scalar universe."""

    base = ScalarModel("constant")
    universe = DiscreteUniverse((0, 0.25, 1))
    risk = base.inputs[0]
    terms = tuple(LinguisticTerm(term.name, ScalarFuzzySet(universe, term.fuzzySet.membershipFunction)) for term in risk.terms)
    model = SugenoModel((FuzzyVariable(risk.name, terms), base.inputs[1]), base.rules, base.policy, base.outputUniverse)
    plan = _PrepareModel(model)

    assert plan.universes[0] == universe, "Prepared coordinates preserve exact discrete membership"
    assert plan.universes[0] is not universe, "Prepared domain metadata is a snapshot"
