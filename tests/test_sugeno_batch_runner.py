# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Prepared batch row restoration, trace fidelity, and payload checks."""

import math
from dataclasses import fields

import pytest

from fuzzyroutines._sugeno_model import _PrepareModel
from fuzzyroutines._sugeno_runner import _EvaluatePreparedBatch
from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.exceptions import InvalidDomainError
from fuzzyroutines.inference import (
    ConstantConsequent,
    SugenoModel,
    SugenoRule,
    TermCondition,
)

np = pytest.importorskip("numpy", reason="Sugeno rule batches use the optional NumPy extra")

from experiments.sugeno_batch_contract_probe import ScalarModel


@pytest.mark.parametrize("chunkSize", (1, 2, 4, 16))
@pytest.mark.parametrize("mode", ("off", "summary", "full"))
def test_TraceModesKeepOriginalRowsAndMatchTheScalarReference(chunkSize, mode):
    """Check mixed rule values, ordered traces and failed-row sentinels."""

    model = ScalarModel("mixed")
    plan = _PrepareModel(model)
    source = np.array([
        [0.25, 0.25],
        [0.3, 0.0],
        [np.nan, 0.5],
        [0.2, 0.75],
        [0.5, 1.1],
        [0.75, 0.5],
        [0.0, 0.25],
    ], dtype=">f8")[::-1]
    source.setflags(write=False)
    result = _EvaluatePreparedBatch(plan, source, chunkSize=chunkSize, traceMode=mode, raiseOnError=False)
    np.testing.assert_array_equal(result.status, [0, 0, 2, 4, 1, 3, 0])
    np.testing.assert_array_equal(result.validMask, result.status == 0)
    assert np.isnan(result.values[~result.validMask]).all(), "Failed rows must retain NaN predictions"
    assert result.featureNames == plan.featureNames and result.termNames == plan.termNames and result.ruleNames == plan.ruleNames, (
        "Result metadata must preserve the prepared feature, term and rule order"
    )
    arrays = [result.values, result.status, result.validMask]
    validRows = np.flatnonzero(result.validMask)
    scalar = [model.Evaluate(dict(zip(plan.featureNames, source[index].tolist(), strict=True))) for index in validRows]
    np.testing.assert_allclose(result.values[validRows], [item.value for item in scalar], rtol=0, atol=1e-12)

    if mode == "off":
        assert result.trace is None, "Trace-off must not retain trace arrays"

    else:
        assert result.trace is not None, "Summary counts and maxima must be present"
        summary = result.trace
        arrays.extend((summary.firedRuleCount, summary.maxFiringStrength))
        np.testing.assert_array_equal(summary.firedRuleCount, [1, 2, -1, -1, -1, 0, 2])
        np.testing.assert_allclose(summary.maxFiringStrength[validRows], [max(rule.firingStrength for rule in item.rules) for item in scalar])
        assert summary.maxFiringStrength[5] == 0, "True no-fire rows must retain an exact zero maximum"
        assert np.isnan(summary.maxFiringStrength[2:5]).all(), "Other failed rows must not retain partial maxima"

        if mode == "summary":
            assert summary.full is None, "Summary must not retain full rule arrays"

        else:
            full = summary.full
            assert full is not None, "Full mode must expose term and rule evidence"
            arrays.extend(getattr(full, field.name) for field in fields(full))
            np.testing.assert_array_equal(full.ruleWeights, plan.weights)
            np.testing.assert_array_equal(full.inputGrades[validRows], [[grade.grade for grade in item.inputGrades] for item in scalar])
            assert np.isnan(full.inputGrades[~result.validMask]).all(), "Failed rows must not retain partial term evidence"

            for array, name in (
                (full.antecedents, "antecedentGrade"), (full.firings, "firingStrength"),
                (full.consequents, "consequentValue"), (full.normalized, "normalizedStrength"),
                (full.contributions, "contribution"),
            ):
                np.testing.assert_allclose(
                    array[validRows], [[getattr(rule, name) for rule in item.rules] for item in scalar], rtol=0, atol=1e-12,
                )
                assert np.isnan(array[~result.validMask]).all(), "Failed rows must not retain partial rule evidence"

            assert not full.exactRatios.any(), "The ordinary model has no exact-ratio branch"

    size = len(source)
    expectedBytes = {"off": 10 * size, "summary": 26 * size, "full": 140 * size + 16}
    assert sum(array.nbytes for array in arrays) == expectedBytes[mode], "Retained arrays must match the trace payload contract"
    assert all(not array.flags.writeable and not np.shares_memory(array, source) for array in arrays), (
        "Published arrays must be independent of the caller and read-only"
    )


@pytest.mark.parametrize("mode", ("off", "summary", "full"))
def test_RaiseUsesGlobalRowIndexAcrossChunksAndTraceModes(mode):
    """Keep the first failing row even when a later row fails an earlier stage."""

    plan = _PrepareModel(ScalarModel("mixed"))
    rows = np.array([[0.25, 0.25], [0.75, 0.5], [0.25, 0.25], [0.2, 0.75], [np.nan, 0.5]])

    with pytest.raises(InvalidDomainError, match=r"row 3 \(high\):"):
        _EvaluatePreparedBatch(plan, rows, chunkSize=2, traceMode=mode, raiseOnError=True)


def test_FullTracePreservesExactSubnormalContributionAcrossSingleAndEmptyBatches():
    """Retain exact-ratio evidence for a rounded-zero normalized strength."""

    base = ScalarModel("constant")
    term = TermCondition("risk", "high")
    rules = (
        SugenoRule("subnormal", term, ConstantConsequent(2.0**1023), math.ulp(0.0)),
        SugenoRule("zeroOne", term, ConstantConsequent(0.0)),
        SugenoRule("zeroTwo", term, ConstantConsequent(0.0)),
    )
    plan = _PrepareModel(SugenoModel((base.inputs[0],), rules, base.policy, ContinuousUniverse()))
    singleton = _EvaluatePreparedBatch(plan, np.array([[1.0]]), chunkSize=3, traceMode="full", raiseOnError=True)
    empty = _EvaluatePreparedBatch(plan, np.empty((0, 1)), chunkSize=1, traceMode="full", raiseOnError=True)
    assert singleton.trace is not None and singleton.trace.full is not None, "A singleton has full rule evidence"
    assert empty.trace is not None and empty.trace.full is not None, "Empty arrays must keep full trace shape"
    assert empty.values.shape == (0,) and empty.trace.full.firings.shape == (0, 3), (
        "Empty batches preserve the declared rule axis"
    )
    np.testing.assert_array_equal(singleton.values, [2.0**-52])
    np.testing.assert_array_equal(singleton.trace.full.normalized, [[0.0, 0.5, 0.5]])
    np.testing.assert_array_equal(singleton.trace.full.exactRatios, [[True, False, False]])
    np.testing.assert_array_equal(singleton.trace.full.contributions, [[2.0**-52, 0.0, 0.0]])
