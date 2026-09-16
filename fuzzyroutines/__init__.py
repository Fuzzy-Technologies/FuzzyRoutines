"""Modern public API for explicit fuzzy-set domain and property contracts."""

from fuzzyroutines.domain import (
    ContinuousUniverse,
    DiscreteUniverse,
    IntegrationDomain,
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

__all__ = [
    "ContinuousFuzzyProperties",
    "ContinuousInterval",
    "ContinuousRegion",
    "ContinuousUniverse",
    "DeriveProperties",
    "DiscreteFuzzyProperties",
    "DiscreteRegion",
    "DiscreteUniverse",
    "IntegrationDomain",
    "SampleProperties",
    "SampledFuzzyProperties",
]
