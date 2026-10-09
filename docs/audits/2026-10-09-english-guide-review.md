<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Canonical English guide review — 2026-10-09

This wave implements the English quick start, eight worked scenarios, a
membership gallery, practical API recipes, and reproducible SVG figures for
Tasks #280 and #294. It starts from merged `develop` commit
`bd239d2b0972a796c4084498676042bdb7016bed`. It changes documentation, executable
examples, validators, and CI integration; it introduces no public runtime API.

These are **AI-assisted review passes**, not independent human or native-language
approvals. The English source hashes are recorded in `docs/i18n/units.toml`.
Russian and Simplified Chinese units remain missing. No locale is marked
approved by this work, and this report does not declare stable-release readiness.

## Engineering pass

Installation distinguishes moving `develop` from the future published 2.0.0
package; older PyPI code is not presented as providing the modern API. Every
scenario declares units or a score range. Different sensor universes combine
scalar grades; set compositions use the same universe. Invalid domains,
zero-area centroids, generic-callable limits, and adaptive exhaustion are
explained where they affect a reader's decision. No rule engine, fuzzy-number
arithmetic, automatic backend selector, or empirical calibration is invented.

The scenario CLI and Python fences run independently. Full wheel/sdist and
supported-version checks belong to CI. Plotting dependencies are pinned in a
separate documentation requirements file and are absent from runtime metadata.

## Scientific pass

Independent calculations check the two temperature grades, severity grades,
four scalar operator combinations, directed difference, weak alpha-cut boundary,
triangle centroid, disjoint-triangle area moments, and the custom linear model's
integrals. The triangle oracle is $10/3$; the composed-set oracle is $44/9$;
the custom linear centroid is $200/3$. The explicit four-point trapezoidal
calculation differs from the analytical triangle centroid by $2/9$.

The prose distinguishes exact discrete exhaustiveness, analytical continuous
geometry, and finite-grid observations. It does not equate floating-point tail
underflow with mathematical support, statistical probability with membership,
or moment tolerances with a proven centroid-coordinate error bound. Continuous
comparison certifies only its declared finite coordinates. These checks cover
the new examples; the all-module mathematical audit remains Task #298.

## Data-science pass

Intermediate grades accompany label selection. Minimum confidence is described
as a membership threshold, not calibrated confidence. Tie ordering, abstention,
coverage gaps, and the sample-dependent gap fraction are visible. Parameters
are labelled illustrative expert choices. No accuracy, calibration, or predictive
performance claim is made without data. The reader can copy computations into
their own project without importing plotting packages.

## Editorial and reader pass

The route is installation → a short physical example → eight scenarios → API
recipes/reference. Each scenario states its question, gives expected numbers,
explains the figure, and identifies a practical use and limitation. All eight
membership families have an executable assertion and a gallery description.
Images have meaningful alternatives and text equivalents. SVGs retain text,
descriptive titles, fixed metadata, and a reproducible toolchain.

The generated PNG previews were inspected for labels, clipping, spacing, and
contrast. Mathematical prose uses GitHub-compatible dollar-delimited math;
strict rendered documentation and anchor checks run in CI. This review must not
be interpreted as human approval of the final rendered multilingual release.

A [second scientific figure review](2026-10-09-figure-verification.md) independently
checks all plotted curve data and key markers, records presentation corrections,
and establishes shared English-labelled SVGs with localized explanations.

## Remaining M6 work

- Complete per-symbol example coverage and the final canonical-English review
  under #294; these recipes do not assert every result property has its own example.
- Translate the finalized English source and perform separate Russian and
  Simplified Chinese scientific/editorial reviews under #295 and #296.
- Require complete fresh hashes, approved locale states, and rendered language
  parity under #297; a valid inventory alone is not translation completeness.
- Complete the independent all-module mathematical, modern coverage, and
  parallel-test audit under #298.
- Finish approved stable metadata/tag/release and CI-only PyPI publication,
  with installed published-package evidence, under #299 and #121.

Tasks #280 and #294 therefore remain open after this incremental wave. Release
urgency does not waive their remaining acceptance criteria.
