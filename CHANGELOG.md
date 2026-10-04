<!--
SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Changelog

## Unreleased — planned 2.0.0 modernization release

The development package is `2.0.0.dev0`. `2.0.0` is the
[selected stable target](docs/release-version-decision.md), not a published
release. These notes cover merged implementation; final release readiness and
human approval remain pending. Existing users should read the
[1.0.3 migration notes](docs/migration/1.0.3-to-2.0.0.md).

### Correctness fixes

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

Merged PRs and focused regression tests are collected in the
[corrected-bug ledger](docs/compatibility/corrected-bug-ledger.md).

### Compatibility guarantees

- ADR-0001's historical imports, operators, classes, methods, identifiers,
  keyword meanings, and parameter order remain supported through
  `fuzzyroutines.FuzzyRoutines`.
- Historical mutable objects, complete-name uppercase lookup, returned level
  dictionary identity, and later-term ties remain available. Pickle identity
  is preserved across facade extraction, with a pre-extraction fixture.
- Modern error categories preserve applicable built-in catches; historical
  adapters retain their concrete built-in failures. See
  [PR #274](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/274).

The [compatibility guide](docs/COMPATIBILITY.md) distinguishes ADR-protected
names from the wider currently tested observed surface.

### New API

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

See [PR #273](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/273)
for export curation and the
[historical-to-modern guide](docs/migration/historical-to-modern.md) for
supported operation-by-operation migration.

### Deprecation and compatibility boundaries

- CPython 3.13 is the minimum supported runtime; 3.13 and 3.14 form the
  mandatory stable CI matrix. Earlier interpreters are historical evidence.
- Historical wildcard imports now contain exactly fifteen supported names.
  Imported helper modules are excluded; `math` and `copy` are no longer facade
  imports. Import standard-library modules directly.
- No protected historical name is removed or newly deprecated by these notes.
  `MFunction.accuracy` and `FuzzyNOTParabolic`'s `epsilon` argument remain for
  source compatibility but no longer select the numerical algorithms.

### Packaging, licensing, and tooling

- PEP 517/518 builds use `setuptools.build_meta` and PEP 621 metadata in
  `pyproject.toml`; `setup.py` is a compatibility shim. Wheel and source
  distribution clean-install checks replace the retired Travis publishing
  path. Routine PR workflows cannot publish packages.
- The current project-owned tree is Apache-2.0 licensed with `LICENSE`,
  `NOTICE`, SPDX metadata and provenance documentation. The immutable 1.0.3
  baseline remains MIT licensed.
- Deterministic process-based tests, JSON benchmark evidence, installed-package
  API documentation, source-link/coverage checks, and multilingual drift
  controls support review. Reserved translations are not approved translations.
- A protected PyPI Trusted Publishing workflow and human release gate are
  documented; their presence does not mean a stable release is approved.

### Explicitly outside this release's implemented API

ADR-0015 selects a future optional vectorization strategy. The NumPy prototype
and measurements live outside the package; there is no public NumPy backend or
transparent cache. Executable convexity, symmetric difference, and free-threaded
CPython support remain roadmap work. No universal speed or FMA throughput claim
is made. See [PR #272](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/272)
and the [current implementation boundary](docs/current-status.md).

## Historical 1.0.3 baseline

The immutable 1.0.3 tag and published wheel are preserved in the
[provenance record](docs/baseline/fuzzyroutines-1.0.3-provenance.md), including
the 2019 publication date, artifact hash, MIT license, Python classifier, and
Travis build lineage. These modernization notes do not reconstruct historical
release entries or change that baseline.
