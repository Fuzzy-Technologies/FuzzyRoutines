<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Installed FuzzyRoutines comparison

Measured installed-wheel evidence; independent parity passed.

Times are microseconds per operation (scale lookup: per single lookup). Each timing cell is median / minimum / IQR; ratio is baseline median divided by candidate median.

- Baseline: version `2.0.0`; wheel SHA256 `501eefd15cefdbb137ad05f2887cb63d662b0f574c64a818ccb6675b2138a2c4`; package source commit `49c9aee67a60cad74bc9494943b8745b72d2f43c`.
- Candidate: version `2.1.0`; wheel SHA256 `cf694da86b560d3619a5480f67a943ca7eb87a90e1c9fde97e188b380e86b883`; package source commit `4b9efcf67f42aee15bbce3aeac7bbb55388a4822`.
- Wrapper source commit: `bd6f0af22be325967c2694c9497e50b0af2cbff7`; workload source commit: `49c9aee67a60cad74bc9494943b8745b72d2f43c`. Both are separate from installed package commits.
- Samples: 7 per artifact, alternating paired process order; warmups: 1 per operation per worker.

Environment: 3.14.8 (main, Oct  3 2026, 01:04:31) [Clang 22.1.3 ]; Linux-6.18.44-x86_64-with-glibc2.39; AMD EPYC 9V74 80-Core Processor.
Runner SHA256: `c75c14b858d60904b37aebb6150c55ae5485dd58f0f14832510842ac914d5142`; immutable harness snapshot dirty state: `False`.

## Process startup and package import

| Workload        | 2.0.0 median / min / IQR (µs)             | Candidate median / min / IQR (µs)         | Baseline / candidate |
| --------------- | ----------------------------------------- | ----------------------------------------- | -------------------- |
| process_startup | 11582.297000 / 9732.126000 / 1040.516500  | 12064.579000 / 10089.450000 / 1421.533000 | 0.960×               |
| package_import  | 18279.296000 / 14527.427000 / 2661.438500 | 18142.660000 / 16847.651000 / 3201.325500 | 1.008×               |

## Membership evaluation

| Workload                | 2.0.0 median / min / IQR (µs)  | Candidate median / min / IQR (µs) | Baseline / candidate |
| ----------------------- | ------------------------------ | --------------------------------- | -------------------- |
| membership_hyperbolic   | 0.510981 / 0.428696 / 0.113382 | 0.378336 / 0.342263 / 0.058869    | 1.351×               |
| membership_bell         | 0.695534 / 0.511318 / 0.173768 | 0.492447 / 0.466539 / 0.047676    | 1.412×               |
| membership_parabolic    | 0.589209 / 0.475622 / 0.101189 | 0.464973 / 0.442101 / 0.046462    | 1.267×               |
| membership_triangle     | 0.568224 / 0.411998 / 0.125599 | 0.380996 / 0.350011 / 0.060162    | 1.491×               |
| membership_trapezium    | 0.585685 / 0.450275 / 0.123705 | 0.388333 / 0.366054 / 0.039697    | 1.508×               |
| membership_exponential  | 0.512527 / 0.390837 / 0.113596 | 0.370030 / 0.346072 / 0.027110    | 1.385×               |
| membership_sigmoidal    | 0.580353 / 0.434334 / 0.148486 | 0.392338 / 0.373963 / 0.042856    | 1.479×               |
| membership_desirability | 0.626448 / 0.524230 / 0.156164 | 0.459973 / 0.440406 / 0.085236    | 1.362×               |

## Operator evaluation

| Workload          | 2.0.0 median / min / IQR (µs)  | Candidate median / min / IQR (µs) | Baseline / candidate |
| ----------------- | ------------------------------ | --------------------------------- | -------------------- |
| tnorm_logic       | 0.676076 / 0.537628 / 0.238097 | 0.566629 / 0.497839 / 0.088778    | 1.193×               |
| sconorm_logic     | 0.709670 / 0.552307 / 0.231998 | 0.537953 / 0.494736 / 0.060169    | 1.319×               |
| tnorm_algebraic   | 0.572824 / 0.525248 / 0.214472 | 0.520076 / 0.497916 / 0.036047    | 1.101×               |
| sconorm_algebraic | 0.586533 / 0.528542 / 0.131054 | 0.567122 / 0.534471 / 0.111974    | 1.034×               |
| tnorm_boundary    | 0.697739 / 0.570049 / 0.273810 | 0.587438 / 0.549801 / 0.039655    | 1.188×               |
| sconorm_boundary  | 0.791928 / 0.572944 / 0.247037 | 0.577774 / 0.549806 / 0.078238    | 1.371×               |
| tnorm_drastic     | 0.583493 / 0.496913 / 0.163189 | 0.557088 / 0.507571 / 0.072711    | 1.047×               |
| sconorm_drastic   | 0.648266 / 0.551664 / 0.107342 | 0.543757 / 0.524361 / 0.079897    | 1.192×               |

## Scale construction

| Workload                     | 2.0.0 median / min / IQR (µs)    | Candidate median / min / IQR (µs) | Baseline / candidate |
| ---------------------------- | -------------------------------- | --------------------------------- | -------------------- |
| scale_default_construction   | 24.284480 / 22.841600 / 2.020490 | 20.745140 / 18.751140 / 1.906020  | 1.171×               |
| scale_universal_construction | 33.394280 / 30.662980 / 7.690030 | 56.396330 / 49.156320 / 8.813520  | 0.592×               |

## Scale lookup

| Workload               | 2.0.0 median / min / IQR (µs)  | Candidate median / min / IQR (µs) | Baseline / candidate |
| ---------------------- | ------------------------------ | --------------------------------- | -------------------- |
| scale_default_lookup   | 1.766801 / 1.420429 / 0.367624 | 1.401861 / 1.335491 / 0.104538    | 1.260×               |
| scale_universal_lookup | 2.526375 / 2.197439 / 0.657224 | 2.405192 / 2.101385 / 0.406412    | 1.050×               |

## Fuzzy-set construction

| Workload                         | 2.0.0 median / min / IQR (µs)    | Candidate median / min / IQR (µs) | Baseline / candidate |
| -------------------------------- | -------------------------------- | --------------------------------- | -------------------- |
| fuzzyset_hyperbolic_construction | 23.738940 / 20.328110 / 2.836725 | 5.152660 / 4.627570 / 0.453440    | 4.607×               |
| fuzzyset_bell_construction       | 7.208060 / 6.739750 / 2.054890   | 5.567690 / 5.195420 / 0.384380    | 1.295×               |
| fuzzyset_triangle_construction   | 6.728030 / 6.226180 / 2.749230   | 6.662130 / 6.423970 / 1.708220    | 1.010×               |
| fuzzyset_parabolic_construction  | 4.715900 / 4.452400 / 0.772760   | 6.382210 / 5.891870 / 3.138015    | 0.739×               |

## Centroid recalculation

| Workload                     | 2.0.0 median / min / IQR (µs)          | Candidate median / min / IQR (µs)      | Baseline / candidate |
| ---------------------------- | -------------------------------------- | -------------------------------------- | -------------------- |
| fuzzyset_hyperbolic_centroid | 1256.966900 / 1169.470100 / 170.782650 | 5261.266800 / 4944.305600 / 534.909150 | 0.239×               |
| fuzzyset_bell_centroid       | 15.559500 / 13.694600 / 1.919850       | 15.580500 / 15.217900 / 0.806750       | 0.999×               |
| fuzzyset_triangle_centroid   | 11.511400 / 11.145800 / 0.681000       | 12.438700 / 11.901000 / 4.581400       | 0.925×               |
| fuzzyset_parabolic_centroid  | 10.974600 / 10.335600 / 2.233900       | 11.941000 / 11.437200 / 1.049050       | 0.919×               |

Independent parity precedes timing: analytical membership/operator references (absolute 1e-12), exact scale term order and midpoint lookup, closed-form centroids over [0, 1] (absolute 1e-10), and cross-version observations. Relative tolerance is zero.

Interpretation is limited to these fixed workloads on this host. There is no timing pass/fail threshold. Imports use fresh processes but a warm filesystem cache; startup includes subprocess launch/teardown. Operation timings exclude tracemalloc. Scale lookup retains the existing counting instrumentation. Optional NumPy and other runtime extras are not installed.
