<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines 2.1 release acceptance

The corrected implementation at `0dba28a072c6d8dff3eacdc336b922e1ab264b23` satisfies the planned 2.1 implementation acceptance. All ten full workflows passed. This review supersedes the earlier candidate acceptance for the changed numerical and onboarding paths; it does not authorize the maintainer's final master merge, release tag or PyPI publication. The existing [release PR #348](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/348) remains the single promotion review. The isolated [correction PR #353](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/353) completes Task #337 through develop.

## Scope and independent review

The review covered the complete master-to-develop change, the six native milestone Features and their eighteen native child Tasks. Before correction, the three open milestone items were Task #337, its parent Feature #323 and release PR #348. They were not three missing capabilities. All other native child Tasks were confirmed completed.

| Area                          | Accepted evidence                                                                                                                       |
| ---                           | ---                                                                                                                                     |
| Human and agent onboarding    | Exact 2.1 pins, version preflight, conditional PyPI availability, reviewed-wheel fallback, executable recipes and expected JSON.        |
| Historical scale and encoding | Original coefficients, term order, tie policy and integration windows; explicit lossy encodings and independent reference tests.        |
| Mamdani and Sugeno inference  | Explicit policies and traces; exact independent references for rational geometry, clipped polynomials and numerical failure boundaries. |
| Optional NumPy batches        | Current source/installed parity on both supported Pythons, baseline/resolver dependency matrices and dependency-free core imports.      |
| Neural integration            | Fresh installed-wheel CPU experiments: 600 observations and 400 epochs for both the neural comparison and bounded Sugeno study.         |
| Documentation and website     | Strict installed API builds, 306 approved units per locale, 229-symbol/37-block example index and rendered desktop/mobile acceptance.   |

The production mathematics, contracts and evidence were reviewed independently of their implementer. Editorial, mathematical and technical review accepted the changed English, Russian and Chinese material. Source and translation hashes bind that review to `docs/i18n/units.toml`; reviewers are identified honestly as AI reviewers acting under delegated acceptance. The three explanatory Mamdani/Sugeno figures were also inspected visually. No historical classifier code or model was ported.

## Findings corrected before acceptance

- A valid triangle with distinct rational vertices near 1 collapsed during float conversion, although its positive area and centroid were well-defined. Polynomial fallback now preserves original rational geometry, including windows containing no binary64 coordinate.
- Subtracting nearby polynomial antiderivatives could return a centroid outside a narrow integration window. Integration now uses distance from each clipped panel's left endpoint. Independent monomial integrals cover every supported polynomial branch.
- Trusted Mamdani knots also preserved only float images of the supplied geometry. Original rational knots now remain distinct. Generic numerical results outside their original domain fail explicitly with `NumericalError`; they are never clamped.
- Relative README links broke when embedded in the PyPI description, and an unpinned NumPy installation could resolve the published 2.0 package before using 2.1-only imports. Absolute links, exact version checks and conditional reviewed-wheel instructions repair those reader paths. Primary entrypoints now target 2.1 without claiming it is already published.
- Rendered acceptance omitted the new scientific pages. It now checks ten API/onboarding routes in every locale, plus the three landing pages, at desktop and mobile widths. The regenerated example index and the benchmark-link assertion were synchronized after the implementation change.

Forty-six new precision/geometry/failure regressions were added. Focused numerical and integration acceptance passed 302 cases on each of CPython 3.13.16 and 3.14.8. Documentation/style acceptance passed 92 cases; optional neural feature checks passed another 33 cases. Compile checks, changed-file Ruff, public typing, licensing and multilingual approval validation passed.

## Full CI and installed artifacts

The [workflow record](evidence/release-2.1-acceptance/ci-workflows.json) identifies all ten successful full runs at the accepted head. Both supported interpreters passed 1,671 tests with 22 explicit skips. Actual sequential and process runs had identical test identities/outcomes, zero worker errors and zero timeouts. Combined line/branch coverage was reported as 88%; acceptance does not claim complete coverage. Separate NumPy and CPU neural workflows exercised their optional dependencies.

The [package run](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/39168270761) built synthetic merge `9ab20c7e7b3d98e056f2670a7eebc75083e00553` from the accepted PR head. Downloaded artifact ZIP digests were checked against GitHub metadata. Each package job compared two independent builds; Python 3.13 and 3.14 produced byte-identical wheel and sdist files. Clean installs, executable examples, version/origin checks and optional-dependency isolation passed.

- CI wheel SHA-256: `3054f737f2cd247c20647abc5627f2368864563fd228544bb3bf01e8d76d44f7`.
- CI sdist SHA-256: `c398585750118b55d648aa277cd2c76ba6161d1d9e2f640ccfe7efa1c9fed6d2`.
- The separately built local wheel used for full neural experiments has SHA-256 `0a7d2565ad0f1943bf32b6ea2774b8764ba171d0f15dac74c3330211188b042f`. All 31 decompressed entries, including all 25 package files, equal the CI wheel. Different archive hashes remain distinct.

The [acceptance manifest](evidence/release-2.1-acceptance/acceptance.json) binds raw reports, provenance, source and artifact identities. Later integration/promotion artifacts must retain their own hashes and prove package-payload equality rather than reuse these archive identities.

## Scientific and performance results

The [fresh installed scalar comparison](../performance/release-2.1-scalar.md) ran thirty fixed scenarios against the actual PyPI 2.0 wheel, with seven alternating pairs and independent numerical parity. Its clean, pinned harness was separate from both installed packages. Results remain workload-dependent: the historical generic hyperbolic centroid measured about 5.031 ms against 1.202 ms, approximately 4.19 times slower under the stronger global numerical policy. The measured polynomial centroids were approximately 13–17 microseconds. Shared-host timings are observations, not guarantees. Existing batch timings remain evidence for their named revisions; current NumPy correctness is separately verified by the new full CI.

The fresh [neural comparison](evidence/release-2.1-acceptance/neural-current.json) and [Sugeno study](evidence/release-2.1-acceptance/sugeno-current.json) use the same deterministic dataset and 360/120/120 split as their earlier records, now against the corrected installed package. All displayed six-decimal Sugeno RMSE values, label accuracies and invalid-output counts remain unchanged. Raw inputs still outperform the fixed fuzzy encodings on this task; trainable memberships do not establish superiority over the fixed-membership control. Two first-order predictions outside the output domain remain reported. The decision remains no public trainable tensor backend in 2.1.

Arbitrary callbacks retain the unsampled-feature limitation, and quadrature error estimates are conditional. The bounded exact polynomial path does not imply symbolic Mamdani integration. Private FMA/robot application migration remains unverified; public migration fixtures and upstream replay inputs do not replace that testing. Membership grades are not probabilities, and no automatic backend dispatch, GPU platform or free-threaded support is claimed.

## Website and publication handoff

The [rendered API run](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/39168270817) passed 66 page views and 44 figure views. It checks corporate fonts/colors, SVG mathematics, language routes, direct locale refresh, responsive layout, image dialogs, focus restoration and clipboard behavior. New scientific pages require rendered mathematics without MathJax errors. All generated internal links and installed examples passed the documentation gates.

The [pre-promotion HTTP record](evidence/release-2.1-acceptance/entry-links.json) confirms that the old project Pages address redirects to `fuzzy-technologies.com` and the current API locales respond. New 2.1 landing/scientific routes were absent before publication, as expected; a built preview is not a claim of live deployment. Corporate PR #52 is merged. [Corporate navigation PR #57](https://github.com/Fuzzy-Technologies/fuzzy-technologies.github.io/pull/57) must follow deployment of the localized project pages.

Final owner-controlled promotion must use the current #348 head and its successful checks, deploy Pages, verify the live locale/scientific/agent routes, then create the annotated matching `v2.1.0` tag when publication is approved. Both release-tag rulesets were confirmed active; tag updates/deletions are prohibited. Repository/environment and PyPI Trusted Publisher controls must be checked at publication rather than inferred from historical settings. After publication, compare actual PyPI artifact hashes and repeat clean-install verification before recording production acceptance. No master merge, tag, GitHub Release or PyPI upload was performed by this acceptance.
