<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Multilingual Documentation Architecture

- Status: accepted design from Task #205; implemented by Task #255
- Decision: [ADR-0011](../adr/0011-multilingual-documentation-pipeline.md)
- Generator foundation: [ADR-0010](../adr/0010-api-documentation-architecture.md)
- Initial locales: `en`, `ru`, `zh-CN`

## Scope boundary

This document specifies the tracked inputs and deterministic state transitions
implemented by Task #255. It does not create translations or a translation
service. Russian and Simplified Chinese remain explicit `missing` states until
accountable human review approves native editorial content.

## Repository layout

The production documentation implementation uses this layout without moving
existing English documents unnecessarily:

```text
docs/
├── site/
│   ├── mkdocs.yml
│   ├── content/
│   │   ├── en/                  # canonical narrative Markdown
│   │   ├── ru/                  # reviewed Russian pages
│   │   └── zh-CN/               # reviewed Simplified Chinese pages
│   └── assets/                  # shared, language-neutral theme assets
├── i18n/
│   ├── project.toml             # reusable project inputs and locale policy
│   ├── units.toml               # page/symbol identity and translation state
│   ├── symbols/                 # translated API-symbol Markdown fragments
│   │   ├── ru/
│   │   └── zh-CN/
│   └── glossaries/
│       ├── ru.toml
│       └── zh-CN.toml
└── api-evaluation/              # Task #198 evidence, not production input
```

Generated output remains outside this tree:

```text
_build/docs/<version>/en/
_build/docs/<version>/ru/
_build/docs/<version>/zh-CN/
```

Task #206 owns the public URL and Pages artifact layout. The generated path
above remains a local contract and does not redefine deployment URLs.

## Stable identifiers

### Page IDs

A page ID uses lowercase ASCII segments separated by dots and prefixed with
`page:`:

```text
page:index
page:mathematics.fuzzy-set.operations
page:compatibility.historical-api
```

The ID is stored in the unit manifest. A path or page title may change while the
ID remains stable. Splitting one page creates new IDs; the old record is marked
`retired` with replacements. Merging pages similarly retires old IDs rather
than reassigning them.

### Symbol IDs

Public API symbols use the fully qualified Python name discovered statically by
Griffe and prefixed with `symbol:`:

```text
symbol:fuzzyroutines.fuzzysets.ScalarFuzzySet
symbol:fuzzyroutines.fuzzysets.ScalarFuzzySet.Membership
```

Historical aliases keep their own symbol IDs and may declare `aliasOf`. This
preserves compatibility documentation without presenting an old name as the
canonical modern symbol.

English symbol content is extracted statically from source annotations and
docstrings. An approved translated symbol body is a Markdown fragment under
`docs/i18n/symbols/<locale>/`, referenced by the unit manifest and composed into
the locale API page at build time. It never replaces or shadows the English
docstring in Python source.

### Concept IDs

Glossary concepts are language-independent and prefixed with `concept:`:

```text
concept:fuzzy-set.core
concept:fuzzy-set.positive-support
concept:numerical.integration-domain
```

The concept ID, not the English spelling, joins equivalent terminology across
locales.

## Canonical source hash

Every translatable unit is hashed independently. The digest is lower-case
SHA-256 written as `sha256:<64 hexadecimal characters>`.

Before hashing, text is decoded as UTF-8, a leading byte-order mark is rejected,
and CRLF/CR newlines are normalized to LF. Trailing spaces and final newlines
are preserved because they remain source changes.

The versioned payload is:

```text
fuzzy-doc-unit-v1\n
id:<stable-id>\n
kind:<page|symbol>\n
signature-length:<UTF-8-byte-count>\n
<public-signature-or-empty>\n
body-length:<UTF-8-byte-count>\n
<canonical-English-body>
```

For a page, the body is the complete canonical English Markdown file and the
signature is empty. For a symbol, pinned Griffe extracts the public signature
and English docstring without importing the package. Including the signature
makes a parameter, default, or return-annotation change stale even when prose
was not updated.

Hashing never reads rendered HTML. Generated output cannot become a source of
truth.

## Project manifest

`docs/i18n/project.toml` contains reusable project inputs:

```toml
schemaVersion = 1
projectId = "fuzzyroutines"
projectName = "FuzzyRoutines"
sourceLocale = "en"
locales = ["en", "ru", "zh-CN"]
packageNames = ["fuzzyroutines"]
contentRoot = "docs/site/content"
unitManifest = "docs/i18n/units.toml"
buildRoot = "_build/docs"

[branding]
organization = "Fuzzy Technologies"
assetRoot = "docs/site/assets"
```

Another project supplies its own values. Generic validation must not contain a
hard-coded FuzzyRoutines import, package name, site path, or product title.

## Unit manifest

`docs/i18n/units.toml` is the authoritative inventory. A representative record
is:

```toml
schemaVersion = 1

[[units]]
id = "page:mathematics.fuzzy-set.operations"
kind = "page"
sourcePath = "docs/site/content/en/mathematics/fuzzy-set-operations.md"
sourceHash = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
reviewClass = "mathematical"

[units.translations.ru]
path = "docs/site/content/ru/mathematics/fuzzy-set-operations.md"
state = "approved"
title = "Операции над нечёткими множествами"

[[units.translations.ru.reviews]]
role = "editorial"
reviewedSourceHash = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
reviewer = "editorial-reviewer-handle"
reviewedAt = "2026-09-18T00:00:00Z"

[[units.translations.ru.reviews]]
role = "mathematical"
reviewedSourceHash = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
reviewer = "mathematical-reviewer-handle"
reviewedAt = "2026-09-18T00:00:00Z"

[units.translations.zh-CN]
state = "missing"
```

Required fields by unit kind are:

| Field                  | Page        | Symbol      | Meaning                                       |
|------------------------|-------------|-------------|-----------------------------------------------|
| `id`                   | required    | required    | Stable page or fully qualified symbol ID      |
| `kind`                 | required    | required    | `page` or `symbol`                            |
| `sourcePath`           | required    | derived     | English page path or statically found source  |
| `sourceHash`           | required    | required    | Fresh canonical English payload digest        |
| `reviewClass`          | required    | required    | `editorial`, `technical`, or `mathematical`   |
| `aliasOf`              | n/a         | optional    | Canonical symbol ID for a historical alias    |
| translation `path`     | conditional | conditional | Locale page or symbol-fragment path           |
| translation `state`    | required    | required    | State-machine value                           |
| translation `reviews`  | conditional | conditional | Role-specific human approval records          |
| `reviewedSourceHash`   | conditional | conditional | Hash explicitly approved by that reviewer     |
| review `reviewer`      | conditional | conditional | Accountable human reviewer identity           |
| review `reviewedAt`    | conditional | conditional | UTC review timestamp                          |

Conditional translation paths are required whenever locale content exists.
Every approved translation requires the review records selected by its review
class, and every such record requires its hash, reviewer, role, and timestamp.

## Translation states

| State       | Meaning                                                       | Publish as translated? |
|-------------|---------------------------------------------------------------|------------------------|
| `missing`   | No locale content exists                                      | no                     |
| `draft`     | Translation is being written                                  | no                     |
| `review`    | Draft awaits required human review                            | no                     |
| `approved`  | Human review covers the current source hash                   | yes                    |
| `stale`     | English source hash changed after translation/review          | no                     |
| `retired`   | Canonical unit was deliberately removed, split, or superseded | no                     |

Only a human review action may move `review` to `approved`. Drift automation
may move `approved` to `stale`, and inventory automation may identify
`missing`. No tool adds a review record or updates `reviewedSourceHash` merely
because a file exists.

## Glossaries

Each target locale has one TOML glossary keyed by stable concept ID. A record
contains the canonical English term, preferred translation, prohibited or
discouraged alternatives, scope note, and references:

```toml
schemaVersion = 1
locale = "ru"

[[terms]]
id = "concept:fuzzy-set.positive-support"
english = "positive support"
preferred = "положительный носитель"
avoid = ["область интегрирования"]
note = "Coordinates where membership is strictly positive; not a numerical integration interval."
references = ["docs/mathematics/universe-support-contract.md"]
```

The Simplified Chinese glossary uses the same IDs and records preferred Chinese
terms; it may also retain the canonical English term in parentheses where the
editorial standard requires it. Glossary validation detects duplicate IDs,
missing preferred values, prohibited terminology, and references to unknown
concepts. A glossary change requires locale editorial review; mathematical
concept changes require mathematical review.

## Deterministic stale detection

Task #204 implemented English public-API inventory, documentation coverage,
repository-link, rendered-anchor, and generated-output gates. Task #255 adds
the tracked locale manifests and glossaries and performs these steps without
network access:

1. statically inventory canonical English pages and public symbols;
2. require exactly one active manifest record per stable ID;
3. recompute every canonical source hash using the versioned payload;
4. validate every locale path, state, glossary reference, and review record;
5. classify a translation as `stale` when its reviewed hash differs from the
   fresh source hash;
6. reject `approved` when the file, reviewer, timestamp, matching hash, or
   required glossary/review evidence is absent;
7. emit deterministic diagnostics containing stable ID, locale, source path,
   translation path, expected hash, actual hash, and required action;
8. produce a machine-readable summary for build and release evidence.

The deterministic gate fails for malformed manifests and falsely approved
content. Translation incompleteness may remain non-blocking during development,
but release policy must define and report locale coverage explicitly. External
link health remains a separate non-deterministic report.

## Navigation and search

Each build receives the same ordered active page-ID inventory. Locale-specific
navigation titles come from approved locale metadata; missing titles fall back
to a visibly labelled English title. The locale switcher maps the current page
ID and fragment/symbol ID into the target locale.

Search is built separately for `en`, `ru`, and `zh-CN` so stemming, tokenization,
and ranking do not mix languages. A localized index contains only approved
locale content. Explicit English fallback blocks use `lang="en"` and the
generator's search-exclusion marker. Search results may offer a separate link
to English, but they must not label English prose as a Russian or Chinese hit.

## Missing and stale fallback

Every active page ID produces a route in every locale build:

- `approved`: render the reviewed translation;
- `missing`, `draft`, or `review`: render a locale-language status page with a
  direct link to the canonical English unit;
- `stale`: render a warning with both the last reviewed hash and current source
  revision, then link to English;
- `retired`: redirect only when an explicit replacement ID exists; otherwise
  render a retirement notice.

Fallback is explicit and fail-closed. It never copies English into a translated
file, mutates manifest state, hides staleness, or produces a broken navigation
target.

## Human review contract

| Review class   | Required review                                           |
|----------------|-----------------------------------------------------------|
| `editorial`    | Native-language editorial reviewer                        |
| `technical`    | Editorial reviewer plus relevant engineering reviewer     |
| `mathematical` | Editorial reviewer plus fuzzy/numerical subject reviewer  |

One person may satisfy multiple roles only when the review record states that
responsibility explicitly. Mathematical review covers formulas, variable
meaning, domains, boundary behavior, tolerances, examples, and glossary usage.
Executable examples must also pass the language-independent clean-install test
gate; translated prose cannot override executable results.

Automated or AI-assisted translation is permitted only as draft provenance.
It cannot populate `reviewedBy`, advance state to `approved`, or waive a
mathematical reviewer.

## Transfer to other Fuzzy Technologies projects

A reusable implementation consumes only:

- the project manifest;
- canonical Markdown and statically discoverable Python sources;
- the unit manifest and locale glossaries;
- project-supplied branding and navigation metadata.

Project-specific mathematical text, FuzzyRoutines imports, existing product
URLs, and generated HTML are not reusable pipeline code. Task #207 can extract
the configuration schema, validator contract, templates, and adoption guide
after Task #255 is merged and its drift gate is proved on `develop`. Tasks
#203, #204, and #206 establish the English build, English quality gates, and
safe publication boundary; they do not by themselves prove the full
translation pipeline.

## Task boundaries

| Task                   | Responsibility                                                               |
|------------------------|------------------------------------------------------------------------------|
| #200                   | Complete canonical English production docstrings                             |
| #203                   | Build the canonical English API reference                                    |
| #204                   | Implement English API inventory, coverage, link, and generated-output gates  |
| #205                   | Own this multilingual architecture decision                                  |
| #206                   | Publish English Pages plus honest reserved-locale and version routes         |
| #255                   | Add manifests, glossaries, review state, source hashes, and drift validation |
| #207                   | Extract and validate the reusable Fuzzy Technologies blueprint               |

Bulk translation is intentionally outside Tasks #205, #206, and #255.
Translation work begins only after canonical English units, stable IDs,
manifests, validation, and human review ownership exist.
