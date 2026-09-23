<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Canonical API reference

This directory contains the tracked English source, configuration, and shared
assets for the canonical FuzzyRoutines API reference. Generated HTML is a
disposable view under `_build/api-reference/` and must not be committed.

## One-command clean build

Run from the repository root with a supported CPython interpreter:

```bash
python tools/build_api_reference.py
```

The command creates an isolated environment, builds a wheel, installs that
wheel and the exactly pinned documentation toolchain, and runs MkDocs in strict
mode against the installed package. MkDocs documentation warnings therefore
fail the build. Informational tool messages and upstream lifecycle advisories
are reported separately and are not documentation diagnostics. The command
replaces only its own disposable `_build/api-reference/` directory.

To preview the same installed-package reference locally:

```bash
python tools/build_api_reference.py --serve
```

The preview listens on `127.0.0.1:8000` by default. Use `--dev-addr` to select
another local address.

## Source-of-truth boundary

The English Python annotations and docstrings in the built package are the API
source of truth. These Markdown pages provide navigation and architectural
context; they do not duplicate individual API contracts. Russian and
Simplified Chinese content remains outside Python source as specified by
[ADR-0011](../adr/0011-multilingual-documentation-pipeline.md).

The build does not import FuzzyRoutines for API discovery. Griffe reads the
installed package statically from its isolated environment. Documentation
dependencies remain separate from runtime package metadata.

## Quality gates

Task #204 established deterministic gates around the strict build:

- `docs/site/api-coverage.toml` declares every public module and the reviewed
  reason for each excluded module or symbol;
- `python -m tools.documentation_gates all` validates public source docstrings,
  mkdocstrings coverage, repository-local Markdown targets, exact rendered
  anchors, and the ADR-0010 generated-output policy;
- documented migration examples run from the clean wheel installation rather
  than from the source tree;
- `python tools/report_external_links.py --output REPORT.json` produces a
  source-located network health report in a separate non-blocking CI job.

Generated reference HTML is intentionally not committed, so a generated-file
drift comparison is inapplicable. The gate instead fails if generated output
appears under version control.

## GitHub Pages composition

Task #206 composes this generated English reference with the tracked product
page by running:

```bash
python tools/compose_pages_site.py
```

The disposable result is `_build/pages/site`. The canonical English route is
`/api/latest/en/`. Russian and Simplified Chinese routes are reserved with
explicit untranslated fallback pages, so language navigation never points to
missing content or presents English as reviewed translation. `/api/versions/`
distinguishes the moving latest documentation from immutable stable-release
paths; no stable 2.x documentation is claimed before a release exists.

Pull requests and `develop` upload preview artifacts without production side
effects. Only a push to the approved `master` branch can run the Pages deploy
job. The generated API continues to load the version-pinned MathJax browser
asset selected in ADR-0010; this is an intentional browser-time dependency and
does not affect offline static generation.
