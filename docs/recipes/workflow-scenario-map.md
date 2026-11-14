<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Practical fuzzy workflow map

This map fixes the ten scenarios for [Feature #368](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/368).
Every input below is synthetic. Several are reused from the linked executable
guides, which contain the full models. Other rows specify small reference cases
for future recipes. The expected outputs are acceptance anchors, not evidence
of suitability for operational decisions. Membership grades are not event
probabilities.

[Русский (review draft)](workflow-scenario-map.ru.md) ·
[简体中文 (review draft)](workflow-scenario-map.zh-CN.md)


| Workflow                             | Capability and reference                                                                                                                  | Synthetic input and expected result                                                                                                                                                            | Figure or report                                                                                                                |
|--------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| 1. Measurement levels                | [Scalar linguistic scale][temperature]                                                                                                    | At 24 °C, `Comfort = 2/3` and `Warm = 1/8`; select `Comfort`. Keep both grades.                                                                                                                | Mark the measurement on both membership curves.                                                                                 |
| 2. Risk scoring                      | [Fuzzification with abstention][severity]                                                                                                 | A severity index of 65/100 yields `Moderate = 0.4`. At a minimum confidence of 0.45 the policy returns no match and retains the grades.                                                        | Show grades beside the threshold. This is a policy illustration for an input score.                                             |
| 3. Alert triage                      | [Directed fuzzy difference][alert]                                                                                                        | At 100 °C, warning grade 1 and critical grade 0.5 yield warning-without-critical grade `min(1, 1 − 0.5) = 0.5`.                                                                                | Plot warning, critical and residual curves. This illustrates queue triage for a synthetic monitor.                              |
| 4. Fan control                       | [Mamdani activation, aggregation and centroid][inference]                                                                                 | Normalized thermal demand 0.25 fires two ramp rules at 0.75 and 0.25. Min activation and max aggregation give centroid `37/96`, or about 38.54% of a normalized duty range.                    | Shade the aggregate and mark its centroid. Treat the result as an illustrative command before plant constraints.                |
| 5. Multicriteria scoring             | [Sugeno with explicit weights][inference]                                                                                                 | Criteria 0.25 and 0.75 give antecedent grades 0.75 and 0.25 in the two-rule example. Weights 0.5 and 1 give normalized strengths 0.6 and 0.4; consequences 0.2 and 0.625 give `0.37`.          | Show the two contributions. The value is a model-defined score.                                                                 |
| 6. Sensor quality                    | [Grade combination][sensors]                                                                                                              | If 80 °C and 10 mm/s give criterion grades 0.5 and 0.75, a minimum policy gives 0.5 and a product policy gives 0.375.                                                                          | Show the input grades and both outputs. The grades express fit to chosen criteria, not calibration or failure rates.            |
| 7. Bulk labelling                    | [Explicit NumPy batch fuzzification][batch]                                                                                               | Historical-scale inputs `[0, 0.3, 0.5, 0.7, 1]` select `[Min, Low, Med, High, Max]` in row order.                                                                                              | Show per-row grades and label masks. File transport is planned in [#391][batch files].                                          |
| 8. Neural preprocessing and decoding | [Fixed encodings and held-out example][neural]                                                                                            | Synthetic inputs `(0.37, 0.63)` give reference score `0.4795`, which encodes to the `Med` centroid 0.5. The fixed decoder maps a reference prediction of 0.4705 to `Med`.                      | Show input encoding and output decoding. The numeric prediction is a recorded witness, not a cross-environment training target. |
| 9. Rule diagnosis                    | Existing [scalar inference trace][inference]; structural checks planned in [#408][rule diagnostics].                                      | Two differently named rules with the same antecedent, consequent and unit weight both fire at 0.75. The structural recipe should identify the redundant pair.                                  | Mark both rule names in the report. A partial overlap alone is not evidence of an incorrect rule.                               |
| 10. Project and figure reuse         | Existing [figure script][figures]; portable [project restore][project restore] and [project-driven figures][project figures] are planned. | Restore a fixture containing the [historical scale][scale]. At `x = 0.2` the restored model should still select `Low` at 0.5; a display-only palette change should leave all grades identical. | Compare grades before and after restoration and render the altered palette headlessly.                                          |


The existing guides document Python APIs and repository scripts. Delivery as
portable models, installed [CLI commands][installed CLI], file-based workflows
and [exported diagnostics][diagnostic export] is tracked in the
[scalar recipes][scalar recipes] and [advanced recipes][advanced recipes] tasks.
Their fixtures should check the stated outputs plus applicable boundary and
no-match cases. Reproduce figures through the versioned scripts or commands
once those are available. Keep neural splits and seeds fixed as specified in
[ADR-0019](../adr/0019-optional-neural-integration-example.md).

[temperature]: ../site/content/en/guides/temperature.md
[severity]: ../site/content/en/guides/risk.md
[alert]: ../site/content/en/guides/alarm.md
[inference]: ../site/content/en/guides/inference.md
[sensors]: ../site/content/en/guides/sensors.md
[batch]: ../site/content/en/guides/numpy-batches.md
[neural]: ../site/content/en/guides/neural-integration.md
[figures]: ../site/content/en/guides/figures.md
[scale]: ../site/content/en/guides/universal-fuzzy-scale.md
[rule diagnostics]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/408
[project restore]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/387
[project figures]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/395
[installed CLI]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/390
[batch files]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/391
[diagnostic export]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/410
[scalar recipes]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/417
[advanced recipes]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/418
