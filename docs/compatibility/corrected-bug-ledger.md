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

No runtime defect correction has been merged into the v2 implementation yet.
The completed contract and evidence work defines what future implementation
tasks must change; it does not itself alter public runtime behaviour.

## Tracked correction candidates

| Behaviour                    | Legacy observation                                                                                          | Required v2 behaviour                                            | Evidence / implementation                                                           | Status  |
|------------------------------|-------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|-------------------------------------------------------------------------------------|---------|
| Parametric negation endpoint | `FuzzyNOT(x, alpha=1)` returns a degenerate non-involutive result.                                          | Reject `alpha=1`; the strong-negation domain is `0 < alpha < 1`. | [ADR-0004](../adr/0004-operator-and-negation-contracts.md), Task #55                | Planned |
| Parabolic negation scan      | `FuzzyNOTParabolic` searches with a caller-controlled epsilon and can fail to terminate for `epsilon=0`.    | Use the documented closed-form valid branch; no epsilon scan.    | [derivation](../mathematics/parabolic-negation-derivation.md), Task #57             | Planned |
| Variadic operator validation | One-element composition can bypass fuzzy-domain validation and unknown names do not fail deterministically. | Validate every operand and reject unknown families.              | [ADR-0004](../adr/0004-operator-and-negation-contracts.md), Task #61                | Planned |
| Defuzzification cache        | `FuzzySet.Defuz()` returns a construction-time cached centroid after membership mutation.                   | Return a result derived from the current state.                  | [strict regression](../../tests/test_stale_defuzzification_regression.py), Task #66 | Planned |


## Record format for each merged correction

Every future **Corrected** row must include:

1. the exact historical behaviour and why it is incorrect;
2. the new v2 contract;
3. the merged implementation PR and linked Task;
4. the correctness and compatibility-test locations;
5. user-visible migration impact and any available safe alternative.

No release note may rely on an unlisted bug-compatible behaviour.
