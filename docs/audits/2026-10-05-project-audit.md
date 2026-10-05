<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Project readiness audit — 2026-10-05

## Scope and conclusion

The audited baseline is `develop` at
[`f700e0ed99da821419c6fa16a6370ec2a66c1cf0`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/f700e0ed99da821419c6fa16a6370ec2a66c1cf0),
after PRs #275, #276 and #277. Release-preparation changes and audit corrections
are separate review candidates; this report does not describe them as merged.
Tracking task: [#279](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/279).

The architecture follows the modern-core-first plan: explicit scalar universes,
immutable built-in membership functions and policies, focused mathematical
modules, a compatibility facade, and no mandatory numerical dependency. The
library supports useful membership, set algebra, centroid and linguistic
classification scenarios. It is **not ready for unconditional stable-release
approval**: the audit reproduced four correctness defects, package byte
reproducibility needed work, and the exact final candidate still needs CI and
publishing-protection evidence.

All 20 production Python files were reviewed, including the historical adapters
and executable example module. Mathematical review covered `membership`,
`numeric`, `operators`, `domain`, `fuzzysets`, `properties`, `relations`,
`alphacuts`, `defuzzification` and `linguistic`. The remaining review covered
package exports, exception categories, facade identities, adapter semantics,
build/release workflows, typing, documentation generation and example execution.
Repository-wide AST inspection checked source/documentation structure. Tests
and tooling were assessed through that inventory and relevant implementation
paths; this is not a claim that every test/tool line received a manual proof.

## Reproduced findings and dispositions

| Finding                              | Observable problem                                                                                                                                                                               | Disposition                                                                                                                                          |
|--------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| Gaussian centroid cancellation       | `Gaussian(0, 1)` on `[8, 8.1]` returned approximately `8.38709`; on `[8.3, 8.4]`, approximately `4.46858`. Both violate the integration-domain bound.                                            | [#282](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/282): stabilize tail moments and reject unreliable analytical results.             |
| Lossy linguistic tie comparison      | Grades `Fraction(1, 2) - Fraction(1, 10**20)` and `Fraction(1, 2)` became an invented default tie, selecting the smaller grade.                                                                  | [#283](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/283): preserve exact zero-tolerance and rational/mixed comparisons.                |
| Borrowed analytical certificates     | An overridden `MembershipFunction` evaluator returning a constant retained Triangle height/centroid evidence unrelated to its actual grades. Historical overridden adapters need the same check. | [#284](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/284): verify the active evaluator before accepting formula evidence.               |
| Extreme finite-coordinate arithmetic | `Triangle(-1e308, 1e308, 1e308)` returned NaN at its apex and zero at its midpoint; a scaled Logistic difference saturated incorrectly after intermediate overflow.                              | [#285](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/285): stable difference ratios/scaled differences, preserving ordinary arithmetic. |
| Nondeterministic source archives     | Equal-source builds had different sdist bytes because archive timestamps varied; wheel equality alone did not establish reproducibility.                                                         | [#278](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/278): deterministic archive creation and two independent builds in CI.             |
| Contradictory composition arity      | ADR-0004 required two operands; historical 1.0.3, the current implementation and migration guide support a valid unary identity fold.                                                            | [#281](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/281): proposed ADR amendment; preserve protected runtime behavior.                 |
| Stale capability and style guidance  | README/site/status still treated implemented typing and analytical operations as future work; local style guidance contradicted the shared standard.                                             | [#279](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/279): refresh guidance and preserve existing public keyword spellings.             |
| Missing test-function docstrings     | At the baseline, 314 of 525 test functions/helpers had no docstring, despite the shared standard requiring one.                                                                                  | [#286](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/286): separate maintenance task; distinguish this debt from numerical blockers.    |

The numerical findings arise in existing scalar contracts and do not justify a
new backend, hidden epsilon, arbitrary clamping or a breaking API cleanup.
Corrections should have independent reference evidence and targeted regression
tests, followed by the existing CI gates.

## ADR and plan alignment

| ADR                                                           | Assessment and evidence boundary                                                                                                                                                      |
|---------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [0001](../adr/0001-backward-compatibility-contract.md)        | Modern modules own formulas; the facade and private adapters preserve historical imports, signatures, concrete failures and serialized identities.                                    |
| [0002](../adr/0002-universe-support-semantics.md)             | Universe, finite integration domain and mathematical support remain distinct. Exact properties require valid analytical evidence; #284 repairs certificate trust.                     |
| [0003](../adr/0003-membership-function-contracts.md)          | Modern geometric parameters and historical triangle/trapezium ordering remain separate; construction validates geometry. #285 addresses avoidable arithmetic overflow.                |
| [0004](../adr/0004-operator-and-negation-contracts.md)        | Operator families and analytical negation branches agree; #281 resolves the documented arity contradiction without changing valid calls.                                              |
| [0005](../adr/0005-numerical-defuzzification-policy.md)       | Explicit immutable tolerances, adaptive convergence failure and zero-area errors exist. #282/#285 correct violations found at numerical boundaries.                                   |
| [0006](../adr/0006-packaging-versioning-release-policy.md)    | PEP 621 owns `2.0.0.dev0`; backend remains setuptools; CPython 3.13/3.14 and human-approved tagged publication remain the contract. #278 and #121 retain unfinished release evidence. |
| [0007](../adr/0007-parallel-test-execution.md)                | Process-isolated tests and explicit result reporting exist. Full local gates were not run during this wave; user-authorized targeted checks and PR CI apply.                          |
| [0008](../adr/0008-fuzzy-set-difference-semantics.md)         | Directed difference has explicit norm/negation policies and equal-universe checks. Symmetric difference remains outside the implemented contract.                                     |
| [0009](../adr/0009-fuzzy-set-convexity-semantics.md)          | Exact, discrete and sampled evidence are distinguished. A general public convexity query remains planned; #284 protects the analytical evidence boundary.                             |
| [0010](../adr/0010-api-documentation-architecture.md)         | English Google/Markdown docstrings, annotations, static Griffe discovery and disposable generated MkDocs output remain authoritative.                                                 |
| [0011](../adr/0011-multilingual-documentation-pipeline.md)    | Stable identities, source hashes and explicit translation states exist. Russian/Chinese fallbacks are not represented as reviewed complete translations.                              |
| [0012](../adr/0012-apache-2.0-relicensing.md)                 | Current metadata, LICENSE, NOTICE and owned-source SPDX headers use Apache-2.0; historical MIT releases remain immutable provenance.                                                  |
| [0013](../adr/0013-linguistic-fuzzification-policy.md)        | Ordered scores, confidence, no-match and first/last/all selection exist. #283 corrects exact-grade tie detection.                                                                     |
| [0014](../adr/0014-sampled-scale-diagnostics.md)              | Diagnostics expose domain/grid/threshold and sampled evidence; they do not retune scales or prove unsampled behavior.                                                                 |
| [0015](../adr/0015-optional-vectorized-execution-strategy.md) | Installed scalar core has no NumPy dependency or automatic selector. The repository prototype remains separate from future explicit optional batch implementation.                    |

No process-wide backend, operator policy or transparent cross-call result cache
was found in the modern core. Frozen wrappers do not freeze caller-owned custom
callback state: callbacks must remain consistent during an operation, and legacy
mutable objects need caller synchronization. Independent Python processes have
independent library state. Free-threaded CPython remains outside the initial
support promise; this review is not a new concurrency certification.

## Usability, documentation and examples

The root offers 51 curated modern exports; the historical facade offers its 15
documented compatibility names. Inline annotations, `py.typed`, a structural
custom-callback protocol and installed-wheel typing consumers are present.
Construction and evaluation errors are explicit; custom evaluator exceptions
propagate without being misclassified as library failures.

The canonical mathematical model, API reference, migration guide, corrected-bug
ledger, benchmark evidence and three migration scripts give developers a usable
entry point. Source AST inventory found docstrings for every module and all 209
production functions, 166 tooling functions, 21 prototype functions and four
migration-example functions. Those counts do not prove explanation quality or
mathematical correctness; the reproduced defects demonstrate why reference
checks remain necessary.

Documentation needs more practical teaching material. The current modern
migration example covers membership, domains, complement and intersection; the
custom callback example covers numerical centroid. They do not yet supply the
explained end-to-end linguistic scenarios, comparative plots and intermediate
results expected of a mature scientific guide. Separate M6 task
[#280](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/280) specifies
membership/operator plots, centroid and scale explanations, a compact API flow,
two worked scenarios, accessible captions and installed-package execution.
These are mathematical explanation assets, separate from existing branding.

## Verification and release limits

Local verification is intentionally targeted. The baseline facade/import and
historical/modern example checks passed **19 tests**. The documentation stream
passed **48 composition tests**, **four product-site checks**, and **three
executed README/site examples**, plus changed-file links, table alignment and
static checks. Each numerical/artifact PR records its own affected-test evidence.
No full local regression gate, documentation build or package build was run.

The first five baseline CI workflows failed because their jobs were never
acquired by a hosted runner; they had no executed steps. GitHub's annotation
states: “The job was not acquired by Runner of type hosted even after multiple
attempts.” They were retried once. This is infrastructure evidence, not a passed
or failed numerical test. The separate optional prototype parity workflow
completed successfully. Exact candidate CI must be read back before approval.

The repository ruleset API returned no visible rulesets during the audit.
Protected tag/environment configuration and the external PyPI Trusted Publisher
binding therefore remain **unverified**, not implicitly satisfied by workflow
YAML. [The runbook](../trusted-publishing-runbook.md) and
[#121](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/121) own the
final checks: reviewed stable version/changelog, approved source promotion,
green exact-candidate matrix, protected annotated tag, verified publishing
binding, artifact hashes/provenance, and GitHub/PyPI release evidence.

Stable publication remains a separate human-approved action. A successful audit
fix PR does not approve publication or establish that every possible input has
been mathematically proved correct.
