<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 2.0.0 candidate handoff — 2026-10-09

## Prepared result

The draft integration candidate combines the current `develop` mathematical
audit (merged #303) with the reviewable changes in #304, #305 and #306. It
proposes `2.0.0` package metadata and the stable classifier, aligns active
version/compatibility/migration records and clean-install assertions, and
puts the stable pip installation route first in all three quick starts.
The development installation route remains available for an unpublished
candidate. Historical benchmark measurements and reproducibility fixtures
retain their original version; future optional benchmark runs read the actual
source metadata instead of a hard-coded development version.

No tag, branch promotion, GitHub Release or PyPI publication has occurred.
The changelog entry remains a proposal with a clearly identified preparation
date. Finalize it against the approved revision and actual publication date.
The candidate is kept in draft pending the prerequisites below. After the
individual prerequisite PRs are merged, refresh this branch from that exact
`develop` and repeat candidate CI; earlier green revisions do not substitute.

## Documentation review target

There are 257 required units per language: 52 pages, 193 public symbol
contracts and 12 module overviews. Russian and Chinese drafts are complete;
no human approval has been invented. This version transition changes three
canonical user units and their two translations:

- `page:quick-start`;
- `page:migration.1.0.3-to-2.0.0`;
- `page:contracts.compatibility`.

Their current canonical hashes are recorded in `docs/i18n/units.toml`. The
updated translations retain the code, formulas and original stable anchors.
Review these candidate texts, not just the earlier #304 versions. An actual
editorial and technical/mathematical reviewer must approve the applicable
source and translation hashes under ADR-0011. The same human may only be
recorded for roles they actually performed; AI assistance is not such evidence.

`python -m tools.locale_documentation validate` passes draft freshness and
protected-content checks. The stable `--require-approved` gate intentionally
remains blocked until the required human records exist. Public locale routes
retain explicit fallbacks during that state; use the PR's labelled preview
artifact to review the complete translations.

## Publishing controls to verify

The repository ruleset API, including inherited rules, returned an empty list
during this session. This is not evidence of a protected `v*` release-tag
ruleset. The GitHub connector excludes environment and Actions-variable
administration endpoints, so this session cannot certify their current values.
The private PyPI publisher binding has not been inspected either.

An authorized maintainer must verify the actual configuration described in
the [publishing runbook](../trusted-publishing-runbook.md):

- a `v*` tag ruleset restricting creation to release maintainers and preventing
  routine tag update/deletion;
- environment `pypi`, required reviewers and deployment restrictions for
  protected release tags;
- PyPI Trusted Publisher: owner `Fuzzy-Technologies`, repository
  `FuzzyRoutines`, workflow `release-pypi.yml`, environment `pypi`;
- repository variable `PYPI_TRUSTED_PUBLISHING_ENABLED=true`, enabled only
  after the other controls are verified.

Record configuration evidence in Task #299 or #121. Workflow source and a
successful PR dry run cannot establish these settings. No long-lived token or
manual upload is an alternative to the approved OIDC workflow.

## Final execution order

1. Review and merge the prerequisite PRs, then refresh the candidate from the
   resulting `develop` without changing the approved mathematical contracts.
2. Complete the real hash-bound editorial and scientific reviews on the exact
   candidate texts. Record findings and resolutions, not inferred approvals.
3. Attach exact-candidate CI evidence: full supported-runtime suite, per-module
   coverage, sequential/process outcome parity, installed examples, complete
   locale builds and reproducible wheel/sdist hashes.
4. Verify the external publishing controls and complete the human release
   readiness decision in #121. Review/promote the final source through the
   protected branch process and use the actual release date in the changelog.
5. Create the approved annotated `v2.0.0` tag on the verified commit and review
   the `pypi` environment deployment. PR and manual workflow runs cannot publish.
6. Require both post-publication Python jobs to pass: downloaded PyPI artifacts
   must match approved bytes, hash-pinned pip installation must succeed, and
   installed quick start/scenarios/compatibility examples must execute.
7. Attach the tag, workflow, provenance, artifact hashes, PyPI URL and verified
   documentation link to the final GitHub Release and #121.

These remaining items are explicit release prerequisites, not completed boxes.
