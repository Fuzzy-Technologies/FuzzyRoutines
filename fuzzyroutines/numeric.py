# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Internal scalar validation shared by modern mathematical modules.

Validation rejects booleans, non-real values, non-finite numbers, and invalid
membership degrees. It does not coerce, clamp, or configure global policy.
"""

import math
from numbers import Real

from fuzzyroutines.exceptions import (
    InvalidParameterError,
    InvalidParameterTypeError,
)


def _RequireFiniteReal(value: Real, parameter_name: str) -> Real:
    """Return a finite real scalar unchanged or raise a deterministic error."""

    if isinstance(value, bool) or not isinstance(value, Real):
        raise InvalidParameterTypeError(f"{parameter_name} must be a real number")

    if not math.isfinite(value):
        raise InvalidParameterError(f"{parameter_name} must be a finite real number")

    return value


def _RequireGrade(value: Real, parameter_name: str) -> Real:
    """Return a finite real membership degree in the closed unit interval."""

    value = _RequireFiniteReal(value, parameter_name)

    if not 0 <= value <= 1:
        raise InvalidParameterError(f"{parameter_name} must lie in the closed interval [0, 1]")

    return value
