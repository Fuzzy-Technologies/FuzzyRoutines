<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0022 acceptance fixtures

These are review inputs for the [plotting contract](../0022-scientific-plotting-and-export.md),
with expected data derived from the existing scalar API and independent
values. The rendering assertions are for [#394](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/394);
there is no new renderer to run in this change.

## Inspect artist data before serialization

| Input                                                                  | Expected evidence                                                                                                                                                                                                                                                                                                                                                                                                   |
| ---                                                                    | ---                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `CreateUniversalFuzzyScale()` on `[0, 1]`, input `x = 0.17`            | Curves, legend and bars use `Min, Low, Med, High, Max` with the five ADR colors. At `0.17`, the ordered grades are `(1 / (1 + (8 × 0.17)^20), 0, 0, 0, 0)`. Use absolute tolerance `1e-12`, relative tolerance zero. With `minimumConfidence=0.1` the outcome is no match; with the historical policy it is `Min`. On the `Min` curve at `0.5`, the grade is positive despite the centroid window ending at `0.23`. |
| Closed `[0, 1]`, `Triangle(0, 0.37, 1)`, base count `4`, input `0.41`  | Keep the four base coordinates and add `0.37` and `0.41`. The apex grade is exactly `1`; the input marker and bar are `(1 - 0.41) / (1 - 0.37)`. Compare the plotted values with the scalar evaluator at those coordinates.                                                                                                                                                                                         |
| Open left, closed right `(-1, 1]`, `Triangle(-1, 0, 0)`                | The callback is never evaluated at `-1`; the known limit there is `0`. The included value at `0` is `1` and the right limit is `0`. Draw a filled point at `(0, 1)` and an open point at `(0, 0)`, with no stroke connecting the two. Anchor grades at `-0.5` and `0.5` are `0.5` and `0`.                                                                                                                          |
| Discrete points `(0, 0.4, 1)`, grades `(0, 0.7, 0.5)`, threshold `0.5` | Evaluate only the three declared coordinates. Include the zero grade and draw unconnected marks. The exact weak cut contains `(0.4, 1)`; do not draw an interval between them.                                                                                                                                                                                                                                      |
| Unbounded Gaussian and a custom callable with an undeclared jump       | The unbounded set requires a finite view. A custom callable of unknown continuity draws markers only. Once the caller declares the jump, segments still do not bridge it; do not invent a one-sided limit.                                                                                                                                                                                                          |

The existing scalar and compatibility suite can verify the model assumptions
before any renderer is introduced. From the repository root, run:

```bash
python -m pytest -q tests/test_modern_scale_preset.py \
  tests/test_universal_fuzzy_scale_regression.py tests/test_domain_model.py \
  tests/test_membership_function_contracts.py tests/test_custom_membership_protocol.py \
  tests/test_alpha_cuts.py
```

## Inspect exports in a clean installation

Use a temporary output directory with a space and Unicode in its path,
for example `review figures/温度`. Render headlessly with the documentation
[plot lock](../../requirements-plots.txt) and record interpreter, font,
renderer and encoder identities. With default single-panel sizing:

| File or request                                              | Assert                                                                                                                                                                                                              |
| ---                                                          | ---                                                                                                                                                                                                                 |
| `membership.png`, transparent                                | PNG signature; `1728 × 848` pixels; an empty corner with alpha zero. The opaque default has the corporate canvas color at an empty corner.                                                                          |
| `membership.jpg`, opaque background `#ffffff`                | JPEG signature; `1728 × 848` pixels; decodes as RGB. Check an empty corner is white within one code value per channel, allowing encoder rounding. Missing background or transparency request fails without writing. |
| `membership.svg`, text mode                                  | XML root is SVG and viewBox is `0 0 777.6 381.6` in points. Label text such as `Temperature (°C)` survives in a text element. Creator is fixed and no date appears in metadata.                                     |
| `membership.svg`, path mode, separate run                    | SVG contains path outlines for the label in place of selectable text. Geometry and physical dimensions remain the same.                                                                                             |
| Second export with a different basename                      | Compare complete bytes for each format in the same environment. The destination and its name do not become metadata.                                                                                                |
| A collision, missing parent or conflicting format and suffix | Fail with the relevant path or format in the error; a prior file's bytes remain intact. A renderer error also leaves an existing file intact under explicit overwrite.                                              |

For [#395](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/395),
repeat the checks through the project-file CLI with one explicit command
per format. The model supplies data, not code to execute.
