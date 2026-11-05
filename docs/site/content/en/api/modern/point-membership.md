<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Membership from explicit points

A calibration record gives membership grades at coordinates 10, 13, and 21.
Use a discrete table if those three grades are the entire model. Use
piecewise-linear membership if the application assigns grades between the
measurements along straight segments.

```python
from fuzzyroutines import ContinuousUniverse, ScalarFuzzySet
from fuzzyroutines.point_membership import (
    DiscreteMembershipTable,
    PiecewiseLinearMembership,
)

points = ((10, 0.25), (13, 0.75), (21, 0.5))
table = DiscreteMembershipTable(points)
curve = PiecewiseLinearMembership(points, boundary="zero")
discrete = ScalarFuzzySet(table.universe, table)
continuous = ScalarFuzzySet(ContinuousUniverse(), curve)

assert discrete.Membership(13) == continuous.Membership(13) == 0.75
assert continuous.Membership(11.5) == 0.5
assert continuous.Membership(17) == 0.625
assert continuous.Membership(22) == 0
```

At 17 the table has no grade: 17 is absent from its universe. The curve has
grade 0.625 because 17 is halfway between 13 and 21, whose grades are 0.75 and
0.5. The first interval is three units wide and the second is eight; each
segment uses its own width.

## API reference

`DiscreteMembershipTable(points)` accepts a nonempty tuple of
`(coordinate, grade)` tuples. The read-only `points` and `universe`
attributes expose the data and its `DiscreteUniverse`. The table validates
and stores every grade at construction, whereas `DiscreteUniverse` plus a
callback declares coordinates and delegates grade evaluation to that callback.
Calling the table at any undeclared coordinate raises `InvalidDomainError`.
There is no matching tolerance.

`PiecewiseLinearMembership(knots, boundary="error")` accepts at least two
pairs in the same tuple format. Its `knots` and `boundary` are read-only.
At each knot the original grade is returned. For adjacent knots
$(x_i,g_i)$ and $(x_{i+1},g_{i+1})$, let $t=(x-x_i)/(x_{i+1}-x_i)$.
At an interior coordinate $x$ the grade is $(1-t)g_i+tg_{i+1}$.
All-rational interpolation returns a `Fraction`; interpolation involving a
floating-point value returns a Python float.

Outside the closed knot interval:

- `"error"` raises `InvalidDomainError` (the default).
- `"zero"` returns 0. A nonzero endpoint grade creates a jump at that endpoint.
- `"clamp"` returns the nearest endpoint grade.

Interior jumps cannot be represented. In particular, repeating a coordinate
to encode a jump raises `InvalidDomainError`.

Both callables accept a single positional `MembershipScalar`. Coordinates
must be finite and strictly increasing in the supplied data; grades must
be finite in $[0,1]$. Booleans and other non-real values raise
`InvalidParameterTypeError`. Non-finite coordinates, non-finite or
out-of-range grades, and unknown boundary strings raise
`InvalidParameterError`. The inputs are neither sorted nor normalized.

The piecewise callable's boundary policy does not override the universe of
a containing `ScalarFuzzySet`. The scalar callable contract does not register
the curve for exact continuous properties or analytical centroid calculation.
See [ADR-0024](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/adr/0024-point-membership-contracts.md)
and the [analytical membership reference](membership.md).

::: fuzzyroutines.point_membership
    options:
      members:
        - DiscreteMembershipTable
        - PiecewiseLinearMembership
