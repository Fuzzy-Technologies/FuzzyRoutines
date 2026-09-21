<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0009: Fuzzy-Set Convexity Semantics

- Status: Accepted
- Date: 2026-09-16
- Related planning task: #77
- Related Feature: #25
- Related tasks: #75, #76
- Supersedes: none

## Context

The classical term *convex fuzzy set* does not mean that its membership
function is a convex real-valued function. It means that the membership
function is quasiconcave: points between two coordinates cannot have a grade
below the smaller endpoint grade. Equivalently, every positive alpha-cut is a
convex crisp set.

FuzzyRoutines supports three materially different evidence scopes:

- analytical membership families on a `ContinuousUniverse`;
- exhaustive membership values on a finite ordered `DiscreteUniverse`;
- finite observations of a continuous membership function.

A single Boolean assembled from those scopes would be misleading. In
particular, no finite grid can prove the universal convexity inequality for an
otherwise arbitrary continuous callable. A callable can agree at every sampled
coordinate and contain an arbitrarily narrow valley between two of them.

## Decision

### Continuous scalar universe

Let `A` be a scalar fuzzy set with membership function `mu_A` on a
`ContinuousUniverse` `X`. Such a universe is a real interval and is therefore
convex, including when it is open or unbounded.

`A` is fuzzy-convex exactly when

```text
for every x, y in X and lambda in [0, 1]:
    mu_A(lambda*x + (1 - lambda)*y) >= min(mu_A(x), mu_A(y))
```

This is quasiconcavity of `mu_A`; it is not ordinary convexity of the
membership function.

The equivalent alpha-cut formulation uses the existing weak-cut contract:

```text
A_alpha = {x in X | mu_A(x) >= alpha}, 0 < alpha <= 1
```

`A` is fuzzy-convex if and only if every `A_alpha` is a convex crisp subset of
`X`. Empty cuts are convex. The zero cut is not part of the required family:
with weak-cut semantics it is all of `X` and contributes no information.

The equivalence does not require continuity. In the forward direction, the
membership inequality keeps every segment between two cut members inside the
same cut. In the reverse direction, choose
`alpha = min(mu_A(x), mu_A(y))`; when this value is zero, the required
inequality follows from the membership range `[0, 1]`.

### Discrete scalar universe

A finite `DiscreteUniverse` is not closed under real affine combinations.
Applying Euclidean set convexity directly would make almost every multi-point
cut non-convex because the undeclared coordinates between its points are not
members of the universe. That is not the library contract.

Convexity on a `DiscreteUniverse` is **order-convexity relative to the declared
coordinates**. For strictly increasing declared points
`x_0 < ... < x_(n-1)`, `A` is discrete-convex exactly when

```text
for every i <= j <= k:
    mu_A(x_j) >= min(mu_A(x_i), mu_A(x_k))
```

Equivalently, every positive weak alpha-cut is an order-convex subset: whenever
it contains two declared points, it contains every declared point between
them. Irregular coordinate spacing has no effect, and no interpolation between
declared points is implied.

Because every declared coordinate is evaluated, this result is exact for the
discrete representation. It is not evidence about any continuous function
that a caller might later interpolate through those values.

### Continuous analytical certification

An exact continuous result requires a representation-specific mathematical
certificate. The accepted `MFunction` families have such a certificate because
their validated formulas are monotone or increase to one maximum region and
then decrease:

| Canonical family | Exact certification basis                  |
| ---------------- | ------------------------------------------ |
| `Hyperbolic`     | constant, then monotonically decreasing    |
| `Bell`           | increasing, plateau, then decreasing       |
| `Parabolic`      | monotonically increasing S-shoulder        |
| `Triangle`       | increasing, one apex, then decreasing      |
| `Trapezium`      | increasing, plateau, then decreasing       |
| `Exponential`    | increasing to its centre, then decreasing  |
| `Sigmoidal`      | monotone, with direction fixed by `a`      |
| `Desirability`   | monotonically increasing                   |

Their registry aliases inherit the canonical family certificate. Restricting
one of these functions to any declared continuous interval preserves
quasiconcavity. The certificate is based on the validated formula and parameter
contract, not on sampling the formula.

An arbitrary `ScalarFuzzySet` callable, an unknown future family, or a composed
set without a proved closure rule has no exact certificate merely because it
can be evaluated. Its exact continuous convexity status is unknown until an
analytical certificate or a counterexample is available.

### Evidence states

A future convexity query must preserve its evidence strength. Its result model
must distinguish at least these semantic states, even if the eventual public
names differ:

| State                  | Meaning                                                         |
| ---------------------- | --------------------------------------------------------------- |
| `PROVEN_CONVEX`        | Universal property established for the declared representation  |
| `COUNTEREXAMPLE`       | Explicit coordinates and grades violate the defining inequality |
| `NO_SAMPLED_VIOLATION` | Finite observations contain no detected violation               |
| `UNKNOWN`              | Neither a certificate nor a counterexample is available         |

`PROVEN_CONVEX` is available for certified analytical families and exact
discrete evaluation. `COUNTEREXAMPLE` must carry reproducible witness
coordinates `x < z < y` and their grades; `z` is the convex combination with
`lambda = (y - z) / (y - x)`. `NO_SAMPLED_VIOLATION` must record the analysis
domain, coordinates or generation policy, resolution, and comparison policy.
It must never be exposed as `isConvex = True`, a proof, a confidence
percentage, or an exact alpha-cut claim.

A strict inequality observed from authoritative membership results is a
counterexample to that evaluated representation. When the results approximate
a different ideal real-valued formula, the numerical error policy limits what
can be claimed about the ideal formula. Exact certification has no implicit
tolerance; a future tolerance mode requires a separate explicit numerical
contract.

### Boundary conventions

- Membership grades are in `[0, 1]`; no extrapolation outside the declared
  universe participates in convexity.
- Weak alpha-cuts include coordinates whose grade equals `alpha`.
- `alpha = 1` is valid and yields the core; empty and singleton cuts are
  convex.
- Open, closed, and unbounded universe endpoints are inherited exactly. Fuzzy
  convexity alone does not make an alpha-cut closed.
- The empty fuzzy set is convex. Normality, height, upper semicontinuity,
  support boundedness, and non-emptiness are independent properties.
- A finite integration or sampling domain never replaces an unbounded
  universe and cannot establish global convexity.

## Consequences

- Task #77 is design-only and introduces no public convexity API.
- Task #75 can represent weak alpha-cuts without adding a special convexity
  convention.
- Exact discrete implementation can evaluate all declared grades and compare a
  linear-time unimodality check with an exhaustive triple-condition oracle.
- Exact analytical implementation must dispatch only through an audited family
  certificate or a separately proved closure rule.
- Arbitrary continuous callables fail closed to `UNKNOWN`; optional sampling
  returns only bounded evidence.
- Euclidean convexity and discrete order-convexity must be named distinctly in
  reports and documentation.

## Executable evidence required by future implementation

The implementation PR must include:

- exact continuous cases for every certified family, aliases, valid parameter
  boundaries, restricted universes, and open or unbounded endpoints;
- a failure-closed case proving that an arbitrary callable cannot receive an
  analytical certificate;
- exhaustive discrete comparisons against the defining triple inequality,
  including the empty fuzzy set, singleton universes, monotone sequences,
  maximum plateaus, irregular spacing, and interior valleys;
- equivalence checks between the discrete triple condition and order-convex
  cuts at every distinct positive membership level;
- deterministic counterexample witnesses;
- a continuous function with a narrow off-grid valley that passes a finite
  grid, proving that the result remains `NO_SAMPLED_VIOLATION` rather than
  `PROVEN_CONVEX`;
- provenance and boundary tests for any sampled report.

Finite grids and finitely many selected alpha values are regression evidence
for code paths, not mathematical proof of an arbitrary continuous callable.

## References

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- S. Boyd and L. Vandenberghe, *Convex Optimization*, Cambridge University
  Press, 2004, section 3.4. <https://doi.org/10.1017/CBO9780511804441>
- G. J. Klir and B. Yuan, *Fuzzy Sets and Fuzzy Logic: Theory and
  Applications*, Prentice Hall, 1995, ISBN 978-0-13-101171-7.

## Acceptance and supersession

This ADR is **Accepted**. A change to the defining inequalities, alpha-cut
equivalence, discrete order-convexity, or evidence-strength boundary requires
an amendment or a new ADR.
