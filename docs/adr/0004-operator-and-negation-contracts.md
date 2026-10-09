<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0004: Fuzzy Operator Families, Negation Domains, and Strict Validation

- Status: Accepted on merge
- Date: 2026-09-14
- Related planning task: #11
- Related amendment task: [#281](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/281)
- Related Features: #19 and #20

## Context

The legacy library implements familiar t-norm and s-norm families, but its
input validation is inconsistent. In particular, `FuzzyNOT(alpha=1)` produces
a degenerate result rather than a valid fuzzy negation, and
`FuzzyNOTParabolic` performs an epsilon-driven brute-force scan.

## Decision

### Truth-value domain

All public fuzzy truth values accepted by operators are finite real numbers in
the closed interval `[0, 1]`. Booleans, NaN, infinities, and values outside
that interval are invalid.

Implementations must reject invalid values explicitly. They must not clamp,
coerce, print-and-continue, or return a plausible fuzzy value for invalid
input.

### Supported binary families

The supported historical names and formulas are:

| Family      | T-norm                                    | SCo-norm                                  |
|-------------|-------------------------------------------|-------------------------------------------|
| `logic`     | `min(x, y)`                               | `max(x, y)`                               |
| `algebraic` | `xy`                                      | `x + y - xy`                              |
| `boundary`  | `max(x + y - 1, 0)`                       | `min(x + y, 1)`                           |
| `drastic`   | `y` if `x=1`; `x` if `y=1`; otherwise `0` | `y` if `x=0`; `x` if `y=0`; otherwise `1` |

Unknown family names are invalid. Variadic composition requires at least one
operand and validates every operand and the selected family before evaluation.
Composition of one valid degree is the identity: `TNormCompose(x)` and
`SCoNormCompose(x)` return `x` for every supported family. Two or more operands
use the left-associated fold of the selected binary formula. Empty input is
invalid.

### Parametric negation

`FuzzyNOT(x, alpha)` is the historical parametric family with fixed point
`alpha`. Its valid domain is:

```text
x in [0, 1]
alpha in (0, 1)
```

The endpoints `alpha=0` and `alpha=1` are not valid members of this family.
Rejecting `alpha=1` is a compatible defect correction: the legacy result is
not an involutive fuzzy negation.

### Parabolic negation

The historical parabolic relation is a separate family from `FuzzyNOT`:

```text
2*alpha - x - y = (2*alpha - 1) * (y - x)^2
```

The branch satisfying the negation boundary conditions exists exactly for:

```text
x in [0, 1]
alpha in [1/4, 3/4]
```

For that domain, the implementation must use the analytical branch documented
in [the derivation](../mathematics/parabolic-negation-derivation.md). It must
satisfy all of:

- output `y` is in `[0, 1]`;
- `N(0)=1`, `N(1)=0`, and `N(alpha)=alpha`;
- continuity and monotone decrease on `[0, 1]`;
- involution within the numerical tolerance defined by ADR-0005.

An epsilon step size is not part of the formula or its bounded analytical
solution. Task #56 owns the derivation and documentation; Task #57 owns the
replacement; Task #58 owns its regression tests.

## Consequences

- Tasks #55–#58 implement and test negation under this contract.
- Tasks #59–#61 implement the operator invariant suite and composition
  validation.
- Existing historical identifiers stay available; no new family name is
  introduced by this decision.

## Acceptance and supersession

This ADR is **Accepted**. A new operator family or a change to the truth-value
domain requires an amendment or a new ADR.

### Amendment: historical unary composition identity — 2026-10-05

Task #281 records this amendment; it becomes accepted with the implementing
PR's human review and merge.

The original text required at least two operands. The project audit found that
this contradicted the established valid historical call contract and the
implemented migration boundary. Both composition functions at the immutable
[1.0.3 source revision](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/ceb9403d44c19ba73fd351e1b05091d337280864/fuzzyroutines/FuzzyRoutines.py)
accept one degree and return it unchanged; strict validation subsequently
rejected empty input, invalid degrees, and unknown families without removing
valid unary calls.

This amendment adopts the nonempty fold convention and its unary identity to
align the ADR with [ADR-0001's compatibility policy](0001-backward-compatibility-contract.md),
the [migration notes](../migration/1.0.3-to-2.0.0.md), and existing behavior.
It changes no binary formula, truth-value domain, public signature, or runtime
implementation. The
[composition tests](../../tests/test_composition_validation.py) cover unary
identity across every accepted family, invalid unary/later operands, and
unknown families. The
[finite-input tests](../../tests/test_finite_number_policy.py) cover rejection
of empty composition.
