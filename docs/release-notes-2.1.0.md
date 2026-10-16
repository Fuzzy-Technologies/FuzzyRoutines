<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines 2.1.0 — Rules, scales and explainable results

**Version 2.1.0 has not been published.** The published release remains [2.0.0](https://pypi.org/project/fuzzyroutines/2.0.0/). Post-audit numerical fixes require fresh exact-revision acceptance under Task #337 and the existing release PR #348. The [earlier handoff](audits/2026-10-14-2.1-candidate-handoff.md) retains historical artifact evidence; final promotion and publication remain subject to maintainer approval.

FuzzyRoutines 2.1 adds explainable rule inference, a ready-made historical Universal Fuzzy Scale, explicit linguistic encoding and optional NumPy batch evaluation. The default scalar core remains free of external runtime dependencies on CPython 3.13 and 3.14. Existing scalar calls remain available, including the basic agent recipe for published 2.0.0.

The [Universal Fuzzy Scale](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/universal-fuzzy-scale/) now has a factory and explicit policy/domain helpers. They preserve the original Min, Low, Med, High and Max terms, coefficients, exact-last tie selection and centroid integration windows. They do not retune weakly covered regions or restore incorrect legacy numerical results. [LinguisticCodec](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/linguistic-encoding/) connects labels, representative coordinates and ordered membership vectors through explicit contracts. Membership grades are not probabilities, and centroids used as input features or targets are not learned neural weights.

[Mamdani and Sugeno inference](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/inference/) make the route from rules to a result inspectable. Mamdani combines activated fuzzy output sets and can calculate the centroid of their aggregate. Zero-order and first-order Sugeno models combine constant or affine rule consequences using normalized firing strengths. Operators, domains and failure behavior are explicit, with rule traces explaining each contribution. Worked examples, formulas and reproducible stage diagrams show why these calculations differ; an average of term representatives is not an aggregate-set centroid.

[Optional NumPy batches](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/numpy-batches/) evaluate supported built-in memberships and linguistic scales through dedicated functions. The caller selects the batch API and optional dependency; ordinary scalar calls do not switch backends. The guide describes float64 conversion, array shapes, ties, no-match masks and unsupported callables. Workload size and conversion costs matter; no universal speedup or automatic switching threshold is claimed.

A new [CPU PyTorch example](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/neural-integration/) compares raw inputs, label centroids and full membership vectors on one fixed synthetic task. A separate output head predicts membership grades. The example reports held-out errors, decoded labels and out-of-domain results, with figures drawn from recorded predictions. These are optional repository programs, not a neural-network core or a promise that fuzzy preprocessing improves accuracy. The separate [differentiable Sugeno study](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/differentiable-sugeno/) checks scalar parity, gradients and constrained smooth memberships. Its decision is **no public tensor backend in 2.1**: the bounded experiment does not establish a general trainable API or alter the historical scale.

The project homepage gains [English](https://fuzzy-technologies.github.io/FuzzyRoutines/), [Russian](https://fuzzy-technologies.github.io/FuzzyRoutines/ru/) and [Simplified Chinese](https://fuzzy-technologies.github.io/FuzzyRoutines/zh-CN/) entry points. The [agent quick start](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/agent-quickstart/) separates the published 2.0 recipe from candidate 2.1 capabilities, checks the exact installed version and produces JSON evidence and optional headless plots. API documentation and scientific guides explain the new contracts in all three languages.

## Try the candidate

Use a fresh CPython 3.13 or 3.14 environment and the exact wheel supplied by the candidate CI run. The agent quick start describes how to supply its local path and metadata version, verify the basic recipe and preserve the resulting evidence. NumPy, plotting and Torch dependencies are optional and installed separately for their respective examples. Repository neural and research scripts also require the matching source revision. The final published-version installation command will be added after release approval and publication.

## Candidate evidence and release decision

Preparation [PR #346](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/346) passed all ten opening workflows on CPython 3.13 and 3.14 where applicable. Its [artifact record](performance/evidence/installed-candidate/acceptance.json) identifies the measured `2.1.0` wheel and reproducible source distribution. The [installed scalar comparison](performance/installed-scalar-comparison.md) preserves seven alternating pairs and independent numerical checks against published 2.0.0. Results were mixed on the shared host, so no general speedup or causal regression is claimed. The [installed NumPy study](performance/installed-batch-results.md) shows advantages for the measured large batches and no consistent advantage for the small public-consumer replay groups. Conversion, memory and optional-dependency costs remain explicit.

The candidate passed 27 synthetic public-boundary migration cases; a separate batch replay covers 30 actual upstream test inputs. These checks do not validate private FMA projects, the robot or complete production applications. Their migrations still need application-specific testing. The bounded neural experiments remain examples and research, with no public trainable tensor API.

The [review handoff](audits/2026-10-14-2.1-candidate-handoff.md) supplies the acceptance package for Task [#337](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/337). Independent acceptance of that package completes release preparation without implying that the owner has approved the final `develop` to `master` PR. The final PR remains open for the maintainer; its own CI and package-payload comparison must be recorded. A later documentation-only revision can change wheel archive timestamps, so a new artifact must retain its own hash. No release tag or PyPI publication is authorized by this draft.

| Stage                                                                    | Status                                                               |
| ---                                                                      | ---                                                                  |
| Recorded candidate source, artifacts and full opening CI                 | Complete; identities and successful runs are retained in the handoff |
| Installed scalar/NumPy measurements and public fixtures                  | Complete; raw samples, parity and limits are retained                |
| Final handoff independent acceptance                                     | Record in the integrating evidence PR                                |
| Final promotion CI and artifact-payload comparison                       | Pending on the final promotion PR                                    |
| Maintainer promotion/release decision                                    | Pending; final PR reserved for owner review                          |
| GitHub Release, PyPI publication and published hash/install verification | Pending; require separate approval                                   |
