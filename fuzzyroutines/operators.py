# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Immutable scalar negation, t-norm, and s-norm policies.

This module owns the operator formulas and depends only on scalar validation.
Set algebra consumes explicit policy values; no global family is configured.
Existing fuzzysets import paths re-export these same class objects.
"""

import math
from dataclasses import dataclass
from typing import cast

from fuzzyroutines.exceptions import (
    InvalidParameterError,
)
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.numeric import _RequireFiniteReal, _RequireGrade

__all__ = ["NegationPolicy", "SNormPolicy", "TNormPolicy"]

OPERATOR_FAMILIES = ("logic", "algebraic", "boundary", "drastic")


@dataclass(frozen=True, slots=True)
class NegationPolicy:
    """Explicit fuzzy-negation family and its optional fixed-point parameter.

    Attributes:
        family: `"standard"`, `"parametric"`, or `"parabolic"`.
        alpha: Fixed point for parametric or parabolic negation; absent for
            standard negation.
    """

    family: str
    alpha: MembershipScalar | None = None

    def __post_init__(self) -> None:
        """Validate the complete negation configuration before evaluation."""

        if self.family == "standard":
            if self.alpha is not None:
                raise InvalidParameterError("standard negation does not accept alpha")

            return

        if self.family == "parametric":
            alpha = _RequireFiniteReal(self.alpha, "alpha")

            if not 0 < alpha < 1:
                raise InvalidParameterError("parametric negation alpha must lie in the open interval (0, 1)")

            object.__setattr__(self, "alpha", alpha)
            return

        if self.family == "parabolic":
            alpha = _RequireFiniteReal(self.alpha, "alpha")

            if not 0.25 <= alpha <= 0.75:
                raise InvalidParameterError("parabolic negation alpha must lie in the closed interval [1/4, 3/4]")

            object.__setattr__(self, "alpha", alpha)
            return

        raise InvalidParameterError(f"unknown negation family: {self.family!r}")

    def Evaluate(self, grade: MembershipScalar) -> MembershipScalar:
        """Evaluate the configured negation for one membership grade.

        Args:
            grade: Finite membership degree in $[0, 1]$.

        Returns:
            The complemented membership degree under this policy.

        Raises:
            TypeError: If `grade` is not a real scalar.
            ValueError: If `grade` is non-finite or outside $[0, 1]$.
        """

        grade = _RequireGrade(grade, "grade")

        return _EvaluateNegation(self.family, cast(float | None, self.alpha), grade)


@dataclass(frozen=True, slots=True)
class TNormPolicy:
    """Explicit t-norm family used by fuzzy-set intersection.

    Attributes:
        family: One of the names in `OPERATOR_FAMILIES`.
    """

    family: str

    def __post_init__(self) -> None:
        """Reject every family not accepted by ADR-0004."""

        if self.family not in OPERATOR_FAMILIES:
            raise InvalidParameterError(f"unknown t-norm family: {self.family!r}")

    def Evaluate(self, leftGrade: MembershipScalar, rightGrade: MembershipScalar) -> MembershipScalar:
        """Evaluate the configured t-norm for two membership grades.

        Args:
            leftGrade: Left membership degree in $[0, 1]$.
            rightGrade: Right membership degree in $[0, 1]$.

        Returns:
            Conjunction under the configured family.

        Raises:
            TypeError: If an operand is not a real scalar.
            ValueError: If an operand is non-finite or outside $[0, 1]$.
        """

        leftGrade = _RequireGrade(leftGrade, "leftGrade")
        rightGrade = _RequireGrade(rightGrade, "rightGrade")

        return _EvaluateTNorm(self.family, leftGrade, rightGrade)


@dataclass(frozen=True, slots=True)
class SNormPolicy:
    """Explicit s-norm family used by fuzzy-set union.

    Attributes:
        family: One of the names in `OPERATOR_FAMILIES`.
    """

    family: str

    def __post_init__(self) -> None:
        """Reject every family not accepted by ADR-0004."""

        if self.family not in OPERATOR_FAMILIES:
            raise InvalidParameterError(f"unknown s-norm family: {self.family!r}")

    def Evaluate(self, leftGrade: MembershipScalar, rightGrade: MembershipScalar) -> MembershipScalar:
        """Evaluate the configured s-norm for two membership grades.

        Args:
            leftGrade: Left membership degree in $[0, 1]$.
            rightGrade: Right membership degree in $[0, 1]$.

        Returns:
            Disjunction under the configured family.

        Raises:
            TypeError: If an operand is not a real scalar.
            ValueError: If an operand is non-finite or outside $[0, 1]$.
        """

        leftGrade = _RequireGrade(leftGrade, "leftGrade")
        rightGrade = _RequireGrade(rightGrade, "rightGrade")

        return _EvaluateSNorm(self.family, leftGrade, rightGrade)


def _EvaluateNegation(family: str, alpha: float | None, grade: float) -> float:
    """Evaluate a prevalidated negation without allocating a policy."""

    if family == "standard":
        return 1 - grade

    # Construction validates alpha for every non-standard policy.
    alpha = cast(float, alpha)

    if family == "parametric":
        if grade <= alpha:
            return grade * (alpha - 1) / alpha + 1

        return (grade - 1) * alpha / (alpha - 1)

    if grade == 0:
        return 1.0

    if grade == 1:
        return 0.0

    # Stable rationalized root of the implicit quadratic relation; see
    # docs/mathematics/parabolic-negation-derivation.md.
    if alpha <= 0.5:
        discriminant = (4 * alpha - 1) ** 2 + 8 * (1 - 2 * alpha) * grade

    else:
        discriminant = (4 * alpha - 3) ** 2 + 8 * (2 * alpha - 1) * (1 - grade)

    return grade + 4 * (alpha - grade) / (1 + math.sqrt(discriminant))


def _EvaluateTNorm(family: str, left_grade: float, right_grade: float) -> float:
    """Evaluate a prevalidated t-norm without allocating a policy."""

    if family == "logic":
        return min(left_grade, right_grade)

    if family == "algebraic":
        return left_grade * right_grade

    if family == "boundary":
        return max(left_grade + right_grade - 1, 0)

    if family != "drastic":
        raise InvalidParameterError(f"unknown t-norm family: {family!r}")

    if left_grade == 1:
        return right_grade

    if right_grade == 1:
        return left_grade

    return 0


def _EvaluateSNorm(family: str, left_grade: float, right_grade: float) -> float:
    """Evaluate a prevalidated s-norm without allocating a policy."""

    if family == "logic":
        return max(left_grade, right_grade)

    if family == "algebraic":
        return left_grade + right_grade - left_grade * right_grade

    if family == "boundary":
        return min(left_grade + right_grade, 1)

    if family != "drastic":
        raise InvalidParameterError(f"unknown s-norm family: {family!r}")

    if left_grade == 0:
        return right_grade

    if right_grade == 0:
        return left_grade

    return 1
