<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Benchmark Methodology and Results

This page publishes one reproducible observation set for the dependency-free
scalar benchmark tools. It is evidence for Tasks
[#100](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/100),
[#101](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/101), and
[#102](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/102) under
the [benchmark protocol](performance/benchmark-reproducibility-protocol.md).
The [cache decision](performance/cache-and-precomputation-evaluation.md)
defines the related correctness boundary for mutable objects.

The numbers below describe one virtualized host and one source revision. They
are not cross-machine comparisons, release guarantees, or claims that one
implementation is faster than another.

## Evidence identity

| Item                  | Recorded value                                                                                                                             |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Source revision       | `33e517325fcd9337e75efd52bf7b80e8aa9912b8`                                                                                                 |
| Source state          | Clean worktree                                                                                                                             |
| Package               | `fuzzyroutines==2.0.0.dev0`, installed from the local checkout                                                                             |
| Interpreter           | CPython 3.13.15, Clang 22.1.3                                                                                                              |
| Platform              | Linux 6.18.44, x86_64, glibc 2.39, KVM virtual machine                                                                                     |
| Processor             | Intel Xeon Platinum 8573C, 9 logical CPUs exposed                                                                                          |
| Physical memory       | 23,109,894,144 bytes reported by the host                                                                                                  |
| Environment manager   | `uv 0.12.17`                                                                                                                               |
| CPU controls          | No affinity, governor, or process-priority change was applied                                                                              |
| Measurement date      | 2026-09-23                                                                                                                                 |

The benchmark processes use only the Python standard library and the installed
local package. Test-only dependencies are not imported by the benchmark tools.
The environment was prepared and the evidence was captured from the repository
root with these commands:

```bash
uv python install 3.13
uv run --python 3.13 python --version
.venv/bin/python -m tools.benchmark_membership_operators \
  > /tmp/fr113-membership-313.json
.venv/bin/python -m tools.benchmark_fuzzyset_centroid \
  > /tmp/fr113-centroid-313.json
.venv/bin/python -m tools.benchmark_scale_lookup \
  > /tmp/fr113-scale-313.json
```

Each JSON document was parsed successfully. Every report identified the same
clean Git revision, interpreter, package version, platform, logical CPU count,
and physical-memory value shown above.

## Methodology

### Membership functions and fuzzy operators

`tools.benchmark_membership_operators` covers all eight supported legacy
membership families and all four supported t-norm and s-norm families. Each
workload performs one warm-up operation followed by seven measured samples of
10,000 operations. The tool uses `time.perf_counter_ns()`, divides each elapsed
sample by 10,000, and reports nanoseconds per scalar operation. The primary
statistic is the median; minimum and inclusive interquartile range (IQR) expose
local variation.

Before timing, each workload compares its result with an analytical reference
using absolute tolerance $10^{-12}$ and zero relative tolerance. All 16 parity
checks passed in this evidence set.

| Workload                    | Median ns/op | Minimum ns/op | IQR ns/op | Parity |
|-----------------------------|-------------:|--------------:|----------:|:------:|
| `membership_hyperbolic`     |      310.647 |       298.279 |     7.276 |  PASS  |
| `membership_bell`           |      699.538 |       583.869 |   253.632 |  PASS  |
| `membership_parabolic`      |      382.997 |       375.719 |    44.102 |  PASS  |
| `membership_triangle`       |      303.779 |       296.483 |    17.896 |  PASS  |
| `membership_trapezium`      |      357.618 |       284.933 |   161.055 |  PASS  |
| `membership_exponential`    |      399.255 |       318.822 |   321.996 |  PASS  |
| `membership_sigmoidal`      |      430.550 |       344.012 |   205.052 |  PASS  |
| `membership_desirability`   |      686.617 |       506.447 |   174.807 |  PASS  |
| `tnorm_logic`               |      572.033 |       477.840 |   293.041 |  PASS  |
| `tnorm_algebraic`           |      477.470 |       465.661 |    11.653 |  PASS  |
| `tnorm_boundary`            |      581.074 |       523.723 |    49.181 |  PASS  |
| `tnorm_drastic`             |      602.120 |       495.499 |   137.697 |  PASS  |
| `sconorm_logic`             |      537.064 |       520.489 |    47.329 |  PASS  |
| `sconorm_algebraic`         |      477.295 |       474.018 |    21.717 |  PASS  |
| `sconorm_boundary`          |      514.751 |       490.947 |    25.844 |  PASS  |
| `sconorm_drastic`           |      532.395 |       512.493 |   191.793 |  PASS  |

Raw timing samples, in nanoseconds per operation and original execution order:

```text
membership_hyperbolic   = 311.529, 313.249, 304.737, 298.279, 305.489, 310.647, 332.144
membership_bell         = 906.385, 921.884, 699.538, 649.836, 962.653, 671.170, 583.869
membership_parabolic    = 378.749, 375.719, 532.997, 381.805, 382.997, 402.159, 446.599
membership_triangle     = 303.779, 297.572, 296.483, 348.676, 299.213, 313.881, 318.695
membership_trapezium    = 284.933, 319.848, 390.764, 557.622, 357.618, 306.429, 1147.224
membership_exponential  = 1217.815, 566.133, 743.470, 339.114, 326.497, 318.822, 399.255
membership_sigmoidal    = 355.481, 365.913, 569.881, 430.550, 602.965, 561.616, 344.012
membership_desirability = 531.520, 686.617, 705.664, 767.786, 932.999, 592.316, 506.447
tnorm_logic             = 477.840, 903.556, 726.443, 479.243, 1474.408, 564.674, 572.033
tnorm_algebraic         = 480.714, 469.707, 465.661, 488.716, 477.470, 465.939, 478.238
tnorm_boundary          = 573.714, 632.355, 625.994, 590.085, 581.074, 523.723, 544.004
tnorm_drastic           = 533.768, 501.226, 495.499, 697.879, 602.120, 656.347, 654.042
sconorm_logic           = 537.064, 693.455, 569.023, 526.324, 531.190, 583.150, 520.489
sconorm_algebraic       = 483.990, 477.028, 477.246, 513.718, 477.295, 474.018, 538.080
sconorm_boundary        = 511.795, 549.882, 566.079, 517.992, 514.751, 504.392, 490.947
sconorm_drastic         = 857.264, 566.970, 532.395, 521.695, 512.493, 512.997, 851.307
```

### Fuzzy-set construction and centroid recalculation

`tools.benchmark_fuzzyset_centroid` separates construction from explicit
legacy centroid recalculation for representative `hyperbolic`, `bell`,
`triangle`, and `parabolic` shapes on support $(0, 1)$. Each cell below is one
seven-sample workload measured with `time.perf_counter_ns()` while
`tracemalloc` records peak Python allocation. The IQR values were derived from
the published raw samples with the same inclusive-quartile method used by the
membership benchmark.

| Shape        | Workload                 | Median ns | Minimum ns | Maximum ns | IQR ns      | Median peak bytes |
|--------------|--------------------------|----------:|-----------:|-----------:|------------:|------------------:|
| `hyperbolic` | construction             |    24,300 |     21,211 |     96,244 |     8,773.5 |             2,384 |
| `hyperbolic` | centroid recalculation   | 1,936,409 |  1,705,914 |  2,460,943 |   360,889.5 |               152 |
| `bell`       | construction             |    24,254 |     22,223 |     37,882 |     3,729.0 |             2,240 |
| `bell`       | centroid recalculation   | 1,767,720 |  1,612,235 |  2,446,258 |   245,615.5 |               152 |
| `triangle`   | construction             |    23,340 |     22,346 |     36,718 |     1,936.5 |             2,128 |
| `triangle`   | centroid recalculation   | 1,578,263 |  1,423,033 |  1,925,849 |   164,450.5 |               152 |
| `parabolic`  | construction             |    22,668 |     21,570 |     43,044 |    10,348.0 |             2,064 |
| `parabolic`  | centroid recalculation   | 2,013,154 |  1,863,378 |  5,491,256 | 1,014,031.0 |               152 |

Raw samples use `duration_ns / peak_bytes` pairs in original order:

```text
hyperbolic construction           = 96244/2432, 35147/2416, 26486/2400, 24300/2384, 22294/2368, 21792/2336, 21211/2320
hyperbolic centroid recalculation = 2264499/152, 1917633/152, 2460943/152, 1936409/152, 1855524/152, 2230437/152, 1705914/152
bell construction                 = 37882/2288, 25500/2272, 24254/2256, 22223/2240, 28769/2224, 23773/2192, 23038/2176
bell centroid recalculation       = 1767720/152, 2446258/152, 1863785/152, 2072220/152, 1722798/152, 1721976/152, 1612235/152
triangle construction             = 36718/2144, 25629/2128, 23455/2112, 23340/2160, 22576/2144, 22635/2112, 22346/2096
triangle centroid recalculation   = 1688428/152, 1569629/152, 1714000/152, 1503898/152, 1925849/152, 1578263/152, 1423033/152
parabolic construction            = 33167/2064, 31491/2064, 22668/2064, 22150/2064, 21570/2064, 43044/2064, 21812/2064
parabolic centroid recalculation  = 1878857/152, 1863378/152, 2891651/152, 2013154/152, 5491256/152, 3009850/152, 1994582/152
```

This tool records timing and allocation observations, but it does not embed a
separate centroid parity oracle. Therefore these values cannot support a
correctness or optimization claim by themselves; analytical centroid evidence
and regression tests remain independent gates.

### Scale construction and repeated lookup

`tools.benchmark_scale_lookup` separates construction from batches of 100
lookups at input `0.5`. Each workload has seven samples. The default scale has
three terms and the universal scale has five. Instrumentation confirmed exactly
one membership evaluation per term per lookup: 300 and 500 evaluations per
sample respectively. Both workloads selected `Med`.

| Scale       | Workload              | Median ns | Minimum ns | Maximum ns | IQR ns   | Median peak bytes |
|-------------|-----------------------|----------:|-----------:|-----------:|---------:|------------------:|
| `default`   | construction          |    86,356 |     76,816 |    351,255 | 75,806.0 |             6,541 |
| `default`   | 100 repeated lookups  |   291,635 |    265,638 |    392,812 | 60,772.5 |               200 |
| `universal` | construction          |   125,885 |    122,684 |    461,951 | 18,971.5 |             9,477 |
| `universal` | 100 repeated lookups  |   503,912 |    458,913 |    604,431 | 71,397.0 |               216 |

Raw samples use `duration_ns / peak_bytes` pairs in original order:

```text
default construction         = 164510/7061, 86356/6861, 154440/6709, 83965/6541, 83373/6361, 76816/6197, 351255/6013
default 100 repeated lookups = 392812/200, 272748/200, 364348/200, 268293/200, 298238/200, 291635/200, 265638/200
universal construction       = 154689/9693, 461951/9621, 130236/9485, 125885/9477, 122755/9469, 124227/9453, 122684/9445
universal 100 repeated lookups = 503912/216, 600886/216, 604431/216, 504844/216, 480975/216, 458913/216, 481961/216
```

## Interpretation and limitations

- Virtualized shared-host scheduling is visible in several wide ranges. The
  median is descriptive for this run; it is not a stable service-level target.
- `tracemalloc` measures traced Python allocations, not process RSS, allocator
  arenas, native allocations, or total machine memory.
- The centroid and scale tools currently perform no explicit warm-up phase and
  report min/median/max rather than IQR in their JSON. This page preserves that
  limitation and derives IQR only as a transparent presentation statistic.
- The centroid benchmark has no embedded parity result. Its timings are useful
  for profiling only when paired with separate mathematical tests.
- The scale instrumentation checks evaluation count and selected level. It does
  not prove equivalence to another implementation.
- No before/after candidate was measured on this host. These observations do
  not establish an optimization result or a comparison with the historical
  implementation.

Any future performance claim must name both revisions, repeat both measurements
in the same controlled environment, preserve raw samples, and pass numerical
and compatibility evidence before interpreting timing differences.
