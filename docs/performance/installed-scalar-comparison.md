<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Installed FuzzyRoutines comparison

Measured installed-wheel evidence; independent parity passed.

Times are microseconds per operation (scale lookup: per single lookup). Each timing cell is median / minimum / IQR; ratio is baseline median divided by candidate median.

- Baseline: version `2.0.0`; wheel SHA256 `501eefd15cefdbb137ad05f2887cb63d662b0f574c64a818ccb6675b2138a2c4`; package source commit `49c9aee67a60cad74bc9494943b8745b72d2f43c`.
- Candidate: version `2.1.0`; wheel SHA256 `de07010468aceea6059225f867e44c80bd89ed64984826aad9e85b4b8723a7e0`; package source commit `c44983ab4be2ef58d7847e758c118875a51738db`.
- Wrapper source commit: `b451e502930d581fdffdc2a69ac44a8f3ab18174`; workload source commit: `49c9aee67a60cad74bc9494943b8745b72d2f43c`. Both are separate from installed package commits.
- Samples: 7 per artifact, alternating paired process order; warmups: 1 per operation per worker.

Environment: 3.14.8 (main, Oct  3 2026, 01:04:31) [Clang 22.1.3 ]; Linux-6.18.44-x86_64-with-glibc2.39; INTEL(R) XEON(R) PLATINUM 8573C.
Runner SHA256: `c75c14b858d60904b37aebb6150c55ae5485dd58f0f14832510842ac914d5142`; immutable harness snapshot dirty state: `False`.

## Process startup and package import

| Workload        | 2.0.0 median / min / IQR (µs)              | Candidate median / min / IQR (µs)          | Baseline / candidate |
| --------------- | ------------------------------------------ | ------------------------------------------ | -------------------- |
| process_startup | 45417.150000 / 22494.617000 / 30044.390000 | 37071.140000 / 29454.374000 / 24752.404000 | 1.225×               |
| package_import  | 51288.373000 / 33618.344000 / 17459.751500 | 53513.588000 / 30851.215000 / 27774.986500 | 0.958×               |

## Membership evaluation

| Workload                | 2.0.0 median / min / IQR (µs)  | Candidate median / min / IQR (µs) | Baseline / candidate |
| ----------------------- | ------------------------------ | --------------------------------- | -------------------- |
| membership_hyperbolic   | 0.712076 / 0.617538 / 0.145917 | 0.805905 / 0.607887 / 0.226581    | 0.884×               |
| membership_bell         | 1.006628 / 0.687717 / 0.345475 | 0.947009 / 0.732276 / 0.300956    | 1.063×               |
| membership_parabolic    | 0.909633 / 0.620787 / 0.270424 | 0.913090 / 0.517973 / 0.324462    | 0.996×               |
| membership_triangle     | 0.721088 / 0.534598 / 0.301122 | 0.991536 / 0.646939 / 0.277639    | 0.727×               |
| membership_trapezium    | 0.701932 / 0.649457 / 0.142963 | 0.821520 / 0.600141 / 0.127542    | 0.854×               |
| membership_exponential  | 0.703920 / 0.587997 / 0.268335 | 0.655663 / 0.459295 / 0.205208    | 1.074×               |
| membership_sigmoidal    | 0.762912 / 0.522331 / 0.222888 | 0.770031 / 0.590992 / 0.171775    | 0.991×               |
| membership_desirability | 0.890638 / 0.701863 / 0.069153 | 1.013178 / 0.705604 / 0.304045    | 0.879×               |

## Operator evaluation

| Workload          | 2.0.0 median / min / IQR (µs)  | Candidate median / min / IQR (µs) | Baseline / candidate |
| ----------------- | ------------------------------ | --------------------------------- | -------------------- |
| tnorm_logic       | 1.011522 / 0.793786 / 0.515214 | 1.098461 / 0.748537 / 0.483176    | 0.921×               |
| sconorm_logic     | 1.531233 / 0.973582 / 0.380295 | 1.387838 / 0.691214 / 0.483414    | 1.103×               |
| tnorm_algebraic   | 1.278291 / 0.835182 / 1.027147 | 1.379112 / 0.812033 / 0.515500    | 0.927×               |
| sconorm_algebraic | 1.075573 / 0.833140 / 0.398138 | 1.155596 / 0.817748 / 0.757312    | 0.931×               |
| tnorm_boundary    | 1.163889 / 0.856629 / 0.253668 | 1.828183 / 0.921237 / 1.012536    | 0.637×               |
| sconorm_boundary  | 0.904959 / 0.816708 / 0.161410 | 1.488079 / 0.948816 / 0.379985    | 0.608×               |
| tnorm_drastic     | 0.937650 / 0.805091 / 0.445141 | 1.388643 / 0.855028 / 0.673055    | 0.675×               |
| sconorm_drastic   | 1.222565 / 0.898928 / 0.327982 | 1.371547 / 0.850995 / 0.203182    | 0.891×               |

## Scale construction

| Workload                     | 2.0.0 median / min / IQR (µs)     | Candidate median / min / IQR (µs) | Baseline / candidate |
| ---------------------------- | --------------------------------- | --------------------------------- | -------------------- |
| scale_default_construction   | 59.963600 / 40.544470 / 13.123060 | 64.310020 / 33.201130 / 40.105210 | 0.932×               |
| scale_universal_construction | 81.654280 / 69.227540 / 38.040330 | 97.107090 / 52.022440 / 53.988190 | 0.841×               |

## Scale lookup

| Workload               | 2.0.0 median / min / IQR (µs)  | Candidate median / min / IQR (µs) | Baseline / candidate |
| ---------------------- | ------------------------------ | --------------------------------- | -------------------- |
| scale_default_lookup   | 2.713832 / 2.175305 / 0.955708 | 2.335492 / 2.099741 / 1.481726    | 1.162×               |
| scale_universal_lookup | 5.719162 / 3.730991 / 2.521044 | 5.228156 / 3.855152 / 2.439385    | 1.094×               |

## Fuzzy-set construction

| Workload                         | 2.0.0 median / min / IQR (µs)     | Candidate median / min / IQR (µs) | Baseline / candidate |
| -------------------------------- | --------------------------------- | --------------------------------- | -------------------- |
| fuzzyset_hyperbolic_construction | 69.438820 / 42.466290 / 28.328360 | 59.706620 / 37.126610 / 61.286760 | 1.163×               |
| fuzzyset_bell_construction       | 20.174190 / 10.897660 / 18.333505 | 23.435330 / 14.454140 / 18.846595 | 0.861×               |
| fuzzyset_triangle_construction   | 16.815090 / 10.586210 / 9.093130  | 21.410070 / 17.719950 / 9.684800  | 0.785×               |
| fuzzyset_parabolic_construction  | 12.162570 / 6.604250 / 9.913765   | 13.689530 / 6.474850 / 28.370000  | 0.888×               |

## Centroid recalculation

| Workload                     | 2.0.0 median / min / IQR (µs)          | Candidate median / min / IQR (µs)       | Baseline / candidate |
| ---------------------------- | -------------------------------------- | --------------------------------------- | -------------------- |
| fuzzyset_hyperbolic_centroid | 2711.358000 / 2024.418100 / 235.799800 | 3477.225000 / 2044.790700 / 3465.095500 | 0.780×               |
| fuzzyset_bell_centroid       | 25.141700 / 17.847700 / 51.592150      | 31.613800 / 18.242300 / 65.466450       | 0.795×               |
| fuzzyset_triangle_centroid   | 46.292400 / 17.320200 / 13.811150      | 24.071200 / 14.957800 / 72.142500       | 1.923×               |
| fuzzyset_parabolic_centroid  | 34.438800 / 13.789200 / 24.019050      | 14.219400 / 13.999900 / 6.456450        | 2.422×               |

Independent parity precedes timing: analytical membership/operator references (absolute 1e-12), exact scale term order and midpoint lookup, closed-form centroids over [0, 1] (absolute 1e-10), and cross-version observations. Relative tolerance is zero.

Interpretation is limited to these fixed workloads on this host. There is no timing pass/fail threshold. Imports use fresh processes but a warm filesystem cache; startup includes subprocess launch/teardown. Operation timings exclude tracemalloc. Scale lookup retains the existing counting instrumentation. Optional NumPy and other runtime extras are not installed.

## Reading this result

These installed-wheel measurements completed on 2026-10-14. Results are mixed: some candidate medians are lower and others higher. For example, universal-scale lookup measured 5.719162 µs for 2.0.0 and 5.228156 µs for 2.1.0; hyperbolic centroid recalculation measured 2711.358 µs and 3477.225 µs respectively. The process-startup control also varied between the two environments despite using the same interpreter. Several IQRs are large relative to their medians, including candidate hyperbolic centroid recalculation. These observations establish neither a general speedup nor a causal regression, and they do not predict production throughput.

Both environments contained exactly one installed distribution: `fuzzyroutines`, at the version being measured. The explicit NumPy extra was not installed. The 28 mathematical workloads passed their independent references in both untimed preflights and all 14 measured workers; cross-version observations also agreed before timing. Process startup and package import account for the remaining two rows.

## Evidence and artifact provenance

- [Raw scalar measurements](evidence/installed-scalar-python314.json): SHA256 `e1e29ac68e2a2a11177ea0141c5e8b97b277bd40522a6af989be83622f72074b`. All samples, elapsed times, iteration counts, per-unit calculations, environment details, installed origins, commands, and source/payload hashes are retained unchanged.
- [Installed consumer-boundary observations](evidence/consumer-scale-installed-2.1.0.json): SHA256 `8fa1ea3f8e254aaf78dcb922b893132d852bf75f6ed5dcf7116204546a99aa40`. After timing, the candidate environment passed `consumer_scale_migration.py --check-current` for all 27 synthetic boundary inputs. Term order, normalization, selected labels and percentages agree exactly with the frozen 2.0.0 fixture; grades use absolute tolerance `1e-12` and centroids `1e-10`. These are synthetic inputs derived from public consumer semantics, not production traces or private FMA/robot validation.
- Baseline identity is bound to the [PyPI 2.0.0 release metadata](https://pypi.org/pypi/fuzzyroutines/2.0.0/json). All 21 package source files/markers match source commit `49c9aee67a60cad74bc9494943b8745b72d2f43c`.
- Candidate identity is bound to the successful [package workflow run 38627553915](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/38627553915), artifact ID `11923929952`, and its downloaded archive SHA256 `b771b38a7654b0b9aa2dc2fab626006b7be957edaa892a599ce7185755c52412`. The workflow head is `f0d09c30189509a9a5237b4869e5aeeb5868e5f2`; the actual built source is the synthetic PR merge `c44983ab4be2ef58d7847e758c118875a51738db`. All 25 candidate package source files/markers match that built source. The complete archive binding and both source identities are recorded in the raw report.

The measured artifact is a CI-built `2.1.0` candidate. A later report-only commit can change wheel ZIP timestamps through `SOURCE_DATE_EPOCH`. Its release artifact requires a separate payload comparison; this report does not claim identical archive bytes for an artifact built from a later revision.

## Reproduction

The [installed scalar protocol](installed-scalar-comparison-protocol.md) defines the artifact guards, isolated environments, independent oracles and units. The [general benchmark protocol](benchmark-reproducibility-protocol.md) defines the sampling and reporting requirements. Keep the recorded baseline/candidate wheel bytes and their provenance files; ensure all recorded source commits are available in Git. Use a CPython 3.14 coordinator with pip, a clean checkout of the recorded harness commit, and a new output directory. Copy the recorded `configuration`, adjusting filesystem paths for the new host while preserving artifact hashes, source revisions, workload settings and sampling counts.

```bash
git worktree add --detach /tmp/fr-scalar-harness b451e502930d581fdffdc2a69ac44a8f3ab18174
cd /tmp/fr-scalar-harness
python3.14 -I experiments/benchmark_installed_scalar.py --config /absolute/path/scalar-config.json --run
```

After timing, run the boundary check with the candidate environment created by that invocation:

```bash
/absolute/path/results/candidate-venv/bin/python -I /tmp/fr-scalar-harness/tools/consumer_scale_migration.py --fixture /tmp/fr-scalar-harness/tests/fixtures/consumer_scale_migration.json --check-current --output /absolute/path/results/consumer-scale-installed.json
```

The complete table section above is the unchanged 7,633-byte output of the recorded renderer, SHA256 `cff9d08494baedecdaf764ee3d7bf46f36c9184a52c36985ddd2cd493c7d1c78`. This publication appends the interpretation and provenance sections. From a checkout containing these evidence files, regenerate that exact prefix without installing either package or collecting new timings:

```bash
python3.14 -I tools/render_installed_scalar_comparison.py --input docs/performance/evidence/installed-scalar-python314.json --output /tmp/installed-scalar-generated.md
sha256sum /tmp/installed-scalar-generated.md
```

The renderer recomputes per-unit rates from raw elapsed times and declared counts, then verifies all raw samples, minimum/median/IQR statistics and ratios before writing the tables. The raw report preserves the original execution paths for auditability; those paths are not required merely to regenerate this table.
