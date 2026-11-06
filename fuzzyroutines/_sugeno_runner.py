# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private multi-chunk Sugeno result and trace assembly."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, Any, Literal

from fuzzyroutines._sugeno_chunk import _EvaluateChunk, _FullTrace, _RowFailure, _Trace
from fuzzyroutines._sugeno_model import _PreparedModel
from fuzzyroutines.batches import _Numpy
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    NumericalError,
    UndefinedResultError,
)

if TYPE_CHECKING:
    from numpy import bool_ as Bool
    from numpy import float64 as Float64
    from numpy import uint8 as UInt8
    from numpy.typing import NDArray

type _TraceMode = Literal["off", "summary", "full"]

_STATUS_ERRORS = {
    1: InvalidParameterError,
    2: InvalidDomainError,
    3: UndefinedResultError,
    4: InvalidDomainError,
    5: NumericalError,
}
_STATUS_DESCRIPTIONS = {
    1: "non-finite coordinate",
    2: "coordinate outside its universe",
    3: "no rule fires",
    4: "consequent or output outside its universe",
    5: "numerical failure",
}


@dataclass(frozen=True, slots=True)
class _PreparedBatchResult:
    """Read-only result arrays and model-order metadata for one prepared batch."""

    values: NDArray[Float64]
    status: NDArray[UInt8]
    validMask: NDArray[Bool]
    featureNames: tuple[str, ...]
    termNames: tuple[tuple[str, str], ...]
    ruleNames: tuple[str, ...]
    trace: _Trace | None


def _AllocateTrace(np: Any, plan: _PreparedModel, size: int, mode: _TraceMode) -> _Trace | None:
    """Allocate only the trace payload selected for the whole result."""

    if mode == "off":
        return None

    full = None

    if mode == "full":
        ruleShape = (size, len(plan.ruleNames))
        full = _FullTrace(
            np.full((size, len(plan.termNames)), np.nan, dtype=np.float64),
            np.full(ruleShape, np.nan, dtype=np.float64),
            np.full(ruleShape, np.nan, dtype=np.float64),
            np.full(ruleShape, np.nan, dtype=np.float64),
            np.full(ruleShape, np.nan, dtype=np.float64),
            np.full(ruleShape, np.nan, dtype=np.float64),
            np.zeros(ruleShape, dtype=np.bool_),
            np.array(plan.weights, dtype=np.float64),
        )

    return _Trace(
        np.full(size, -1, dtype=np.int64),
        np.full(size, np.nan, dtype=np.float64),
        full,
    )


def _FreezeTrace(trace: _Trace | None) -> None:
    """Publish the independently allocated trace arrays read-only."""

    if trace is None:
        return

    trace.firedRuleCount.setflags(write=False)
    trace.maxFiringStrength.setflags(write=False)

    if trace.full is not None:
        for field in fields(trace.full):
            getattr(trace.full, field.name).setflags(write=False)


def _RaiseRowFailure(failure: _RowFailure, offset: int) -> None:
    """Translate an ordered chunk failure to its original observation index."""

    subject = f" ({failure.subject})" if failure.subject is not None else ""
    message = f"row {offset + failure.index}{subject}: {_STATUS_DESCRIPTIONS[failure.status]}"

    raise _STATUS_ERRORS[failure.status](message) from failure.cause


def _EvaluatePreparedBatch(
    plan: _PreparedModel,
    coordinates: NDArray[Float64],
    *,
    chunkSize: int,
    traceMode: _TraceMode,
    raiseOnError: bool,
) -> _PreparedBatchResult:
    """Evaluate validated binary64 observations in consecutive private chunks.

    The caller has already bound coordinates to model feature order and
    validated options. Failed row indices and trace payload positions refer
    to the input row sequence, independent of chunk size.
    """

    np = _Numpy()
    size = coordinates.shape[0]
    values: NDArray[Float64] = np.empty(size, dtype=np.float64)
    status: NDArray[UInt8] = np.empty(size, dtype=np.uint8)
    trace = _AllocateTrace(np, plan, size, traceMode)

    for offset in range(0, size, chunkSize):
        end = min(offset + chunkSize, size)
        chunk = np.array(coordinates[offset:end], dtype=np.float64, order="C", copy=True)
        result = _EvaluateChunk(plan, chunk, trace=trace, offset=offset)

        if raiseOnError and result.failure is not None:
            _RaiseRowFailure(result.failure, offset)

        values[offset:end] = result.values
        status[offset:end] = result.status

    validMask = status == 0
    values.setflags(write=False)
    status.setflags(write=False)
    validMask.setflags(write=False)
    _FreezeTrace(trace)

    return _PreparedBatchResult(values, status, validMask, plan.featureNames, plan.termNames, plan.ruleNames, trace)
