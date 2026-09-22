<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Current implementation status

This page records the public boundary of the active `develop` branch. It
separates implemented and tested behavior from the FuzzyRoutines 2 roadmap. The
first stable modernization release remains planned as `2.0.0`; current package
metadata uses `2.0.0.dev0`.

## Implemented and verified

- Historical imports and public names remain covered by compatibility tests.
- Built-in membership families have documented formulas and strict construction-time parameter validation.
- Forward-looking registry names share one interim implementation with their historical `MFunction` identifiers: `sShoulder`, `gaussian`, `logistic`, and `harringtonDesirability`.
- Classical logic, algebraic, bounded, and drastic t-norm/s-norm families have reference and property tests.
- `TNormCompose` and `SCoNormCompose` validate every operand before evaluation.
- `FuzzyNOT` requires a finite real `alpha` in the open interval `(0, 1)`.
- `FuzzyNOTParabolic` uses the proved analytical branch and cannot enter an epsilon-driven scan.
- Bell membership evaluation does not mutate its parameter mapping and has a concurrent reentrancy regression test.
- `FuzzySet.Defuz()` and `defuzValue` recalculate from the current membership parameters and integration interval.
- `FuzzyScale.Fuzzy()` evaluates each term once and deliberately selects the later term when memberships tie.
- Transparent cross-call caches remain absent from mutable legacy objects and
  caller-supplied callables because those surfaces have no safe invalidation
  token. Explicit immutable derived values may retain snapshots that cannot
  become stale, as normalization does for a discrete universe. The distinction
  and future cache gate are documented in
  [the cache and precomputation decision](performance/cache-and-precomputation-evaluation.md).
- `UniversalFuzzyScale` no longer constructs and discards the default three-level scale.
- Benchmark and diagnostic tools emit machine-readable JSON and have end-to-end command-line tests.

Representative accepted changes for the historical correctness baseline are
[#184](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/184),
[#185](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/185),
[#186](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/186),
[#187](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/187),
[#188](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/188),
[#189](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/189),
[#190](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/190),
[#192](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/192), and
[#193](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/193).

## Accepted contracts awaiting implementation

- ADR-0009 defines continuous fuzzy convexity as quasiconcavity, discrete
  convexity as order-convexity, and finite-grid success as sampled evidence
  rather than proof. The public convexity query and evidence-result API remain
  future implementation work.
- ADR-0010 selects MkDocs + Material for MkDocs + mkdocstrings-python + Griffe
  and English Google-style Markdown docstrings. The source standard, public
  docstring migration, and reproducible installed-package API reference are
  implemented by Tasks #199, #200, and #203. Production Pages composition and
  deployment remain the separate scope of Task #206.

## Implemented modern domain surface

- immutable scalar `ContinuousUniverse`, `DiscreteUniverse`, and
  `IntegrationDomain` value objects implement the representation layer of
  ADR-0002;
- the legacy `FuzzySet.supportSet` tuple delegates internally to
  `IntegrationDomain` without changing its constructor, getter, or setter
  shape;
- analytical support, support closure, core, boundary, and height are derived
  exactly for every accepted `MFunction` family and clipped to the declared
  continuous universe;
- discrete-universe properties are exhaustive over every declared coordinate;
- continuous grid inspection returns a separately typed sampled report with
  explicit domain, resolution, method, and `isExact == False` provenance;
- weak alpha-cuts use the exact `>= alpha` boundary convention, evaluate
  discrete universes exhaustively, and expose continuous finite-grid
  observations through a separate `SampledAlphaCut` result;
- immutable `ScalarFuzzySet` values support complement, intersection, and
  union with mandatory `NegationPolicy`, `TNormPolicy`, and `SNormPolicy`
  arguments;
- directed fuzzy-set difference implements `T(mu_A(x), N(mu_B(x)))` with
  mandatory t-norm and negation policies and no classical self-difference
  assumption;
- exact height queries evaluate discrete universes exhaustively and reuse
  analytical `MFunction` property derivation for continuous universes;
- normalization returns a distinct height-one set, rejects zero height, and
  rejects generic continuous callables rather than treating a sample maximum
  as exact;
- immutable `LinguisticTerm` values associate exact names with modern
  `ScalarFuzzySet` values, while `LinguisticScale` preserves an explicit term
  tuple without defining lookup, tie-breaking, or fuzzification policy;
- historical dictionary-based `FuzzyScale.levels` remains available and
  unchanged as a compatibility surface;
- executable historical-to-modern examples document the supported migration
  boundary without inventing future membership, lookup, or defuzzification APIs;
- binary fuzzy-set operations fail closed when their continuous or discrete
  universes are not exactly equal;
- the set-level operator families preserve the accepted scalar formulas and
  have commutativity, associativity, boundary, range, and De Morgan tests.

The recent accepted documentation and domain wave is
[#224](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/224),
[#225](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/225),
[#226](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/226),
[#227](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/227),
[#228](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/228),
[#229](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/229), and
[#230](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/230).

## Documentation source of truth

- Python annotations and docstrings remain authoritative for the generated API
  reference, while mathematical narratives remain hand-authored Markdown;
- the reproducible three-generator comparison is retained under
  [`docs/api-evaluation/`](api-evaluation/README.md), but it is not a production
  Pages integration;
- the canonical English API-reference source and build contract live under
  [`docs/site/`](site/README.md) and build with
  `python tools/build_api_reference.py`;
- generated HTML is disposable `_build/` output and must not be committed;
- the historical-to-modern migration guide and executable examples are
  available under [`docs/migration/`](migration/historical-to-modern.md) and
  `examples/migration/`.

## Still in the v2 roadmap

- symmetric-difference semantics;
- executable convexity queries with evidence-strength-preserving results;
- analytical centroid moments where stable closed forms exist;
- deterministic adaptive quadrature with explicit tolerance and convergence errors elsewhere;
- typed linguistic lookup, tie-breaking, and fuzzification policies;
- completion of the focused typed module API with the historical module retained as a compatibility facade;
- optional vectorized execution, subject to numerical-parity, time, memory, and dependency evidence;
- free-threaded CPython support, subject to race-safety and scaling evidence.

## Performance and concurrency claims

Performance changes are accepted only with reproducible before/after
measurements and numerical-parity tests. Current scalar optimizations remove
known duplicate work; they do not establish a universal speed claim.

Ordinary independent Python processes can execute independent models.
Thread-safe or free-threaded execution is not yet a supported contract for the
complete library. Individual paths may receive reentrancy tests before that
broader claim is made.

The focused typed modules will be the canonical API for new code. The existing
`FuzzyRoutines.py` module and its parameter conventions will remain available
as compatibility aliases or adapters rather than defining the new architecture.

## Release status

Routine pull-request workflows build and clean-install packages but cannot
publish them. Release candidates, signed tags, GitHub Releases, and PyPI Trusted
Publishing belong to the release milestone and require the complete
human-reviewed readiness gate.
