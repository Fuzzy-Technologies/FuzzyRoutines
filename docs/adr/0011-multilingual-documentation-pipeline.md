<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0011: Multilingual Documentation Pipeline

- Status: Accepted on merge
- Date: 2026-09-18
- Related planning task: #205
- Depends on: [ADR-0010](0010-api-documentation-architecture.md)
- Detailed contract: [Multilingual documentation architecture](../architecture/multilingual-documentation-pipeline.md)
- Supersedes: none

## Context

FuzzyRoutines requires English, Russian, and Simplified Chinese documentation
without placing translated docstrings in Python source or allowing translations
to remain silently current after the English contract changes. The selected
MkDocs, Material, mkdocstrings-python, and Griffe stack in ADR-0010 provides the
static-discovery and site-generation foundation, but it does not define
translation identity, review state, drift detection, or fallback behavior.

The pipeline must preserve several invariants:

- English source docstrings and English Markdown are canonical;
- translated prose is native editorial content, not a mechanical replacement
  of English words;
- mathematical claims, formulas, examples, and terminology receive human
  subject-matter review;
- every translation is bound to the exact English source revision it reviewed;
- missing or stale translations are visible states, never silently published
  as current;
- the architecture can be reused by another Fuzzy Technologies Python project
  without importing FuzzyRoutines.

This ADR designs the pipeline and tracked metadata. It does not bulk-translate
existing pages, generate production sites, or select the final Pages deployment
layout reserved for Task #206.

## Decision

### Canonical language and locale keys

English is the canonical source language. The only initial publication locale
keys are:

| Locale  | Language             | Role                         |
|---------|----------------------|------------------------------|
| `en`    | English              | Canonical source             |
| `ru`    | Russian              | Reviewed native translation  |
| `zh-CN` | Simplified Chinese   | Reviewed native translation  |

Locale keys are stable identifiers used in paths, manifests, navigation, and
search indexes. A future locale requires an explicit manifest and glossary; it
must not reuse or silently alias one of these keys.

### Source and translation ownership

Canonical inputs remain:

- English Google-style docstrings and Python annotations in the installed
  package;
- English Markdown pages in the production documentation source;
- stable identifiers, manifests, locale glossaries, and reviewed translations;
- MkDocs configuration, theme assets, and pinned documentation dependencies.

Russian and Simplified Chinese text lives outside Python source. Generated HTML,
generated search indexes, and generated fallback pages remain disposable build
outputs under `_build/` and are never edited or committed.

### Stable identity

Every translatable unit has one permanent ASCII identifier:

- narrative pages use `page:<hierarchical-id>`, for example
  `page:mathematics.fuzzy-set.operations`;
- public API symbols use their fully qualified Python name prefixed with
  `symbol:`, for example
  `symbol:fuzzyroutines.fuzzysets.ScalarFuzzySet`;
- terminology entries use `concept:<hierarchical-id>`, for example
  `concept:fuzzy-set.positive-support`.

Identifiers survive file moves, title edits, translated headings, and URL
changes. Identifiers are never translated or recycled for a different concept.
Qualified Python symbol names follow actual compatibility decisions: a rename
creates a new symbol identifier and the old identifier remains as an alias or
retired record rather than being rewritten in translation history.

### Hash-bound translation state

Each page or symbol unit records a SHA-256 hash of a deterministic canonical
English payload. The payload includes schema version, stable identifier, unit
kind, public signature when applicable, and newline-normalized English content.
The exact serialization is defined in the detailed contract.

A translation manifest records the English `sourceHash` it reviewed. A
translation is current only when:

1. its recorded source hash equals the freshly computed English source hash;
2. its state is `approved`;
3. its required approval records name human reviewers and the same source hash;
4. required terminology and executable-example checks pass.

Any English change creates a hash mismatch and deterministically changes the
translation state to `stale`. Editing a translation does not update its reviewed
source hash automatically.

### Manifests, glossaries, and review

One project manifest declares project-neutral inputs and supported locales. One
unit manifest records stable IDs, canonical sources, translation paths, hashes,
states, and review evidence. Locale glossaries bind stable concept IDs to
preferred terms, disallowed ambiguous alternatives, context, and authoritative
references.

Allowed translation states are `missing`, `draft`, `review`, `approved`,
`stale`, and `retired`. Automation may compute `missing` and `stale`, but it may
not grant `approved`.

Every approved translation requires editorial review. Units containing
mathematical claims, formulas, numerical tolerances, parameter semantics, or
executable examples additionally require a human mathematical/technical
reviewer. Machine translation or AI assistance may produce a draft, but it is
recorded as `draft` and never treated as review evidence.

### Locale builds, navigation, search, and fallback

The static site is built once per locale from the same stable page inventory.
Each locale has its own navigation and search index. Locale switchers resolve by
stable page ID or symbol ID, not by translating URLs heuristically.

Missing, draft, review, or stale content is not presented as a current
translation. The locale route renders an explicit fallback page or fragment
that identifies its state and links to the canonical English unit. English
fallback text is marked as English and excluded from the localized search index
where the generator supports fragment exclusion. Navigation never points to a
nonexistent page, and fallback never masquerades as translated content.

### Reuse boundary

The pipeline contract accepts project name, package names, source roots,
locales, site paths, branding assets, and glossary locations as configuration.
Drift detection operates on Markdown and statically discovered Python symbols;
it does not import FuzzyRoutines or depend on fuzzy mathematics. Reusable
implementation and templates belong to Task #207 after the FuzzyRoutines
pipeline has passed its own build and drift gates.

## Consequences

- Canonical English remains close to code and mathematical source material.
- Locale content can evolve editorially without duplicating Python docstrings.
- Hash mismatches make translation debt measurable and fail closed.
- Stable IDs allow file moves and localized titles without breaking locale
  relationships.
- Separate locale indexes prevent Russian, Chinese, and English search results
  from becoming one ambiguous corpus.
- Human mathematical review adds deliberate latency but prevents fluent text
  from being mistaken for validated mathematics.
- Manifests and glossaries add maintained metadata. Task #204 established the
  English API inventory and documentation gates; Task #255 implements locale
  manifests, glossaries, review-state validation, and source-hash drift gates
  before translations can be approved.
- Tasks #203, #204, and #206 establish canonical English generation, English
  quality gates, and Pages publication with honest reserved-locale fallbacks.

## Rejected alternatives

### Translate Python docstrings in place

This would make source files multilingual, duplicate API contracts, complicate
static discovery, and make one language appear authoritative per checkout.

### Use paths or translated titles as identity

Paths and titles change during information-architecture and editorial work.
Binding translations to them would create false deletions and accidental
cross-language mismatches.

### Store translations without source hashes

Timestamps and Git history show when files changed, not whether a translator
reviewed the current English contract. Hash binding is deterministic and can be
checked offline.

### Publish stale translations until someone notices

An apparently complete but obsolete mathematical page is more dangerous than
an explicit English fallback. Stale content must be labelled and excluded from
the current translated corpus.

### Treat machine translation as approval

Language fluency does not prove mathematical correctness, parameter semantics,
or numerical validity. Automated assistance can accelerate drafts but cannot
replace accountable human review.

## Acceptance and supersession

This ADR is **Accepted**. Changes to the canonical language, stable-identity
rules, hash contract, approval model, or fallback semantics require a
superseding ADR. Concrete build tooling may be implemented by later Tasks
without superseding this decision when it preserves these invariants.
