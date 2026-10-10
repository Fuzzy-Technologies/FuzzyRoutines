<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0012: Apache-2.0 relicensing and provenance boundary

- Status: Accepted
- Date: 2026-09-21
- Related Tasks: #199, #208, #209
- Implementation PR: #236

## Context

FuzzyRoutines historically used the MIT License and an Open DevOps Community
copyright notice. The modernized project is maintained as a Fuzzy Technologies
library and requires one coherent license across source code, documentation,
tests, examples, tooling, workflows, configuration, and owned visual assets.

The repository must not claim a new license until authorship, third-party
content, package metadata, source headers, and distribution notices agree.

## Provenance evidence

The full reachable Git history at the PR #236 audit point contains 96 commits.
Every commit records Timur Gilmullin as its author. The initial commit and the
2019 source, examples, tests, build scripts, and documentation all have the same
recorded author. No copied or vendored third-party source was found. External
packages are dependency declarations and remain governed by their own licenses.

Timur Gilmullin, as the original author and copyright owner, explicitly
approved relicensing the complete project-owned tree to Apache-2.0. Historical
release provenance remains factual documentation and does not create a second
license for current revisions.

## Decision

FuzzyRoutines is distributed under Apache License 2.0 only:

- the repository-root `LICENSE` contains the unmodified Apache-2.0 text;
- `NOTICE` preserves project identity and historical attribution;
- package metadata uses the SPDX expression `Apache-2.0` and packages both
  `LICENSE` and `NOTICE`;
- every project-owned text file carries the Apache-2.0 SPDX identifier in its
  native comment syntax, except `LICENSE` and `NOTICE`;
- Python files also carry project, maintainer, and evidence-based copyright
  fields;
- CI rejects missing headers, conflicting current-license claims, or metadata
  drift;
- third-party material must retain its actual upstream licensing and notices
  and must be explicitly inventoried before merge.

## Consequences

Redistribution and derivative works remain permitted, including commercially,
but Apache-2.0 section 4 requires preservation of the license and applicable
notices and requires modified files to be identified. Contributors receive and
grant the explicit patent rights and conditions defined by Apache-2.0.

Apache-2.0 does not transfer Fuzzy Technologies trademarks or product identity.
The name may be used for reasonable attribution, including preservation of
`NOTICE`, but the license does not grant broader trademark rights.

Any future license change requires a new provenance audit, explicit copyright-
holder approval, coordinated metadata/header changes, and a superseding ADR.
