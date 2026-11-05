<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Split-conformal service latency baseline

## Status

Proposed research decision for [Task #430]. The experiment uses the existing
scalar Sugeno contract and leaves the installed package unchanged.

## Context

The target is the median latency in a synthetic five-minute service window,
expressed in milliseconds. A fixed two-rule Sugeno model estimates latency
from CPU utilization using complementary ramps and constant consequences of
80 ms and 240 ms. The data generator adds a quadratic component and noise
whose amplitude increases with CPU utilization.

The fixed rules are specified before observing any rows. The training split
fits one additive offset by averaging signed errors. The model and offset
are frozen before calibration. Calibration and test rows come from separate
seeded draws under the same simulated regime. Tests also perturb the held-out
targets and verify that the training offset and calibration radii stay fixed.

## Method and evidence

For a frozen prediction, use its absolute error as the calibration score.
For target coverage `c` and `n` calibration scores, select sorted rank
`ceil((n + 1) * c)`, counting from one. When that rank exceeds `n`, use
an unbounded interval. The prediction interval is the prediction plus and
minus the chosen radius, with endpoints included.

The mathematical guarantee concerns marginal coverage for a fresh observation
under exchangeability of calibration and test scores conditional on training.
The simulator draws independent rows from one distribution. A production
latency stream may have dependence, drift, or subgroup coverage differences.
The two membership grades express compatibility with CPU terms. Their values
have no coverage interpretation.

Run from the repository root:

```bash
python -m research.conformal_baseline.run
python -m pytest -q tests/test_research_conformal_baseline.py
```

The [committed report](results.json) uses 200 training, 199 calibration,
and 1,000 test rows. The held-out mean absolute point error is 10.261719 ms.

| Target coverage | Calibration rank | Covered test rows | Empirical coverage | Interval width |
| --------------- | ---------------- | ----------------- | ------------------ | -------------- |
| 90%             | 180              | 917/1000          | 91.7%              | 41.801087 ms   |
| 95%             | 190              | 949/1000          | 94.9%              | 45.605281 ms   |

The nominal guarantee does not constrain every finite test sample to achieve
the target exactly. The two rows summarize one simulation, with a fixed
width at each level because the chosen score is an absolute residual.

## Proposed decision

Keep this as a reproducible baseline for later comparison with a calibrated
Type-2 model. A production decision needs chronological data, coverage and
width by regime, and an explicit plan for handling calibration drift. Leave
e-value prediction sets as a separate research question. Their evidence
scores do not belong to the grade range of `ScalarFuzzySet`.

## References

- [Angelopoulos and Bates, *A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification*](https://arxiv.org/abs/2107.07511v6).
- [Msaddi and Kumbasar, *An Alliance for Uncertainty Quantification: Type-2 Fuzzy Logic Systems and Conformal Prediction*](https://doi.org/10.1109/TETCI.2025.3647649).
- [Koning and van Meer, *Fuzzy Prediction Sets*](https://arxiv.org/abs/2509.13130v3).

[Task #430]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/430
