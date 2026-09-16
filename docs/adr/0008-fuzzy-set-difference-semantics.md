# ADR-0008: Directed Fuzzy-Set Difference Semantics

- Status: Accepted on merge
- Date: 2026-09-16
- Related planning task: #74
- Related Feature: #24
- Supersedes: none

## Context

Classical set difference is defined as intersection with the complement of the
right operand. A fuzzy-set analogue is not unique until both the fuzzy
intersection and fuzzy negation are selected. Choosing either operation
implicitly would contradict the explicit operator-policy boundary established
by ADR-0004.

Symmetric difference has an additional ambiguity. A composition such as the
union of both directed differences also needs an s-norm and does not preserve
all classical symmetric-difference laws for arbitrary fuzzy operator families.
In particular, a generic composition cannot promise that the symmetric
difference of a fuzzy set with itself is empty.

## Decision

The modern API defines only directed difference in this decision:

```text
mu_Difference(A, B)(x) = T(mu_A(x), N(mu_B(x)))
```

`Difference(leftSet, rightSet, tNormPolicy, negationPolicy)` therefore requires:

- two `ScalarFuzzySet` operands over exactly equal universes;
- one explicit `TNormPolicy`;
- one explicit `NegationPolicy`;
- no default, process-wide, or inferred operator family.

The operation returns a new immutable `ScalarFuzzySet` over the left operand's
universe and does not mutate either input. It is directional: exchanging the
operands can change the result.

With standard negation and the logic t-norm, crisp membership grades recover
classical set difference. For non-crisp grades, the selected fuzzy operators
remain authoritative. The API does not claim that `Difference(A, A)` is empty
or that arbitrary classical identities hold.

Python subtraction syntax is not overloaded. A named operation keeps the
operator policies visible at every call site.

## Symmetric difference boundary

No public symmetric-difference operation is introduced by this ADR. A future
operation requires a separate decision that specifies:

- its complete composition and required negation, t-norm, and s-norm policies;
- the algebraic laws promised by the selected family combination;
- whether alternative definitions need distinct public names.

## Consequences

- Task #74 can implement directed difference without inventing a hidden global
  operator policy.
- Executable tests must cover the defining composition, crisp compatibility,
  directionality, universe mismatch, policy validation, and the absence of a
  classical self-difference guarantee for general fuzzy grades.
- Symmetric difference remains roadmap work rather than an undocumented
  convenience composition.

## Acceptance and supersession

This ADR becomes **Accepted** when the implementation PR is merged. Changing
the formula, adding implicit defaults, or exposing symmetric difference
requires an amendment or a new ADR.
