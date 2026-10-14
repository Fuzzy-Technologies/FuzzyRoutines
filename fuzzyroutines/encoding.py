# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Framework-neutral scalar encodings for linguistic inputs and predictions.

Operations reuse explicit scalar fuzzification and centroid contracts. There is
no fitted normalization, automatic clipping, probabilistic interpretation,
neural dependency, or mutable centroid cache.
"""

import math
from dataclasses import dataclass
from fractions import Fraction
from numbers import Rational

from fuzzyroutines.defuzzification import Centroid, CentroidPolicy
from fuzzyroutines.domain import ContinuousUniverse, IntegrationDomain
from fuzzyroutines.exceptions import (
    InvalidParameterError,
    InvalidParameterTypeError,
    UndefinedResultError,
)
from fuzzyroutines.linguistic import (
    FuzzificationPolicy,
    FuzzificationResult,
    LinguisticScale,
)
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.numeric import _RequireGrade


def _ExactRatio(value: MembershipScalar) -> Fraction:
    """Preserve rational and float values; use the binary64 image of other reals."""

    if isinstance(value, (Rational, float)):
        return Fraction(value)

    return Fraction(float(value))


@dataclass(frozen=True, slots=True)
class LinguisticCodec:
    """Immutable configuration for one continuous scale and its representatives.

    Every operation concerns one sample. Membership vectors are explicit
    tuples of length `len(scale.terms)` in declaration order, without a batch
    dimension. Inputs and predictions already use the scale's coordinates;
    physical-unit conversion and fitted preprocessing belong to the caller.
    No method clamps an input, fits state, or silently replaces an unknown
    label with zero. Centroids encode data or targets, not learned weights.

    Attributes:
        scale: Ordered continuous terms sharing all evaluated coordinates.
        integrationDomains: One explicit centroid window per term, in scale
            order, contained in that term's universe.
        selectionPolicy: Explicit tie and no-match policy for predictions.
        centroidPolicy: Optional numerical integration limits; `None` uses
            the scalar centroid defaults.

    Notes:
        Label reduction and centroid encoding discard information. Neither
        fuzzification nor defuzzification is generally an inverse mapping.
        User-supplied membership callables retain their own state/ownership
        contract; this frozen configuration does not make callbacks pure.
    """

    scale: LinguisticScale
    integrationDomains: tuple[IntegrationDomain, ...]
    selectionPolicy: FuzzificationPolicy
    centroidPolicy: CentroidPolicy | None = None

    def __post_init__(self) -> None:
        """Validate ordered continuous domains and explicit numerical policies."""

        if not isinstance(self.scale, LinguisticScale):
            raise InvalidParameterTypeError("scale must be a LinguisticScale")

        if not isinstance(self.integrationDomains, tuple):
            raise InvalidParameterTypeError("integrationDomains must be an explicit tuple")

        if len(self.integrationDomains) != len(self.scale.terms):
            raise InvalidParameterError("integrationDomains must contain one domain per scale term")

        if not isinstance(self.selectionPolicy, FuzzificationPolicy):
            raise InvalidParameterTypeError("selectionPolicy must be a FuzzificationPolicy")

        if self.centroidPolicy is not None and not isinstance(self.centroidPolicy, CentroidPolicy):
            raise InvalidParameterTypeError("centroidPolicy must be a CentroidPolicy or None")

        for term, domain in zip(self.scale.terms, self.integrationDomains, strict=True):
            if not isinstance(domain, IntegrationDomain):
                raise InvalidParameterTypeError("integrationDomains must contain only IntegrationDomain values")

            if not isinstance(term.fuzzySet.universe, ContinuousUniverse):
                raise InvalidParameterTypeError("linguistic encoding requires continuous term universes")

            domain.ValidateWithin(term.fuzzySet.universe)

    @property
    def termNames(self) -> tuple[str, ...]:
        """Return the immutable column order used by every membership vector."""

        return tuple(term.name for term in self.scale.terms)

    def EncodeLabel(self, label: str) -> MembershipScalar:
        """Return a named term's centroid on its explicit integration window.

        Args:
            label: Complete case-sensitive term name; no prefix, approximate,
                or case-insensitive matching is applied.

        Returns:
            One numeric representative in the scale's coordinate units.

        Raises:
            TypeError: `label` is not a string.
            InvalidParameterError: The exact label is unknown.
            UndefinedResultError: The selected term has zero area or unresolved
                non-finite moments on its window.
            CentroidConvergenceError: Adaptive integration exceeds its limit.
        """

        term = self.scale.GetTermByName(label)

        if term is None:
            raise InvalidParameterError(f"unknown exact linguistic label: {label!r}")

        domain = self.integrationDomains[self.termNames.index(label)]

        return Centroid(term.fuzzySet, domain, self.centroidPolicy)

    def EncodeMemberships(self, coordinate: MembershipScalar) -> tuple[MembershipScalar, ...]:
        """Return all membership grades for one coordinate in declared order.

        Args:
            coordinate: Finite scalar in every term universe, already in the
                scale's units; no normalization or clipping is performed.

        Returns:
            An immutable length-N tuple with each grade in `[0, 1]`. Grades
            need not sum to one and are not probabilities; weak or zero
            coverage is retained even when the policy selects no label.

        Raises:
            TypeError: The coordinate is not a real scalar.
            ValueError: The coordinate is non-finite or outside any universe.
        """

        return tuple(item.grade for item in self.DecodePrediction(coordinate).memberships)

    def DecodePrediction(self, prediction: MembershipScalar) -> FuzzificationResult:
        """Interpret one numeric prediction with complete membership evidence.

        Args:
            prediction: Finite scalar already in the scale's coordinates and
                belonging to every term universe.

        Returns:
            Ordered grades, confidence, ties and selected terms under the
            configured policy. No match yields an empty `selectedTerms` tuple.

        Raises:
            TypeError: The prediction is not a real scalar.
            ValueError: The prediction is non-finite or outside any universe.
        """

        return self.scale.Fuzzify(prediction, self.selectionPolicy)

    def AverageRepresentatives(self, grades: tuple[MembershipScalar, ...]) -> float:
        r"""Return a grade-weighted average of the active term representatives.

        For grade $g_i$ and term centroid $c_i$, the result is
        $\sum_i g_i c_i / \sum_i g_i$. This is not the centroid of a clipped,
        scaled, or otherwise aggregated fuzzy set. Such a centroid requires
        explicit aggregation and its own integration domain.

        Args:
            grades: Explicit length-N tuple in `termNames` order, with every
                finite real grade in `[0, 1]`; the sum need not equal one.

        Returns:
            A finite numeric representative in the scale's coordinate units.
            Rational and binary64 grades and computed centroids are accumulated
            as exact ratios before a single final binary64 conversion. Other
            real scalar types use their binary64 image. Only positive-grade
            terms require a defined centroid; zero-grade terms contribute zero.

        Raises:
            TypeError: The vector is not a tuple or contains a non-real grade.
            InvalidParameterError: The vector length or a grade is invalid.
            UndefinedResultError: All grades are zero, an active term has
                zero area, or the average cannot be represented finitely.
            CentroidConvergenceError: An active centroid exceeds its limit.
        """

        if not isinstance(grades, tuple):
            raise InvalidParameterTypeError("grades must be an explicit tuple")

        if len(grades) != len(self.scale.terms):
            raise InvalidParameterError("grades must contain one value per scale term")

        validatedGrades = tuple(_RequireGrade(grade, "grade") for grade in grades)
        exactGrades = tuple(_ExactRatio(grade) for grade in validatedGrades)
        total = sum(exactGrades, Fraction(0))

        if total == 0:
            raise UndefinedResultError("representative average is undefined for all-zero grades")

        # Round only the quotient: dividing tiny weights first can erase a
        # representable contribution, while summing float moments can overflow.
        numerator = sum((
            grade * _ExactRatio(Centroid(term.fuzzySet, domain, self.centroidPolicy))
            for originalGrade, grade, term, domain in zip(
                validatedGrades, exactGrades, self.scale.terms, self.integrationDomains, strict=True,
            )
            if originalGrade > 0
        ), Fraction(0))

        try:
            result = float(numerator / total)

        except OverflowError as error:
            raise UndefinedResultError("representative average must be finite") from error

        if not math.isfinite(result):
            raise UndefinedResultError("representative average must be finite")

        return result
