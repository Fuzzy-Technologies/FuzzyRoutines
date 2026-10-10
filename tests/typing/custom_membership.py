# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Isolated static consumer checks for the custom membership callable contract.

Run mypy with strict checking and unused-ignore reporting. Expected-invalid
assignments carry precise ignores so weakening the protocol makes this smoke
fail with an unused ignore, rather than silently accepting incompatible types.
"""

from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.membership import (
    MembershipCallable,
    MembershipFunction,
    MembershipScalar,
)


def BroadGrade(coordinate: MembershipScalar) -> float:
    """Accept the complete scalar input contract and return a built-in grade."""

    return 0.5


def FloatOnlyGrade(coordinate: float) -> float:
    """Model a callback whose annotation cannot promise every Real input."""

    return 0.5


def InvalidGrade(coordinate: MembershipScalar) -> str:
    """Model a callback whose result violates the structural scalar contract."""

    return "0.5"


def MissingCoordinate() -> float:
    """Model a callback that cannot receive the required positional coordinate."""

    return 0.5


def CheckConsumers(builtIn: MembershipFunction, fuzzySet: ScalarFuzzySet) -> None:
    """Check stock evaluators, bound methods, set fields, floats, and integers."""

    custom: MembershipCallable = BroadGrade
    analytical: MembershipCallable = builtIn
    boundMethod: MembershipCallable = builtIn.Evaluate
    setEvaluator: MembershipCallable = fuzzySet.membershipFunction
    custom(0.5)
    custom(1)
    analytical(0.5)
    analytical(1)
    boundMethod(0.5)
    setEvaluator(1)


NARROW_CALLBACK: MembershipCallable = FloatOnlyGrade  # type: ignore[assignment]
INVALID_RESULT: MembershipCallable = InvalidGrade  # type: ignore[assignment]
INVALID_SIGNATURE: MembershipCallable = MissingCoordinate  # type: ignore[assignment]
