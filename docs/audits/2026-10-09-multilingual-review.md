<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Multilingual documentation review — 2026-10-09

## Scope and authority

PR #304 implements Tasks #295–297 after the canonical English work in #302.
The required corpus has **257 units per locale**: 52 user pages, 193 public
symbol contracts and 12 module overviews. The 52 pages include the existing
mathematical model, 13 mathematics chapters, two migration guides, compatibility
and public typing. Aliases share physical translated docstrings; they are not
separate implementations. The unit manifest binds every draft to its exact
canonical source hash.

ADRs, historical benchmark records, contributor protocols, audit reports,
licensing/provenance evidence and internal implementation-status records remain
English engineering records. User pages link to them where their original
evidence is relevant. They are not silently counted as translated user guides.

These are **AI-assisted** engineering, scientific, data-science and editorial
passes. They are not independent human, native-speaker or release approval.
All Russian and Simplified Chinese units remain `draft`. ADR-0011 requires
accountable editorial and technical/mathematical review bound to both the
English source hash and the translation hash before stable publication.

## Engineering and canonical English corrections

Reviewing the external chapters against the implemented modern API exposed
stale statements that were corrected before translating their final text:

- The finite-number policy now distinguishes historical `int`/`float` and
  `ValueError` contracts from modern `numbers.Real`/`Fraction` inputs and the
  modern type/domain error categories. Callback exceptions remain unchanged.
- Zero area is defined on the declared integration domain. It is not a claim
  about the model's entire positive support.
- Universe/support and membership contracts describe the already implemented
  modern objects and shared analytical core, rather than a future migration.
- Normalization uses the frozen analytical snapshot; it does not reconstruct
  a mutable historical `MFunction`. No automatic backend selection is implied.
- Adaptive centroid integration applies to other analytical families and
  generic callables, not only to historical evaluators.
- Migration notes now identify public typing as implemented, while retaining
  the separate final-candidate evidence requirement.
- `MembershipFunction` constructor parameter/error documentation was moved
  into its canonical class contract so it receives the same translation and
  hash checks as the rest of that class. Its runtime behavior is unchanged.

Static Griffe discovery changes only rendered docstring text. Python source,
identifiers, annotations, signatures and examples remain English and unchanged.
Only five enumerated redundant constructor summaries may be suppressed; a new
untracked constructor contract fails rather than disappearing from translation.

## Scientific and data-science passes

All locale units are checked for preservation of fenced code, display and
inline mathematics, API sections and parameter/exception field identities.
This prevents accidental formula or executable-example translation. It cannot
prove that every translated prose claim is semantically correct.

The reader/scientific second pass specifically revisited quick start, alpha
cuts, centroids, sensor combination, finite-number and numerical-edge policy,
the mathematical model and compatibility/typing contracts. The prose retains
these distinctions:

- membership is not probability; product conjunction does not prove
  probabilistic independence;
- sensors may have different physical universes before their dimensionless
  grades are combined; set operations require a common universe;
- an exact discrete alpha cut enumerates the declared points; grid observations
  do not establish the exact continuous cut;
- positive support, its closure and the core have different endpoint rules;
- integration bounds, adaptive tolerance and sampling error are explicit;
  quadrature tolerance is not presented as a proven centroid error bound;
- sampled height/partition diagnostics do not certify continuous properties;
- the optional NumPy experiment is not an automatic runtime backend, and the
  scalar library is not presented as a multivariable inference engine.

The eight installed scenarios and 29 executable guide blocks remain canonical
English code. They cover all 193 public symbol identities through the existing
usage gate. The ten scientific SVGs retain English labels and identical bytes
in all three locales. The translations supply captions, alternatives and
interpretation. No new numerical curve was generated in this PR.

## Russian reader/editor pass

Terminology uses «универсальное множество», «множество поддержки», «ядро» and
«область интегрирования» consistently with the glossary and the maintainer's
requested support term. The alpha-cut explanation distinguishes «точный
дискретный срез» from sampled observations. Reader routes explain the physical
inputs, expected grades and practical limits before linking to the API.
Names such as `positiveSupport`, policy identifiers and English figure labels
remain literal so a reader can match prose, source and graphs.

## Simplified Chinese reader/editor pass

The corresponding distinctions use 论域, 模糊集的支集, 核, 积分域, 隶属度 and
α-截集. Explanations distinguish language terms from probabilities and explain
why a finite sample does not establish a continuous certificate. Code, units
and mathematical notation remain the canonical ones. This editorial pass does
not certify native-speaker acceptance; that review remains explicitly pending.

Browser review found that an apparently successful Chinese build could have an
unusable Chinese search index. The pinned documentation environment lacked
Material's `jieba` segmenter. The dependency is now pinned alongside the
existing compatible setuptools pin. A real one-page Chinese MkDocs test checks
the segmented term, and every Chinese build rejects an unsegmented index.
This dependency is documentation-only. Material's
[search segmentation contract](https://squidfunk.github.io/mkdocs-material/plugins/search/#segmentation)
describes the integration.

## Rendered review and evidence

The initial visual review used the actual CI preview for commit
`64b5c382942f0ca8bc11e6ae2b20c71b03c1b474`,
[run 37977852703](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/37977852703),
artifact `fuzzyroutines-pages-preview` (ID `11639039114`). Its ZIP SHA-256 was
`9bc161d1f90d69252e455e934a4d528032858be5ee8af8a09db730aad968488c`.

Chromium 153 inspected quick start, membership API, the mathematical model,
workflow diagrams, compatibility and public typing in all three locales at
1440 × 1000 and 390 × 844. All 18 pages had no broken image or page-level
horizontal overflow. Code and wide tables retain their own scrolling areas.
The 86 mathematical-model expressions and three introductory membership
expressions rendered in each locale without MathJax errors. The three workflow
diagrams were visually inspected. Language alternatives keep the same route.
English and Russian search queries returned results; the failed Chinese query
led to the segmentation repair above. Final-head Chinese query verification
and CI links are recorded in the PR after rebuilding.

The local browser needed its environment's normal TLS proxy for CDN resources
and an actual CJK font for Chinese glyphs. The review used the unchanged CDN
scripts and a local Noto Sans CJK font; those environment provisions do not
change the distributed site. Visual review also found two English navigation
labels and the default English preview-warning title. Those UI labels are now
localized. Shared English scientific labels remain intentional.

The same source revision passed all nine PR workflows. Its Python 3.14 audit
reported 1,214 passed and seven skipped tests with exact sequential/process
identity and outcome parity, zero failures, process errors or timeouts.
Full regressions, packaging, clean installed examples and full documentation
builds ran in CI. Only affected locale/API/style tests ran locally.

This is development evidence, not the final `2.0.0` candidate approval. The
remaining human review, exact-candidate CI and actual protected publication
belong to Tasks #295–299 and #121. Public locale routes retain explicit
fallbacks until approval; the review artifact exposes the complete drafts with
visible banners. No release tag or publication is authorized by this report.
