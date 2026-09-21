<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Cache and Precomputation Evaluation

- Status: Decision record for Task #106
- Baseline: `develop` at `bb83748afb31176ac338eb4fe638a5470feb5122`
- Decision: do not add a cross-call cache or a persistent precomputed grid

## Decision

FuzzyRoutines keeps evaluation state uncached across public calls. Operation-local
values may be retained only for the duration of one call, as
`FuzzyScale.Fuzzy()` already does when it evaluates every level exactly once.

No persistent cache is accepted by this task. The current public objects do not
provide an invalidation token that can prove a cached value is current, and the
available benchmarks do not demonstrate a workload-specific benefit large
enough to justify changing that contract.

## Candidate assessment

| Candidate                       | Correctness boundary                                                                    | Evidence                                                                                                                                   | Result                                      |
|---------------------------------|-----------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| Membership result by coordinate | Legacy `MFunction.parameters`, `mju`, and modern callable closure state can change      | No bounded key space or representative hit-rate workload is defined                                                                        | Rejected                                    |
| Legacy centroid                 | Membership parameters, callable, accuracy, and integration domain can change            | `benchmark_fuzzyset_centroid` measures recalculation cost, but no safe invalidation design or same-environment candidate comparison exists | Rejected                                    |
| Derived properties              | The universe values are immutable, but the accepted `MFunction` is mutable              | Exact derivation is covered by correctness tests; no versioned function identity exists                                                    | Rejected                                    |
| Discrete membership grid        | A grid would be a snapshot, while `ScalarFuzzySet` accepts arbitrary stateful callables | Snapshot lifetime and memory bound are not part of the public API                                                                          | Deferred to a separately typed snapshot API |
| Linguistic-scale lookup         | Levels, fuzzy sets, and membership functions remain mutable                             | `benchmark_scale_lookup` proves one evaluation per term per lookup after Task #105                                                         | Keep operation-local reuse only             |

## Lifetime and invalidation contract

The compatibility facade has a deliberately simple rule: every public query
observes state that is current when the query begins. It must not return a value
computed by an earlier public query.

This rule applies to:

- `FuzzySet.Defuz()` and `FuzzySet.defuzValue` after changes to the membership
  function, its parameters or accuracy, or `supportSet`;
- `FuzzyScale.Fuzzy()` after changes to `levels` or any contained membership
  function;
- `DeriveProperties()` after changes to an `MFunction`;
- `ScalarFuzzySet.Membership()` when its callable closes over mutable state.

The frozen `ScalarFuzzySet` wrapper does not make the supplied callable pure or
immutable. Object immutability alone is therefore not a valid cache lifetime.

## Reproduction and evidence

Run the existing benchmark and correctness evidence from the repository root:

```bash
python -m tools.benchmark_fuzzyset_centroid
python -m tools.benchmark_scale_lookup
python -m pytest -q tests/test_cache_safety_contract.py \
  tests/test_stale_defuzzification_regression.py \
  tests/test_scale_lookup_evaluation.py
```

The benchmark commands emit raw timing and allocation samples as JSON. Their
numbers are local observations, not an optimization claim. In particular, the
scale report must show three membership evaluations per default-scale lookup
and five per universal-scale lookup: one for every term, with no duplicate
evaluation inside a call.

The focused contract tests prove that mutating caller-owned state is visible on
the next query. A cache that makes either test fail is incompatible even if it
is faster.

## Gate for a future cache

A future proposal may proceed only if all of these conditions are met:

1. The cached API accepts an immutable membership definition, not an arbitrary
   callable or the mutable legacy facade.
2. The key includes every semantic input: membership definition, universe or
   integration domain, numerical policy, tolerance, and resolution.
3. The lifetime, memory bound, eviction policy, and concurrency behavior are
   public and deterministic.
4. A named workload records a meaningful reuse rate and compares the baseline
   and candidate commits in the same environment under the benchmark protocol.
5. Numerical parity and mutation-visibility tests pass before timing results are
   considered.

Until those preconditions exist, recalculation is the correctness-preserving
behavior and no transparent persistent cache on a mutable evaluation surface
is part of the FuzzyRoutines contract.

## Subsequent immutable snapshot boundary

Task #76 later introduced normalization as an explicit derived-value operation.
For a `DiscreteUniverse`, `Normalize` evaluates every declared coordinate once
and stores the normalized grades in the distinct immutable result. For a
supported analytical continuous set, it snapshots the canonical family and
parameters so later mutation of the source cannot invalidate the result's
height-one evidence.

Those values are not transparent caches on the mutable source object: callers
request a new mathematical object with snapshot semantics, and subsequent
queries against the original set still observe current source state. This does
not authorize cross-call memoization for `ScalarFuzzySet.Membership()`,
`DeriveProperties()`, legacy defuzzification, or linguistic-scale lookup. Any
future cache on those surfaces must still satisfy the gate above.
