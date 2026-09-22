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
mode against the installed package. It replaces only its own disposable
`_build/api-reference/` directory.

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
