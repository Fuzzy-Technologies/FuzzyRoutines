<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0024: Discrete tables and piecewise-linear membership

- Status: Accepted on merge
- Date: 2026-11-05
- Task: [#399](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/399)
- Feature: [#362](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/362)
- Extends: [ADR-0002](0002-universe-support-semantics.md)

## Context

A finite collection of measured or assigned grades does not determine the
grades of any intermediate coordinates. `DiscreteUniverse` declares the
coordinates of a set, but it does not store or validate the grades supplied
by a callback. A model must explicitly choose whether its points define a
finite table or the knots of a continuous-domain function.

## Decision

The focused `fuzzyroutines.point_membership` module provides two immutable
scalar callables that implement `MembershipCallable` structurally:

- `DiscreteMembershipTable(points)` stores at least one coordinate-grade
  pair and exposes the corresponding `DiscreteUniverse` as `universe`.
  Lookup uses exact numeric equality. An absent coordinate, including one
  in a gap between stored points, raises `InvalidDomainError`.
- `PiecewiseLinearMembership(knots, boundary="error")` stores at least two
  coordinate-grade pairs. At each knot it returns the stored grade unchanged.
  Between adjacent knots $(x_i, g_i)$ and $(x_{i+1}, g_{i+1})$, it returns
  $(1-t)g_i+tg_{i+1}$ with $t=(x-x_i)/(x_{i+1}-x_i)$. Segment widths follow
  the supplied coordinates, so the grid need not be regular.

Both constructors take a tuple of two-item tuples. Coordinates and grades
must be finite non-boolean reals under the scalar validation policy; grades
must lie in $[0,1]$. Coordinates must be strictly increasing. Duplicates,
unsorted input, and malformed data are rejected at construction. Neither
constructor sorts coordinates, combines points, or normalizes grades.

The boundary policy applies strictly outside the closed knot interval:

- `"error"` (default) raises `InvalidDomainError`.
- `"zero"` returns zero on either side.
- `"clamp"` returns the nearest endpoint's grade.

Linear segments meet at their shared grade. Duplicate knots cannot encode an
interior jump or a vertical segment. Zero extension produces an endpoint
jump when that endpoint has a nonzero grade; clamp extension is continuous.
Non-finite inputs are invalid in all modes.

Interpolation uses integer ratios so that opposite extreme finite endpoints
do not overflow on subtraction and distinct rational knots do not collapse
to a single binary64 coordinate. All-rational interpolation yields a
`Fraction`. Otherwise the computed grade is rounded to a Python float.
Real implementations without an integer ratio use their float representation
for the interpolation; unresolved segment geometry raises
`InvalidDomainError`. Exact knot and table lookups preserve the stored
grade, including its numeric type.

## Consequences

- Use `ScalarFuzzySet(table.universe, table)` to compose a discrete set
  without writing a callback. The piecewise evaluator can be paired with a
  separately chosen `ContinuousUniverse`; the set validates its own
  universe before applying the evaluator's boundary policy.
- Existing analytical geometry discovery is unchanged. Piecewise functions
  participate as scalar callables without claiming exact continuous property
  or defuzzification support. Config, plotting and batch execution remain
  separate concerns.
- There is no change to the analytical families, compatibility facade, or
  historical Universal Fuzzy Scale.

The [point membership guide](../site/content/en/api/modern/point-membership.md) gives a
worked example and the public API contract.
