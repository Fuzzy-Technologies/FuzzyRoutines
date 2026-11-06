# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Scalar differential evidence for the private Sugeno batch firing stage."""

import math
from fractions import Fraction

import pytest

from fuzzyroutines._sugeno_batch import _ComputeFirings
from fuzzyroutines.exceptions import NumericalError, UndefinedResultError
from fuzzyroutines.inference import (
    ConstantConsequent,
    SugenoModel,
    SugenoRule,
    TermCondition,
)

np = pytest.importorskip("numpy", reason="Sugeno rule batches use the optional NumPy extra")

from experiments.sugeno_batch_contract_probe import ScalarModel


def test_ChunkFiringsMatchScalarRulesAndHandCalculatedWeights():
    """Preserve declaration order and exact quarter-point weighted strengths."""

    model = ScalarModel("constant")
    coordinates = [(0.25, 0.25), (0.5, 0.5), (1.0, 0.5)]
    antecedents = np.array([[0.375, 0.125], [0.5, 0.5], [0.0, 1.0]])
    firings, status = _ComputeFirings(antecedents, np.array([0.5, 1.0]))
    expected = [model.Evaluate({"risk": risk, "exposure": exposure}) for risk, exposure in coordinates]

    np.testing.assert_array_equal(status, np.zeros(3, dtype=np.uint8), strict=True)
    np.testing.assert_array_equal(firings, [[0.1875, 0.125], [0.25, 0.5], [0.0, 1.0]])
    np.testing.assert_array_equal(firings, [[rule.firingStrength for rule in row.rules] for row in expected])

    left, right = (Fraction(float(strength)) for strength in firings[0])
    mean = (left * Fraction(1, 4) + right * Fraction(3, 4)) / (left + right)

    assert mean == Fraction(9, 20), "Quarter-point weights must produce the independent exact mean"
    assert expected[0].value == pytest.approx(float(mean)), "Scalar mean must agree at the fixture anchor"


def test_FiringStatusDistinguishesUnderflowFromTrueZero():
    """Classify lost positive strength even when a later rule fires."""

    base = ScalarModel("constant")
    variable = base.inputs[0]
    condition = TermCondition("risk", "high")
    rule = SugenoRule("half weight", condition, ConstantConsequent(1), 0.5)
    model = SugenoModel((variable,), (rule,), base.policy, base.outputUniverse)
    tiny = math.ulp(0.0)
    grades = np.array([[0.0, 0.0], [tiny, 1.0], [0.0, tiny], [np.nan, 1.0], [-1.0, 1.0], [2.0, 1.0]])
    weights = np.array([0.5, 1.0])
    grades.setflags(write=False)
    weights.setflags(write=False)

    with np.errstate(all="raise"):
        policy = np.geterr()
        firings, status = _ComputeFirings(grades, weights)
        assert np.geterr() == policy, "The chunk must restore the caller's NumPy error policy"

    with pytest.raises(UndefinedResultError):
        model.Evaluate({"risk": 0.0})

    with pytest.raises(NumericalError):
        model.Evaluate({"risk": tiny})

    np.testing.assert_array_equal(status, [3, 5, 0, 5, 5, 5])
    np.testing.assert_array_equal(firings[2], [0.0, tiny])
    assert np.isnan(firings[status != 0]).all(), "Failed rows must not expose partial firing evidence"
    assert not np.shares_memory(firings, grades), "Chunk scratch must not alias source grades"


def test_EmptyPreparedChunkPreservesRuleAxis():
    """Accept the internal empty shape without fabricating any row evidence."""

    firings, status = _ComputeFirings(np.empty((0, 2)), np.array([0.5, 1.0]))

    assert firings.shape == (0, 2), "An empty chunk must retain its rule axis"
    assert status.shape == (0,), "An empty chunk has no row statuses"
