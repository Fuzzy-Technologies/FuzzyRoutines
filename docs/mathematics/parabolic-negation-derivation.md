<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Analytical Derivation of the Legacy Parabolic Negation

- Status: Mathematical contract for Task #56
- Related ADR: [ADR-0004](../adr/0004-operator-and-negation-contracts.md)
- Historical callable: `FuzzyNOTParabolic(x, alpha, epsilon)`

## Scope and terminology

The legacy callable is defined by the implicit symmetric relation

```text
2*alpha - x - y = (2*alpha - 1) * (y - x)**2
```

This document derives its valid analytical branch. No source found in the
review establishes this exact equation as a named canonical family; therefore
the project must retain the historical name `FuzzyNOTParabolic` and must not
present it as a standard published “parabolic negation”.

The endpoint, antitonicity, and involution requirements follow the usual
strong-fuzzy-negation contract; see the formal treatment of fuzzy negations in
[Bedregal et al. (2017)](https://arxiv.org/abs/1707.08617).

## Derivation

Let `k = 2*alpha - 1` and `d = y - x`. The relation becomes

```text
k*d**2 + d + 2*(x - alpha) = 0
```

For `alpha != 1/2`, the branch that passes through the fixed point
`(alpha, alpha)` is

```text
D = 1 - 8*k*(x - alpha)
d = (-1 + sqrt(D)) / (2*k)
y = x + d
```

The numerically stable equivalent, which also gives the continuous limit at
`alpha = 1/2`, is

```text
y = x + 4*(alpha - x) / (1 + sqrt(D))
```

At `alpha = 1/2`, this reduces exactly to `y = 1 - x`.

## Valid parameter domain

The fixed-point branch has `N(0) = 1` only when `alpha >= 1/4`, and it has
`N(1) = 0` only when `alpha <= 3/4`. Over the closed interval

```text
alpha in [1/4, 3/4]
```

the discriminant is non-negative on `x in [0, 1]`; the selected branch is
continuous, decreases monotonically, fixes `alpha`, and is involutive. The
last property follows because the defining relation is symmetric in `x` and
`y`, while the selected branch is the unique valid output branch.

Outside that interval, the branch through the fixed point violates at least
one endpoint requirement. It is therefore not a strong fuzzy negation under
the project contract.

## Consequences

- The brute-force `epsilon` scan is mathematically unnecessary and must not
  survive Task #57.
- Task #57 must implement the stable closed form above with no scan loop.
- The parabolic family requires `alpha in [1/4, 3/4]`; this is distinct from
  the `0 < alpha < 1` domain of the separate piecewise-linear `FuzzyNOT`
  family.
- Task #58 must test endpoints, the fixed point, monotone decrease, involution,
  and the two out-of-domain regions.
