# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Modern public API for explicit fuzzy-set domain and property contracts.

The literal `__all__` list defines the curated modern API, including immutable
membership factories, typing contracts, universes, sets, and policies. Historical
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
    Normalize,
    ScalarFuzzySet,
    Union,
)
from fuzzyroutines.linguistic import (
    FuzzificationPolicy,
    FuzzificationResult,
    LinguisticScale,
    LinguisticTerm,
    ScaleDiagnosticPoint,
    ScaleDiagnosticsPolicy,
    ScaleDiagnosticsResult,
    TermMembership,
)
from fuzzyroutines.membership import (
    Bell,
    Gaussian,
    HarringtonDesirability,
    Hyperbolic,
    Logistic,
    MembershipCallable,
    MembershipFunction,
    MembershipScalar,
    SShoulder,
    Trapezoid,
    Triangle,
)
from fuzzyroutines.operators import NegationPolicy, SNormPolicy, TNormPolicy
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
    "Bell",
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
    "FuzzificationPolicy",
    "FuzzificationResult",
    "Gaussian",
    "HarringtonDesirability",
    "Height",
    "Hyperbolic",
    "IncludedOnDomain",
    "IntegrationDomain",
    "Intersection",
    "IsNormal",
    "LinguisticScale",
    "LinguisticTerm",
    "Logistic",
    "MembershipCallable",
    "MembershipFunction",
    "MembershipScalar",
    "NegationPolicy",
    "Normalize",
    "SNormPolicy",
    "SShoulder",
    "SampleAlphaCut",
    "SampleProperties",
    "SampledAlphaCut",
    "SampledFuzzyProperties",
    "ScalarFuzzySet",
    "ScaleDiagnosticPoint",
    "ScaleDiagnosticsPolicy",
    "ScaleDiagnosticsResult",
    "TNormPolicy",
    "TermMembership",
    "Trapezoid",
    "Triangle",
    "Union",
]
