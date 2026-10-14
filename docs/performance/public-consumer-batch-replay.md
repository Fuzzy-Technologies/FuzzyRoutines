<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Public consumer test replays

These measurements replay the **actual ordered inputs of two public consumer
tests**. They complement the [synthetic batch comparison](public-batch-comparison.md)
with independently specified expected outputs. The groups contain 17 `RiskLong`
cases and 13 `RiskShort` cases. They are regression-test workloads, not observed
production batches or a distribution of trading traffic.

## Source and extraction

Both files come from TKSBrokerAPI commit
`b963c54039f013d432220186ae35a22359c5a773`:

- [TradeRoutines.py](https://github.com/Fuzzy-Technologies/TKSBrokerAPI/blob/b963c54039f013d432220186ae35a22359c5a773/tksbrokerapi/TradeRoutines.py), Git blob `012caf30a61daf79117f95ee880c4d224213e103`.
- [test_TradeRoutines.py](https://github.com/Fuzzy-Technologies/TKSBrokerAPI/blob/b963c54039f013d432220186ae35a22359c5a773/tests/test_TradeRoutines.py), Git blob `0a09fc3e30fe7182320fb776979d4b704e81fe0f`. The positive loops occupy lines 908–932 and 950–970.
- [Apache-2.0 license](https://github.com/Fuzzy-Technologies/TKSBrokerAPI/blob/b963c54039f013d432220186ae35a22359c5a773/LICENSE), Git blob `2bb9ad240fa04c8cf706a4901c4807878e90c2dc`. The source test file attributes authorship to Timur Gilmullin; the extracted fixture preserves that attribution and records its transformation.

The [fixture](../../tests/fixtures/public_consumer_batches.json) retains all 30
price triples, their original order, independently authored labels and expected
percentages rounded to four decimal places. Its SHA-256 is
`352fa0cd67c3a5ddbc45f50c0271ba0eae081c9bb306c83aba0a7c6208f82736`.
The [extractor](../../tools/extract_consumer_replay.py) verifies the complete
SHA-256 of both upstream files, parses the test AST and reads only literal data.
It applies the pinned clipping and directional-distance normalization before
recording the coordinate vectors. It neither imports nor executes TKSBrokerAPI.
Independent review also evaluated the two isolated scalar function ASTs with a
coordinate-recording scale stub and confirmed all 30 derived coordinates and
percentages exactly.

Every original `RiskLong`/`RiskShort` invocation classifies **one** coordinate.
The replay groups combine those individual test cases for measuring the modern
batch API. The original scalar calls are not silently reclassified as a batch
interface. The same source also contains `ReachLong`/`ReachShort`, which reduce
a price history to one extremum-position coordinate, and
`EstimateTargetReachability`, which classifies one aggregated `pFinal` value.
Their history lengths are therefore not fuzzy-batch sizes, and these routines
are outside the measured replay.

## Measurement boundary

The scalar reference and NumPy path use the same modern historical-scale
factory and explicit historical tie policy. Both return complete membership
and selection evidence. Price normalization and model construction happen
before timing. Prepared-array cases provide an existing float64 array;
list-input cases include conversion in the measured call. Both include
validation, result allocation and the public API's ownership guarantees.
The benchmark excludes the consumer engine and network access.

- Exact source candidate and scalar baseline: `39b782022922172f63106e948a054235768665ec`; the measured checkout was clean.
- CPython 3.14.8, NumPy 2.3.5, Linux x86-64 on the same shared execution host as the synthetic study. The complete host metadata is recorded in JSON.
- Four workload/mode combinations, one warmup and seven paired repeats with alternating backend order. Raw wall/CPU samples and their summaries are retained.
- All four parity checks passed: maximum grade error `0.0`, absolute acceptance bound `1e-12`, relative tolerance zero. Selected/tied masks and all upstream expected labels/rounded percentages matched exactly.
- [Raw replay JSON](evidence/public-consumer-replays-python314-linux.json), SHA-256 `8d787b6bba4992177893367c9da141cdc808727f40fe7b450b30166451d9b97c`. All seven recorded source/fixture hashes were checked against the named commit.

| Public replay | Coordinates | Input           | Scalar median, ms | NumPy median, ms | Scalar / NumPy |
| ------------- | ----------: | --------------- | ----------------: | ---------------: | -------------: |
| RiskLong      | 17          | Prepared array  | 0.928             | 1.049            | 0.89×          |
| RiskLong      | 17          | List conversion | 1.674             | 1.659            | 1.01×          |
| RiskShort     | 13          | Prepared array  | 1.538             | 1.760            | 0.87×          |
| RiskShort     | 13          | List conversion | 1.692             | 2.607            | 0.65×          |

A ratio below one means NumPy was slower. These small replay groups produced
ratios from 0.65× to 1.01×, with no consistent speed advantage for NumPy. Keep
scalar evaluation for such small calls unless measurements of the actual caller
justify grouping them. Differences between input modes include shared-host
variation; this run establishes neither a universal crossover nor application
throughput. There are no timing thresholds in FuzzyRoutines CI.

Isolated memory observations gave whole-process peak RSS of
approximately 21.6 MiB for scalar and 36.6–38.2 MiB for NumPy. Traced operation peaks were
4.72–5.94 KiB and 6.24–7.03 KiB respectively. These are single
process observations, not incremental array costs or memory distributions.
Import and installation costs were not remeasured: the unchanged, separately
pinned [synthetic record](evidence/public-batches-python314-linux.json) supplies
that evidence, and the replay JSON records its SHA-256 explicitly.

## Reproduce

From the checkout with NumPy 2.3.5 installed:

```bash
python -m pytest -q tests/test_consumer_batch_replay.py
python -m experiments.benchmark_public_batches --consumer-replays --output /tmp/public-consumer-replays.json
```

To audit extraction, download the two pinned source files linked above and
provide their local paths. A different revision fails the byte-hash check:

```bash
python -m tools.extract_consumer_replay --source /tmp/TradeRoutines.py --tests /tmp/test_TradeRoutines.py --check
```

The original 24-case synthetic raw record and its two SVG figures remain
unchanged. These replay results supply bounded public-consumer workload
evidence. They do not establish private FMA/robot integration, trading
decisions or production throughput. Those claims still require authorized
application data and application-level checks. Installed-wheel execution and
the supported Python/NumPy matrix are separate PR/release evidence.
