<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0029 Controlled drift research decision

- Status: Proposed research decision for 2.2
- Task: [#431](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/431)
- Feature: [#376](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/376)
- Builds on [ADR-0017](0017-scalar-fuzzy-rule-inference.md)

## Decision

No-go for advancing this particular threshold-and-bounded-step offset
policy. Keep the periodic refit as a baseline for later research. The
experiment supports a decision about this implementation and these
synthetic streams. It establishes no supported adaptive API or
recommendation for a production stream.

## Evidence

A fixed two-rule Sugeno model evaluates each observation. Periodic and
adaptive policies apply a shared offset to the two constant consequents.
Every prediction precedes the update from its label. The intervention test
changes a boundary label and all following labels, checks unchanged
predictions through the intervention row, and verifies a real subsequent
update. Both candidates operate without observing the drift schedule.

The original abrupt scenarios used noise uniformly distributed on
`[-0.015, 0.015]`. For seed 431 the 24-row periodic baseline recovered
24 rows after a shift at index 96 and 36 rows after a shift at index 84.
The bounded policy did not reach eight consecutive absolute errors at
or below 0.05 in either case.

Before evaluating the gradual challenge, [the Task protocol](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/431#issuecomment-6674991501)
fixed seed 431, 224 observations, a 48-row linear intercept increase
starting at index 84 and ending at index 131 with shift 0.25, and noise
uniformly distributed on `[-0.04, 0.04]`. Shifted MAE starts at index 84.
Recovery starts at the first eight-row qualifying error window at or
after index 131.

| Policy            | Shifted MAE | Recovery delay from full shift | Stable steps at least 0.01 |
| ----------------- | ----------- | ------------------------------ | -------------------------- |
| Fixed             | 0.21052     | No qualifying window           | 0                          |
| Periodic refit    | 0.05347     | 13 observations                | 1                          |
| Bounded adaptive  | 0.04205     | 65 observations                | 0                          |

Advancement required every gate. The bounded candidate had zero stable
steps at least 0.01, improved shifted MAE by at least 10% relative to
fixed and kept it below periodic. It failed the recovery gate by 52
observations relative to periodic. The smaller average error therefore
does not establish faster recovery.

The periodic model retains at most 24 residuals and refits once per
24 observations. The adaptive candidate retains one offset and tries at
most one update per revealed label. These constraints and the recorded
operation counts are independent of machine timing.

## Reproduction

From the repository root, with the pinned `docs/requirements-plots.txt`
toolchain for SVG generation:

```bash
python -m research.controlled_drift --challenge
python -m research.controlled_drift --evidence --drift-at 84
python -m research.plot_controlled_drift --challenge --output-dir ./drift-figures
```

Future candidates require a separate protocol and untouched challenge
streams. Evaluate other seeds, non-additive drift and delayed feedback
before drawing broader conclusions.
