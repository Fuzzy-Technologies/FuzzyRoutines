<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Current implementation status

This page records the public boundary of the active `develop` branch. It
separates implemented and tested behavior from the FuzzyRoutines 2 roadmap. The
first stable modernization release remains planned as `2.0.0`; current package
metadata uses `2.0.0.dev0`.

The [release version review](release-version-decision.md) reaffirms that stable
target from observable compatibility impact. The
[development changelog](../CHANGELOG.md) and
[1.0.3 migration notes](migration/1.0.3-to-2.0.0.md) describe the implemented
boundary; release approval remains pending.

The [2026-10-05 project audit](audits/2026-10-05-project-audit.md) reviews the
production modules, all accepted ADRs, practical usage, documentation and
examples. It records concrete correctness findings and distinguishes pending
review candidates from merged release evidence.

## Implemented and verified

- Historical imports and public names remain covered by compatibility tests.
- Built-in membership families have documented formulas and strict construction-time parameter validation.
- Focused `membership`, `operators`, and internal `numeric` modules own the
  scalar implementations. Modern membership factories are immutable callables
  with semantic parameter names; `Triangle` and `Trapezoid` use conventional
  left-to-right parameters. Historical membership methods adapt to the same
  formula source while preserving their protected signatures.
- Modern exact-property, normalization, and centroid operations consume
  analytical snapshots without importing the historical module. Existing
  `fuzzysets` and `linguistic` module paths stay stable; see
  [focused module ownership](architecture/focused-modern-modules.md).
- Additive registry names select the shared scalar formulas of their historical
  `MFunction` identifiers: `sShoulder`, `gaussian`, `logistic`, and
  `harringtonDesirability`.
- Classical logic, algebraic, bounded, and drastic t-norm/s-norm families have reference and property tests.
- `TNormCompose` and `SCoNormCompose` validate every operand before evaluation.
- `FuzzyNOT` requires a finite real `alpha` in the open interval `(0, 1)`.
- `FuzzyNOTParabolic` uses the proved analytical branch and cannot enter an epsilon-driven scan.
- Bell membership evaluation does not mutate its parameter mapping and has a concurrent reentrancy regression test.
- modern `Centroid` consumes a continuous fuzzy set and explicit integration
  domain, uses stable analytical moments for supported polynomial and Gaussian
  families, and otherwise uses deterministic adaptive quadrature with explicit
  tolerance and convergence failure;
- `FuzzySet.Defuz()` and `defuzValue` delegate to that strategy on every access,
  ignore retained `MFunction.accuracy`, and never expose stale centroid state;
- `FuzzyScale.Fuzzy()` evaluates each term once and deliberately selects the later term when memberships tie.
- Transparent cross-call caches remain absent from mutable legacy objects and
  caller-supplied callables because those surfaces have no safe invalidation
  token. Explicit immutable derived values may retain snapshots that cannot
  become stale, as normalization does for a discrete universe. The distinction
  and future cache gate are documented in
  [the cache and precomputation decision](performance/cache-and-precomputation-evaluation.md).
- `UniversalFuzzyScale` no longer constructs and discards the default three-level scale.
- Benchmark and diagnostic tools emit machine-readable JSON and have end-to-end command-line tests.
- The root `__all__` now defines the curated modern exports; the historical
  facade exports exactly fifteen supported names and excludes helper modules.
- Modern `fuzzyroutines.exceptions` categories distinguish input, domain,
  and numerical failures while preserving built-in catch compatibility.
  Historical adapters retain their concrete built-in failures and serialized
  class/function identities.
- The modern public modules ship inline annotations and the `py.typed` marker.
  Strict source typing and consumer fixtures cover root and focused imports,
  custom callbacks, policy families, immutable results, and return types.
  CI checks those consumers against an independently installed wheel on
  CPython 3.13 and 3.14; legacy adapters retain their runtime contract outside
  the modern static-typing promise. See [public modern typing](public-typing.md).

The latest accepted architecture and contract wave includes
[PR #272](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/272)
([`7f13ebb`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/7f13ebb)),
[PR #273](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/273)
([`d654c9b`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/d654c9b)),
and [PR #274](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/274)
([`126986a`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/126986a)).
These establish the vectorization decision, curated exports, and error model;
the vectorized backend itself remains future work.

The subsequent accepted preparation wave includes
[PR #276](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/276)
([`82647a7`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/82647a7)),
which implements public modern typing and signature coverage,
[PR #277](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/277)
([`f29858c`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/f29858c)),
which adds the Alice project artwork while retaining compact branding, and
[PR #275](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/275)
([`f700e0e`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/f700e0e)),
which records version, migration, and shared changelog preparation. Merged
implementation evidence does not approve the future stable release candidate.

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

- ADR-0015 retains the dependency-free scalar default and adopts optional,
  explicitly selected vectorization for large batches of supported built-in
  membership families. The measured NumPy experiment remains outside the
  package; public backend implementation, packaging and API gates remain
  separate future work. See the
  [strategy decision](adr/0015-optional-vectorized-execution-strategy.md) and
  [recorded comparison](performance/vectorized-membership-comparison.md).
- ADR-0009 defines continuous fuzzy convexity as quasiconcavity, discrete
  convexity as order-convexity, and finite-grid success as sampled evidence
  rather than proof. The public convexity query and evidence-result API remain
  future implementation work.

## Implemented multilingual documentation controls

- ADR-0011 keeps English pages and source docstrings canonical while reserving
  `ru` and `zh-CN` for accountable native editorial translations;
- stable page and public-symbol IDs bind every canonical English unit to a
  deterministic versioned SHA-256 source hash;
- tracked locale glossaries share language-independent concept IDs;
- the offline documentation gate rejects false approval, incomplete human
  review evidence, malformed locale state, and approved translations made
  stale by a canonical English change;
- untranslated locale routes remain explicit fallbacks and are never presented
  as reviewed translations.

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
  tuple and provides exact or Unicode case-insensitive complete-name lookup;
- modern scale fuzzification exposes every ordered membership score, maximum
  confidence, explicit no-match thresholds, and `first`, `last`, or `all` tie
  policies;
- sampled scale diagnostics expose their finite domain, endpoint-preserving
  grid, activity threshold, partition tolerance, per-point maximum membership,
  gaps, overlaps, and aggregate partition-quality evidence without modifying
  scale coefficients;
- modern and historical scales reject case-insensitive name collisions, and
  historical dictionary-based `FuzzyScale.levels` plus `GetLevelByName()`
  remain available as compatibility surfaces;
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

- ADR-0010's source standard, English public docstrings, installed-package API
  reference, and composed product/API site are implemented. Production Pages
  deployment is restricted to the approved default branch; reserved locale and
  release-version routes remain explicit fallbacks.
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

Explanatory visual guides remain a separate documentation deliverable under
[M6 Task #280](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/280):
reproducible membership and operation graphs, exact-versus-sampled evidence,
centroid geometry, and linguistic tie/no-match examples with readable captions
and corresponding executable code. They do not change mathematical contracts
or introduce runtime plotting dependencies.

Existing test-function docstring debt is tracked separately in
[Task #286](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/286).
The updated source standard governs new and modified code; it does not claim
that every existing test already satisfies the shared documentation rules.

## Still in the v2 roadmap

- symmetric-difference semantics;
- executable convexity queries with evidence-strength-preserving results;
- public optional vectorized execution under ADR-0015's API, numerical-parity,
  time, memory and dependency gates;
- free-threaded CPython support, subject to race-safety and scaling evidence.

## Performance and concurrency claims

Performance changes are accepted only with reproducible before/after
measurements and numerical-parity tests. Current scalar optimizations remove
known duplicate work; they do not establish a universal speed claim.

Ordinary independent Python processes can execute independent models.
Thread-safe or free-threaded execution is not yet a supported contract for the
complete library. Individual paths may receive reentrancy tests before that
broader claim is made.

The focused modules are the canonical implementation source for new code. The existing
`FuzzyRoutines.py` module and its parameter conventions will remain available
as compatibility aliases or adapters rather than defining the new architecture.

## Release status

Routine pull-request workflows build and clean-install packages but cannot
publish them. Release candidates, signed tags, GitHub Releases, and PyPI Trusted
Publishing belong to the release milestone and require the complete
human-reviewed readiness gate.

The [readiness checklist](release-readiness.md) remains unchecked until evidence
for the exact release commit and Task #121's human approval are recorded.
Accepted release notes and a selected version do not authorize publication.

The current code audit identified correctness follow-ups for remote-interval
Gaussian centroids ([#282](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/282)),
exact-rational fuzzification comparisons
([#283](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/283)),
analytical certificates for evaluator overrides
([#284](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/284)),
and extreme finite membership arithmetic
([#285](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/285)). Their
fixes require separate review and merge; see the
[audit follow-up gate](release-readiness.md#audit-follow-ups).
