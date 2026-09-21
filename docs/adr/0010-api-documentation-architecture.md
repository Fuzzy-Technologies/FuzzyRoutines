<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0010: API Documentation Architecture

- Status: Accepted
- Date: 2026-09-16
- Related planning task: #198
- Related follow-up tasks: #199, #200, #206
- Supersedes: none

## Context

FuzzyRoutines needs an API reference that can grow with the v2 mathematical
modules without making runtime imports part of documentation discovery. The
reference must coexist with the current hand-authored GitHub Pages site and the
engineering documents already stored under `docs/`.

Task #198 evaluated current pdoc, mkdocstrings-python, and Sphinx autodoc builds
against the same real `fuzzyroutines.fuzzysets` module and its
`fuzzyroutines.domain` type dependency. The comparison used CPython 3.14.7,
pinned docs-only dependencies, strict HTML builds, import-time tracing, and
generated-output checks. The complete method and evidence are recorded in
`docs/api-evaluation/comparison-evidence.md`.

The decision criteria are:

- type and object cross-references;
- local search;
- rendered mathematical notation;
- stable object anchors;
- links or expandable views for implementation source;
- reproducible builds without a network after dependencies are provisioned;
- Fuzzy Technologies theming;
- API discovery that does not import project modules;
- dependencies isolated from the runtime package;
- composition with the existing GitHub Pages site.

## Decision

The canonical API-documentation stack is:

```text
MkDocs + Material for MkDocs + mkdocstrings-python + Griffe
```

The canonical source docstring dialect is **English Google style with Markdown
content**. Python type annotations remain the authoritative type declaration;
docstrings explain semantics, units, valid domains, errors, invariants, and
mathematical behavior rather than duplicating annotations.

Canonical docstrings may use:

- Google-style sections such as `Args:`, `Returns:`, `Raises:`, and `Examples:`;
- Markdown links and qualified mkdocstrings references such as
  `[ScalarFuzzySet][fuzzyroutines.fuzzysets.ScalarFuzzySet]`;
- fenced Python examples;
- inline `$...$` and display `$$...$$` LaTeX notation where a formula is the
  clearest contract.

Repository-wide docstring migration belongs to Tasks #199 and #200. This
decision does not rewrite existing docstrings.

## Why this stack

The spike demonstrated all required output features. Its decisive advantage is
safe discovery: mkdocstrings-python collected the API from source through
Griffe without importing `fuzzyroutines.fuzzysets`. The equivalent pdoc and
Sphinx autodoc builds imported the module; Sphinx's official autodoc and
viewcode documentation explicitly warns that imports execute module side
effects.

The selected stack also keeps narrative mathematical documentation and API
objects in the same Markdown information architecture. Fully qualified object
anchors, the generated `objects.inv`, Material's local search index, source
views, and a project CSS layer provide a direct path to a branded reference
site. A later integration can build the static result into a dedicated subtree
without replacing the current Pages landing page.

## Generated HTML policy

Generated HTML is disposable build output and must not be committed.

The sources of truth are:

- Python annotations and docstrings;
- hand-authored Markdown under the future production documentation source;
- the MkDocs configuration and Fuzzy Technologies theme assets;
- pinned docs-only dependency manifests;
- the reproducible build command.

All local generated sites belong under `_build/`, which is ignored by Git.
Production Pages composition and deployment are reserved for Task #206. That
task must select a dedicated output subtree, preserve the existing `docs/index.html`,
and prevent generated files from becoming competing editable sources.

The current math spike uses a version-pinned MathJax browser URL. This does not
affect offline HTML generation, which was verified with unusable network proxy
settings. Task #206 must either vendor the approved MathJax assets for a fully
offline-viewable site or document the intentional browser-time dependency.

## Consequences

- API collection does not execute FuzzyRoutines import-time code by default.
- Runtime package metadata remains free of documentation dependencies.
- Strict builds can fail closed on unresolved references and plugin warnings.
- Mathematical narratives and generated API reference can share navigation,
  search, theme, and cross-references.
- Documentation authors use one English Google/Markdown dialect instead of
  mixing reStructuredText roles with Markdown syntax.
- Material theming adds a larger static payload than pdoc or the default Sphinx
  theme; the measured spike produced approximately 2.76 MB and 55 files.
- MkDocs plugins are executable build dependencies and remain pinned and
  reviewable even though project-module discovery is static.

## Alternatives

### pdoc 16.0.0

pdoc produced the smallest and fastest candidate site and supplied search,
MathJax support, object links, and inline source views with minimal
configuration. It was not selected because it imported the project package for
discovery, used shorter object anchors, and would require custom template work
to compose the API with the broader engineering documentation and Fuzzy
Technologies site structure.

### Sphinx 9.1.0 autodoc

Sphinx produced mature cross-references, search, inventories, math, and source
pages. It was not selected because autodoc and default viewcode imported the
documented modules, and adopting it would introduce a parallel reStructuredText
authoring stack where the repository already uses Markdown. Sphinx remains a
valid future choice if a requirement emerges that its broader extension or
multi-format publishing ecosystem uniquely satisfies.

## Acceptance and supersession

This ADR is **Accepted**. Replacing the canonical generator or docstring
dialect requires a superseding ADR with a repeated comparison against the
then-current FuzzyRoutines modules. Deployment details may be refined by Task
#206 without superseding this decision as long as the source-of-truth and
safe-discovery invariants remain intact.
