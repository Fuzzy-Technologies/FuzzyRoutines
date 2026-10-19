<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines 2.1.0 — Rules, scales and explainable results

**FuzzyRoutines 2.1.0 was published on 19 October 2026**, following maintainer-approved promotion and independent release acceptance. The [PyPI release](https://pypi.org/project/fuzzyroutines/2.1.0/) and [GitHub Release](https://github.com/Fuzzy-Technologies/FuzzyRoutines/releases/tag/v2.1.0) identify the same approved distributions. [Production acceptance](audits/2026-10-19-2.1-production-acceptance.md) records the annotated tag, exact source and artifact hashes, successful protected publication and verified PyPI installations on CPython 3.13 and 3.14. The earlier [scientific and engineering acceptance](audits/2026-10-19-release-acceptance.md) retains the scalar measurements and CPU experiments.

FuzzyRoutines 2.1 adds explainable rule inference, a ready-made historical Universal Fuzzy Scale, explicit linguistic encoding and optional NumPy batch evaluation. The default scalar core remains free of external runtime dependencies on CPython 3.13 and 3.14. Existing scalar calls remain available, including the basic agent recipe for published 2.0.0.

The [Universal Fuzzy Scale](https://fuzzy-technologies.com/FuzzyRoutines/api/latest/en/guides/universal-fuzzy-scale/) now has a factory and explicit policy/domain helpers. They preserve the original Min, Low, Med, High and Max terms, coefficients, exact-last tie selection and centroid integration windows. They do not retune weakly covered regions or restore incorrect legacy numerical results. [LinguisticCodec](https://fuzzy-technologies.com/FuzzyRoutines/api/latest/en/guides/linguistic-encoding/) connects labels, representative coordinates and ordered membership vectors through explicit contracts. Membership grades are not probabilities, and centroids used as input features or targets are not learned neural weights.

[Mamdani and Sugeno inference](https://fuzzy-technologies.com/FuzzyRoutines/api/latest/en/guides/inference/) make the route from rules to a result inspectable. Mamdani combines activated fuzzy output sets and can calculate the centroid of their aggregate. Zero-order and first-order Sugeno models combine constant or affine rule consequences using normalized firing strengths. Operators, domains and failure behavior are explicit, with rule traces explaining each contribution. Worked examples, formulas and reproducible stage diagrams show why these calculations differ; an average of term representatives is not an aggregate-set centroid.

[Optional NumPy batches](https://fuzzy-technologies.com/FuzzyRoutines/api/latest/en/guides/numpy-batches/) evaluate supported built-in memberships and linguistic scales through dedicated functions. The caller selects the batch API and optional dependency; ordinary scalar calls do not switch backends. The guide describes float64 conversion, array shapes, ties, no-match masks and unsupported callables. Workload size and conversion costs matter; no universal speedup or automatic switching threshold is claimed.

A new [CPU PyTorch example](https://fuzzy-technologies.com/FuzzyRoutines/api/latest/en/guides/neural-integration/) compares raw inputs, label centroids and full membership vectors on one fixed synthetic task. A separate output head predicts membership grades. The example reports held-out errors, decoded labels and out-of-domain results, with figures drawn from recorded predictions. These are optional repository programs, not a neural-network core or a promise that fuzzy preprocessing improves accuracy. The separate [differentiable Sugeno study](https://fuzzy-technologies.com/FuzzyRoutines/api/latest/en/guides/differentiable-sugeno/) checks scalar parity, gradients and constrained smooth memberships. Its decision is **no public tensor backend in 2.1**: the bounded experiment does not establish a general trainable API or alter the historical scale.

The project homepage gains [English](https://fuzzy-technologies.com/FuzzyRoutines/), [Russian](https://fuzzy-technologies.com/FuzzyRoutines/ru/) and [Simplified Chinese](https://fuzzy-technologies.com/FuzzyRoutines/zh-CN/) entry points. The [agent quick start](https://fuzzy-technologies.com/FuzzyRoutines/api/latest/en/agent-quickstart/) documents the published 2.1 capabilities and preserves the compatible basic recipe, checks the exact installed version and produces JSON evidence and optional headless plots. API documentation and scientific guides explain the new contracts in all three languages.

## Install the release

Use a fresh CPython 3.13 or 3.14 environment:

```bash
python -m pip install "fuzzyroutines==2.1.0"
```

NumPy, plotting and Torch dependencies are optional and installed separately for their respective examples. The agent quick start checks the exact installed version and preserves execution evidence. Repository neural and research scripts require the matching source revision; use tag `v2.1.0` to reproduce the release examples.

## Acceptance evidence

Preparation [PR #346](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/346) passed all ten opening workflows on CPython 3.13 and 3.14 where applicable. Its [artifact record](performance/evidence/installed-candidate/acceptance.json) identifies the measured `2.1.0` wheel and reproducible source distribution. The [installed scalar comparison](performance/installed-scalar-comparison.md) preserves seven alternating pairs and independent numerical checks against published 2.0.0. Results were mixed on the shared host, so no general speedup or causal regression is claimed. The [installed NumPy study](performance/installed-batch-results.md) shows advantages for the measured large batches and no consistent advantage for the small public-consumer replay groups. Conversion, memory and optional-dependency costs remain explicit.

The candidate passed 27 synthetic public-boundary migration cases; a separate batch replay covers 30 actual upstream test inputs. These checks do not validate private FMA projects, the robot or complete production applications. Their migrations still need application-specific testing. The bounded neural experiments remain examples and research, with no public trainable tensor API.

The [original review handoff](audits/2026-10-14-2.1-candidate-handoff.md) and the [16 October correction](audits/2026-10-16-post-audit-handoff.md) remain historical acceptance packages. Task [#337](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/337) completed the renewed acceptance of the corrected implementation. The maintainer merged promotion [PR #348](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/348) and explanatory documentation [PR #354](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/354), then pushed the annotated release tag on `bbc47529cf1e0baa17d74b0f008d26f5b36ef68b`. The [production workflow](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/39241460028) rebuilt and verified the exact release artifacts before publishing and checked their actual PyPI bytes afterwards. Later documentation commits do not change that immutable release source or its distributions.

| Stage                                                                    | Status                                                               |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| Recorded candidate source, artifacts and full opening CI                 | Complete; identities and successful runs are retained in the handoff |
| Installed scalar/NumPy measurements and public fixtures                  | Complete; raw samples, parity and limits are retained                |
| Final handoff independent acceptance                                     | Complete; see the 19 October acceptance                              |
| Final promotion CI and artifact-payload comparison                       | Complete; see the exact production source and hashes                 |
| Maintainer promotion/release decision                                    | Complete; promotion merged and annotated tag pushed                  |
| GitHub Release, PyPI publication and published hash/install verification | Complete; both supported Python installations verified               |
