<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0002: Universe, Integration Domain, and Mathematical Support

- Status: Accepted on merge
- Date: 2026-09-16
- Related planning task: #9
- Related Feature: #23
- Related mapping task: #67

## Context

A fuzzy set is defined relative to a universe of discourse, but the historical
`FuzzySet` class stores only a tuple named `supportSet`. The implementation uses
that tuple as the finite interval for centroid integration. It does not prove or
store the mathematical support of the membership function.

Those concepts coincide for some bounded membership functions only when a
caller deliberately chooses the same interval. They do not coincide in
general. A Gaussian is positive on the real line, and a shoulder may have an
unbounded core, while every numerical integration performed by the legacy code
uses a finite tuple.

The modern model needs unambiguous terms before it can implement fuzzy-set
algebra, alpha-cuts, derived properties, or new defuzzification methods.

## Decision

### Fuzzy-set identity

A scalar fuzzy set `A` is defined by:

```text
A = (X, mu_A)
mu_A: X -> [0, 1]
```

`X` is the universe of discourse. It is part of the set's mathematical
identity, not a plotting range or an integration hint. The focused v2 API will
require an explicit universe. The legacy facade may adapt its scalar membership
functions to the real line because their accepted contracts take finite real
coordinates.

### Universe

The initial modern implementation supports one-dimensional scalar universes.
It must not introduce a premature multidimensional framework.

A universe may be continuous or discrete:

- a continuous universe is an explicitly bounded or unbounded real interval,
  including its endpoint-closure policy;
- a discrete universe is an explicit finite ordered collection of distinct
  finite real coordinates.

The representation kind is never inferred from an arbitrary iterable or a
sampling resolution.

### Numerical integration domain

An integration domain is an operational input to a numerical method. For the
initial continuous implementation it is a finite closed interval `[left,
right]` with finite real endpoints and `left < right`.

An integration domain must lie within the universe. It is not part of the
mathematical definition of support, core, boundary, or height. A bounded
continuous universe may be used as the default integration domain. An unbounded
universe requires either:

- an explicit finite integration domain; or
- an analytical method with a documented convergence result.

The implementation must not silently truncate an unbounded set, infer a window
from floating-point underflow, or relabel a numerical window as support.

### Derived mathematical sets

For `x` in `X`, the canonical definitions are:

```text
positiveSupport(A) = {x in X | mu_A(x) > 0}
supportClosure(A)  = closure_X(positiveSupport(A))
core(A)            = {x in X | mu_A(x) = 1}
boundary(A)        = {x in X | 0 < mu_A(x) < 1}
height(A)          = sup({mu_A(x) | x in X})
alphaCut(A, alpha) = {x in X | mu_A(x) >= alpha}, 0 < alpha <= 1
```

The public word `support` is otherwise ambiguous because fuzzy-set literature
often means the positive set while topology commonly means its closure. The
modern API and documentation must use `positiveSupport` and `supportClosure`
when the distinction matters.

`core` deliberately means full membership. A non-normal set may have a
non-empty set of maximizers but an empty core. A future `maximumSet` or
`argmaxSet` is a separate concept and must not redefine `core`.

### Exact and approximate knowledge

Exact derived regions come from the declared membership-family geometry, not
from scanning floating-point evaluations. In particular, Gaussian
floating-point underflow to zero does not make its mathematical support
bounded.

When exact geometry is unavailable, a sampled query must return an explicitly
approximate result carrying its analysis domain and numerical policy. It must
not populate an exact-support property with a sampled estimate.

Continuous and sampled fuzzy sets therefore have distinct evidence:

- analytical continuous families may expose exact regions and exact boundary
  points;
- sampled sets derive properties only on their declared discrete universe;
- interpolation, if later supported, is an explicit policy and creates a
  continuous representation rather than silently changing the sampled set.

### Empty and zero-area semantics

The empty fuzzy set is valid: `mu_A(x) = 0` for every `x` in `X`. Its positive
support, support closure, core, boundary, and every positive alpha-cut are
empty; its height is zero.

Zero continuous area is not the same as an empty fuzzy set. A singleton can
have height one and non-empty support while its integral is zero. Continuous
centroid defuzzification is undefined whenever the denominator integral over
the selected integration domain is zero or non-finite, as required by
ADR-0005. A discrete weighted centroid follows its separately declared finite
sum and is undefined when the sum of weights is zero.

### Legacy `supportSet` mapping

The historical name remains available only through the compatibility facade.
Its exact mapping is:

```text
legacy supportSet <-> integrationDomain
```

The getter returns the configured interval. The setter changes the interval
used by legacy numerical operations. It does not mutate the membership
function, the modern universe, or any mathematical-support result.

Legacy construction and serialization must preserve the two endpoint values
without silently reinterpreting them as exact support. The modern serialized
model uses explicit `universe` and `integrationDomain` fields; mathematical
support is derived and is not accepted as a substitute for either field.

## Examples

### Bounded triangle

For a triangle with feet at `0` and `2` and apex at `1` on the real line:

```text
positiveSupport = (0, 2)
supportClosure  = [0, 2]
core            = {1}
boundary        = (0, 1) union (1, 2)
height          = 1
```

An integration domain of `[-1, 3]` remains valid and distinct from all of
those regions.

### Increasing shoulder

For an increasing S-shoulder that is zero through `a`, transitions on `(a,
b)`, and equals one from `b` onward:

```text
positiveSupport = (a, +infinity)
core            = [b, +infinity)
boundary        = (a, b)
```

Centroid evaluation still requires a finite integration domain. No finite
legacy `supportSet` can be the mathematical support of this set.

### Gaussian

An exact Gaussian is positive for every finite real coordinate. Its positive
support and support closure are the real line even though a floating-point
evaluation may underflow to zero far from the centre.

## Consequences

- Task #68 implements the minimal explicit scalar universe/domain types.
- Task #69 implements support, closure, core, boundary, and height without
  presenting sampled estimates as exact results.
- Task #70 proves that `supportSet` remains a compatibility alias for the
  integration domain.
- Tasks #79 and #80 consume an explicit integration domain and preserve the
  zero-area contract.
- Fuzzy-set operations must reject or explicitly reconcile incompatible
  universes; they cannot combine coordinates solely because membership values
  can be evaluated there.

## References

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- D. Dubois and H. Prade, *Fuzzy Sets and Systems: Theory and Applications*,
  Academic Press, 1980, ISBN 978-0-12-222750-9.
- H.-J. Zimmermann, *Fuzzy Set Theory—and Its Applications*, 4th ed.,
  Springer, 2001. <https://doi.org/10.1007/978-94-010-0646-0>

## Acceptance and supersession

This ADR is accepted when its pull request is reviewed and merged. Any change
to the meaning of universe, integration domain, positive support, support
closure, core, boundary, height, or the legacy `supportSet` mapping requires an
amendment or a superseding ADR.
