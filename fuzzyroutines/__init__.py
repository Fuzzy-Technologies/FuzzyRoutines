"""Modern public API for explicit fuzzy-set domain and property contracts."""

from fuzzyroutines.domain import (
    ContinuousUniverse,
    DiscreteUniverse,
    IntegrationDomain,
)
from fuzzyroutines.fuzzysets import (
    Complement,
    Difference,
    Intersection,
    NegationPolicy,
    ScalarFuzzySet,
    SNormPolicy,
    TNormPolicy,
    Union,
)
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
    "IncludedOnDomain",
    "IntegrationDomain",
    "Intersection",
    "NegationPolicy",
    "SNormPolicy",
    "SampleProperties",
    "SampledFuzzyProperties",
    "ScalarFuzzySet",
    "TNormPolicy",
    "Union",
]
