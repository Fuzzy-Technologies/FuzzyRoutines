<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Stable release readiness checklist

## Status

This is a human-reviewed release gate. Checking a box requires a direct immutable evidence link. An unchecked blocker means the release is not approved.

The selected first stable version is **`2.0.0`**; current metadata remains
**`2.0.0.dev0`**. The [version rationale](release-version-decision.md),
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

These follow-ups are pending review. Do not check the correctness or
no-unresolved-regression items solely because a fix branch exists; verify the
merged fixes and CI evidence on the exact release candidate.

Documentation maintenance has separate follow-ups:
[Task #280](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/280)
for explained visual examples and
[Task #286](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/286)
for missing test-function docstrings. They remain reviewable documentation
work and do not substitute for correcting the numerical blockers.

## Mandatory evidence

- [ ] Mathematics: every supported formula and domain has an accepted contract, primary-source citation where applicable, and executable reference tests.
- [ ] Correctness repairs: every changed legacy behavior has an entry in the corrected-bug ledger, migration impact, and regression evidence.
- [ ] Compatibility: public API surface, imports, parameter conventions, and deprecations have tested evidence and release-note links.
- [ ] Version and migration: the selected version, runtime floor, helper-import changes, corrected numerical behavior, and license transition have been reviewed against the changelog and migration notes.
- [ ] Test quality: deterministic suite, branch-coverage report, negative cases, and supported-runtime CI links are attached.
- [ ] Packaging: independent wheel and source distribution builds have matching bytes; clean installation, metadata validation, and supply-chain evidence are attached.
- [ ] Licensing: Apache-2.0 metadata, `LICENSE`, `NOTICE`, SPDX headers, provenance audit, and packaged artifacts agree.
- [ ] Documentation: README, API/mathematics documents, compatibility notes, and links have been reviewed for accuracy and accessibility.
- [ ] Performance: reproducible benchmark evidence is attached; no performance claim is made without raw measurements and environment metadata.
- [ ] Security and publishing: release credentials, provenance, and publishing configuration have been explicitly reviewed by an authorized maintainer.

## Hard blockers

- [ ] No open blocker or unresolved correctness regression affects the release.
- [ ] No known invalid legacy behavior is presented as supported compatibility.
- [ ] All required GitHub Actions are green for the exact release commit.
- [ ] A human maintainer has approved the release decision and version number.

A release is approved only when every item above has evidence and the final human approval is recorded in the release issue or pull request.
