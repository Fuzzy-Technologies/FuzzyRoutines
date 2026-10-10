<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Stable release readiness checklist

## Status

This is a human-reviewed release gate. Checking a box requires a direct immutable evidence link. An unchecked blocker means the release is not approved.

The selected first stable version is **`2.0.0`**; the proposed candidate metadata is
**`2.0.0`**. This branch is prepared for review, not approved for publication. The [version rationale](release-version-decision.md),
[development changelog](../CHANGELOG.md), and
[migration notes](migration/1.0.3-to-2.0.0.md) are preparation artifacts, not
publication approval. [Task #121](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/121)
owns the final human gate. No tag, stable metadata change, `master` promotion,
GitHub Release, or PyPI publication follows from these documents alone.

Curated exports and the domain-error model already have merged evidence in
[PR #273](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/273) and
[PR #274](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/274).
Public typing and signature coverage under Tasks
[#92](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/92) and
[#95](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/95) are merged in
[PR #276](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/276)
([`82647a7`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/82647a7)).
The [typing contract](public-typing.md) describes the source and installed-wheel
checks; merged development evidence is not final release-candidate evidence.
Required Actions, package artifacts and final review
must refer to the exact candidate commit; green earlier commits do not check
these boxes.

Preparation under [Feature #36](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/36)
and [Feature #37](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/37)
also requires two independent builds of the same source revision with matching
wheel and sdist bytes. Compare builds within the same interpreter, platform,
and pinned toolchain; this gate does not promise byte equality across different
Python or backend versions. [Task #278](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/278)
owns the archive normalization and CI comparison implementation. Record the
fixed build environment, artifact hashes, and clean-install evidence for the
exact approved version. Repository workflow
code alone does not verify the production PyPI publisher binding, GitHub
environment reviewers, tag rules, or activation switch; use the
[Trusted Publishing runbook](trusted-publishing-runbook.md) for those checks.

## Audit follow-ups

The [2026-10-09 all-module audit](audits/2026-10-09-math-coverage-review.md)
records per-module branch coverage, independent-reference evidence, newly
covered public boundaries and exact sequential/process test parity on both
supported Python versions. Its measured revision and justified remaining gaps
are explicit; final candidate acceptance still requires its own CI evidence.

The [2026-10-05 project audit](audits/2026-10-05-project-audit.md) records the
baseline, source and ADR inventory, reproduced defects, usability assessment,
and verification limits.

The current audit has identified four correctness issues requiring their own
reviewed fixes and affected-test evidence before stable approval:

- [Task #282](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/282):
  Gaussian centroid cancellation on intervals remote from the membership
  centre;
- [Task #283](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/283):
  distinct exact rational membership grades can be rounded into an apparent
  fuzzification tie;
- [Task #284](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/284):
  evaluator subclasses that override membership behavior must not inherit
  stock analytical certificates;
- [Task #285](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/285):
  extreme finite membership inputs can trigger avoidable overflow in accepted
  triangular, trapezoidal, Gaussian, and logistic families.

These repairs are merged into `develop`: exact rational fuzzification in
[PR #287](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/287),
Gaussian centroid corrections in
[PR #289](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/289), and
evaluator-certificate and extreme-coordinate membership corrections in
[PR #291](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/291).
Their merged development evidence does not by itself check the final
correctness or no-unresolved-regression items: verify the repairs and full CI
on the exact release candidate.

Documentation maintenance has separate follow-ups:
[Task #280](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/280)
for explained visual examples and
[Task #286](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/286)
for missing test-function docstrings. The test-documentation repair is merged
in [PR #300](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/300);
#280 remains open for complete multilingual visual-example acceptance. Neither
substitutes for final numerical acceptance.

## Complete three-language documentation for 2.0.0

The English scenario/figure baseline is merged in
[PR #301](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/301)
([`518bc9d`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/518bc9dd5750afde569b1593e243490fc42ce658)).
The [final English corpus review](audits/2026-10-09-english-corpus-review.md)
records the subsequent per-symbol example gate, result/error/historical
recipes and review corrections under #294. AI-assisted English preparation
does not approve missing Russian or Chinese translations or check final
release-candidate boxes.

The [multilingual implementation review](audits/2026-10-09-multilingual-review.md)
records the original 257-unit Russian/Chinese drafts, canonical corrections,
rendered findings and the remaining hash-bound human reviews. Complete draft
coverage is not approval.

The maintainer requires complete English, Russian and Simplified Chinese user
documentation for the first stable release. English fallback pages are useful
during development but do not satisfy this release criterion. Follow
[ADR-0011](adr/0011-multilingual-documentation-pipeline.md) for hash-bound
translation state and human review; automated or AI-assisted passes must not
invent human/native-speaker approval.

Complete the work in this order:

1. Finalize canonical English under
   [Task #294](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/294).
   Record engineering, mathematical/scientific, data-science and reader/editor
   findings. Make installation, domains, assumptions, outputs and limitations
   understandable without reading the implementation.
2. Complete the visual examples under
   [Task #280](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/280):
   a prominent pip-install quick start, supported API examples, at least six
   distinct end-to-end scenarios and deterministic membership/operator/centroid
   graphs. Show inputs, units, intermediate values, outputs and interpretations;
   execute examples from installed distributions in CI.
3. Translate the finalized corpus under
   [Task #295](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/295)
   for Russian and
   [Task #296](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/296)
   for Simplified Chinese. Review each translated language separately for
   scientific meaning, terminology, natural prose and usability.
4. Verify complete, current locale coverage and actual rendered pages under
   [Task #297](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/297).
   Record desktop/mobile navigation, language switching, search, formulas,
   figures, captions, accessible descriptions and installed-example evidence.

[Task #298](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/298)
records the completed all-module mathematics, meaningful per-module line/branch
coverage and process-based parallel-test audit. The historical legacy-only
coverage report cannot establish coverage adequacy for the modern modules.

[Task #299](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/299)
owns protected CI-only PyPI publication and verification of the published
installation. Coordinate the approved promotion, annotated tag and final
GitHub Release with Task #121. A successful PR dry run is workflow evidence;
it does not mean the stable artifacts have been published to PyPI.

The maintainer target is 2026-10-09 ahead of the conference week. The target
does not waive any review, correctness, documentation or publication gate.

The [candidate handoff](audits/2026-10-09-release-candidate-handoff.md) lists
the prepared integration, the three changed locale-review targets, observed
external-control limits and the remaining execution order.

## Integrated candidate evidence

The maintainer accepted and squash-merged [PR #307](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/307)
into `develop` at `45c9db375033437fc01e73789fbac968e730f0d0`. All seven
post-merge workflows pass; the [updated handoff](audits/2026-10-09-release-candidate-handoff.md#verified-integration-evidence)
links the immutable mathematics, packaging, documentation, typing and correctness
runs. The checked technical items below refer to that integrated revision.
This records completed work while keeping actual publication and locale-role
acceptance visible as separate outstanding decisions.

## Mandatory evidence

- [x] Mathematics: every supported formula and domain has an accepted contract, primary-source citation where applicable, and executable reference tests.
- [x] Correctness repairs: every changed legacy behavior has an entry in the corrected-bug ledger, migration impact, and regression evidence.
- [x] Compatibility: public API surface, imports, parameter conventions, and deprecations have tested evidence and release-note links.
- [x] Version and migration: the selected version, runtime floor, helper-import changes, corrected numerical behavior, and license transition have been reviewed against the changelog and migration notes.
- [x] Test quality: deterministic suite, branch-coverage report, negative cases, and supported-runtime CI links are attached.
- [x] Packaging: independent wheel and source distribution builds have matching bytes; clean installation, metadata validation, and supply-chain evidence are attached.
- [x] Licensing: Apache-2.0 metadata, `LICENSE`, `NOTICE`, SPDX headers, provenance audit, and packaged artifacts agree.
- [ ] Documentation: README, API/mathematics documents, compatibility notes, and links have been reviewed for accuracy and accessibility.
- [x] Canonical English: engineering, mathematical/scientific, data-science and reader/editor findings are resolved; every supported public API has a usable example or a justified tested alias link.
- [ ] Russian and Simplified Chinese: every required user-documentation unit is translated, current and individually scientifically/editorially reviewed; no missing/stale fallback is accepted.
- [x] Practical examples: the pip-install quick start, at least six complete end-to-end scenarios and their numerical results/figures execute from installed artifacts in CI.
- [ ] Rendered documentation: all three languages have reviewed navigation, search, formulas, links, shared English-labelled figures with byte-identical assets, localized captions/alternatives and desktop/mobile readability evidence.
- [x] Mathematical audit: every supported module has an accepted contract, independent reference/invariant evidence and assessed line/branch coverage; process-based parallel execution is verified on the candidate.
- [x] Performance: [raw measurements and environment metadata](audits/2026-10-09-release-candidate-handoff.md#retained-performance-measurements) are retained for installed wheel/sdist on both supported Python versions; no universal speedup is claimed.
- [ ] Security and publishing: release credentials, provenance, and publishing configuration have been explicitly reviewed by an authorized maintainer.

## Hard blockers

- [ ] No open blocker or unresolved correctness regression affects the release.
- [ ] No known invalid legacy behavior is presented as supported compatibility.
- [ ] All required GitHub Actions are green for the exact release commit.
- [ ] A human maintainer has approved the release decision and version number.
- [ ] The approved wheel and sdist are actually published to PyPI through protected CI, match the approved hashes, and pass clean pip-install quick-start and compatibility checks.

A release is approved only when every item above has evidence and the final human approval is recorded in the release issue or pull request.
