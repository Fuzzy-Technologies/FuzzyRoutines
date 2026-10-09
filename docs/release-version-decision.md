<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# First modernization release version decision

- Decision: retain **`2.0.0` as the planned first stable modernization version**.
- Proposed stable candidate metadata: **`2.0.0`**, owned by
  [`pyproject.toml`](../pyproject.toml).
- Planning: [Task #119](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/119)
  under [Feature #37](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/37).
- Governing policy: [ADR-0006](adr/0006-packaging-versioning-release-policy.md).

This review reaffirms the accepted version policy against the implemented
public impact. The candidate PR proposes the metadata transition; that proposal does not
announce a published release or supply human approval. The final human gate remains
[Task #121](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/121).

## Baseline and observable impact

The comparison baseline is the immutable
[1.0.3 tag and artifact record](baseline/fuzzyroutines-1.0.3-provenance.md),
not the moving `develop` branch. The first stable version remains `2.0.0`
because the release has deliberate compatibility boundaries alongside retained
historical calls:

- **Runtime floor:** v2 requires CPython 3.13 or later, with mandatory stable
  CI for 3.13 and 3.14. Older runtimes are outside the support contract. The
  historical Python 3.6 classifier is provenance, not a v2 promise. This
  intentional boundary was accepted in ADR-0006 and implemented by
  [PR #154](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/154).
- **Observed helper imports:** the historical wildcard surface now explicitly
  exports fifteen supported functions and classes. Imported helper modules
  are excluded; `math` and `copy` are no longer facade attributes. Code that
  imported those modules through the facade must import them directly. They
  are outside ADR-0001's protected names, but their removal is a visible
  migration requirement, recorded in the
  [1.0.3 surface snapshot](compatibility/legacy-public-api-1.0.3.md).
- **Correctness impact:** strict finite-input and parameter validation,
  analytical negation, current-state centroid calculation, and explicit
  zero-area failure change invalid-input behavior and some numerical results.
  ADR-0001 classifies these as documented defect corrections, not removal of
  valid historical calls. The
  [corrected-bug ledger](compatibility/corrected-bug-ledger.md) records evidence
  and migration impact.

A patch or minor release number would understate the runtime and observed
import changes. Module extraction, new immutable APIs, typing, and new build
tooling alone do not justify a major number. Apache-2.0 relicensing is a
separate redistribution change under
[ADR-0012](adr/0012-apache-2.0-relicensing.md); it must be disclosed regardless
of the chosen number.

## Guarantees and merged evidence

[ADR-0001](adr/0001-backward-compatibility-contract.md) still protects the
historical module paths, named operators and classes, documented methods,
membership identifiers, keyword meanings, and parameter ordering. Modern
`Triangle(left, peak, right)` is additive and does not reorder historical
`MFunction("triangle", a=left, b=right, c=peak)`.

The current decision includes these merged changes:

- [PR #272](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/272),
  [commit `7f13ebb`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/7f13ebb):
  ADR-0015 accepts an optional vectorization strategy; the NumPy experiment
  remains outside the package and establishes no public backend promise.
- [PR #273](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/273),
  [commit `d654c9b`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/d654c9b):
  curated modern root exports and the explicit historical wildcard contract.
- [PR #274](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/274),
  [commit `126986a`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/126986a):
  modern error categories at `fuzzyroutines.exceptions`, with built-in catch
  compatibility and preserved concrete historical failures.

Facade extraction preserves historical serialization identities and has a
pre-extraction pickle fixture; it does not promise arbitrary pickle portability
across every Python or package version. See
[`test_legacy_facade.py`](../tests/test_legacy_facade.py).

## Release execution remains pending

The [changelog](../CHANGELOG.md) and
[release migration notes](migration/1.0.3-to-2.0.0.md) describe implemented
changes. Public typing and signature coverage under Tasks
[#92](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/92) and
[#95](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/95) are now merged
in [PR #276](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/276)
([`82647a7`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/82647a7)).
Their source and installed-wheel checks are documented in
[public modern typing](public-typing.md). Every item in the
[readiness checklist](release-readiness.md) must be reviewed against the exact
candidate commit, including supported-runtime CI and artifact evidence.

Only the approved release procedure may change the stable metadata, create the
matching annotated tag, promote the approved source, create a GitHub Release,
or publish to PyPI. This decision authorizes none of those actions.
