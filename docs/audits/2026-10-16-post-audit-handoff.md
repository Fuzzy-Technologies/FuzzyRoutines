<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines 2.1 post-audit handoff

The corrected implementation passed all ten full workflows at `bd6f0af22be325967c2694c9497e50b0af2cbff7` in [development PR #352](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/352). This supersedes the 14 October implementation acceptance. The existing [release PR #348](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/348) remains the single owner promotion review. Version 2.1.0 is unpublished; no release merge, tag or PyPI publication is authorized here.

## Corrections and review

- #331: narrow/disjoint built-in Mamdani consequents retain trusted quadrature knots. Independent clipped-polygon moments cover overlap, clipping, restricted windows, translations and zero weights. The disjoint example is `1161/1700`, not `0.75`.
- #351: bounded polynomial moment fallback, explicit nonzero firing/adaptive underflow errors and rational preservation of subnormal normalized Sugeno strengths. Ordinary traces remain floating-point values; existing rational callbacks retain their arithmetic. Later callback exceptions propagate unchanged.
- #350: complete NumPy first/last selection avoids cumulative integer scans, preserving full array validation/copying. The [paired full-call audit](../performance/batch-selection-audit.md) reports gains at 200,000 values and small-call overhead rather than a universal speedup.
- #349: the README opens with a stable installed example and a copyable AI request, then gives short version-aware source routes. The example ran in an isolated installed 2.0.0 environment without NumPy.
- The [Russian scientific review](2026-10-16-russian-scientific-review.md) records university sources, adaptive terminology, AI reviewer identities and independent scientific follow-through. It does not claim a human line-by-line review. EN/RU/zh-CN contracts and source-bound review hashes align.
- Three inference figures explain Mamdani, zero/first-order Sugeno and disjoint support. The corrected max-aggregation wording allows a consequent to be dominated. A fresh 400-epoch research run preserved the conclusions, including two first-order held-out outputs outside the output domain; no clipping hides them.

## Exact installed acceptance

The [acceptance manifest](../performance/evidence/post-audit-installed/acceptance.json) binds source, artifacts, raw reports and supporting provenance. [Installed results](../performance/post-audit-installed.md) retain all 30 scalar cases, 24 NumPy combinations and 30 public upstream replay inputs, with seven alternating pairs and independent numerical checks. The candidate and baseline environments were isolated; scalar and batch studies ran sequentially.

- Successful package run: [38903501182](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38903501182).
- Built source: `4b9efcf67f42aee15bbce3aeac7bbb55388a4822`; its PR head is `bd6f0af22be325967c2694c9497e50b0af2cbff7`.
- Wheel SHA-256: `cf694da86b560d3619a5480f67a943ca7eb87a90e1c9fde97e188b380e86b883`.
- Sdist SHA-256: `a2d3aff466073c9e93123d80fbe85df5d522a2b2d7465f1c9f58c0f1b2c547cd`.
- Python 3.13/3.14 artifact ZIPs have their own recorded digests; their contained wheels and sdists are byte-identical. Each build compares two independent builds. Installed package bytes and origins were verified against declared Git sources.
- CPython 3.14 mathematics: 1,601 passed / 22 skipped, with identical actual sequential/process outcomes and zero worker errors/timeouts. CPython 3.13 and both optional dependency matrices also passed their full workflows.
- Clean installed agent preflight accepted 2.1.0; all 27 synthetic public migration-boundary cases passed. Private FMA/robot application migration is still unverified.

Full source-bound workflow results:

- [Quick deterministic gate](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38903501456): completed / success.
- [Public modern typing](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38903501387): completed / success.
- [Optional NumPy scalar parity](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38903501352): completed / success.
- [Optional neural CPU examples](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38903501320): completed / success.
- [Trusted PyPI release](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38903501278): completed / success.
- [Mathematical coverage and execution parity](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38903501409): completed / success.
- [Documentation quality gates](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38903501302): completed / success.
- [Close linked Tasks after merge](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38903501107): completed / success.
- [Package build and clean-install](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38903501182): completed / success.
- [Canonical API reference](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38903501127): completed / success.

## Limits and remaining owner actions

The stricter global adaptive algorithm has a measured cost: the historical generic hyperbolic centroid is about 4.19 times slower than 2.0.0 (5.2613 versus 1.2570 ms). Cached replacement sums reduced the intermediate 24.6531 ms result by about 4.69 times; full compensated partition evidence is still recomputed before acceptance. Analytical polynomial paths remain in microseconds. Raw mixed results and shared-host variability are explicit; no universal performance guarantee is made.

Arbitrary callbacks retain the unsampled-feature limitation. Error estimates are not general mathematical certificates. Rational fallback is bounded to the stated polynomial path and tiny Sugeno normalization; adaptive erased intermediates fail explicitly. Membership grades remain distinct from probabilities. Historical scale coefficients and default runtime dependencies are unchanged.

[Source/HTTP checks](../performance/evidence/post-audit-installed/entry-links.json) returned 200 for pinned agent/inference sources and the stable tagged quick start. The new live `/latest/` agent/inference routes still returned 404 before publication; source fallback is intentional. Verify live routes only after approved documentation publication.

The [corporate card companion PR #52](https://github.com/Fuzzy-Technologies/fuzzy-technologies.github.io/pull/52) corrects Apache-2.0, stable 2.0.0, runtime support and modern examples in EN/RU/zh-CN. All eight external links returned 200, installed examples passed, and all three files are Viewed with an AI COMMENT review. Owner merge remains required: its [development protocol](https://github.com/Fuzzy-Technologies/fuzzy-technologies.github.io/blob/master/DEVELOPMENT_PROTOCOL.md#4-branching-and-pull-requests) says agents must not self-merge without explicit instruction for that PR. Task #337 / Feature #323 remain open until that prerequisite and the final handoff are reconciled.

Report-only integration commits do not change measured core code. The final promotion build must record its own archive digests and compare package source/typing payload to the measured wheel. Matching payload does not make different archive hashes interchangeable. Final PR #348 merge, release tag and PyPI publication remain the maintainer's separate decision.

