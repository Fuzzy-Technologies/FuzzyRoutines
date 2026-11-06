# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Scalar parity and failure precedence for prepared Sugeno consequents."""

import math
import sys
from fractions import Fraction

import pytest

from fuzzyroutines._sugeno_consequents import _EvaluateConsequents, _PrepareConsequents
from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterTypeError,
    NumericalError,
)
from fuzzyroutines.inference import (
    AffineConsequent,
    ConstantConsequent,
    SugenoModel,
    SugenoRule,
    TermCondition,
)

np = pytest.importorskip("numpy", reason="Sugeno rule batches use the optional NumPy extra")

from experiments.sugeno_batch_contract_probe import ScalarModel

FEATURE_COLUMNS = {"risk": 0, "exposure": 1}


def _ReferenceModel(consequents, universe, term="low"):
    """Give every rule a shared term, with only the first rule active."""

    base = ScalarModel("constant")
    condition = TermCondition("risk", term)
    rules = tuple(
        SugenoRule(str(index), condition, consequent, 1.0 if index == 0 else 0.0)
        for index, consequent in enumerate(consequents)
    )

    return SugenoModel(base.inputs, rules, base.policy, universe)


def test_ConsequentChunkPreservesScalarCoefficientOrderAndUnitResidual():
    """Evaluate constant and inactive affine rules on the declared closed endpoints."""

    large = 2.0**54
    universe = ContinuousUniverse(0.0, 2.0, True, True)
    consequents = (
        ConstantConsequent(2.0),
        AffineConsequent(large, (("risk", 1.0), ("exposure", -large))),
    )
    reference = _ReferenceModel(consequents, universe, "high")
    expected = reference.Evaluate({"risk": 1.0, "exposure": 1.0})
    plan = _PrepareConsequents(consequents, {"risk": 1, "exposure": 0}, universe)
    values, status, failedRule = _EvaluateConsequents(plan, np.array([[1.0, 1.0], [1.0, 0.0]]))

    np.testing.assert_array_equal(values, [[2.0, 1.0], [2.0, 0.0]])
    np.testing.assert_array_equal(values[0], [rule.consequentValue for rule in expected.rules])
    np.testing.assert_array_equal(status, [0, 0])
    np.testing.assert_array_equal(failedRule, [-1, -1])


@pytest.mark.parametrize(("swap", "statuses", "firstRules", "firstError"), (
    (False, [4, 5, 0], [1, 2, -1], InvalidDomainError),
    (True, [5, 5, 0], [1, 1, -1], NumericalError),
))
def test_EarliestInvalidInactiveConsequentDeterminesTheRowFailure(swap, statuses, firstRules, firstError):
    """Do not let a later numerical failure replace an earlier domain failure."""

    universe = ContinuousUniverse(0.0)
    domainFailure = AffineConsequent(0.0, (("risk", 1.0),))
    overflow = AffineConsequent(sys.float_info.max, (("exposure", sys.float_info.max),))
    ordered = (overflow, domainFailure) if swap else (domainFailure, overflow)
    consequents = (ConstantConsequent(1.0), *ordered)
    scalar = _ReferenceModel(consequents, universe)
    plan = _PrepareConsequents(consequents, FEATURE_COLUMNS, universe)
    rows = np.array([[0.0, 1.0], [0.5, 1.0], [0.5, 0.0]])
    rows.setflags(write=False)

    with np.errstate(all="raise"):
        previous = np.geterr()
        values, status, failedRule = _EvaluateConsequents(plan, rows)
        assert np.geterr() == previous, "Consequent evaluation must preserve the ambient NumPy policy"

    with pytest.raises(firstError):
        scalar.Evaluate({"risk": 0.0, "exposure": 1.0})

    with pytest.raises(NumericalError):
        scalar.Evaluate({"risk": 0.5, "exposure": 1.0})

    expected = scalar.Evaluate({"risk": 0.5, "exposure": 0.0})
    np.testing.assert_array_equal(status, statuses)
    np.testing.assert_array_equal(failedRule, firstRules)
    np.testing.assert_array_equal(values[2], [rule.consequentValue for rule in expected.rules])
    assert np.isnan(values[:2]).all(), "Failed rows must erase all partial consequent evidence"


def test_EmptyAffineSumAndConstantPreserveTheirScalarZeroSigns():
    """Keep the distinction between a constant and an affine intercept-only sum."""

    universe = ContinuousUniverse()
    consequents = (ConstantConsequent(-0.0), AffineConsequent(-0.0, ()))
    plan = _PrepareConsequents(consequents, FEATURE_COLUMNS, universe)
    values, _, _ = _EvaluateConsequents(plan, np.array([[0.0, 0.0]]))
    expected = _ReferenceModel(consequents, universe).Evaluate({"risk": 0.0, "exposure": 0.0})
    empty, status, failedRule = _EvaluateConsequents(plan, np.empty((0, 2)))

    np.testing.assert_array_equal(np.signbit(values[0]), [math.copysign(1.0, rule.consequentValue) < 0 for rule in expected.rules])
    assert empty.shape == (0, 2), "An empty chunk retains the consequent axis"
    assert status.shape == failedRule.shape == (0,), "An empty chunk has no row diagnostics"


@pytest.mark.parametrize("value", (Fraction(1, 2), 2**53 + 1))
def test_ConsequentPreparationRejectsUnsupportedExactNumericTypesAndValues(value):
    """Reject a custom real or inexact int before a prepared batch can run."""

    consequent = AffineConsequent(0.0, (("risk", value),))

    with pytest.raises(InvalidParameterTypeError, match="batch parameters"):
        _PrepareConsequents((consequent,), FEATURE_COLUMNS, ContinuousUniverse())
