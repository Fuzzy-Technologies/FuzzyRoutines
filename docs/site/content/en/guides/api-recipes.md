<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Practical API recipes

The [worked scenarios](index.md) explain complete calculations. These smaller
recipes cover domain validation, sampled properties, operator alternatives,
finite comparisons, and error handling. Each Python block stands alone and is
executed against installed wheel and sdist artifacts in CI.

## Validate a domain before integration

```python
from fuzzyroutines import ContinuousUniverse, DiscreteUniverse, IntegrationDomain

universe = ContinuousUniverse(0, 10, leftClosed=True, rightClosed=True)
domain = IntegrationDomain.FromLegacyInterval((2, 8)).ValidateWithin(universe)
assert universe.isBounded and universe.Contains(0)
assert domain.Contains(2) and domain.ToLegacyInterval() == (2, 8)
discrete = DiscreteUniverse((1, 3, 5))
assert discrete.Contains(3) and not discrete.Contains(2)
print(domain.ToLegacyInterval(), discrete.points)
```

An integration window is a finite closed interval, not the mathematical
positive support. A universe may be unbounded or have open endpoints; a
requested integration window must respect those endpoint restrictions.

## Read exact and sampled properties

```python
from fuzzyroutines import (
    ContinuousInterval, ContinuousRegion, ContinuousUniverse, DeriveProperties,
    DiscreteRegion, IntegrationDomain, IsNormal, SampleProperties,
    ScalarFuzzySet, Triangle,
)

model = Triangle(0, 2, 4)
universe = ContinuousUniverse(0, 4, leftClosed=True, rightClosed=True)
properties = DeriveProperties(model, universe)
sampled = SampleProperties(model, IntegrationDomain(0, 4), sampleCount=5)
assert properties.isExact and properties.height == 1
assert properties.core.Contains(2) and not properties.positiveSupport.Contains(0)
assert not sampled.isExact and sampled.heightEstimate == 1
assert sampled.coreSamples.points == (2,)
assert IsNormal(ScalarFuzzySet(universe, model))
interval = ContinuousInterval(1, 3, leftClosed=True, rightClosed=False)
region = ContinuousRegion((interval,))
assert region.Contains(1) and not region.Contains(3) and not region.isEmpty
assert not interval.isSingleton and not DiscreteRegion((1, 3)).isEmpty
print(properties.height, sampled.coordinates)
```

For built-in analytical families, `DeriveProperties` computes exact geometry
restricted to the universe. `SampleProperties` reports observed support, core,
boundary, and a height estimate on a stated grid. Hitting the peak in this
example makes the estimate one; missing a narrow peak in another model can
underestimate height. Generic continuous exact height is not inferred from
samples. `IsNormal` uses exact height and an explicit tolerance, defaulting to
$10^{-12}$.

## Choose scalar operator families deliberately

```python
from math import isclose
from fuzzyroutines import NegationPolicy, SNormPolicy, TNormPolicy

expectedAnd = {"logic": 0.4, "algebraic": 0.28, "boundary": 0.1, "drastic": 0}
expectedOr = {"logic": 0.7, "algebraic": 0.82, "boundary": 1, "drastic": 1}
for family in expectedAnd:
    assert isclose(TNormPolicy(family).Evaluate(0.4, 0.7), expectedAnd[family], abs_tol=1e-12)
    assert isclose(SNormPolicy(family).Evaluate(0.4, 0.7), expectedOr[family], abs_tol=1e-12)
assert NegationPolicy("standard").Evaluate(0.4) == 0.6
assert NegationPolicy("parametric", alpha=0.5).Evaluate(0.5) == 0.5
assert NegationPolicy("parabolic", alpha=0.5).Evaluate(0.5) == 0.5
print(expectedAnd, expectedOr)
```

The parametric negation requires $0<\alpha<1$; parabolic negation requires
$1/4\leq\alpha\leq3/4$. Their alpha is a negation parameter, not an alpha-cut
threshold. Boundary and drastic policies are explicit alternatives; abrupt
endpoint behavior can have consequences for your model.

## Compare continuous models at explicit coordinates

```python
from fuzzyroutines import (
    ComparisonDomain, ComparisonPolicy, ContinuousUniverse,
    EqualOnDomain, IncludedOnDomain, ScalarFuzzySet, Triangle,
)

universe = ContinuousUniverse(0, 4, leftClosed=True, rightClosed=True)
left = ScalarFuzzySet(universe, Triangle(0, 2, 4))
right = ScalarFuzzySet(universe, Triangle(0, 2, 4))
coordinates = ComparisonDomain((0, 1, 2, 3, 4)).ValidateWithin(universe)
policy = ComparisonPolicy("tolerance", absoluteTolerance=1e-12, relativeTolerance=1e-10)
assert policy.Equal(0.5, 0.5 + 1e-13)
assert policy.Included(0.4, 0.5)
assert EqualOnDomain(left, right, policy, coordinates)
assert IncludedOnDomain(left, right, policy, coordinates)
print(coordinates.points)
```

The result certifies only the five declared observations. It is not a global
continuous equivalence proof, even when a separate analytical argument shows
these particular definitions are identical.

## Handle a mathematically undefined result

```python
from fuzzyroutines import (
    Centroid, CentroidPolicy, ContinuousUniverse, IntegrationDomain,
    MembershipScalar, ScalarFuzzySet,
)
from fuzzyroutines.exceptions import UndefinedResultError


def ZeroGrade(coordinate: MembershipScalar) -> MembershipScalar:
    """Return zero area on every allowed coordinate."""

    return 0


empty = ScalarFuzzySet(
    ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True), ZeroGrade,
)
try:
    Centroid(empty, IntegrationDomain(0, 1), CentroidPolicy(maximumDepth=20))
except UndefinedResultError:
    print("No centroid: the membership area is zero")
else:
    raise AssertionError("zero-area membership unexpectedly had a centroid")
```

Choose a domain-appropriate fallback or propagate this error. Returning zero
silently would invent a representative coordinate. Invalid types, parameters,
and domains have their own documented exception categories; adaptive exhaustion
has `CentroidConvergenceError`. Catch the specific contract your application
can handle instead of suppressing every error.
