# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Independent numerical witnesses for the private Sugeno batch reduction."""

import math
import sys

import pytest

from fuzzyroutines._sugeno_batch import _ReduceConsequents
from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.inference import (
    ConstantConsequent,
    SugenoModel,
    SugenoRule,
    TermCondition,
)

np = pytest.importorskip("numpy", reason="Sugeno rule batches use the optional NumPy extra")

from experiments.sugeno_batch_contract_probe import ScalarModel


def _ScalarResult(strengths, consequences):
    """Build a scalar model whose high term fires at exactly one."""

    base = ScalarModel("constant")
    rules = tuple(
        SugenoRule(str(index), TermCondition("risk", "high"), ConstantConsequent(value), weight)
        for index, (weight, value) in enumerate(zip(strengths, consequences, strict=True))
    )
    model = SugenoModel((base.inputs[0],), rules, base.policy, ContinuousUniverse())

    return model.Evaluate({"risk": 1.0})


def test_ReductionPreservesContributionOfRoundedZeroNormalizedStrength():
    """Keep the exact subnormal ratio long enough to scale a huge consequent."""

    strengths = (math.ulp(0.0), 1.0, 1.0)
    consequences = (2.0**1023, 0.0, 0.0)
    expected = _ScalarResult(strengths, consequences)
    firings = np.array([strengths])
    consequents = np.array([consequences])
    firings.setflags(write=False)
    consequents.setflags(write=False)

    with np.errstate(all="raise"):
        policy = np.geterr()
        values, trace = _ReduceConsequents(firings, consequents, fullTrace=True)
        plain, omittedTrace = _ReduceConsequents(firings, consequents, fullTrace=False)
        assert np.geterr() == policy, "Numerical reduction must preserve the caller's NumPy error policy"

    assert trace is not None, "Full trace must retain normalization evidence"
    assert omittedTrace is None, "Trace-off must skip per-rule trace arrays"
    np.testing.assert_array_equal(values, [2.0**-52])
    np.testing.assert_array_equal(plain, values)
    np.testing.assert_array_equal(trace.normalized, [[0.0, 0.5, 0.5]])
    np.testing.assert_array_equal(trace.contributions, [[2.0**-52, 0.0, 0.0]])
    np.testing.assert_array_equal(trace.exactRatio, [[True, False, False]])
    assert values[0] == expected.value, "The exact-ratio contribution must equal scalar evaluation"
    assert not np.shares_memory(trace.normalized, firings), "Trace output must own its normalization values"
    assert not np.shares_memory(trace.contributions, consequents), "Trace output must own its contributions"


def test_ReductionKeepsUnitResidualThroughCancellation():
    """Preserve the unit residual between huge opposing weighted terms."""

    large = 2.0**57
    strengths = (1.0, 1.0, 1.0)
    consequences = (large, 3.0, -large)
    expected = _ScalarResult(strengths, consequences)
    values, trace = _ReduceConsequents(np.array([strengths]), np.array([consequences]), fullTrace=True)

    assert trace is not None, "Full trace must retain the cancellation witness"
    assert values[0] == expected.value == 1.0, "Cancellation must not erase the unit contribution"
    assert trace.contributions[0, 1] == 1.0, "The middle rule supplies the entire residual"
    assert not trace.exactRatio.any(), "Ordinary normalized strengths do not need the exact trace flag"


def test_ReductionRepairsFiniteConstantEndpointAfterProductSumOverflow():
    """Recompute the weighted ratio when finite trace products sum to overflow."""

    strengths = (0.25, 0.875)
    consequences = (sys.float_info.max,) * 2
    expected = _ScalarResult(strengths, consequences)
    values, trace = _ReduceConsequents(np.array([strengths]), np.array([consequences]), fullTrace=True)

    assert trace is not None, "Full trace must retain the products independently from the value"

    with pytest.raises(OverflowError):
        math.fsum(trace.contributions[0])

    assert values[0] == expected.value == sys.float_info.max, "The exact ratio must recover the constant endpoint"


def test_EmptyReductionPreservesRequestedTraceShape():
    """Return empty arrays for the trace fields of an empty prepared chunk."""

    values, trace = _ReduceConsequents(np.empty((0, 2)), np.empty((0, 2)), fullTrace=True)

    assert trace is not None, "Full trace must preserve the requested fields for an empty chunk"
    assert values.shape == (0,), "Empty reduction produces no scalar outputs"
    assert trace.normalized.shape == trace.contributions.shape == trace.exactRatio.shape == (0, 2), (
        "Empty rule evidence preserves the model's rule axis"
    )
