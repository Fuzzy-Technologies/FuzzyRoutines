<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0016: Explicit Linguistic Encodings and Historical Preset

- Status: Accepted on merge
- Date: 2026-10-14
- Related tasks: [#325](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/325), [#326](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/326)
- Related Feature: [#319](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/319)

## Context

Applications need a modern way to reuse the historical Universal Fuzzy Scale
and turn linguistic inputs or numeric predictions into model features. A label,
a vector of membership grades, a representative coordinate, and a learned
network weight have different meanings. Implicit normalization, zero for an
unknown label, clipping out-of-domain predictions, or substituting full-universe
centroids for historical per-term windows would change consumer mathematics.

## Decision

`CreateUniversalFuzzyScale()` returns a fresh immutable `LinguisticScale` with
the original Min/Low/Med/High/Max coefficients and closed `[0, 1]` universes.
`UniversalFuzzyScalePolicy()` supplies last-exact-maximum selection with zero
tie tolerance and no extra confidence threshold. Generic defaults and the
legacy `UniversalFuzzyScale` import are unchanged.
`UniversalFuzzyScaleDomains()` supplies the five original centroid windows in
term order; these bounds never clip membership evaluation.

The frozen framework-neutral `LinguisticCodec` explicitly receives a scale,
one `IntegrationDomain` per term, a `FuzzificationPolicy`, and an optional
`CentroidPolicy`. It has no learned state, caches or neural dependencies.
Custom callbacks retain their original ownership and purity constraints.

| Operation                | Input                        | Output                                      |
| ------------------------ | ---------------------------- | ------------------------------------------- |
| `EncodeLabel`            | Exact case-sensitive label   | Centroid on that term's explicit window     |
| `EncodeMemberships`      | One scalar coordinate        | Ordered length-N tuple of membership grades |
| `DecodePrediction`       | One scalar prediction        | Complete `FuzzificationResult` evidence     |
| `AverageRepresentatives` | Ordered length-N grade tuple | Grade-weighted representative coordinate    |

`termNames` supplies vector column order. There is no batch dimension, fitted
normalization, automatic physical-unit conversion or implicit clipping. Unknown
labels, wrong shapes, non-finite values and out-of-universe predictions fail
explicitly. Prediction ties and no-match outcomes follow the supplied policy.
Membership grades remain independent bounded grades, not probabilities.

For term centroids $c_i$ and grades $g_i$, representative averaging computes

$$
y=\frac{\sum_i g_i c_i}{\sum_i g_i}.
$$

The implementation accumulates exact rational representations of rational and
binary64 grades and computed centroids, then converts the final quotient to
binary64 once. Other real scalar types use their binary64 image. This avoids
intermediate overflow and premature underflow of meaningful contributions. It
requires a positive denominator and defined centroids only for positive-grade terms.
Zero-grade terms contribute zero. Zero area in an active term and unresolved
quadrature propagate the scalar centroid's specific errors.

This average is **not** the centroid of an aggregated fuzzy set. An aggregate
requires its own declared implication/aggregation operations and integration
domain. For two disjoint triangles with areas 1 and 2, centres 1 and 4, and
grades both 1, representative averaging yields 2.5; the centroid of their
maximum-union is $(1\cdot1+2\cdot4)/3=3$.

Encoding/decoding is generally lossy and not invertible. In particular, the
centroid of one term can belong more strongly to another. Centroids are
representatives for inputs or targets; training determines network weights.

## Evidence and compatibility

Independent piecewise formulas, adjacent-float boundaries, a 1001-point grid,
historical facade parity, centroid-window checks and invalid-input tests cover
the preset. Analytical triangle references, grade-rescaling invariance,
zero-area/denominator tests and a non-invertible counterexample cover codecs.
Installed consumers and executable documentation exercise root imports and
typing. The explanatory plot is generated deterministically from the scalar
API, with independently established numerical expectations.

This additive contract preserves 2.0 behavior. Corrected 2.0 centroids do not
promise equality with sampled or stale cached values from 1.0.3. A downstream
decision's parity still requires consumer-specific migration evidence.

## Alternatives deferred or rejected

- Implicit probability normalization, clipping or default-zero unknown labels:
  rejected because they hide invalid observations or change semantics.
- A tensor/neural dependency in the core: rejected; optional integrations
  convert these explicit values at their own boundary.
- Calling representative averaging a fuzzy-set centroid: rejected because
  unequal areas already provide a direct counterexample.
- Batch, fitted preprocessing and trainable memberships: separate contracts
  and deliverables; this codec does not claim differentiability.
