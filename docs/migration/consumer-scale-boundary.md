<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Public consumer scale migration evidence

This fixture checks the historical Universal Fuzzy Scale at a real consumer
boundary. It covers the normalization and scale selection used by
[TKSBrokerAPI TradeRoutines.py](https://github.com/Fuzzy-Technologies/TKSBrokerAPI/blob/b963c54039f013d432220186ae35a22359c5a773/tksbrokerapi/TradeRoutines.py) at
`b963c54039f013d432220186ae35a22359c5a773`. Its `RiskLong` and `RiskShort`
functions clip the current coordinate to a declared range, normalize distance
from the corresponding endpoint, and call `UniversalFuzzyScale.Fuzzy()`.
The consumer also retains the historical `accuracy = 100` assignment.

The 27 input cases are synthetic prices with a fixed 100–200 range, covering
both directions, term transitions, weak coverage, clipped values and a
zero-width range. They are contract fixtures, not production observations,
trading backtests or measurements of financial risk. Membership grades are
not probabilities.

## Pinned baselines

- Historical source: FuzzyRoutines `1.0.3`, commit
  `ceb9403d44c19ba73fd351e1b05091d337280864`; module SHA-256
  `0785985f91566404b9f17d3531e22a527839e36b0eafed45c662020e7f797561`.
- Published modern baseline: installed PyPI `2.0.0`, source release
  `49c9aee67a60cad74bc9494943b8745b72d2f43c`.
- Fixture: `tests/fixtures/consumer_scale_migration.json`, SHA-256
  `9c97478588e7e5117b3e1ccb3ab079ec3a47e4766a8c327e3d0b2af5ec8cc741`.

The historical snapshot was measured by loading the module extracted with
`git show 1.0.3:fuzzyroutines/FuzzyRoutines.py` and invoking the same
`MeasureCases` harness with that module's `UniversalFuzzyScale`. No historical
source is vendored into the modern library. The 2.0 snapshot was independently
reproduced with the published package under CPython 3.14.8, using isolated
execution and an import origin inside the environment's `site-packages`.

Across these cases, all 27 selected labels and normalized percentages agree.
The largest observed membership difference is `2.73910037e-29`; the fixture
comparison uses an absolute bound of `1e-12`. Order and integration windows
are unchanged. A small winning grade remains a valid historical selection:
this evidence does not impose a confidence threshold or normalize grades.

## Centroid correction remains observable

| Term | Historical 1.0.3 centroid | Published 2.0 centroid | Change          |
| ---- | ------------------------: | ---------------------: | --------------: |
| Min  | 0.0633369792335409        | 0.0632789828672755     | -5.79963663e-05 |
| Low  | 0.285                     | 0.285                  | +0              |
| Med  | 0.5                       | 0.5                    | +5.55111512e-16 |
| High | 0.714999999999998         | 0.715                  | +1.88737914e-15 |
| Max  | 0.925240012914588         | 0.925178571428571      | -6.1441486e-05  |

The endpoint differences are the documented replacement of sampled historical
integration by corrected moments. The public risk-label functions examined
here do not call `Defuz()`, so these differences do not alter the observed
labels. A different consumer that uses centroids must assess them against its
own thresholds. The retained `accuracy = 100` assignment does not change the
2.0 centroid: it is compatibility metadata, not an accuracy control.

The candidate check requires membership grades within `1e-12` and centroids
within `1e-10` of the published 2.0 observations, plus exact term order,
windows, labels, coordinates and percentages. These bounds apply to this
fixture; they are not universal numerical guarantees.

## Reproduce with an installed release or candidate

After installing the wheel into an isolated supported Python environment, run
its interpreter from outside the checkout. Use absolute paths for the script
and fixture:

```bash
/path/to/environment/bin/python -I /path/to/repository/tools/consumer_scale_migration.py \
  --fixture /path/to/repository/tests/fixtures/consumer_scale_migration.json \
  --check-current --output /path/to/evidence/consumer-scale.json
```

The command prints the same JSON that it writes, including the installed
package and Python versions, fixture hash, pinned consumer revision, all grades,
labels and centroids.
It fails if the candidate changes the published boundary. It performs no
network calls and does not import or execute the consumer's trading engine.

Focused source validation:

```bash
python -m pytest -q tests/test_consumer_scale_migration.py
```

## Scope of acceptance

The available consumer inventory separates inspected contracts from missing
application evidence:

| Consumer      | Available evidence                                                          | Acceptance boundary                                          |
| ------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------ |
| TKSBrokerAPI  | Pinned public risk-normalization and scale calls                            | The 27 synthetic boundary cases below the application engine |
| FMA projects  | Maintainer-identified consumers; private source and traces unavailable here | Application migration remains unverified                     |
| Robot project | Maintainer-identified consumer; project version and traces unavailable here | Application migration remains unverified                     |

This evidence validates a public consumer's scale boundary with sanitized,
reproducible inputs. It does not establish whole-application behavior,
strategy performance, private FMA/robot integration, or measured production
workload sizes. Those require their own consumer traces and application tests.
Installed-candidate results must name the actual tested wheel and revision;
source-test results cannot substitute for that artifact evidence.
