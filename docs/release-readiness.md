<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Stable release readiness checklist

## Published 2.0.0 baseline

**FuzzyRoutines 2.0.0 is published and verified.** The GitHub release was
published on 2026-10-10 at 21:30:18 UTC, corresponding to 2026-10-11 in Moscow.
Its approved source is
[`49c9aee67a60cad74bc9494943b8745b72d2f43c`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/49c9aee67a60cad74bc9494943b8745b72d2f43c),
identified by annotated tag `v2.0.0`.

- [PyPI 2.0.0](https://pypi.org/project/fuzzyroutines/2.0.0/) provides the published package.
- [Successful protected production run](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38087564208) records reproducible builds, OIDC publication, published byte/hash checks and clean-install examples on CPython 3.13 and 3.14.
- [GitHub Release](https://github.com/Fuzzy-Technologies/FuzzyRoutines/releases/tag/v2.0.0) retains the wheel, sdist, `SHA256SUMS` and `reproducibility.json`.
- [Recorded production acceptance](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/299#issuecomment-6102397342) confirms completion of the maintainer-approved publication and verification.

The [tagged 2.0 preparation checklist](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/release-readiness.md)
and [dated candidate handoff](audits/2026-10-09-release-candidate-handoff.md)
remain historical records. Their pending statements describe the time before
publication. They are not the current package status or evidence for a future
candidate. Historical ADRs, audit findings and release artifacts remain intact.

## Audit follow-ups

The 2.0 mathematics, coverage, documentation and publication follow-ups are
recorded in the [tagged checklist](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/release-readiness.md#audit-follow-ups)
and [mathematics/coverage review](audits/2026-10-09-math-coverage-review.md).
Those dated records describe their measured revisions. New 2.1 changes require
their own review and candidate checks below.

## Current 2.1 development gate

**The corrected 2.1 implementation passed independent release acceptance on
2026-10-19.** The [current acceptance](audits/2026-10-19-release-acceptance.md)
records all ten successful full workflows at
`0dba28a072c6d8dff3eacdc336b922e1ab264b23`, exact installed artifacts, fresh
thirty-scenario scalar measurements and full 600-observation/400-epoch CPU
experiments. Rational geometry, narrow polynomial windows, Mamdani knots,
PyPI links, versioned onboarding and scientific-page rendering were corrected
and reviewed. Source-bound raw reports remain separate from earlier evidence.

Corporate companion [PR #52](https://github.com/Fuzzy-Technologies/fuzzy-technologies.github.io/pull/52)
is merged. The subsequent [navigation PR #57](https://github.com/Fuzzy-Technologies/fuzzy-technologies.github.io/pull/57)
must follow localized project Pages deployment. Task #337 completes after the
accepted correction is integrated into develop; Feature #323 then completes
its child acceptance. Release PR #348 remains the maintainer's final review.
Its actual current head must pass promotion CI and retain its own artifact
identities. The older checked evidence below describes its named historical
revision.


The release-preparation source sets `pyproject.toml` to **2.1.0**, dated
2026-10-14. This is **unpublished candidate metadata**; the published stable
release remains 2.0.0. The metadata identifies the checked-out source and does
not establish publication. Preparation [PR #346](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/346)
passed all ten opening workflows at `f0d09c3`. Its wheel from built source
`c44983a` has completed installed scalar, NumPy and public-consumer checks.
The [dated handoff](audits/2026-10-14-2.1-candidate-handoff.md) retains exact
identities, run links, raw measurements and limits.
[Task #337](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/337)
completes on independently accepted evidence and a prepared maintainer handoff,
not on the maintainer's later approval of promotion.

The final promotion pull request to `master` is reserved for the maintainer's
review. These documents do not authorize its merge, an annotated release tag,
a GitHub Release or PyPI publication. Earlier green commits and the completed
2.0 publication cannot satisfy the candidate checks below.

### Accepted implementation evidence

| Area                                             | Reviewed source evidence                                                                                                                                             |
| ---                                              | ---                                                                                                                                                                  |
| Historical scale factory and linguistic encoding | Merged [PR #341](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/341), including mathematical contracts, source-bound translations and installed checks.    |
| Three-language product homepage                  | Merged [PR #342](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/342), preserving the shared design, copy controls and image viewer.                        |
| Mamdani and Sugeno inference                     | Merged [PR #343](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/343), including rule traces, independent references and explanatory figures.               |
| Neural examples and bounded Sugeno research      | Merged [PR #344](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/344), including scientific review, recorded experiments and optional installed-CPU checks. |
| Optional NumPy batches                           | Merged [PR #345](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/345) after all required CI passed; includes explicit backend and installed-wheel checks.   |

These accepted feature revisions establish implementation and review evidence.
The [artifact acceptance record](performance/evidence/installed-candidate/acceptance.json)
identifies the measured 2.1.0 wheel and byte-identical wheel/sdist builds on both
supported interpreters. [Scalar](performance/installed-scalar-comparison.md) and
[NumPy](performance/installed-batch-results.md) reports retain the installed
measurements. A later promotion artifact needs its own archive hash and package
payload comparison; report-only commits can change timestamps. Retain feature
source-bound reviews without presenting them as checks of different artifact bytes.

### Mandatory evidence

The checked items below apply to the exact measured preparation candidate in the
[handoff](audits/2026-10-14-2.1-candidate-handoff.md), not an unbuilt future release.

- [x] Candidate source/version, wheel/sdist hashes and reproducible-build/clean-install evidence on CPython 3.13 and 3.14 are retained in the [acceptance record](performance/evidence/installed-candidate/acceptance.json).
- [x] All ten full opening workflows completed successfully at `f0d09c3`, including installed imports, typing, compatibility, mathematics and optional examples; [run metadata](performance/evidence/installed-candidate/ci-workflows.json) is retained.
- [x] Installed PyPI 2.0.0 and candidate scalar/centroid/scale comparison completed with seven alternating pairs, raw samples and independent parity; the [report](performance/installed-scalar-comparison.md) includes mixed results and shared-host limits.
- [x] The [installed migration fixture](performance/evidence/consumer-scale-installed-2.1.0.json) passed all 27 synthetic public-boundary cases after timing in the exact no-dependencies candidate environment. Private FMA/robot integration remains unverified.
- [x] The [installed NumPy study](performance/installed-batch-results.md) retains 24 synthetic combinations, four replay combinations covering 30 upstream test inputs, numerical parity and memory/import/dependency costs.
- [x] Optional CPU examples, scientific figures, source/report provenance and EN/RU/zh-CN gates passed in the recorded neural/documentation/API workflows.
- [x] The composed site's three homepages and API routes passed the automated browser gate in the recorded API workflow, including desktop/mobile layout and shared interactions.
- [x] Independent scientific/editorial review accepted the four-document handoff at `ab77384` on 2026-10-14; numerical/provenance review separately accepted its supporting records. The integrating PR retains this acceptance. This completes preparation; the maintainer's release decision remains separate.

### Hard blockers

These are later promotion/publication conditions, not unimplemented 2.1 features:

- [x] Corrected implementation acceptance, full CI, installed package checks and fresh scalar/neural evidence are recorded in the [19 October acceptance](audits/2026-10-19-release-acceptance.md). Final promotion must record the actual #348 head and its own archive identities in that PR.
- [ ] Obtain the maintainer's final promotion/release approval before merging the final `master` PR or performing protected publication.
- [ ] After approved publication, verify actual PyPI artifact hashes and clean installations, then record production acceptance.

## Scope and final 2.1 documentation pass

Public convexity queries, symmetric-difference operations and free-threaded
support remain outside the planned 2.1 scope. They require separately scoped
contracts, implementation and evidence. The bounded differentiable Sugeno
research task does not authorize a public tensor backend. Do not advertise
these ideas as released or implemented capabilities without their own accepted work.

The current published-product examples may continue to pin 2.0.0. At final
2.1 acceptance, review these locations together; change version claims only
when the corresponding installed-candidate or publication evidence exists:

| Location                                                                       | Final review action                                                                                                           |
| ---                                                                            | ---                                                                                                                           |
| `README.md`; `docs/index.html`, `docs/ru/index.html`, `docs/zh-CN/index.html`  | Align product capabilities, installation pins and expected results across all three landing pages.                            |
| `docs/llms.txt`; agent quick-start translations and `examples/agent_recipe.py` | Keep explicit installed-version checks and distinguish published baseline from candidate recipes.                             |
| `docs/site` API pages, guides, navigation and `docs/i18n/units.toml`           | Verify every newly public import, link and reviewed source/translation hash on the final tree.                                |
| `CHANGELOG.md`; migration and packaging notes                                  | Separate new capabilities, corrected behavior and preserved historical contracts; retain the 2.0 release record.              |
| `docs/release-readiness.md`; candidate performance and artifact reports        | Attach exact revision, package hashes, raw samples, environment and numerical checks without reusing old development timings. |
| `docs/release-notes-2.0.0.md`; `docs/release-notes-2.1.0.md`                   | Preserve 2.0 notes and prepare a separate 2.1 summary with its own verified installation and artifact links.                  |

## External publication controls

After approval, follow the existing
[Trusted Publishing runbook](trusted-publishing-runbook.md) and
[ADR-0006](adr/0006-packaging-versioning-release-policy.md). Platform controls
must be checked for that release; their historical 2026-10-10 state is not a
claim that settings have remained unchanged.
