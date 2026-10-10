<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Simplified Chinese editorial review — 2026-10-10

## Scope and authority

Task #296 follow-up on candidate `86f4afcae4238b33a815f10bc5d1bb3710f4d0b5`.
The manifest contains 257 Chinese units: 52 pages, 193 public symbol contracts
and 12 module overviews, backed by 206 distinct physical Markdown files.
Alias identities share physical contracts.

This is an **AI-assisted editorial and scientific assessment**, not a human
or native-speaker approval. Automated structural inspection covered the entire
manifest. Semantic reading focused on sensor combination, alpha cuts,
centroids, severity labels, scale diagnostics, finite-number policy,
normalization, convexity and linguistic-term contracts, including the affected
API docstrings. It does not claim an independent line-by-line human review of
all 257 units. Translation states and publication policy remain unchanged.

## Corrections

Seven physical files received ten prose-line corrections:

- Numerical regularity now uses **正则性**, replacing the literal **规则性**
  in centroid guidance, the convexity contract and callable API documentation.
- The centroid explanation describes coarse-grid sampling directly. The API
  caveat now describes local features that sampling fails to resolve rather
  than suggesting that the function has an unspecified "unsolved" feature.
- The linguistic-term contract explicitly says that failure to obtain the
  complete membership vector raises an error; the previous wording could be
  read as a mathematical partial-fraction vector.
- The scale guide uses **分割误差**, consistent with the mathematical contract,
  for deviation of the sum of grades from one. Partition of unity terminology
  remains unchanged.
- The future convexity test matrix describes enumeration over a small set of
  exact grade values directly, instead of a literal "grade alphabet". Its
  non-goals now clearly distinguish mathematical definitions from evidence
  requirements.

No formulas, examples, parameter names, exception identities, numeric values,
link destinations, API identifiers or review states changed.

## Scientific assessment

The inspected passages preserve the source distinctions: membership is not
probability; product conjunction does not establish independence; an exhaustive
discrete cut differs from a sampled continuous cut; positive support, relative
closure and core have separate endpoint rules; quadrature tolerances are not
proven centroid-coordinate error bounds. The documented normality convention
uses the supremum and need not imply a nonempty core. Convexity remains a
future API contract, and finite observations do not prove global convexity or
continuous coverage. No new mathematical claim or runtime behavior was added.

## Validation and remaining acceptance

- `python tools/locale_documentation.py validate`: **PASS**.
- Deterministic before/after comparison over all 206 physical files: **PASS**
  for `ProtectedPageParts` (fences and mathematics), `ProtectedApiContract`
  (API sections and fields), and token inventories for inline code, numeric
  literals, Markdown link destinations and ASCII identifiers.
- `python -m pytest -q tests/test_locale_documentation.py`: **14 passed**.
  The default Python has no pytest, so the focused run reused pure-Python
  dependencies from the existing cached environment through
  `PYTHONPATH=/workspace/scratch/30d2c29476e8/fr-camel-python/lib/python3.14/site-packages`.
  This is focused local validation, not a claim about the locked release SDK.
- No full regression suite or browser build was repeated for these prose-only
  edits. Integration CI remains authoritative for the merged candidate.

The edited Chinese corpus has SHA-256 index digest
`0a1557b25380fdd66e7ca6171d67221b0d1318cdfcadf2b8f5e413a887b56d53`.
The index is the UTF-8 concatenation, in sorted distinct manifest-path order,
of `SHA256(file bytes)`, two spaces, the repository-relative path and a newline.
This binds the assessment to the translated files without changing unit IDs.

ADR-0011 human editorial and mathematical/technical acceptance remains a
separate release requirement. This report neither supplies that acceptance nor
changes any unit to `approved`.

## Subsequent delegated acceptance

The human-acceptance-pending statement above records the policy and status at
the time of this earlier review. It is superseded for the 258 explicitly bound
zh-CN 2.0.0 hash pairs by the maintainer-authorized
[AI scientific/editorial acceptance](2026-10-10-chinese-delegated-acceptance.md)
and its narrow ADR-0011 exception. This does not retroactively claim that this
earlier report was human or native-speaker approval.
