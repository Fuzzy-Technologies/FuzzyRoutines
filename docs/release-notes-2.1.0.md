<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines 2.1.0 — Rules, scales and explainable results

**Draft for candidate review. Version 2.1.0 has not been published.** The published release remains [2.0.0](https://pypi.org/project/fuzzyroutines/2.0.0/). The capabilities below describe the 2.1 implementation scope; final artifact and release evidence is still pending.

FuzzyRoutines 2.1 adds explainable rule inference, a ready-made historical Universal Fuzzy Scale, explicit linguistic encoding and optional NumPy batch evaluation. The default scalar core remains free of external runtime dependencies on CPython 3.13 and 3.14. Existing scalar calls remain available, including the basic agent recipe for published 2.0.0.

The [Universal Fuzzy Scale](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/universal-fuzzy-scale/) now has a factory and explicit policy/domain helpers. They preserve the original Min, Low, Med, High and Max terms, coefficients, exact-last tie selection and centroid integration windows. They do not retune weakly covered regions or restore incorrect legacy numerical results. [LinguisticCodec](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/linguistic-encoding/) connects labels, representative coordinates and ordered membership vectors through explicit contracts. Membership grades are not probabilities, and centroids used as input features or targets are not learned neural weights.

[Mamdani and Sugeno inference](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/inference/) make the route from rules to a result inspectable. Mamdani combines activated fuzzy output sets and can calculate the centroid of their aggregate. Zero-order and first-order Sugeno models combine constant or affine rule consequences using normalized firing strengths. Operators, domains and failure behavior are explicit, with rule traces explaining each contribution. Worked examples, formulas and reproducible stage diagrams show why these calculations differ; an average of term representatives is not an aggregate-set centroid.

[Optional NumPy batches](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/numpy-batches/) evaluate supported built-in memberships and linguistic scales through dedicated functions. The caller selects the batch API and optional dependency; ordinary scalar calls do not switch backends. The guide describes float64 conversion, array shapes, ties, no-match masks and unsupported callables. Workload size and conversion costs matter; no universal speedup or automatic switching threshold is claimed.

A new [CPU PyTorch example](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/neural-integration/) compares raw inputs, label centroids and full membership vectors on one fixed synthetic task. A separate output head predicts membership grades. The example reports held-out errors, decoded labels and out-of-domain results, with figures drawn from recorded predictions. These are optional repository programs, not a neural-network core or a promise that fuzzy preprocessing improves accuracy. The separate [differentiable Sugeno study](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/differentiable-sugeno/) checks scalar parity, gradients and constrained smooth memberships. Its decision is **no public tensor backend in 2.1**: the bounded experiment does not establish a general trainable API or alter the historical scale.

The project homepage gains [English](https://fuzzy-technologies.github.io/FuzzyRoutines/), [Russian](https://fuzzy-technologies.github.io/FuzzyRoutines/ru/) and [Simplified Chinese](https://fuzzy-technologies.github.io/FuzzyRoutines/zh-CN/) entry points. The [agent quick start](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/agent-quickstart/) separates the published 2.0 recipe from candidate 2.1 capabilities, checks the exact installed version and produces JSON evidence and optional headless plots. API documentation and scientific guides explain the new contracts in all three languages.

## Try the candidate

Use a fresh CPython 3.13 or 3.14 environment and the exact wheel supplied by the candidate CI run. The agent quick start describes how to supply its local path and metadata version, verify the basic recipe and preserve the resulting evidence. NumPy, plotting and Torch dependencies are optional and installed separately for their respective examples. Repository neural and research scripts also require the matching source revision. The final published-version installation command will be added after release approval and publication.

## Final evidence — pending

This draft does not replace [release readiness](release-readiness.md). Task [#337](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/337) remains open until the candidate evidence is complete. Feature-branch tests and research measurements are supporting evidence, not proof that the final wheel passed release checks.

| Evidence                                                                                 | Status                                                                                        |
| ---                                                                                      | ---                                                                                           |
| Exact integrated candidate revision and version                                          | **Pending** — version is 2.1.0; feature PRs are merged, record the final preparation revision |
| Full CI result for that candidate on CPython 3.13 and 3.14                               | **Pending** — attach successful run links                                                     |
| Reproducible wheel/sdist, SHA-256 manifest and clean installed-artifact checks           | **Pending** — attach final artifacts and consumer results                                     |
| Scalar/NumPy benchmark report with environment, raw samples, parity and dependency costs | **Pending** — attach evidence for the integrated candidate                                    |
| Optional CPU examples and research source/report provenance                              | **Pending** — verify against the final wheel and matching source revision                     |
| English/Russian/Chinese acceptance and rendered homepage/API checks                      | **Pending** — feature translations reviewed in merged PRs; verify the final composed artifact |
| Final promotion PR to `master`                                                           | **Pending** — reserved for maintainer review                                                  |
| GitHub release and PyPI publication, followed by hash and install checks                 | **Pending** — perform only after approval; this draft authorizes no publication               |
