# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Scalar parity and callback isolation for the prepared antecedent stage."""

import math

import pytest

from fuzzyroutines._sugeno_antecedents import _EvaluateAntecedents, _PrepareAntecedents
from fuzzyroutines.exceptions import InvalidParameterTypeError
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.inference import (
    AllOf,
    AnyOf,
    InferencePolicy,
    NotCondition,
    SugenoModel,
    TermCondition,
    _EvaluateCondition,
)
from fuzzyroutines.operators import NegationPolicy, SNormPolicy, TNormPolicy

np = pytest.importorskip("numpy", reason="Sugeno rule batches use the optional NumPy extra")

TERM_COLUMNS = {("risk", "low"): 1, ("risk", "high"): 0, ("exposure", "low"): 2}
TERMS = tuple(TermCondition(variable, term) for variable, term in TERM_COLUMNS)


@pytest.mark.parametrize("family", ("logic", "algebraic", "boundary", "drastic"))
@pytest.mark.parametrize("negation", (
    NegationPolicy("standard"),
    NegationPolicy("parametric", math.ulp(0.0)),
    NegationPolicy("parametric", 0.3),
    NegationPolicy("parametric", math.nextafter(1.0, 0.0)),
    NegationPolicy("parabolic", 0.25),
    NegationPolicy("parabolic", 0.5),
    NegationPolicy("parabolic", 0.75),
))
def test_NestedAntecedentsMatchScalarAcrossAllOperatorFamilies(family, negation):
    """Preserve rule order, cross-variable name binding and exact branch endpoints."""

    first, second, third = TERMS
    expressions = (
        AllOf((first, NotCondition(AnyOf((second, third))), third)),
        AnyOf((NotCondition(first), AllOf((second, third)), third)),
        NotCondition(first),
        second,
    )
    policy = InferencePolicy(TNormPolicy(family), SNormPolicy(family), negation)
    rows = np.array([
        [0.0, 1.0, 0.5],
        [1.0, 0.0, 1.0],
        [math.ulp(0.0), math.nextafter(1.0, 0.0), 0.3],
        [0.25, 0.75, 1.0],
        [0.3, 0.5, 0.75],
    ])[::-1]
    rows.setflags(write=False)
    expected = np.array([
        [
            _EvaluateCondition(expression, {key: float(row[index]) for key, index in TERM_COLUMNS.items()}, policy)
            for expression in expressions
        ]
        for row in rows
    ])
    plan = _PrepareAntecedents(expressions, TERM_COLUMNS, policy)

    with np.errstate(all="raise"):
        settings = np.geterr()
        output = _EvaluateAntecedents(plan, rows)
        assert np.geterr() == settings, "Chunk evaluation must preserve the caller's NumPy error policy"

    np.testing.assert_allclose(output, expected, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(output == 0, expected == 0)
    np.testing.assert_array_equal(output == 1, expected == 1)
    assert not np.shares_memory(output, rows), "Output grades must not alias the term matrix"


def test_PreparedEvaluationFoldsLeftWithoutCallingScalarEvaluators(monkeypatch):
    """Use ordered array operations and term snapshots after plan construction."""

    def RejectCallback(*args):
        """Fail if any scalar evaluator is invoked by the array engine."""

        raise AssertionError("The array engine must not call a scalar evaluator")

    policy = InferencePolicy(TNormPolicy("algebraic"), SNormPolicy("logic"), NegationPolicy("standard"))

    for owner, name in ((SugenoModel, "Evaluate"), (ScalarFuzzySet, "Membership"), (TNormPolicy, "Evaluate")):
        monkeypatch.setattr(owner, name, RejectCallback)

    plan = _PrepareAntecedents((AllOf(TERMS),), TERM_COLUMNS, policy)
    result = _EvaluateAntecedents(plan, np.array([[0.2, 0.1, 0.3]]))

    assert result[0, 0] == (0.1 * 0.2) * 0.3, "The array fold must preserve scalar rounding order"
    assert result[0, 0] != 0.1 * (0.2 * 0.3), "The witness must distinguish left and right association"
    assert _EvaluateAntecedents(plan, np.empty((0, 3))).shape == (0, 1), "Empty chunks preserve the rule axis"


def test_PreparationRejectsExpressionSubclassBeforeReadingFields():
    """Avoid calling subclass hooks even if a caller bypassed dataclass construction."""

    class HookedCondition(TermCondition):
        """Condition subclass with an observable field-access callback."""

        def __getattribute__(self, name):
            """Fail if the compiler reads any field on this untrusted instance."""

            raise AssertionError(f"Subclass callback invoked for {name}")

    expression = object.__new__(HookedCondition)
    policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))

    with pytest.raises(InvalidParameterTypeError, match="built-in condition"):
        _PrepareAntecedents((expression,), TERM_COLUMNS, policy)
