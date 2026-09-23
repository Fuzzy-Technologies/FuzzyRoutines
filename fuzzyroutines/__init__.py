# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Modern public API for explicit fuzzy-set domain and property contracts.

The root package re-exports the immutable v2 surface from the domain,
fuzzy-set, property, alpha-cut, relation, and linguistic modules. Historical
mutable names remain available only from `fuzzyroutines.FuzzyRoutines`; package
import performs no evaluation, I/O, or configuration changes.
"""

from fuzzyroutines.alphacuts import AlphaCut, SampleAlphaCut, SampledAlphaCut
from fuzzyroutines.defuzzification import (
    Centroid,
    CentroidConvergenceError,
    CentroidPolicy,
)
from fuzzyroutines.domain import (
    ContinuousUniverse,
    DiscreteUniverse,
    IntegrationDomain,
)
from fuzzyroutines.fuzzysets import (
    Complement,
    Difference,
    Height,
    Intersection,
    IsNormal,
    NegationPolicy,
    Normalize,
    ScalarFuzzySet,
    SNormPolicy,
    TNormPolicy,
    Union,
)
from fuzzyroutines.linguistic import LinguisticScale, LinguisticTerm
from fuzzyroutines.properties import (
    ContinuousFuzzyProperties,
    ContinuousInterval,
    ContinuousRegion,
    DeriveProperties,
    DiscreteFuzzyProperties,
    DiscreteRegion,
    SampledFuzzyProperties,
    SampleProperties,
)
from fuzzyroutines.relations import (
    ComparisonDomain,
    ComparisonPolicy,
    EqualOnDomain,
    IncludedOnDomain,
)

__all__ = [
    "AlphaCut",
    "Centroid",
    "CentroidConvergenceError",
    "CentroidPolicy",
    "ComparisonDomain",
    "ComparisonPolicy",
    "Complement",
    "ContinuousFuzzyProperties",
    "ContinuousInterval",
    "ContinuousRegion",
    "ContinuousUniverse",
    "DeriveProperties",
    "Difference",
    "DiscreteFuzzyProperties",
    "DiscreteRegion",
    "DiscreteUniverse",
    "EqualOnDomain",
    "Height",
    "IncludedOnDomain",
    "IntegrationDomain",
    "Intersection",
    "IsNormal",
    "LinguisticScale",
    "LinguisticTerm",
    "NegationPolicy",
    "Normalize",
    "SNormPolicy",
    "SampleAlphaCut",
    "SampleProperties",
    "SampledAlphaCut",
    "SampledFuzzyProperties",
    "ScalarFuzzySet",
    "TNormPolicy",
    "Union",
]
