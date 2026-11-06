# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Explicit optional NumPy batches for built-in Sugeno rule models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

from fuzzyroutines._sugeno_chunk import SugenoBatchFullTrace, SugenoBatchTrace
from fuzzyroutines._sugeno_model import _PrepareModel
from fuzzyroutines._sugeno_runner import (
    SugenoBatchResult,
    _CoordinatesInput,
    _EvaluatePreparedBatch,
)
from fuzzyroutines.batches import _Numpy
from fuzzyroutines.exceptions import InvalidParameterError, InvalidParameterTypeError
from fuzzyroutines.inference import SugenoModel

if TYPE_CHECKING:
    from numpy.typing import NDArray

__all__ = [
    "EvaluateSugenoBatch",
    "SugenoBatchFullTrace",
    "SugenoBatchResult",
    "SugenoBatchTrace",
]


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
