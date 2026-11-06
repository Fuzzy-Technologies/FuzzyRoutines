# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""End-to-end scalar differential and row precedence for a prepared chunk."""

import pytest

from fuzzyroutines._sugeno_chunk import _EvaluateChunk
from fuzzyroutines._sugeno_model import _PrepareModel
from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    UndefinedResultError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.inference import (
    ConstantConsequent,
    FuzzyVariable,
    SugenoModel,
    SugenoRule,
    TermCondition,
)
from fuzzyroutines.linguistic import LinguisticTerm
from fuzzyroutines.membership import Hyperbolic, Triangle

np = pytest.importorskip("numpy", reason="Sugeno rule batches use the optional NumPy extra")

from experiments.sugeno_batch_contract_probe import ScalarModel


def test_ChunkKeepsScalarValuesAndReportsEarliestOriginalRowAcrossStages(monkeypatch):
    """Run all private stages without falling back to a scalar model call."""

    model = ScalarModel("mixed")
    plan = _PrepareModel(model)
    coordinates = np.array([
        [0.25, 0.25],
        [0.3, 0.0],
        [np.nan, 0.5],
        [0.2, 0.75],
        [0.5, 1.1],
        [0.75, 0.5],
    ])
    coordinates.setflags(write=False)
    accepted = [
        model.Evaluate(dict(zip(plan.featureNames, coordinates[index].tolist(), strict=True))).value
        for index in (0, 5)
    ]

    with pytest.raises(UndefinedResultError):
        model.Evaluate({"risk": 0.3, "exposure": 0.0})

    with pytest.raises(InvalidDomainError):
        model.Evaluate({"risk": 0.2, "exposure": 0.75})

    def RejectScalar(*args):
        """Fail if the private batch engine delegates evaluation to the scalar model."""

        raise AssertionError("Unexpected scalar Sugeno fallback")

    monkeypatch.setattr(SugenoModel, "Evaluate", RejectScalar)
    outcome = _EvaluateChunk(plan, coordinates)

    np.testing.assert_array_equal(outcome.status, [0, 3, 1, 4, 2, 0])
    np.testing.assert_allclose(outcome.values[[0, 5]], accepted, rtol=0, atol=1e-12)
    assert np.isnan(outcome.values[outcome.status != 0]).all(), "Failed rows must not retain predictions"
    assert outcome.failure is not None, "A failing chunk must carry its earliest diagnostic"
    assert (outcome.failure.index, outcome.failure.status) == (1, 3), (
        "A later row failing in an earlier stage must not displace the first row error"
    )


def test_MembershipFailureIsIsolatedAfterAllDomainChecks():
    """Keep unused-term numerical errors local and retain the original cause."""

    universe = ContinuousUniverse()
    points = DiscreteUniverse((0, 0.5, 1))
    risk = FuzzyVariable("risk", (
        LinguisticTerm("active", ScalarFuzzySet(universe, Hyperbolic(1, 1, 0))),
        LinguisticTerm("unused", ScalarFuzzySet(universe, Hyperbolic(1, 4, 0))),
    ))
    exposure = FuzzyVariable("exposure", (
        LinguisticTerm("term", ScalarFuzzySet(points, Triangle(0, 1, 1))),
    ))
    rule = SugenoRule("prediction", TermCondition("risk", "active"), ConstantConsequent(0.25))
    base = ScalarModel("constant")
    model = SugenoModel((risk, exposure), (rule,), base.policy, base.outputUniverse)
    plan = _PrepareModel(model)
    coordinates = np.array([[1e100, 0.6], [1e100, 0.5], [1.0, 0.5], [0.0, 2.0], [np.inf, 0.4]])

    with pytest.raises(OverflowError):
        model.Evaluate({"risk": 1e100, "exposure": 0.5})

    with np.errstate(all="raise"):
        policy = np.geterr()
        outcome = _EvaluateChunk(plan, coordinates)
        isolated = _EvaluateChunk(plan, coordinates[1:])
        assert np.geterr() == policy, "A row error must not change the caller's NumPy policy"

    np.testing.assert_array_equal(outcome.status, [2, 5, 0, 2, 1])
    assert outcome.values[2] == 0.25, "A neighboring numerical failure must not change the valid row"
    assert outcome.failure is not None and outcome.failure.subject == "exposure", (
        "The first row's discrete domain failure must take priority over its unused membership overflow"
    )
    assert isolated.failure is not None, "The isolated overflowing term must have a diagnostic"
    assert isolated.failure.index == 0 and isolated.failure.subject == "risk.unused", (
        "The diagnostic must identify the original failed row and declared term"
    )
    assert isinstance(isolated.failure.cause, OverflowError), "Keep the expected numerical cause for raise mode"
    assert isolated.failure.cause.__traceback__ is None, "A retained error must not retain failed work arrays"


def test_EmptyPreparedChunkHasNoValuesOrErrors():
    """Return the empty internal shape with no row diagnostic."""

    outcome = _EvaluateChunk(_PrepareModel(ScalarModel("constant")), np.empty((0, 2)))

    assert outcome.values.shape == outcome.status.shape == (0,), "No row buffers may contain dummy values"
    assert outcome.failure is None, "Empty chunks cannot have a failing row"
