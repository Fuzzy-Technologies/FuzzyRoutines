<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines Visual Identity

## Rationale

The FuzzyRoutines identity belongs to the mathematical library rather than the
general Fuzzy Technologies corporate mark. Its sign joins a crisp geometric
`F` to an `R` whose bowl and leg transition through layered membership curves.
The construction communicates the library's contract: explicit software
structure on the left, fuzzy mathematical behavior on the right.

The open `R` construction intentionally avoids a closed almond, eye, fish, or
lens silhouette. The primary path remains legible at favicon sizes; the two
lighter echoes add fuzzy-set depth at larger sizes without becoming required
for recognition.

## Asset set

| Asset                                       | Purpose                                      | View box     |
|---------------------------------------------|----------------------------------------------|--------------|
| `assets/favicon.svg`                        | Self-contained browser favicon               | `0 0 64 64`  |
| `assets/brand/fuzzyroutines-sign.svg`       | Reusable square sign for navigation and UI   | `0 0 64 64`  |
| `assets/brand/fuzzyroutines-horizontal.svg` | Product wordmark for landing and wide spaces | `0 0 520 96` |

Paths in this table are relative to `docs/api-evaluation/source/`. The favicon
duplicates the compact sign geometry deliberately so browsers receive one
self-contained file without an external SVG dependency.

## Color contract

| Token         | Value     | Role                                      |
|---------------|-----------|-------------------------------------------|
| Graphite      | `#101316` | Sign base and code-oriented product tone  |
| Deep graphite | `#0d0d0d` | Documentation background                  |
| Strong text   | `#e7f8ff` | Crisp geometry and primary wordmark       |
| Cyan          | `#66d9ef` | Exact structure entering the fuzzy range  |
| Violet        | `#9b7bff` | Transition between exact and fuzzy states |
| Pink          | `#ff79c6` | Fuzzy curve endpoint and interaction      |
| Green         | `#50fa7b` | Keyboard focus and verified state         |

Do not recolor the compact sign with unrelated palettes, close the curved `R`
into a lens, add glow filters, or place detail behind the monogram. Preserve
the graphite base and minimum clear space equal to one quarter of the sign's
width.

## Usage

- Use the compact sign at 16, 32, and 64 CSS pixels.
- Use the horizontal wordmark only at widths of 240 CSS pixels or greater.
- Keep `FuzzyRoutines` as semantic HTML text in page titles and navigation;
  the SVG wordmark is decorative brand reinforcement, not a text replacement.
- Keep the Fuzzy Technologies motto as real footer text rather than embedding
  it in this product-specific logo.
