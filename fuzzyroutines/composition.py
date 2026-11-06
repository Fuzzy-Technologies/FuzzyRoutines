# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Named outputs from independent scalar Mamdani and Sugeno models.

An ordered tuple of output bindings routes exact external input IDs to
scalar variables. Construct a composition with an explicit failure policy.
Evaluation retains each component's existing result and trace.

This module adds no optional dependency or wire-format support.
"""

from ._model_composition import (
    CompositionEvaluationError,
    FailureCategory,
    FailurePolicy,
    ModelComposition,
    OutputBinding,
    OutputFailure,
    OutputRecord,
)

__all__ = [
    "CompositionEvaluationError",
    "FailureCategory",
    "FailurePolicy",
    "ModelComposition",
    "OutputBinding",
    "OutputFailure",
    "OutputRecord",
]
