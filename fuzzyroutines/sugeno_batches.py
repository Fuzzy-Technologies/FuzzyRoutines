# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Explicit optional NumPy batches for built-in Sugeno rule models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, cast

from fuzzyroutines._sugeno_model import _PrepareModel
from fuzzyroutines.batches import _Numpy
from fuzzyroutines.exceptions import InvalidParameterError, InvalidParameterTypeError
from fuzzyroutines.inference import SugenoModel

if TYPE_CHECKING:
    from numpy import bool_ as Bool
    from numpy import float64 as Float64
    from numpy import int64 as Int64
    from numpy import uint8 as UInt8
    from numpy.typing import NDArray

    from fuzzyroutines._sugeno_runner import _CoordinatesInput

__all__ = [
    "EvaluateSugenoBatch",
    "SugenoBatchFullTrace",
    "SugenoBatchResult",
    "SugenoBatchTrace",
]


@dataclass(frozen=True, slots=True)
class SugenoBatchFullTrace:
    """Read-only rule and input evidence in model declaration order.

    Failed rows have NaN grades, strengths, outputs, and contributions. The
    exact-ratio mask is false on failed rows and marks a retained exact ratio
    on successful rows. Static rule weights occupy a single vector.
    """

    inputGrades: NDArray[Float64]
    antecedents: NDArray[Float64]
    firings: NDArray[Float64]
    consequents: NDArray[Float64]
    normalized: NDArray[Float64]
    contributions: NDArray[Float64]
    exactRatios: NDArray[Bool]
    ruleWeights: NDArray[Float64]


@dataclass(frozen=True, slots=True)
class SugenoBatchTrace:
    """Read-only firing counts and maxima, with optional full rule evidence.

    True no-fire rows have count and maximum zero. Other failures have count
    -1 and maximum NaN. Full evidence is present only in full trace mode.
    """

    firedRuleCount: NDArray[Int64]
    maxFiringStrength: NDArray[Float64]
    full: SugenoBatchFullTrace | None


@dataclass(frozen=True, slots=True)
class SugenoBatchResult:
    """Read-only batch predictions, statuses, and model-order metadata.

    Each value, status, and validity entry corresponds to one source row.
    Valid rows have status zero and a finite value. Failed rows have NaN
    values and nonzero statuses. Trace data is absent in trace-off mode.
    """

    values: NDArray[Float64]
    status: NDArray[UInt8]
    validMask: NDArray[Bool]
    featureNames: tuple[str, ...]
    termNames: tuple[tuple[str, str], ...]
    ruleNames: tuple[str, ...]
    trace: SugenoBatchTrace | None


def _ValidateCoordinates(np: Any, values: object, width: int) -> _CoordinatesInput:
    """Validate all source shapes and cell kinds before any chunk executes."""

    if type(values) is np.ndarray:
        array = cast("NDArray[Any]", values)

        if array.dtype.kind not in "iuf":
            raise InvalidParameterTypeError("values must have a real numeric dtype")

        if array.ndim != 2 or array.shape[1] != width:
            raise InvalidParameterError("values must have shape (rows, feature count)")

        return array

    if type(values) is not list and type(values) is not tuple:
        raise InvalidParameterTypeError("values must be a plain ndarray, list or tuple")

    for row in values:
        if type(row) is not list and type(row) is not tuple:
            raise InvalidParameterError("values must be a rank-two list or tuple of rows")

        if len(row) != width:
            raise InvalidParameterError("every values row must match the feature count")

        for cell in row:
            cellType = type(cell)

            if cellType is int or cellType is float:
                continue

            if isinstance(cell, (np.integer, np.floating)):
                dtype = np.dtype(cellType)

                if dtype.type is cellType and dtype.kind in "iuf":
                    continue

            raise InvalidParameterTypeError("values cells must be built-in int/float or NumPy real numeric scalars")

    return cast("_CoordinatesInput", values)


def EvaluateSugenoBatch(
    model: SugenoModel,
    values: object,
    *,
    featureNames: tuple[str, ...],
    backend: Literal["numpy"] = "numpy",
    onError: Literal["raise", "mask"] = "raise",
    trace: Literal["off", "summary", "full"] = "off",
    chunkSize: int = 4096,
) -> SugenoBatchResult:
    """Evaluate zero- and first-order Sugeno rules on ordered observation rows.

    Args:
        model: Standard scalar Sugeno model with eligible analytical memberships,
            built-in operators and exact binary64 model parameters.
        values: Plain rank-two real numeric ndarray or rectangular list/tuple.
            Each row is one observation. An empty ndarray retains its feature
            axis; an empty list or tuple has the width declared by featureNames.
        featureNames: Unique names for the supplied columns, in source order.
            They must exactly match the set of model input names.
        backend: Explicit optional backend; only "numpy" is supported.
        onError: Raise at the first failed row or retain all rows with statuses.
        trace: Retain no traces, firing summaries, or full model-order evidence.
        chunkSize: Positive built-in integer number of observations per chunk.

    Returns:
        Independent read-only values, validity and statuses in source row order.
        Trace arrays, when requested, use model feature, term and rule order.

    Raises:
        ImportError: NumPy is unavailable.
        InvalidParameterTypeError: Source or model types are unsupported.
        InvalidParameterError: Shape, names or options are invalid, or a row
            has a nonfinite coordinate in raise mode.
        InvalidDomainError: A row violates an input or output universe in raise mode.
        UndefinedResultError: A row has no firing rules in raise mode.
        NumericalError: A numerical row failure occurs in raise mode.

    Notes:
        Source coordinates are converted to binary64 one chunk at a time.
        Failure statuses are 1 for nonfinite coordinates, 2 for input domain,
        3 for no firing, 4 for output domain and 5 for numerical errors.
        Importing the module does not import NumPy or alter scalar evaluation.
    """

    from fuzzyroutines._sugeno_runner import _EvaluatePreparedBatch

    if type(backend) is not str or backend != "numpy":
        raise InvalidParameterError("backend must be 'numpy'")

    if type(onError) is not str or onError not in ("raise", "mask"):
        raise InvalidParameterError("onError must be 'raise' or 'mask'")

    if type(trace) is not str or trace not in ("off", "summary", "full"):
        raise InvalidParameterError("trace must be 'off', 'summary' or 'full'")

    if type(chunkSize) is not int or chunkSize <= 0:
        raise InvalidParameterError("chunkSize must be a positive built-in integer")

    np = _Numpy(backend)
    plan = _PrepareModel(model)

    if type(featureNames) is not tuple or any(type(name) is not str for name in featureNames):
        raise InvalidParameterError("featureNames must be a tuple of strings")

    if len(featureNames) != len(plan.featureNames) or set(featureNames) != set(plan.featureNames):
        raise InvalidParameterError("featureNames must contain each model input name exactly once")

    source = _ValidateCoordinates(np, values, len(featureNames))
    supplied = {name: index for index, name in enumerate(featureNames)}
    columns = tuple(supplied[name] for name in plan.featureNames)

    return _EvaluatePreparedBatch(
        plan, source, chunkSize=chunkSize, traceMode=trace, raiseOnError=onError == "raise", columns=columns,
    )
