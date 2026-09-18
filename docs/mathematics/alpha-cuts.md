# Alpha-cut contract

## Definition and boundary convention

For a scalar fuzzy set $A$ on universe $X$, FuzzyRoutines defines the
weak alpha-cut as

$$
A_\alpha = \{x \in X \mid \mu_A(x) \ge \alpha\},
\qquad \alpha \in [0, 1].
$$

The comparison is exactly `>=`. A coordinate whose membership grade equals
the threshold belongs to the cut. The API does not silently substitute the
strong cut $\{x \mid \mu_A(x) > \alpha\}$, and it applies no numeric
tolerance.

The endpoint semantics follow directly from this definition:

- $A_0 = X$, because every valid membership grade lies in $[0, 1]$;
- $A_1 = \{x \in X \mid \mu_A(x) = 1\}$, the core of $A$.

For any $0 \le \alpha \le \beta \le 1$, cuts are nested:

$$
A_\beta \subseteq A_\alpha.
$$

## Exact discrete operation

`AlphaCut(fuzzySet, alpha)` exhaustively evaluates every coordinate in a
`DiscreteUniverse` and returns a `DiscreteRegion`. The result is therefore the
exact cut relative to the declared finite universe.

```python
from fuzzyroutines import AlphaCut, DiscreteUniverse, ScalarFuzzySet

universe = DiscreteUniverse((0.0, 0.5, 1.0))
fuzzySet = ScalarFuzzySet(universe, lambda coordinate: coordinate)

assert AlphaCut(fuzzySet, 0.5).points == (0.5, 1.0)
assert AlphaCut(fuzzySet, 0.0).points == universe.points
assert AlphaCut(fuzzySet, 1.0).points == (1.0,)
```

The operation evaluates through `ScalarFuzzySet.Membership`, so non-finite,
non-real, or out-of-range membership grades fail closed.

## Explicitly sampled continuous operation

An arbitrary Python callable over a `ContinuousUniverse` has no general
analytical inverse. A finite scan cannot prove its continuous alpha-cut.
Consequently, `AlphaCut` rejects continuous fuzzy sets instead of presenting
sample points as exact geometry.

`SampleAlphaCut(fuzzySet, alpha, analysisDomain, sampleCount)` is the explicit
numerical alternative. It evaluates a uniform finite grid over an
`IntegrationDomain` contained in the set's universe and returns a
`SampledAlphaCut`. The result records:

- `alpha` and the weak `>= alpha` selection;
- `analysisDomain`, `sampleCount`, and all evaluated `coordinates`;
- every validated membership value in `grades`;
- the selected `cutSamples` as a `DiscreteRegion`;
- `method == "uniform-grid"` and `isExact == False`.

```python
from fuzzyroutines import (
    ContinuousUniverse,
    IntegrationDomain,
    SampleAlphaCut,
    ScalarFuzzySet,
)

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, lambda coordinate: coordinate)
sampledCut = SampleAlphaCut(
    fuzzySet,
    0.5,
    IntegrationDomain(0.0, 1.0),
    sampleCount=5,
)

assert sampledCut.cutSamples.points == (0.5, 0.75, 1.0)
assert sampledCut.isExact is False
```

For `alpha=0`, `cutSamples` contains the entire declared grid, not a
materialized continuous universe. For `alpha=1`, it contains only sampled
coordinates with grade exactly one; it is not proof of the complete
continuous core. The nesting invariant is guaranteed when cuts use the same
fuzzy set, analysis domain, and grid resolution.
