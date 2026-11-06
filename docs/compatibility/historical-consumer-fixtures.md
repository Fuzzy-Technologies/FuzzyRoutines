<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Historical-scale consumer fixtures

[Русский](historical-consumer-fixtures.ru.md) · [简体中文](historical-consumer-fixtures.zh-CN.md)

Use these cases to verify a consumer's transition from FuzzyRoutines 1.x to
2.x at the scale boundary. There is no application or data migration in
this repository. Each consumer owns its normalization, decision rules and
end-to-end acceptance.

- **TKSBrokerAPI.** The [pinned public replay](../performance/public-consumer-batch-replay.md)
  supplies 30 public `RiskLong` and `RiskShort` test cases. The scalar test
  reproduces each normalized coordinate, four-decimal percentage and selected
  label without importing the broker. The
  [older migration capture](../migration/consumer-scale-boundary.md) separately
  records 27 synthetic cases against 1.0.3 and 2.0.0, including the documented
  centroid corrections.
- **PriceGenerator.** An illustrative adapter maps invented integer ticks
  10000–10100 to the unit interval. Lower tick 10000 selects Min, tick 10023
  selects Low at the plateau boundary, and upper tick 10100 selects Max.
- **FMA.** An illustrative adapter maps an invented signed feature over
  −50–50 to the unit interval. Inputs −33, 0 and 27 map to 0.17, 0.5 and
  0.77. These select Min with weak confidence, Med and High respectively.
  At 0.17 the Min grade is `1 / (1 + (8 * 0.17) ** 20)`, approximately
  0.00212959. An explicit minimum confidence of 0.01 makes the modern
  classifier abstain on that input.

The [synthetic fixtures](../../tests/fixtures/historical_consumer_synthetic.json)
use `(sample - lower) / (upper - lower)` for a fixed nonzero range. Those
examples do not prescribe clipping, flat-range handling or abstention for
PriceGenerator or FMA. No authorized representative application inputs or
normalization contract for those two consumers were available here. The
fixtures do not attest to their adoption of 2.x or to trading behavior.

For these cases, require exact normalized coordinates, labels and term order
`Min, Low, Med, High, Max`. Compare ordered grades with an absolute tolerance
of `1e-12` and zero relative tolerance. The synthetic coordinates also point
to equivalent entries in the captured 1.0.3 baseline. Preserving the winning
label and grade does not imply equality of the historical sampled and
corrected 2.x centroids. See [ADR-0001](../adr/0001-backward-compatibility-contract.md)
and [ADR-0016](../adr/0016-linguistic-encodings-and-historical-preset.md).

From a checkout in the locked test environment, run:

```bash
python -m pytest -q tests/test_historical_consumer_fixtures.py tests/test_consumer_scale_migration.py
```
