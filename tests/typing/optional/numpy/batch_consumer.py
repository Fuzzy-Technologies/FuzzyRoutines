# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Static consumer of the explicitly installed NumPy batch extra."""

import numpy as np
from numpy.typing import NDArray

from fuzzyroutines import CreateUniversalFuzzyScale, Gaussian
from fuzzyroutines.batches import (
    EvaluateMembershipBatch,
    FuzzifyBatch,
    ScaleBatchResult,
)

grades: NDArray[np.float64] = EvaluateMembershipBatch(Gaussian(0, 1), [0.0, 1.0], backend="numpy")
result: ScaleBatchResult = FuzzifyBatch(CreateUniversalFuzzyScale(), [0.0, 0.5, 1.0])
selected: NDArray[np.bool_] = result.selected
