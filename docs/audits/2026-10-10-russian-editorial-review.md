<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Russian editorial follow-up — 2026-10-10

## Scope and changes

Task #295 follow-up to the maintainer's provisional acceptance and report of
awkward Russian wording. Baseline: `86f4afcae4238b33a815f10bc5d1bb3710f4d0b5`.
The complete inventory contains 257 units (52 pages, 193 public symbols and
12 module overviews), represented by 206 physical Russian Markdown files;
public aliases share translated symbol files.

A deterministic corpus inventory and phrase search identified recurring
calques; a targeted AI-assisted editorial pass corrected 30 files:

- Describe derived properties as computed properties, avoiding an unintended
  association with mathematical differentiation.
- Replace literal “region” calques with mathematical-domain wording and
  clarify how constructors validate recorded subsets of sampled coordinates.
- Explain non-strict alpha-cut thresholds, inclusive integer ranges and
  evaluation at grid nodes in natural Russian.
- Rewrite confusing operator-choice, classification-threshold and quick-start
  sentences without changing the stated behavior.

The existing glossary's universe, positive support, core and integration-domain
terms remain unchanged. No Python, executable example, formula, numeric value,
link target, API field identity or explicit anchor changes are included.

## Validation and limits

- `python tools/locale_documentation.py validate`: PASS.
- Baseline comparison across all 206 physical files: fenced code, display and
  inline mathematics, API sections/fields, explicit anchors, numeric tokens and
  Markdown link targets preserved exactly under their existing protection rules.
- `git diff --check`: PASS.
- Focused locale tests: `tests/test_locale_documentation.py`, **14 passed**.
  The default Python 3.12 interpreter used the shared pure-Python pytest
  dependencies via `PYTHONPATH`; supported-runtime regression checks remain
  CI evidence. No package runtime or browser-layout result is claimed here.

This is an AI-assisted editorial correction, not a new human mathematical or
native-speaker approval. Translation-state and approval metadata are deliberately
unchanged. Any approval of the edited text must bind its final translation hashes
through the existing ADR-0011 workflow; prior draft review is not silently reused.
