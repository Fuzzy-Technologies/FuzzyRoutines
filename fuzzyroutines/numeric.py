# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Internal scalar validation shared by modern mathematical modules.

Validation rejects booleans, non-real values, non-finite numbers, and invalid
membership degrees. It does not coerce, clamp, or configure global policy.

Private arithmetic uses a static float view of validated Real values because
Typeshed's numeric abstract classes return complex-like operator types. Those
casts describe the supported real arithmetic interface; they never convert the
runtime value. Public inputs, fields, and scalar results retain MembershipScalar,
including Fraction. Casts of interval endpoints occur only after finite endpoint
validation or an explicit check that the endpoint is bounded.
"""

import math
from numbers import Real
from typing import cast

from fuzzyroutines.exceptions import (
    InvalidParameterError,
    InvalidParameterTypeError,
)


def _RequireFiniteReal(value: object, parameterName: str) -> float:
    """Return a finite real scalar unchanged or raise a deterministic error."""

    if isinstance(value, bool) or not isinstance(value, Real):
        raise InvalidParameterTypeError(f"{parameterName} must be a real number")

    if not math.isfinite(value):
        raise InvalidParameterError(f"{parameterName} must be a finite real number")

    # Typeshed models Real arithmetic through a complex-like base. This
    # static arithmetic view preserves the original value, including Fraction.
    return cast(float, value)


def _RequireGrade(value: object, parameterName: str) -> float:
    """Return a finite real membership degree in the closed unit interval."""

    value = _RequireFiniteReal(value, parameterName)

    if not 0 <= value <= 1:
        raise InvalidParameterError(f"{parameterName} must lie in the closed interval [0, 1]")

    return value
