# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private ordered row classification and Sugeno chunk execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from fuzzyroutines._sugeno_antecedents import _EvaluateAntecedents
from fuzzyroutines._sugeno_batch import _ComputeFirings, _ReduceConsequents
from fuzzyroutines._sugeno_consequents import _EvaluateConsequents
from fuzzyroutines._sugeno_model import _PreparedModel
from fuzzyroutines.batches import _Evaluate, _Numpy
from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse
from fuzzyroutines.exceptions import InvalidParameterError
from fuzzyroutines.membership import _AnalyticalSource

if TYPE_CHECKING:
    from numpy import bool_ as Bool
    from numpy import float64 as Float64
    from numpy import int64 as Int64
    from numpy import intp as Intp
    from numpy import uint8 as UInt8
    from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class _RowFailure:
    """First failing row in a chunk and its first failing stage context."""

    index: int
    status: int
    subject: str | None
    cause: Exception | None


@dataclass(slots=True)
class _ChunkState:
    """Mutable internal status buffer and earliest diagnostic."""

    status: NDArray[UInt8]
    failure: _RowFailure | None = None

    def Mark(
        self,
        rows: NDArray[Intp],
        status: int,
        subject: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Set the first failure of the supplied ascending valid row indices."""

        if not rows.size:
            return

        self.status[rows] = status
        first = int(rows[0])

        if self.failure is None or first < self.failure.index:
            self.failure = _RowFailure(first, status, subject, cause)


@dataclass(frozen=True, slots=True)
class _ChunkResult:
    """Fresh values, statuses and earliest failure for one prepared chunk."""

    values: NDArray[Float64]
    status: NDArray[UInt8]
    failure: _RowFailure | None


@dataclass(frozen=True, slots=True)
class _FullTrace:
    """Full rule and input evidence written at original observation indices."""

    inputGrades: NDArray[Float64]
    antecedents: NDArray[Float64]
    firings: NDArray[Float64]
    consequents: NDArray[Float64]
    normalized: NDArray[Float64]
    contributions: NDArray[Float64]
    exactRatios: NDArray[Bool]
    ruleWeights: NDArray[Float64]


@dataclass(frozen=True, slots=True)
class _Trace:
    """Summary buffers and optional full trace buffers for a prepared batch."""

    firedRuleCount: NDArray[Int64]
    maxFiringStrength: NDArray[Float64]
    full: _FullTrace | None


def _DomainMask(
    np: Any,
    universe: ContinuousUniverse | DiscreteUniverse,
    values: NDArray[Float64],
) -> NDArray[Bool]:
    """Check finite coordinates without a row-by-discrete-points grid."""

    if isinstance(universe, DiscreteUniverse):
        points = np.asarray(universe.points, dtype=np.float64)
        index = np.minimum(np.searchsorted(points, values), points.size - 1)

        return cast("NDArray[Bool]", points[index] == values)

    inside: NDArray[Bool] = np.ones(values.shape, dtype=np.bool_)

    if universe.left is not None:
        left = cast(float, universe.left)
        inside &= values >= left if universe.leftClosed else values > left

    if universe.right is not None:
        right = cast(float, universe.right)
        inside &= values <= right if universe.rightClosed else values < right

    return inside


def _EvaluateTerm(
    np: Any,
    source: _AnalyticalSource,
    rows: NDArray[Intp],
    coordinates: NDArray[Float64],
    grades: NDArray[Float64],
    state: _ChunkState,
    subject: str,
) -> None:
    """Isolate expected numerical failures with the same pure analytical kernel."""

    if not rows.size:
        return

    try:
        grades[rows] = _Evaluate(np, source, coordinates[rows])

    except (OverflowError, ZeroDivisionError, InvalidParameterError) as error:
        if rows.size == 1:
            # Retain the diagnostic without holding references to failed arrays.
            cause: BaseException | None = error

            while cause is not None:
                cause.__traceback__ = None
                cause = cause.__cause__

            state.Mark(rows, 5, subject, error)
            return

    else:
        return

    split = rows.size // 2
    _EvaluateTerm(np, source, rows[:split], coordinates, grades, state, subject)
    _EvaluateTerm(np, source, rows[split:], coordinates, grades, state, subject)


def _InputGrades(
    np: Any,
    plan: _PreparedModel,
    coordinates: NDArray[Float64],
    state: _ChunkState,
) -> NDArray[Float64]:
    """Check every input domain before running any term for an accepted row."""

    for column, feature in enumerate(plan.featureNames):
        state.Mark(np.flatnonzero((state.status == 0) & ~np.isfinite(coordinates[:, column])), 1, feature)

    for column, universe in enumerate(plan.universes):
        rows = np.flatnonzero(state.status == 0)
        inside = _DomainMask(np, universe, coordinates[rows, column])
        state.Mark(rows[~inside], 2, plan.featureNames[column])

    grades: NDArray[Float64] = np.full((coordinates.shape[0], len(plan.termSources)), np.nan, dtype=np.float64)

    for termIndex, (featureIndex, source) in enumerate(plan.termSources):
        variable, term = plan.termNames[termIndex]
        _EvaluateTerm(
            np, source, np.flatnonzero(state.status == 0), coordinates[:, featureIndex],
            grades[:, termIndex], state, f"{variable}.{term}",
        )

    return grades


def _EvaluateChunk(
    plan: _PreparedModel,
    coordinates: NDArray[Float64],
    *,
    trace: _Trace | None = None,
    offset: int = 0,
) -> _ChunkResult:
    """Run the prepared stages for one binary64 coordinate chunk in model order.

    Earlier failures within a row take precedence over later stages. Across
    rows, the smallest original chunk index owns the returned diagnostic.
    """

    np = _Numpy()
    rowCount = coordinates.shape[0]
    state = _ChunkState(np.zeros(rowCount, dtype=np.uint8))
    values: NDArray[Float64] = np.full(rowCount, np.nan, dtype=np.float64)
    grades = _InputGrades(np, plan, coordinates, state)
    termRows = np.flatnonzero(state.status == 0)
    antecedents = _EvaluateAntecedents(plan.antecedents, grades[termRows])
    firing, firingStatus = _ComputeFirings(antecedents, np.asarray(plan.weights, dtype=np.float64))
    state.Mark(termRows[firingStatus == 3], 3)
    state.Mark(termRows[firingStatus == 5], 5)
    fired = firingStatus == 0
    rows = termRows[fired]
    firing = firing[fired]
    consequents, consequentStatus, failedRule = _EvaluateConsequents(plan.consequents, coordinates[rows])

    for position in np.flatnonzero(consequentStatus):
        ruleName = plan.ruleNames[int(failedRule[position])]
        state.Mark(rows[position:position + 1], int(consequentStatus[position]), ruleName)

    accepted = consequentStatus == 0
    rows = rows[accepted]
    firing = firing[accepted]
    consequents = consequents[accepted]
    full = trace.full if trace is not None else None
    reduced, weighted = _ReduceConsequents(firing, consequents, fullTrace=full is not None)
    finite = np.isfinite(reduced)
    state.Mark(rows[~finite], 5)
    inside = np.zeros(finite.shape, dtype=np.bool_)
    inside[finite] = _DomainMask(np, plan.consequents.outputUniverse, reduced[finite])
    state.Mark(rows[finite & ~inside], 4)
    values[rows[inside]] = reduced[inside]

    if trace is not None:
        noFire = np.flatnonzero(state.status == 3) + offset
        valid = rows[inside] + offset
        validFirings = firing[inside]
        trace.firedRuleCount[noFire] = 0
        trace.maxFiringStrength[noFire] = 0.0
        trace.firedRuleCount[valid] = np.count_nonzero(validFirings > 0.0, axis=1)
        trace.maxFiringStrength[valid] = validFirings.max(axis=1)

        if full is not None and weighted is not None:
            full.inputGrades[valid] = grades[rows[inside]]
            full.antecedents[valid] = antecedents[fired][accepted][inside]
            full.firings[valid] = validFirings
            full.consequents[valid] = consequents[inside]
            full.normalized[valid] = weighted.normalized[inside]
            full.contributions[valid] = weighted.contributions[inside]
            full.exactRatios[valid] = weighted.exactRatio[inside]

    return _ChunkResult(values, state.status, state.failure)
