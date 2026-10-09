<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Multilingual Documentation Architecture

- Status: accepted design from Task #205; validation from #255, rendering and release gates from #297
- Decision: [ADR-0011](../adr/0011-multilingual-documentation-pipeline.md)
- Generator foundation: [ADR-0010](../adr/0010-api-documentation-architecture.md)
- Initial locales: `en`, `ru`, `zh-CN`

## Scope boundary

This document specifies tracked inputs, deterministic state transitions and
three-language rendering. Automation may prepare explicitly labelled draft
artifacts; it never grants human approval. Stable tagged publication requires
every required Russian and Simplified Chinese unit to be current and approved.

The required corpus is all 34 canonical site pages, 16 existing mathematical
and migration documents, 193 public symbol units and 12 module overviews:
255 independently tracked units per locale. `externalPages` in the
project manifest binds the existing English source files to stable site routes,
avoiding a second canonical copy. Development protocols, ADRs, audit records,
benchmark reports and research provenance remain English engineering records;
they are outside the translated user corpus and remain linked as references.

`tools/build_api_reference.py` builds one wheel, then renders English, Russian
and Simplified Chinese in the isolated documentation environment. Static Griffe
extensions replace in-memory docstring bodies using validated external fragments;
Python source, signatures and installed package content remain unchanged.
Page paths and explicit source-language heading IDs remain stable across locales.
Language navigation stays on the current page. Search is built for each locale.

CI retains all three sites in a labelled review artifact. Production composition
copies a target locale only when all its units are approved; otherwise its public
route retains an explicit English fallback. A stable tag additionally runs
`python -m tools.locale_documentation validate --require-approved`, which rejects
missing, draft, review, stale and retired required content before artifact
publication. Ordinary PR validation permits honest draft progress.

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
_build/api-reference/locales/en/site/
_build/api-reference/locales/ru/site/
_build/api-reference/locales/zh-CN/site/
```

Task #206 owns the public URL and Pages artifact layout. The generated path
above remains a local contract and does not redefine deployment URLs.

## Shared scientific figures

The canonical teaching SVGs live in `docs/site/content/en/assets/figures/`.
Their embedded text is English for every locale. Russian and Simplified Chinese
pages reuse this set; they do not own translated SVGs. A locale build may copy
the assets into its generated output to preserve relative URLs, but copies must
remain byte-identical to the canonical source. Task #297 must verify asset
resolution and byte parity when translated publication is implemented.

Captions, Markdown image alternatives, and explanations belong to the page's
translation unit. Translate and review them, including the meaning of English
labels and units. Every numerical conclusion must remain available as prose.
The figure policy does not change source-hash binding or grant translation
approval. Current reserved-locale fallback pages do not establish translated
figure-publication evidence.

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

Public API symbols use the fully qualified Python name inventoried statically
from the source AST and rendered through Griffe, prefixed with `symbol:`:

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

### Module overview IDs

With `includeModuleDocstrings = true`, the inventory also includes the non-empty
module docstring of every declared API surface, including the package root.
Its ID is `module:<qualified-name>`; its kind is `module` and its signature is
the literal `module <qualified-name>`. It uses the same fragment directory,
hash-bound state and human-review requirements as symbols. Module overviews do
not increase callable API counts or require artificial executable examples.

Four historical constructors have one-line summaries that repeat their class
contracts. Rendering suppresses only those exact, explicitly listed summaries
when the class is translated. An edited or new constructor docstring fails the
locale build until its translation inventory is addressed; additional contract
facts cannot silently disappear. Signatures and displayed source stay intact.

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
kind:<page|symbol|module>\n
signature-length:<UTF-8-byte-count>\n
<public-signature-or-empty>\n
body-length:<UTF-8-byte-count>\n
<canonical-English-body>
```

For a page, the body is the complete canonical English Markdown file and the
signature is empty. For a symbol, the AST inventory extracts the public signature
and English docstring without importing the package. Including the signature
makes a parameter, default, or return-annotation change stale even when prose
was not updated.

For a module, the body is its AST docstring and the signature is
`module <qualified-name>`. An overview-only edit therefore invalidates that
unit independently of the callable symbols it introduces.

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
apiCoverageManifest = "docs/site/api-coverage.toml"
publicationPath = "/FuzzyRoutines"

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
reviewedTranslationHash = "sha256:abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
reviewer = "editorial-reviewer-handle"
reviewedAt = "2026-09-18T00:00:00Z"

[[units.translations.ru.reviews]]
role = "mathematical"
reviewedSourceHash = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
reviewedTranslationHash = "sha256:abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
reviewer = "mathematical-reviewer-handle"
reviewedAt = "2026-09-18T00:00:00Z"

[units.translations.zh-CN]
state = "missing"
```

Required fields by unit kind are shown below. Opted-in `module` units use the
Symbol column, with a `module:` ID and kind `module`; they cannot use `aliasOf`.

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

Every actual approval record also requires `reviewedTranslationHash`, a SHA-256
digest of the normalized UTF-8 translated text. Editing the translation after
review therefore invalidates approval even when English is unchanged. Drafts
record `sourceHash` to detect changes to their source while work is in progress.
The illustrative digests above must be replaced with actual source and
translation digests during human review. AI-assisted passes remain draft
preparation and do not populate human reviewer records.

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
preferred = "носитель нечёткого множества"
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

The extracted configuration templates, adoption sequence, upstream-tool
upgrade boundary, and TKSBrokerAPI migration guidance are published in the
[Fuzzy Technologies documentation blueprint](../documentation-blueprint/README.md).
The validator derives target locales and glossary paths from the project
manifest; the independent `sampleproject` dry-run proves static discovery
without importing either FuzzyRoutines or the fixture package. The canonical
language, stable identity, hash payload, human review, and fail-closed fallback
invariants remain unchanged, so this extraction does not require a new ADR.

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
