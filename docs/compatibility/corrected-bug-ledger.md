<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Corrected-Bug Compatibility Ledger

- Status: Active ledger for Task #98
- Related Feature: [Build compatibility regression and migration suite](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/31)
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
  Tests: [`test_negation_invariants.py`](../../tests/test_negation_invariants.py).
  Migration: replace invalid endpoint parameters with a value in `(0, 1)`;
  old endpoint outputs are not a valid negation contract.
- **Variadic operator validation:** `TNormCompose` and `SCoNormCompose` now
  validate every operand and reject empty input, invalid operands, and unknown
  operator families with `ValueError`. Evidence: Task #61,
  [PR #190](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/190), and
  the completed error-model implementation in
  [PR #194](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/194).
  Tests: [`test_composition_validation.py`](../../tests/test_composition_validation.py)
  and [`test_finite_number_policy.py`](../../tests/test_finite_number_policy.py).
  Migration: supply a nonempty validated operand sequence and known family;
  do not rely on an early fold result to hide an invalid later operand.
- **Defuzzification cache:** `FuzzySet.Defuz()` and `defuzValue` now calculate
  from current membership parameters and the current integration interval
  instead of exposing a construction-time value. Evidence: Task #66 and
  [PR #188](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/188).
  Tests: [`test_stale_defuzzification_regression.py`](../../tests/test_stale_defuzzification_regression.py).
  Migration: assertions must reflect current parameters and bounds; snapshot
  a result explicitly if the application needs the previous value.
- **Parabolic negation scan:** `FuzzyNOTParabolic` now evaluates the documented
  analytical branch over `alpha in [1/4, 3/4]`; the compatibility-only
  `epsilon` argument no longer controls execution. Evidence: Task #57 and
  [PR #192](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/192).
  Tests: [`test_negation_invariants.py`](../../tests/test_negation_invariants.py).
  Migration: use the accepted parameter interval; changing `epsilon` no longer
  selects a numerical approximation.
- **Silent scalar failures:** invalid/non-finite/Boolean operands and invalid
  membership coordinates no longer return `None`, print an error and return
  zero, or conceal programming failures. Historical calls raise `ValueError`
  for invalid scalar input; stable formula branches handle documented extreme
  finite coordinates. Evidence: Task #63 and
  [PR #194](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/194).
  Tests: [`test_finite_number_policy.py`](../../tests/test_finite_number_policy.py).
  Migration: validate inputs and handle explicit failure rather than treating
  a sentinel or fallback zero as membership evidence.
- **Membership geometry:** incomplete, extra, non-finite, or geometrically
  invalid parameters previously allowed evaluation-time failures or misleading
  fallback values. Construction and parameter replacement now enforce exact
  accepted family contracts; replacement is transactional. Evidence: Task #51
  and [PR #193](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/193).
  Tests: [`test_membership_parameter_validation.py`](../../tests/test_membership_parameter_validation.py)
  and [`test_legacy_membership_conventions.py`](../../tests/test_legacy_membership_conventions.py).
  Migration: repair the parameter geometry while preserving historical keyword
  meaning and order; do not reinterpret `a, b, c` as modern triangle order.
- **Bell shared state:** evaluation previously changed the shared parameter
  mapping. It now evaluates without mutation while retaining the accepted
  reference values. Evidence: Task #53 and
  [PR #185](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/185).
  Tests: [`test_bell_reentrancy.py`](../../tests/test_bell_reentrancy.py).
  Migration: remove code that depends on evaluation altering parameters. The
  focused reentrancy test does not establish library-wide thread safety.
- **Centroid numerical method and zero area:** the fixed right-endpoint sum
  and indirect `ZeroDivisionError` for a zero sampled denominator are replaced
  by analytical/adaptive moments, explicit convergence failure, and deliberate
  zero-area rejection with historical `ValueError`. Evidence: Tasks #79
  and #80 and [PR #254](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/254).
  Tests: [`test_defuzzification.py`](../../tests/test_defuzzification.py),
  [`test_numerical_edge_policy.py`](../../tests/test_numerical_edge_policy.py),
  and [`test_legacy_centroid_reference.py`](../../tests/test_legacy_centroid_reference.py).
  Migration: update fixed-grid numerical expectations, replace zero-area
  `ZeroDivisionError` handlers with `ValueError` handlers, catch non-converged
  results, and use modern `CentroidPolicy` for numerical settings.
  Retained `MFunction.accuracy` is ignored. The historical reference-case bound
  of `5e-4` is not a universal guarantee.
- **Scale validation and lookup:** incomplete level dictionaries and
  case-insensitive name collisions previously made lookup ambiguous or failed
  indirectly. Required fields and unique names are now enforced, and complete
  case-insensitive lookup remains callable. Evidence: Task #83 and
  [PR #262](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/262).
  Tests: [`test_linguistic_terms.py`](../../tests/test_linguistic_terms.py)
  and [`test_legacy_facade.py`](../../tests/test_legacy_facade.py).
  Migration: provide the required fields and distinct names. Historical
  uppercase matching and later-term ties remain unchanged; modern Unicode
  case-folding and explicit tie policies are separate contracts.

Single-evaluation historical scale lookup (Task #105,
[PR #189](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/189)) and
removal of discarded default scale construction (Task #104,
[PR #187](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/187)) retain
valid outputs. Evidence is in
[`test_scale_lookup_evaluation.py`](../../tests/test_scale_lookup_evaluation.py)
and [`test_universal_scale_construction.py`](../../tests/test_universal_scale_construction.py).
These changes do not establish a general performance guarantee.

The explicit modern error categories added by Task #94,
[PR #274](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/274), preserve
built-in catch compatibility and historical concrete failures. See
[`test_domain_exceptions.py`](../../tests/test_domain_exceptions.py).
Runtime-floor and helper-import changes are intentional migration boundaries,
not repaired mathematical defects; the
[release migration notes](../migration/1.0.3-to-2.0.0.md) disclose them separately.

## Record format for each merged correction

Every future **Corrected** row must include:

1. the exact historical behaviour and why it is incorrect;
2. the new v2 contract;
3. the merged implementation PR and linked Task;
4. the correctness and compatibility-test locations;
5. user-visible migration impact and any available safe alternative.

No release note may rely on an unlisted bug-compatible behaviour.
