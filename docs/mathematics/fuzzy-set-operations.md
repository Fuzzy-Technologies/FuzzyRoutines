# Explicit Fuzzy-Set Operations

- Status: Executable contract for Tasks #71, #72, and #74
- Related ADRs: [ADR-0004](../adr/0004-operator-and-negation-contracts.md) and
  [ADR-0008](../adr/0008-fuzzy-set-difference-semantics.md)
- Public module: `fuzzyroutines.fuzzysets`

## Set representation

A `ScalarFuzzySet` is the ordered pair

```text
A = (X, mu_A)
mu_A: X -> [0, 1]
```

where `X` is an explicit `ContinuousUniverse` or `DiscreteUniverse`. Membership
evaluation rejects coordinates outside `X` and rejects Boolean, non-finite, or
out-of-range grades instead of coercing them.

The value object's fields are immutable. An operation constructs a new
membership evaluator over the same universe and does not modify either
operand. Callers supplying a custom callable remain responsible for keeping
that callable reentrant and free of externally mutable semantics.

## Universe compatibility

Binary operations require exact universe equality, including continuous
endpoint values, endpoint closure, representation kind, and discrete points.
The initial API does not infer a union, intersection, resampling grid, or
coordinate conversion for different universes. Such reconciliation would be a
separate mathematical operation with its own policy.

## Complement

For an explicit negation `N`, complement is evaluated pointwise:

```text
mu_complement(A)(x) = N(mu_A(x))
```

`NegationPolicy` supports only the families accepted by ADR-0004:

- `standard`: `N(x) = 1 - x`, with no parameter;
- `parametric`: the historical piecewise-linear strong negation with explicit
  `alpha` in `(0, 1)`;
- `parabolic`: the accepted analytical branch with explicit `alpha` in
  `[1/4, 3/4]`.

There is no default or process-wide negation setting. Even the standard
complement must be requested with `NegationPolicy("standard")`.

## Intersection and union

Given an explicit t-norm `T` and s-norm `S`:

```text
mu_intersection(A, B)(x) = T(mu_A(x), mu_B(x))
mu_union(A, B)(x)        = S(mu_A(x), mu_B(x))
```

`TNormPolicy` and `SNormPolicy` accept `logic`, `algebraic`, `boundary`, and
`drastic`. The formulas are exactly those recorded in ADR-0004. Neither
`Intersection` nor `Union` has a hidden default family.

## Directed difference

Difference is intersection with the explicitly selected complement of the
right operand:

```text
mu_Difference(A, B)(x) = T(mu_A(x), N(mu_B(x)))
```

`Difference` therefore requires both a `TNormPolicy` and a `NegationPolicy`.
The operands must have exactly equal universes, and the result preserves that
universe. The operation is directional and does not mutate either operand.

Standard negation with the logic t-norm recovers classical difference for
crisp grades. General fuzzy grades retain the selected operator semantics; in
particular, `Difference(A, A)` is not promised to be empty. ADR-0008 does not
define symmetric difference because composing two directed differences also
requires an s-norm and does not preserve every classical law for arbitrary
operator policies.

## Example

```python
from fuzzyroutines import (
    Complement,
    ContinuousUniverse,
    Difference,
    Intersection,
    NegationPolicy,
    ScalarFuzzySet,
    SNormPolicy,
    TNormPolicy,
    Union,
)

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
increasingSet = ScalarFuzzySet(universe, lambda coordinate: coordinate)
decreasingSet = Complement(increasingSet, NegationPolicy("standard"))

overlap = Intersection(increasingSet, decreasingSet, TNormPolicy("logic"))
envelope = Union(increasingSet, decreasingSet, SNormPolicy("logic"))
directedDifference = Difference(
    increasingSet,
    decreasingSet,
    TNormPolicy("logic"),
    NegationPolicy("standard"),
)
```

## Verified laws

Executable property tests cover all four accepted dual family pairs:

- closure in `[0, 1]`;
- commutativity;
- associativity;
- t-norm identity `T(x, 1) = x`;
- s-norm identity `S(x, 0) = x`;
- both De Morgan laws under standard negation.
- directed difference equivalence to `T(mu_A(x), N(mu_B(x)))`;
- crisp compatibility, directionality, and explicit rejection of incompatible
  universes or missing policies.

The modern scalar policies are also checked against the protected historical
scalar functions on a deterministic reference grid. Equality and inclusion use
the separate fail-closed contract documented in
[Fuzzy-Set Equality and Inclusion](fuzzy-set-relations.md); operator reference
grids are not silently reused as comparison domains.

## References

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- E. P. Klement, R. Mesiar, and E. Pap, *Triangular Norms*, Springer, 2000.
  <https://doi.org/10.1007/978-94-015-9540-7>
