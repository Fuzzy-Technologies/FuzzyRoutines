# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Strict consumer of the optional Sugeno batch result and trace types."""

from typing import assert_type as assertType

import numpy as np
from numpy.typing import NDArray

from fuzzyroutines.inference import SugenoModel
from fuzzyroutines.sugeno_batches import (
    EvaluateSugenoBatch,
    SugenoBatchFullTrace,
    SugenoBatchResult,
    SugenoBatchTrace,
)


def CheckSugenoBatchConsumer(model: SugenoModel) -> None:
    """Verify the public prediction, status, and full trace array annotations."""

    result = EvaluateSugenoBatch(model, [[0.25]], featureNames=("risk",), trace="full")
    assertType(result, SugenoBatchResult)
    assertType(result.values, NDArray[np.float64])
    assertType(result.status, NDArray[np.uint8])
    assertType(result.validMask, NDArray[np.bool_])
    assertType(result.trace, SugenoBatchTrace | None)
    assert result.trace is not None
    assertType(result.trace.firedRuleCount, NDArray[np.int64])
    assertType(result.trace.full, SugenoBatchFullTrace | None)
    assert result.trace.full is not None
    assertType(result.trace.full.inputGrades, NDArray[np.float64])
    assertType(result.trace.full.exactRatios, NDArray[np.bool_])

    EvaluateSugenoBatch(model, [[0.25]], featureNames=["risk"])  # type: ignore[arg-type]
    EvaluateSugenoBatch(model, [[0.25]], featureNames=("risk",), backend="auto")  # type: ignore[arg-type]
