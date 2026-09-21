<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Fuzzy-Set Convexity

- Status: Design contract for Task #77
- Decision: ADR-0009
- Scope: one-dimensional scalar fuzzy sets
- Public API: not implemented

## Meaning of convexity

For a fuzzy set `A` over a real interval `X`, FuzzyRoutines uses Zadeh's
convexity condition:

```text
mu_A(lambda*x + (1 - lambda)*y) >= min(mu_A(x), mu_A(y))
```

for every `x, y` in `X` and every `lambda` in `[0, 1]`.

The graph of `mu_A` does not need to be a convex function. The condition says
that `mu_A` is quasiconcave: along an interval it can rise, possibly remain
level, and fall, but it cannot contain a valley between two higher grades.
Monotone membership functions are therefore fuzzy-convex too.

Fuzzy convexity does not imply normality. A subnormal hill, a monotone
shoulder, and the empty fuzzy set can all be convex.

## Alpha-cut equivalence

The weak alpha-cut is

```text
A_alpha = {x in X | mu_A(x) >= alpha}, 0 < alpha <= 1.
```

The following statements are equivalent on a continuous scalar universe:

1. `A` satisfies the membership inequality for every pair and every convex
   combination.
2. Every positive weak alpha-cut is a convex crisp subset of `X`.

The proof is short and defines the implementation contract. If two coordinates
are in `A_alpha`, both grades are at least `alpha`; the membership inequality
puts every coordinate between them in the same cut. Conversely, set
`alpha = min(mu_A(x), mu_A(y))`. A positive `alpha` invokes cut convexity, and
`alpha = 0` is already covered by the membership range.

This equivalence uses all positive levels, not a convenient finite selection.
For a finite discrete universe it is sufficient to inspect its distinct
positive membership grades because the cuts change only at those levels. For
an arbitrary continuous callable, checking finitely many levels is not a
proof.

## Continuous representation

`ContinuousUniverse` is always a real interval, so the affine coordinate in
the defining inequality remains inside the universe. Only coordinates that
belong to the declared interval participate. An excluded endpoint, infinity,
or a point outside the universe is never evaluated by implication.

The accepted analytical `MFunction` families are exactly certifiable from
their formulas:

| Family          | Shape proving quasiconcavity                 |
| --------------- | -------------------------------------------- |
| Hyperbolic      | constant then decreasing                     |
| Bell            | increasing then constant then decreasing     |
| Parabolic       | increasing shoulder                          |
| Triangle        | increasing then decreasing                   |
| Trapezium       | increasing then constant then decreasing     |
| Exponential     | increasing then decreasing around its centre |
| Sigmoidal       | monotone                                     |
| Desirability    | monotone                                     |

Parameter validation is part of each proof obligation. Registry aliases do not
create new mathematics; they use the canonical family's certificate. Clipping
a certified family to a bounded, open, closed, or half-bounded interval
preserves convexity.

An arbitrary Python membership callable is different. Any algorithm making a
finite number of evaluations can be given a second callable that returns the
same grades at those coordinates but has a narrow lower valley elsewhere.
Consequently, finite evaluation can find a counterexample but cannot certify
global convexity. Such a representation needs an analytical certificate,
symbolic structure, or a proved construction rule before an exact positive
result is possible.

## Discrete representation

Let a discrete universe declare

```text
x_0 < x_1 < ... < x_(n-1).
```

Its exact relative-order condition is

```text
mu_A(x_j) >= min(mu_A(x_i), mu_A(x_k)) for every i <= j <= k.
```

Every weak alpha-cut must therefore be one contiguous block of declared
coordinates, or be empty. This is order-convexity. It deliberately does not
claim that a finite set of coordinates contains every real point on a line
segment.

For example, with `X = {0, 2, 10}`:

- a cut containing `{0, 2}` is order-convex;
- a cut containing `{0, 10}` but not `2` is not order-convex;
- the gaps `(0, 2)` and `(2, 10)` have no membership semantics unless an
  explicit interpolation policy constructs a new continuous fuzzy set.

The check is exact because all declared coordinates are evaluated. A
production implementation may use the equivalent unimodal-sequence rule:
grades are nondecreasing through a maximum region and nonincreasing after it.
Tests should retain the direct triple inequality as an independent oracle.

## Sampled continuous evidence

Sampling a continuous membership function produces evidence with a declared
domain and resolution. It does not change the universe or the representation.

A report may say:

```text
COUNTEREXAMPLE
    sampled coordinates exhibit a strict valley

NO_SAMPLED_VIOLATION
    no tested coordinate triple exhibits a strict valley
```

It must not translate the second outcome into `convex`, `approximately
convex`, a confidence percentage, or a global alpha-cut result. Without an
additional regularity bound, a denser grid only adds observations; it does not
close the universal proof obligation.

When sampled membership results are the authoritative runtime values, a strict
valley is a counterexample to that evaluated callable. If those values are
floating-point approximations to a separate ideal formula, the formula-level
claim is limited by the declared numerical error policy. No implicit epsilon
is part of exact convexity.

## Cut and endpoint conventions

- Alpha-cuts are weak: grade equality includes the coordinate.
- Positive levels are `0 < alpha <= 1`; the level `1` cut is the core.
- A weak zero cut is the complete universe and is redundant for convexity.
- Empty and singleton cuts are convex.
- Cut endpoints may be open because the universe excludes an endpoint or the
  membership function is discontinuous. Convexity does not imply closedness or
  upper semicontinuity.
- Positive support uses the separate strict condition `mu_A(x) > 0`.
- An integration domain is an operational numerical interval and never limits
  a global convexity claim.

## Future executable test matrix

| Representation | Exact positive result                       | Negative result                   | Required guard                                      |
| -------------- | ------------------------------------------- | --------------------------------- | --------------------------------------------------- |
| Analytical     | audited family certificate                  | explicit analytical witness       | unknown families remain unknown                     |
| Discrete       | exhaustive declared-coordinate evaluation   | violating declared triple         | no interpolation claim                              |
| Sampled        | never from samples alone                    | sampled violating triple          | pass means only `NO_SAMPLED_VIOLATION`              |
| Callable       | only a separate certificate or closure rule | explicit evaluated counterexample | finite queries never return `PROVEN_CONVEX`         |

The future implementation suite should:

1. cover every canonical analytical family and alias at parameter boundaries;
2. compare the optimized discrete algorithm with exhaustive triples for all
   short grade sequences over a small exact grade alphabet;
3. compare discrete results with cuts at every distinct positive grade;
4. verify deterministic witness coordinates and grades;
5. exercise open, closed, bounded, and unbounded continuous universes;
6. include a narrow off-grid valley that defeats a coarse and a refined grid;
7. verify that sampled provenance survives serialization and display;
8. reject any conversion from `NO_SAMPLED_VIOLATION` to a proven Boolean.

## Non-goals

This contract does not define multidimensional universes, interpolation,
strict fuzzy convexity, convexity degree, approximate/tolerance convexity, or
closure laws for every t-norm and s-norm. Each changes the mathematical or
evidence contract and requires separate design work.

## References

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- S. Boyd and L. Vandenberghe, *Convex Optimization*, Cambridge University
  Press, 2004, section 3.4. <https://doi.org/10.1017/CBO9780511804441>
- G. J. Klir and B. Yuan, *Fuzzy Sets and Fuzzy Logic: Theory and
  Applications*, Prentice Hall, 1995, ISBN 978-0-13-101171-7.
