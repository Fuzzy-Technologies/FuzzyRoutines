<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Fuzzy-Set Height and Normalization

- Status: Executable contract for Task #76
- Related Feature: #25
- Related ADR: [ADR-0002](../adr/0002-universe-support-semantics.md)
- Public module: `fuzzyroutines.fuzzysets`

## Mathematical contract

For a scalar fuzzy set `A = (X, mu_A)`, height and normality are

```text
height(A)   = sup({mu_A(x) | x in X})
isNormal(A) = height(A) = 1
```

When `height(A) > 0`, normalization constructs a new set on the same universe:

```text
mu_Normalize(A)(x) = mu_A(x) / height(A)
```

The result has exact height one because the supremum is scaled by the positive
constant `1 / height(A)`. Height zero makes this quotient undefined;
`Normalize` raises `ValueError` instead of returning the empty set unchanged or
inventing a unit grade.

## Exactness boundary

`Height` follows the existing property contracts instead of implementing a
second collection of membership-family formulas:

- a `DiscreteUniverse` is finite and is evaluated exhaustively at every
  declared coordinate;
- a `ContinuousUniverse` is supported when the set uses a modern analytical
  `MembershipFunction` or a supported historical `MFunction` evaluator;
  height then comes from
  `DeriveProperties` and its exact family geometry;
- a normalized result retains internal exact height-one evidence;
- an arbitrary continuous callable is rejected because its global supremum
  cannot be proved from finite evaluations.

`SampleProperties(...).heightEstimate` remains an approximate observation on
one finite `IntegrationDomain`. It is deliberately not accepted as exact
normalization evidence. Increasing a sample count can improve an estimate but
cannot prove the supremum of a general continuous function, especially on an
unbounded universe.

## Precision

`Height` returns the exact contract value in the scalar numeric representation.
`IsNormal(fuzzySet, tolerance=1e-12)` compares that value to one with
zero relative tolerance and the caller-visible absolute tolerance. Boolean,
negative, and non-finite tolerances are rejected. Tolerance affects only the
normality predicate; it never turns a small positive height into zero and never
changes the normalization divisor.

The membership evaluator still validates every returned grade in `[0, 1]`.
Normalization does not clamp floating-point overshoot. Generic custom
continuous functions are rejected; supported analytical and discrete
definitions are snapshotted instead of retaining mutable source semantics.

## Immutability and evaluation scope

`Normalize` always returns a distinct frozen `ScalarFuzzySet` and never edits
the source. For a discrete universe, source grades are evaluated once in
universe order and the normalized result uses that exhaustive immutable
snapshot. For a continuous analytical source, the canonical family identifier
and an immutable parameter tuple are captured at normalization time. Lazy
evaluation uses the shared analytical formula core with that frozen
snapshot and scales it by the exact derived height. Later mutation of the
source `MFunction.parameters` therefore cannot invalidate the normalized
result's height-one evidence.

Normality uses a supremum, not the existence of a core point. A continuous set
may therefore be normal even when no finite coordinate attains membership one.

## Example

```python
from fuzzyroutines import (
    ContinuousUniverse,
    Height,
    IsNormal,
    Normalize,
    ScalarFuzzySet,
)
from fuzzyroutines.FuzzyRoutines import MFunction

membershipFunction = MFunction("logistic", a=2.0, b=0.0)
universe = ContinuousUniverse(-1.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, membershipFunction.mju)

assert Height(fuzzySet) < 1.0
normalizedSet = Normalize(fuzzySet)
assert IsNormal(normalizedSet)
assert normalizedSet.universe == fuzzySet.universe
```

## References

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- G. J. Klir and B. Yuan, *Fuzzy Sets and Fuzzy Logic: Theory and
  Applications*, Prentice Hall, 1995, ISBN 978-0-13-101171-7.
  <https://books.google.com/books?id=AOhQAAAAMAAJ>
