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

The release-preparation source sets `pyproject.toml` to **2.1.0**, dated
2026-10-14. This is **unpublished candidate metadata**; the published stable
release remains 2.0.0. The metadata identifies the checked-out source and does
not establish publication. Merged features provide implementation evidence,
while exact-candidate acceptance belongs to
[Task #337](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/337).
That task remains open until the candidate evidence and final handoff are complete.

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
The exact final 2.1.0 wheel, installed benchmark comparisons and maintainer
promotion review remain pending. Retain each feature's source-bound acceptance
when reconciling the final tree; do not reuse an earlier artifact's checks as
verification of a different wheel.

### Mandatory evidence

- [ ] Identify the exact candidate commit, version, wheel and sdist hashes; retain reproducible-build and clean-install evidence on both supported interpreters.
- [ ] Run the complete required CI gate on that candidate, including installed public imports, compatibility and feature-specific mathematical checks.
- [ ] Compare the installed candidate with installed PyPI 2.0.0 in the same environment for relevant scalar, centroid and scale workloads; retain raw timing samples and independent numerical checks.
- [ ] Run the pinned [consumer scale migration CLI](migration/consumer-scale-boundary.md) against the exact installed 2.1.0 wheel, in the candidate scalar environment after timings; source fixture tests do not satisfy this artifact check. Private FMA/robot validation remains unverified.
- [ ] Confirm the accepted examples, deterministic figures, optional-dependency boundaries and EN/RU/zh-CN reviews still match the final candidate and its artifacts.
- [ ] Verify the three product landing pages, matching API language destinations, copy controls, formulas, image interactions and mobile layouts from the composed candidate artifact.
- [ ] Review migration notes, changelog, version decision, scope exclusions and the remaining risks in one concise maintainer handoff.

### Hard blockers

- [ ] Resolve all release-blocking defects and confirm required checks pass on the exact release revision.
- [ ] Obtain the maintainer's final promotion/release approval before protected publication.
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
