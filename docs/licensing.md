<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Licensing and provenance

## Effective license

All project-owned FuzzyRoutines source code, tests, documentation, examples,
tools, workflows, configuration, and site assets are licensed under the
Apache License, Version 2.0 (`Apache-2.0`). The authoritative license text is
the repository-root [`LICENSE`](../LICENSE), and required attribution is in
[`NOTICE`](../NOTICE).

Apache-2.0 permits use, modification, and redistribution, including commercial
use, subject to its conditions. Distributors must provide the license, preserve
applicable copyright and attribution notices, retain `NOTICE` attribution, and
mark modified files as required by section 4. The license includes an explicit
patent grant and does not grant permission to use Fuzzy Technologies trade
names or marks beyond reasonable attribution and reproduction of `NOTICE`.

## Relicensing authority and evidence

The complete reachable Git history audited for PR #236 contains 96 commits,
all authored by Timur Gilmullin (`Tim55667757`). The initial 2019 source,
examples, tests, build files, and later modernization commits have no other
recorded author. Timur Gilmullin explicitly approved relicensing the complete
project-owned repository tree to Apache-2.0 as the original author and
copyright owner.

The historical `fuzzyroutines` 1.0.3 snapshot was distributed under the MIT
License with an Open DevOps Community notice. That immutable historical fact
remains documented in the baseline provenance record. It does not make the
current repository revision dual-licensed: the current project-owned tree is
distributed under Apache-2.0 only.

## Third-party boundary

The audit found no copied or vendored third-party source in the repository.
Packages listed in requirements and documentation-tool manifests are external
dependencies; this repository does not change their licenses. Generated HTML,
indexes, inventories, and build environments are disposable outputs and are
not committed.

If third-party material is added later, its original copyright, source, SPDX
identifier, and attribution requirements must be recorded before merge. It
must not be relabeled as Fuzzy Technologies-owned content.

## File-level policy

Project-owned text files carry `SPDX-License-Identifier: Apache-2.0` using the
native comment syntax for their format. Python files additionally carry the
canonical project and maintainer fields. The first and last copyright years
come from Git history rather than the current calendar year alone.

The deterministic command below checks the repository-wide header and metadata
contract:

```bash
python -m tools.check_license_headers
```

`LICENSE` and `NOTICE` are intentionally exempt from file-header insertion;
their complete contents are themselves part of the licensing contract.
