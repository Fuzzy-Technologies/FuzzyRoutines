<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Full-call batch selection audit — 2026-10-16

Task #350 replaces first/last cumulative integer scans with argmax/indexed
Boolean selection. Public construction still validates and copies every
array. This measures complete `FuzzifyBatch` calls, including list conversion
where named, against the pre-audit implementation; it is not a kernel-only
claim or a comparison with published 2.0 (which has no batch API).

Two independently reproducible local wheel builds were installed into separate
CPython 3.14.8 / NumPy 2.3.5 environments. The baseline is `640199f4`; the fixed
wheel was built from local commit `edb920c`, whose full tree is identical to
published `2a3b655`. These are local artifacts, not CI downloads. The
[raw record](evidence/batch-selection-2026-10-16.json) preserves wheel hashes,
installed package hashes/origins, host limits, seven alternating wall/CPU pairs,
two warmups and separate traced-memory observations. The
[runner](../../experiments/benchmark_batch_selection.py) takes the two installed
interpreters and a new output path; it uses isolated workers and excludes
setup, validation and tracing from timing.

| Scale      | Values | Input           | Before (ms) | After (ms) | Before / after |
| ---------- | ------ | --------------- | ----------- | ---------- | -------------- |
| historical | 16     | prepared_array  | 0.3035      | 0.3157     | 0.961          |
| historical | 16     | list_conversion | 0.2755      | 0.2842     | 0.969          |
| historical | 200000 | prepared_array  | 54.4995     | 42.2862    | 1.289          |
| historical | 200000 | list_conversion | 99.0846     | 84.7607    | 1.169          |
| custom     | 16     | prepared_array  | 0.4007      | 0.3975     | 1.008          |
| custom     | 16     | list_conversion | 0.3777      | 0.3961     | 0.953          |
| custom     | 200000 | prepared_array  | 77.7896     | 59.2504    | 1.313          |
| custom     | 200000 | list_conversion | 112.8721    | 92.6425    | 1.218          |

For 200,000 values, observed speed ratios range from 1.17 to 1.31. Small calls
range from 0.95 to 1.01: the extra indexed-mask setup has no useful small-call
advantage. This shared-host result defines no universal crossover or dispatch
threshold. No dependency or backend-selection behavior changes.

All complete result arrays, including confidence/tie/selection masks, were
byte-identical before and after in all eight cases. Each worker also checked
up to 1,024 scalar reference points with absolute grade tolerance `1e-12` and
exact masks; the separate independent row-wise regression covers 180
shape/policy combinations, including all-false and empty leading dimensions.

Separately traced historical-scale peak allocation at 200,000 values decreased
from 39,802,107 to 28,402,014 bytes. The custom-scale peak stayed about 65 MB
because membership evaluation dominates its high-water mark. Small calls used
roughly 0.7–1.5 KB more peak traced allocation. These are Python/NumPy traced
peaks, not a promise about process RSS or arbitrary term counts.
