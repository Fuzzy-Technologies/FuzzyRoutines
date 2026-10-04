<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Stable release readiness checklist

## Status

This is a human-reviewed release gate. Checking a box requires a direct immutable evidence link. An unchecked blocker means the release is not approved.

The selected first stable version is **`2.0.0`**; current metadata remains
**`2.0.0.dev0`**. The [version rationale](release-version-decision.md),
[unreleased changelog](../CHANGELOG.md), and
[migration notes](migration/1.0.3-to-2.0.0.md) are preparation artifacts, not
publication approval. [Task #121](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/121)
owns the final human gate. No tag, stable metadata change, `master` promotion,
GitHub Release, or PyPI publication follows from these documents alone.

Curated exports and the domain-error model already have merged evidence in
[PR #273](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/273) and
[PR #274](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/274).
Public typing and signature coverage under Tasks
[#92](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/92) and
[#95](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/95) remain
pending release evidence. Required Actions, package artifacts and final review
must refer to the exact candidate commit; green earlier commits do not check
these boxes.

## Mandatory evidence

- [ ] Mathematics: every supported formula and domain has an accepted contract, primary-source citation where applicable, and executable reference tests.
- [ ] Correctness repairs: every changed legacy behavior has an entry in the corrected-bug ledger, migration impact, and regression evidence.
- [ ] Compatibility: public API surface, imports, parameter conventions, and deprecations have tested evidence and release-note links.
- [ ] Version and migration: the selected version, runtime floor, helper-import changes, corrected numerical behavior, and license transition have been reviewed against the changelog and migration notes.
- [ ] Test quality: deterministic suite, branch-coverage report, negative cases, and supported-runtime CI links are attached.
- [ ] Packaging: wheel and source distribution build, clean installation, metadata validation, and supply-chain evidence are attached.
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
