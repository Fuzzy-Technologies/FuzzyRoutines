<!--
SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines Changelog

FuzzyRoutines Changelog — a chronological record of features, mathematical
corrections, compatibility boundaries, tooling, and release-relevant evidence.
The [development protocol](docs/development-evidence-protocol.md#10-changelog-contract)
defines the shared Fuzzy Technologies format.

# Major 2

Major 2 modernizes FuzzyRoutines with explicit mathematical contracts and a
focused modern API while preserving protected historical calls. The CPython
floor and helper-import changes justify the
[selected stable target](docs/release-version-decision.md).

## Minor 2.0

### Patch 0 — v2.0.0.dev0 — 2026-10-05

#### Digest

- Prepared the first modernization development baseline: corrected scalar
  mathematics, explicit modern APIs, preserved historical calls, and
  reproducible package/documentation evidence.
- Stable `2.0.0` remains planned. This entry records merged implementation;
  its date is the preparation date of these notes, not a stable publication
  date. Final readiness and human approval remain pending.

Existing users should read the
[1.0.3 migration notes](docs/migration/1.0.3-to-2.0.0.md).

#### Added

- Curated modern root exports provide immutable membership factories and a
  structural custom-callable protocol, explicit continuous/discrete universes,
  numerical integration domains, immutable scalar sets, and scalar policies.
- Set operations include complement, intersection, union, and directed
  difference. Derived properties, alpha-cuts, relations, exact height and
  normalization preserve distinct exact and sampled evidence contracts.
- `Centroid` exposes an explicit integration domain and numerical policy.
  Linguistic terms and ordered scales provide structured lookup, membership scores,
  confidence, explicit no-match/tie policies, and sampled scale diagnostics.
- `fuzzyroutines.exceptions` exposes modern input, domain, and numerical
  error categories. Error names are available through that explicit module;
  the [API inventory](docs/public-api-documentation-inventory.md) records the
  current root surface.
- Inline modern annotations and the `py.typed` marker provide a strict typing
  contract for root and focused imports. Static consumers exercise custom
  callbacks, policy families, immutable results, and return types against both
  source and clean installed wheels on the supported CPython versions.
- Alice project artwork appears in the README and API documentation; the
  compact project sign remains available for package and small-icon contexts.

See [PR #273](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/273)
for export curation and the
[historical-to-modern guide](docs/migration/historical-to-modern.md) for
supported operation-by-operation migration.

#### Fixed

- Scalar operators reject non-finite, Boolean, non-numeric, and out-of-range
  fuzzy degrees; valid grades lie in `[0, 1]`. Built-in membership coordinates
  must be finite non-Boolean real scalars and may lie outside `[0, 1]`.
  Invalid inputs no longer return silent sentinels or fallback zero;
  composition validates every operand and rejects empty input and unknown
  families.
- Membership construction and replacement require exact finite parameter
  sets and valid family geometry. Bell evaluation no longer mutates its
  parameter mapping. `FuzzyNOT` requires `alpha` in `(0, 1)`;
  `FuzzyNOTParabolic` uses the analytical branch for `[1/4, 3/4]` instead of
  an epsilon-driven scan.
- `FuzzySet.Defuz()` and `defuzValue` use current membership parameters and
  integration bounds. Centroid evaluation uses analytical moments where
  supported and deterministic adaptive quadrature elsewhere; zero area and
  unresolved convergence fail explicitly. Historical zero-area failure is now
  `ValueError` rather than indirect `ZeroDivisionError`. Retained `MFunction.accuracy` no
  longer controls centroid execution.
- Scale validation requires the necessary level fields and rejects name
  collisions under case-insensitive lookup. Historical fuzzification
  evaluates each term once; `UniversalFuzzyScale` avoids a discarded default
  construction.
- Implementation and product documentation identify analytical centroids,
  linguistic fuzzification, and modern typing as implemented capabilities
  rather than future work. Release notes retain the separate exact-candidate
  and human-approval requirements.
- A [project readiness audit](docs/audits/2026-10-05-project-audit.md) records
  source and ADR alignment, reproduced correctness findings, practical usage,
  documentation gaps, and the limits of release evidence.
- ADR-0004 explicitly preserves valid unary norm composition as the identity
  for all supported families, correcting the document's stricter operand
  count. Empty input and invalid values remain rejected; runtime formulas and
  historical signatures are unchanged.

Merged PRs and focused regression tests are collected in the
[corrected-bug ledger](docs/compatibility/corrected-bug-ledger.md).

Audit follow-ups remain pending review:
[Gaussian centroid cancellation on remote intervals](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/282),
[exact rational fuzzification tie comparisons](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/283),
[analytical certificates for overridden evaluators](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/284),
and [extreme finite membership arithmetic](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/285).
Their issue references record discovered regressions, not merged fixes or
stable release approval.

#### Changed

- CPython 3.13 is the minimum supported runtime; 3.13 and 3.14 form the
  mandatory stable CI matrix. Earlier interpreters are historical evidence.
- PEP 517/518 builds use `setuptools.build_meta` and PEP 621 metadata in
  `pyproject.toml`; `setup.py` is a compatibility shim. Wheel and source
  distribution clean-install checks replace the retired Travis build path.
- The current project-owned tree is Apache-2.0 licensed with `LICENSE`,
  `NOTICE`, SPDX metadata and provenance documentation. The immutable 1.0.3
  baseline remains MIT licensed.
- Deterministic process-based tests, JSON benchmark evidence, installed-package
  API documentation, source-link/coverage checks, and multilingual drift
  controls support review. Reserved translations are not approved translations.
- `MFunction.accuracy` and `FuzzyNOTParabolic`'s `epsilon` argument remain for
  source compatibility but no longer select the numerical algorithms.
- New-code naming guidance follows the current shared Python standard:
  `snake_case` variables and parameters, `UPPER_SNAKE_CASE` constants, and
  concise docstrings for tests. Existing public keyword spellings remain
  protected. Routine local validation covers affected paths; full regression,
  documentation, typing, and package gates run in PR CI.
- Release readiness requires identical wheel and source-distribution bytes
  from independent builds of the exact candidate, with a fixed environment
  and recorded hashes, alongside clean-install evidence. Build success alone
  does not satisfy this stronger reproducibility gate. The comparison applies
  within the same Python, platform, and pinned build toolchain; archive and CI
  implementation are tracked separately in
  [Task #278](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/278).

Compatibility preserved during modernization:

- ADR-0001's historical imports, operators, classes, methods, identifiers,
  keyword meanings, and parameter order remain supported through
  `fuzzyroutines.FuzzyRoutines`.
- Historical mutable objects, complete-name uppercase lookup, returned level
  dictionary identity, and later-term ties remain available. Pickle identity
  is preserved across facade extraction, with a pre-extraction fixture.
- Modern error categories preserve applicable built-in catches; historical
  adapters retain their concrete built-in failures. See
  [PR #274](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/274).
- No protected historical name is removed or newly deprecated by this
  development baseline.

The [compatibility guide](docs/COMPATIBILITY.md) distinguishes ADR-protected
names from the wider currently tested observed surface.

ADR-0015 selects a future optional vectorization strategy. The NumPy prototype
and measurements live outside the package; there is no public NumPy backend or
transparent cache. Executable convexity, symmetric difference, and free-threaded
CPython support remain roadmap work. No universal speed or FMA throughput claim
is made. See [PR #272](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/272)
and the [current implementation boundary](docs/current-status.md).

#### Removed

- Historical wildcard imports exclude imported helper modules and now contain
  exactly fifteen supported functions and classes. `math` and `copy` are no
  longer facade attributes; import standard-library modules directly.
- The obsolete Travis publishing path is retired.

#### Security

- Routine PR workflows build and verify artifacts without publishing packages.
- The protected PyPI Trusted Publishing workflow and human release gate are
  documented; their presence does not mean a stable release is approved.

# Major 1

Major 1 is the historical FuzzyRoutines line. Its immutable baseline predates
modernization and retains its original MIT license.

## Minor 1.0

### Patch 3 — v1.0.3 — 2019-09-01

#### Digest

- Published the historical 1.0.3 wheel, now used with its immutable repository
  tag as the modernization comparison baseline.

The [provenance record](docs/baseline/fuzzyroutines-1.0.3-provenance.md)
records the publication date, artifact hash, MIT license, Python classifier,
and Travis build lineage. This is a provenance summary, not a reconstruction
of undocumented historical changes; the baseline remains unchanged.
