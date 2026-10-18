<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Installed FuzzyRoutines comparison

Measured installed-wheel evidence; independent parity passed.

Times are microseconds per operation (scale lookup: per single lookup). Each timing cell is median / minimum / IQR; ratio is baseline median divided by candidate median.

- Baseline: version `2.0.0`; wheel SHA256 `501eefd15cefdbb137ad05f2887cb63d662b0f574c64a818ccb6675b2138a2c4`; package source commit `49c9aee67a60cad74bc9494943b8745b72d2f43c`.
- Candidate: version `2.1.0`; wheel SHA256 `3054f737f2cd247c20647abc5627f2368864563fd228544bb3bf01e8d76d44f7`; package source commit `9ab20c7e7b3d98e056f2670a7eebc75083e00553`.
- Wrapper source commit: `0dba28a072c6d8dff3eacdc336b922e1ab264b23`; workload source commit: `49c9aee67a60cad74bc9494943b8745b72d2f43c`. Both are separate from installed package commits.
- Samples: 7 per artifact, alternating paired process order; warmups: 1 per operation per worker.

Environment: 3.14.8 (main, Oct  3 2026, 01:04:31) [Clang 22.1.3 ]; Linux-6.18.55-x86_64-with-glibc2.39; AMD EPYC 9V74 80-Core Processor.
Runner SHA256: `c75c14b858d60904b37aebb6150c55ae5485dd58f0f14832510842ac914d5142`; immutable harness snapshot dirty state: `False`.

## Process startup and package import

| Workload        | 2.0.0 median / min / IQR (µs)             | Candidate median / min / IQR (µs)         | Baseline / candidate |
| --------------- | ----------------------------------------- | ----------------------------------------- | -------------------- |
| process_startup | 10627.924000 / 10134.641000 / 1337.597000 | 10939.116000 / 10152.448000 / 855.523500  | 0.972×               |
| package_import  | 16243.834000 / 14154.491000 / 3153.861000 | 16787.171000 / 15748.589000 / 1017.741000 | 0.968×               |

## Membership evaluation

| Workload                | 2.0.0 median / min / IQR (µs)  | Candidate median / min / IQR (µs) | Baseline / candidate |
| ----------------------- | ------------------------------ | --------------------------------- | -------------------- |
| membership_hyperbolic   | 0.395673 / 0.358380 / 0.030897 | 0.353435 / 0.332877 / 0.016327    | 1.120×               |
| membership_bell         | 0.498903 / 0.480010 / 0.033670 | 0.485599 / 0.456095 / 0.029532    | 1.027×               |
| membership_parabolic    | 0.437667 / 0.422294 / 0.089456 | 0.437890 / 0.408122 / 0.025923    | 0.999×               |
| membership_triangle     | 0.397632 / 0.356504 / 0.038281 | 0.381553 / 0.371548 / 0.033695    | 1.042×               |
| membership_trapezium    | 0.473162 / 0.380934 / 0.110803 | 0.387783 / 0.375187 / 0.017458    | 1.220×               |
| membership_exponential  | 0.391909 / 0.365928 / 0.080311 | 0.364809 / 0.341204 / 0.027202    | 1.074×               |
| membership_sigmoidal    | 0.429544 / 0.399968 / 0.138992 | 0.395944 / 0.375087 / 0.010471    | 1.085×               |
| membership_desirability | 0.488700 / 0.449582 / 0.167026 | 0.441489 / 0.436784 / 0.020310    | 1.107×               |

## Operator evaluation

| Workload          | 2.0.0 median / min / IQR (µs)  | Candidate median / min / IQR (µs) | Baseline / candidate |
| ----------------- | ------------------------------ | --------------------------------- | -------------------- |
| tnorm_logic       | 0.534169 / 0.513711 / 0.098469 | 0.507274 / 0.489424 / 0.009720    | 1.053×               |
| sconorm_logic     | 0.528172 / 0.494052 / 0.071413 | 0.514259 / 0.496043 / 0.056109    | 1.027×               |
| tnorm_algebraic   | 0.523481 / 0.476947 / 0.076470 | 0.502009 / 0.485860 / 0.017452    | 1.043×               |
| sconorm_algebraic | 0.530777 / 0.492472 / 0.068909 | 0.516249 / 0.501644 / 0.011912    | 1.028×               |
| tnorm_boundary    | 0.590153 / 0.533488 / 0.114527 | 0.568309 / 0.557114 / 0.040491    | 1.038×               |
| sconorm_boundary  | 0.586979 / 0.516495 / 0.128632 | 0.571311 / 0.535991 / 0.032121    | 1.027×               |
| tnorm_drastic     | 0.537011 / 0.513242 / 0.016990 | 0.529186 / 0.498484 / 0.022609    | 1.015×               |
| sconorm_drastic   | 0.563953 / 0.530486 / 0.035923 | 0.549011 / 0.516198 / 0.031013    | 1.027×               |

## Scale construction

| Workload                     | 2.0.0 median / min / IQR (µs)    | Candidate median / min / IQR (µs) | Baseline / candidate |
| ---------------------------- | -------------------------------- | --------------------------------- | -------------------- |
| scale_default_construction   | 22.938470 / 21.181260 / 4.279855 | 19.095450 / 18.584900 / 3.042725  | 1.201×               |
| scale_universal_construction | 31.581700 / 30.136560 / 2.955940 | 49.361510 / 45.382700 / 6.286140  | 0.640×               |

## Scale lookup

| Workload               | 2.0.0 median / min / IQR (µs)  | Candidate median / min / IQR (µs) | Baseline / candidate |
| ---------------------- | ------------------------------ | --------------------------------- | -------------------- |
| scale_default_lookup   | 1.407380 / 1.324938 / 0.202325 | 1.324758 / 1.302665 / 0.051958    | 1.062×               |
| scale_universal_lookup | 2.356500 / 2.180398 / 0.323139 | 2.220648 / 2.076804 / 0.158711    | 1.061×               |

## Fuzzy-set construction

| Workload                         | 2.0.0 median / min / IQR (µs)    | Candidate median / min / IQR (µs) | Baseline / candidate |
| -------------------------------- | -------------------------------- | --------------------------------- | -------------------- |
| fuzzyset_hyperbolic_construction | 23.177020 / 19.845170 / 3.452985 | 4.897080 / 4.627370 / 0.423280    | 4.733×               |
| fuzzyset_bell_construction       | 7.223130 / 6.670510 / 0.321735   | 5.660100 / 5.307490 / 0.482920    | 1.276×               |
| fuzzyset_triangle_construction   | 6.608520 / 6.232850 / 0.976195   | 6.931500 / 6.513470 / 1.118360    | 0.953×               |
| fuzzyset_parabolic_construction  | 4.444400 / 4.354270 / 0.420130   | 6.330200 / 5.870520 / 0.746900    | 0.702×               |

## Centroid recalculation

| Workload                     | 2.0.0 median / min / IQR (µs)         | Candidate median / min / IQR (µs)      | Baseline / candidate |
| ---------------------------- | ------------------------------------- | -------------------------------------- | -------------------- |
| fuzzyset_hyperbolic_centroid | 1201.994100 / 1134.065200 / 76.484150 | 5030.563700 / 4772.036200 / 272.676450 | 0.239×               |
| fuzzyset_bell_centroid       | 14.053900 / 13.618300 / 4.985900      | 16.999300 / 15.986700 / 1.478200       | 0.827×               |
| fuzzyset_triangle_centroid   | 12.572600 / 11.139500 / 3.808150      | 13.516100 / 13.283700 / 0.278950       | 0.930×               |
| fuzzyset_parabolic_centroid  | 11.080400 / 10.302300 / 1.859800      | 12.786000 / 12.272200 / 0.399600       | 0.867×               |

Independent parity precedes timing: analytical membership/operator references (absolute 1e-12), exact scale term order and midpoint lookup, closed-form centroids over [0, 1] (absolute 1e-10), and cross-version observations. Relative tolerance is zero.

Interpretation is limited to these fixed workloads on this host. There is no timing pass/fail threshold. Imports use fresh processes but a warm filesystem cache; startup includes subprocess launch/teardown. Operation timings exclude tracemalloc. Scale lookup retains the existing counting instrumentation. Optional NumPy and other runtime extras are not installed.
