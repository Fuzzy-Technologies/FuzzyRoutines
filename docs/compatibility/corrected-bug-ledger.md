# Corrected-Bug Compatibility Ledger

- Status: Active ledger for Task #98
- Related Feature: [Build compatibility regression and migration suite](../../issues/31)
- Related ADRs: [ADR-0001](../adr/0001-backward-compatibility-contract.md),
  [ADR-0003](../adr/0003-membership-function-contracts.md),
  [ADR-0004](../adr/0004-operator-and-negation-contracts.md), and
  [ADR-0005](../adr/0005-numerical-defuzzification-policy.md)

## Purpose

FuzzyRoutines v2 preserves historical public names and parameter order where
they remain meaningful, but it does not preserve behaviour known to be
mathematically or logically incorrect. This ledger makes every deliberate
incompatibility explicit before a release claims compatibility.

A row may be marked **Corrected** only after its implementation PR is merged,
its linked correctness tests pass, and its migration impact is stated. A
planned correction is not a compatibility promise and must not be represented
as one.

## Current corrected behaviours

- **Parametric negation endpoint:** `FuzzyNOT` now rejects non-finite values,
  booleans, and every `alpha` outside the open interval `(0, 1)`. The public
  name is unchanged. Evidence: Task #55 and
  [PR #186](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/186).
- **Variadic operator validation:** `TNormCompose` and `SCoNormCompose` now
  validate every operand and reject unknown operator families consistently.
  Their historical `None` failure sentinel remains until the explicit error
  model is implemented. Evidence: Task #61 and
  [PR #190](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/190).
- **Defuzzification cache:** `FuzzySet.Defuz()` and `defuzValue` now calculate
  from current membership parameters and the current integration interval
  instead of exposing a construction-time value. Evidence: Task #66 and
  [PR #188](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/188).

## Tracked correction candidates

- **Parabolic negation scan:** `FuzzyNOTParabolic` still searches with a
  caller-controlled epsilon and can fail to terminate for `epsilon=0`. Task
  #57 must replace the scan with the
  [documented closed-form branch](../mathematics/parabolic-negation-derivation.md).


## Record format for each merged correction

Every future **Corrected** row must include:

1. the exact historical behaviour and why it is incorrect;
2. the new v2 contract;
3. the merged implementation PR and linked Task;
4. the correctness and compatibility-test locations;
5. user-visible migration impact and any available safe alternative.

No release note may rely on an unlisted bug-compatible behaviour.
