<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 2.0.0 candidate handoff — updated 2026-10-10

## Integrated candidate

[PR #307](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/307) was
accepted by the maintainer and squash-merged into `develop` at
[`45c9db375033437fc01e73789fbac968e730f0d0`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/45c9db375033437fc01e73789fbac968e730f0d0).
The maintainer explicitly requested removal of Draft and squash merge on
2026-10-10. That integration is complete; it is not an outstanding approval.

The candidate includes the original mathematical audit, complete translations,
post-publication package verification, the Universal Fuzzy Scale example and
comparison plot, editorial corrections, portable mathematical notation and
distribution-only PyPI staging. The corpus contains 258 units per locale,
nine scenarios, 31 executable guide blocks and eleven scientific figures.
The historical scale retains its original coefficients and classification
behavior on the verified 1001-point grid.

## Verified integration evidence

All seven push workflows passed on the merged revision:

- [Mathematics, supported runtimes and serial/process parity](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38004590789).
- [Package reproducibility and clean installs](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38004590808).
- [Documentation, source links and installed examples](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38004590831).
- [Three-language API reference](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38004590734).
- [Deterministic correctness gate](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38004590760).
- [Public typing](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38004590741).
- [Optional vectorized parity](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38004590736).

The final PR head also passed all nine PR workflows before the authorized merge.
These links certify their recorded revision; later changes receive their own CI.

## Remaining documentation acceptance

The maintainer explicitly accepted the Russian translation, with a reservation
about its style, and subsequently accepted the corrected PR #307 for squash
merge. The Russian corpus has not changed since that accepted revision. This
is recorded as maintainer editorial acceptance; another general Russian
editorial approval is not being requested. It does not claim a native-Chinese
or mathematical specialist review. The existing ADR-0011 contract still requires
explicit editorial and applicable technical/mathematical responsibility, tied
to each English-source and translation hash. One human may hold several roles;
separate reviewers or line-by-line approval are not required.

The review manifests still mark all Russian and Chinese units as current drafts. The ordinary locale validator
passes; `--require-approved` reports 516 draft units. No missing translation
implementation is implied by that count. The remaining action is recording real
the remaining review responsibility and hash-bound records for the current
corpus, not translating it again or repeating acceptance already given.

Browser inspection is tracked in existing Task #297. The local Chromium process
cannot start because runtime sockets are denied. The existing API-reference CI
now runs the browser inspection on its hosted runner and uploads desktop/mobile
screenshots and a machine report for actual review. CI execution and screenshot
inspection must succeed before the rendered acceptance is checked.

## Remaining publication configuration

PyPI ownership is confirmed in
[Task #115](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/115#issuecomment-5663895446).
Task #116 explicitly left production configuration to an administrator; its
closure certifies the workflow implementation, not the external settings.
The current repository ruleset response is empty. Environment reviewers,
Actions variables and the private Trusted Publisher binding are not exposed by
the available GitHub connector and have not been certified.

Use the [publishing runbook](../trusted-publishing-runbook.md) to verify:

- protected `v*` tags and environment `pypi` with deployment review;
- PyPI publisher owner `Fuzzy-Technologies`, repository `FuzzyRoutines`,
  workflow `release-pypi.yml`, environment `pypi`;
- `PYPI_TRUSTED_PUBLISHING_ENABLED=true`, enabled after those controls.

## Execution order

1. Finish hosted-browser evidence and the existing locale approval records.
2. Verify actual external publishing controls and record final release approval.
3. Promote the verified candidate from `develop` to `master`, using the actual
   publication date in the changelog, then create annotated tag `v2.0.0`.
4. Let protected GitHub Actions publish the approved wheel and sdist with OIDC.
5. Require both supported-Python post-publication jobs to verify PyPI hashes,
   clean installation and installed scenarios; attach evidence to the release.
6. Close #299/#121 and their parent features only after actual publication.

No release tag, `master` promotion, GitHub Release or PyPI upload has occurred.
