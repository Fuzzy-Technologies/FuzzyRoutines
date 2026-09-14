# ADR-0004: Fuzzy Operator Families, Negation Domains, and Strict Validation

- Status: Accepted on merge
- Date: 2026-09-14
- Related planning task: #11
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

| Family | T-norm | SCo-norm |
|---|---|---|
| `logic` | `min(x, y)` | `max(x, y)` |
| `algebraic` | `xy` | `x + y - xy` |
| `boundary` | `max(x + y - 1, 0)` | `min(x + y, 1)` |
| `drastic` | `y` if `x=1`; `x` if `y=1`; otherwise `0` | `y` if `x=0`; `x` if `y=0`; otherwise `1` |

Unknown family names are invalid. Variadic composition requires at least two
operands and validates every operand before evaluation.

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
