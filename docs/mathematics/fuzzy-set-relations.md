# Fuzzy-Set Equality and Inclusion

- Status: Executable contract for Task #73
- Public module: `fuzzyroutines.relations`

## Mathematical relations

For fuzzy sets `A` and `B` over the same universe `X`, pointwise equality and
inclusion are defined as

```text
A = B  iff  for every x in X: mu_A(x) = mu_B(x)
A <= B iff  for every x in X: mu_A(x) <= mu_B(x)
```

The public API never compares membership-function object identity. Two
different Python callables can therefore represent equal membership behavior.
Both relations require exactly equal universes before evaluating any grade.
Python object equality for `ScalarFuzzySet` remains identity-based and is not a
mathematical relation; callers must use the explicit relation functions.

## Exhaustive and sampled scope

`DiscreteUniverse` is finite, so `EqualOnDomain` and `IncludedOnDomain`
evaluate every declared point. A caller cannot provide a partial comparison
domain and accidentally label that result as whole-universe equality.

An arbitrary Python callable over a `ContinuousUniverse` cannot in general be
proved globally equal to another callable by finite evaluation. Continuous
relations therefore require an explicit `ComparisonDomain` containing finite,
ordered sample points inside the universe. Their Boolean result is valid only
on those declared points; it is not a proof of functional equality or
inclusion between the points.

This boundary is deliberate. Analytical relation proofs for known membership
families would require a separate symbolic representation and contract.

## Exact and tolerance modes

Every relation requires a `ComparisonPolicy`:

- `ComparisonPolicy("exact")` uses exact numeric grade equality and exact
  pointwise ordering;
- `ComparisonPolicy("tolerance", absoluteTolerance=..., relativeTolerance=...)`
  uses `math.isclose` for equality and permits an inclusion violation only when
  the two grades are close under those explicit tolerances.

Tolerance mode requires both tolerance fields and at least one must be
positive. Exact mode rejects tolerance arguments. There is no library-wide or
implicit epsilon.

Tolerance-based closeness is not generally transitive. It must not be used as
an equivalence relation for hashing, canonicalization, or identity.

## Examples

Exhaustive discrete comparison:

```python
from fuzzyroutines import (
    ComparisonPolicy,
    DiscreteUniverse,
    EqualOnDomain,
    IncludedOnDomain,
    ScalarFuzzySet,
)

universe = DiscreteUniverse((0.0, 0.5, 1.0))
leftSet = ScalarFuzzySet(universe, lambda coordinate: coordinate)
rightSet = ScalarFuzzySet(universe, lambda coordinate: coordinate**1)
policy = ComparisonPolicy("exact")

assert EqualOnDomain(leftSet, rightSet, policy)
assert IncludedOnDomain(leftSet, rightSet, policy)
```

Explicit sampled continuous comparison:

```python
from fuzzyroutines import ComparisonDomain, ContinuousUniverse

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
leftSet = ScalarFuzzySet(universe, lambda coordinate: coordinate * coordinate)
rightSet = ScalarFuzzySet(universe, lambda coordinate: coordinate**2)
samplePoints = ComparisonDomain((0.0, 0.25, 0.5, 0.75, 1.0))

assert EqualOnDomain(leftSet, rightSet, policy, samplePoints)
```

## Verified properties

The executable suite covers:

- exhaustive discrete equality and inclusion;
- equality of non-identical callable representations;
- reflexivity and exact antisymmetry;
- explicit absolute and relative tolerance behavior;
- mandatory continuous comparison domains;
- rejection of partial discrete domains;
- rejection of incompatible universes and invalid sample points.

## References

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- G. J. Klir and B. Yuan, *Fuzzy Sets and Fuzzy Logic: Theory and
  Applications*, Prentice Hall, 1995. ISBN 978-0-13-101171-7.
