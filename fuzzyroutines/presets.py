# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Historical scale coefficients exposed through immutable modern objects.

The normalized universe, centroid windows, and winner policy are separate
contracts. Importing this module does not construct or evaluate a scale.
"""

from fuzzyroutines.domain import ContinuousUniverse, IntegrationDomain
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.linguistic import (
    FuzzificationPolicy,
    LinguisticScale,
    LinguisticTerm,
)
from fuzzyroutines.membership import Bell, Hyperbolic, SShoulder


def CreateUniversalFuzzyScale() -> LinguisticScale:
    """Return the historical five-level scale on the closed unit universe.

    Returns:
        Fresh immutable `Min`, `Low`, `Med`, `High`, `Max` terms, in that
        order, retaining the historical membership coefficients.

    Notes:
        The positive Min tail and weak coverage near 0.17 are intentional.
        Grades are not probabilities and need not sum to one. The factory
        does not change the generic first-maximum fuzzification default;
        pass [UniversalFuzzyScalePolicy][fuzzyroutines.presets.UniversalFuzzyScalePolicy]
        for historical winner selection. Coordinates outside the closed
        unit universe fail validation instead of being clamped.
    """

    universe = ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True)
    models = (
        ("Min", Hyperbolic(8, 20, 0)),
        ("Low", Bell(0.17, 0.23, 0.34)),
        ("Med", Bell(0.34, 0.40, 0.60)),
        ("High", Bell(0.60, 0.66, 0.77)),
        ("Max", SShoulder(0.77, 0.95)),
    )

    return LinguisticScale(tuple(
        LinguisticTerm(name, ScalarFuzzySet(universe, model))
        for name, model in models
    ))


def UniversalFuzzyScalePolicy() -> FuzzificationPolicy:
    """Return last-exact-maximum selection without an extra confidence cutoff.

    Returns:
        A policy with `tiePolicy="last"`, `tieTolerance=0`, and
        `minimumConfidence=0`. Zero coverage remains no match; the historical
        scale has a positive Min tail throughout its normalized universe.

    Notes:
        Binary64 evaluation of a mathematically symmetric midpoint may not
        tie exactly. No rounding or near-tie tolerance is introduced.
    """

    return FuzzificationPolicy(tiePolicy="last", minimumConfidence=0, tieTolerance=0)


def UniversalFuzzyScaleDomains() -> tuple[IntegrationDomain, ...]:
    """Return the historical per-level centroid windows in scale order.

    Returns:
        Closed integration intervals for `Min`, `Low`, `Med`, `High`, `Max`:
        `(0, 0.23)`, `(0.17, 0.40)`, `(0.34, 0.66)`, `(0.60, 0.83)`,
        and `(0.77, 1)`.

    Notes:
        These are integration bounds, not term universes or mathematical
        supports. Modern corrected centroids agree with the 2.0 facade but
        need not equal the sampled or stale cached values from version 1.0.3.
    """

    return tuple(IntegrationDomain(left, right) for left, right in (
        (0, 0.23), (0.17, 0.40), (0.34, 0.66), (0.60, 0.83), (0.77, 1),
    ))
