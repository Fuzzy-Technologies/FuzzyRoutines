<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Scalar and optional NumPy workload comparison

Task #108 measures the isolated [array prototype](vectorized-membership-prototype.md)
against the current scalar API. In this Linux/CPython 3.14.7 run, all eight
families were slower through NumPy for 1- and 16-coordinate batches. With
100,000 coordinates and list conversion included, NumPy was 7.14–11.88 times
faster for membership evaluation and 10.03 times faster for default-scale batch
classification. The faster cases consumed more measured process memory and
traced temporary allocations. These observations support
[ADR-0015](../adr/0015-optional-vectorized-execution-strategy.md): retain the
dependency-free scalar default and adopt optional, explicitly selected
vectorization for large built-in batches. Public backend implementation remains
separate future work under that decision's acceptance gates.

## Evidence and source identity

- Measurement date: 2026-10-03 UTC.
- Scalar/prototype baseline: develop
  `42b0d217a7ab74d3be0ab4db96267bf350a80675` (Tasks #89 and #107 merged).
- Measured harness commit:
  [`147694190ae7d07b659d4453faf3973efe1bb4fd`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/147694190ae7d07b659d4453faf3973efe1bb4fd),
  clean source tree. This commit adds the harness/tests; production and
  prototype evaluator bytes match the baseline.
- [Machine-readable evidence](evidence/vectorized-membership-python314-linux.json)
  contains all 72 comparisons, seven raw wall/CPU samples per backend, median,
  minimum, maximum, inclusive IQR, parity and isolated memory observations.
- Evidence SHA-256: `e6d725618bf2712fe073a2a832f03e019a9e936d03b803082216eaa38c5f360e`.
- The evidence records SHA-256 for the harness, prototype and scalar source
  files; report-only commits do not invalidate the measured code identity.

## Environment and reproduction

| Field               | Recorded value                                                       |
| ------------------- | -------------------------------------------------------------------- |
| Runtime             | CPython 3.14.7; Clang 22.1.3; source package 2.0.0.dev0              |
| Optional dependency | NumPy 2.3.5                                                          |
| Installer           | pip 26.2.1                                                           |
| OS                  | Linux 6.18.44, x86_64, glibc 2.39                                    |
| CPU                 | AMD EPYC 9V74 80-Core Processor; 9 visible logical CPUs              |
| CPU allowance       | Affinity 0–8; cgroup `cpu.max = 800000 100000` (8 CPU equivalents)   |
| Memory              | 10,451,464,192 host bytes; cgroup limit 8,589,934,592 bytes          |
| Thread environment  | `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`   |
| Sampling            | One workload warmup; seven paired repeats; alternating backend order |
| Timers              | `time.perf_counter_ns()` and `time.process_time_ns()`                |

Other project test/build jobs were paused during measurement. This was a
shared execution host; global host idleness, frequency governor, priority and
exclusive CPU reservation were not controlled. No cross-machine performance
claim follows from these values.

At the measured commit, create a Python 3.14 environment with pip and install
the isolated dependency. The full resource report currently requires POSIX;
Linux uses `/proc/self/status` `VmHWM` for address-space peak RSS. Portable
workload/parity tests remain usable with NumPy on other platforms.

```bash
python -m pip install -r experiments/requirements-vectorized.txt
python -m pip download --no-deps --only-binary=:all: numpy==2.3.5 --dest /tmp/fr108-wheel
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -m experiments.benchmark_vectorized_membership \
  --sizes 1 16 1024 100000 --repeats 7 --warmups 1 --target-elements 4096 \
  --numpy-wheel /tmp/fr108-wheel/numpy-2.3.5-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl \
  --output /tmp/vectorized-membership-report.json
```

The exact executable/output paths used for this observation are retained in
JSON. A different Python/platform requires its matching wheel; it constitutes
a new environment. Omit `--numpy-wheel` to collect installed/import cost only.
`--skip-memory` omits isolated workload memory probes, not dependency probes.

## Workloads and phase boundaries

Inputs are deterministic binary64 grids: eight-family cases use
$[-5, 5]$ and default-scale classification uses $[0, 1]$. Coordinates come
from `left + width * index / max(1, size - 1)`, without an RNG or seed.
Sizes are 1, 16, 1,024 and 100,000; size 1 uses the left endpoint and can select
an inactive/saturated branch. Family parameters are recorded in the measured
harness. These are representative library workloads, not an FMA trading trace
or an application throughput measurement.

| Mode                         | Scalar path                                                                              | NumPy path                                                                                       |
| ---------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `evaluation`                 | Preconstructed `MFunction`; prepared Python float list; public `mju` for each coordinate | Prepared contiguous float64 array; public experimental `EvaluateMembership`                      |
| `end_to_end`                 | Construct `MFunction` per batch; evaluate original Python float list                     | Supply the same original list to public `EvaluateMembership`, including list-to-array conversion |
| Classification, `evaluation` | Preconstructed actual default `FuzzyScale`; public `Fuzzy` per coordinate                | Preconstructed same scale; public `EvaluateMembership` per term, stack grades and select index   |
| Classification, `end_to_end` | Construct the actual default scale per batch, then scalar classification                 | Construct the same scale per batch, convert each term's list input, evaluate and select index    |

Both modes include all their public input/parameter checks and result
allocation. The prototype snapshots parameters and copies its input on each
call even for an existing ndarray; this cost remains included in
`evaluation`. Scalar preconstruction has no array counterpart in the current
prototype API. No private formula kernel is timed. Import/process startup,
input-grid generation, tracing and parity checks are outside workload timing.
"End to end" refers to construction/conversion/evaluation of one supplied
batch, excluding application data ingestion or defuzzification.

Classification returns zero-based level indices in both paths. The array
selector reverses the grade rows before `argmax` to preserve the actual
scalar rule that later levels win ties. This benchmark-only selector is not
an implementation of a public array scale API. It covers the default
three-level scale; no universal-scale or inference-engine extrapolation is
made.

Warmup uses one batch per backend. Each timing repeat performs
`max(1, min(256, 4096 // size))` batches and reports elapsed time divided by
that batch count. Returned results are discarded after each call. Raw timing
samples and spread are available in JSON; values below are medians.

## Timing results

Speedup is scalar time divided by NumPy time; a value below 1 means NumPy is
slower. Wall and process CPU agree closely here; this does not imply identical
behavior under different scheduling or concurrent application load.

### Original-list input (`end_to_end`)

| Workload                       | Wall speedup, 16 | Wall speedup, 1,024 | Scalar ms, 100,000 | NumPy ms, 100,000 | Wall speedup, 100,000 | CPU speedup, 100,000 |
| ------------------------------ | ---------------: | ------------------: | -----------------: | ----------------: | --------------------: | -------------------: |
| `hyperbolic`                   | 0.43             | 4.91                | 28.813             | 4.036             | 7.14                  | 7.14                 |
| `bell`                         | 0.22             | 4.24                | 35.197             | 4.243             | 8.30                  | 8.30                 |
| `parabolic`                    | 0.30             | 4.48                | 32.643             | 3.547             | 9.20                  | 9.21                 |
| `triangle`                     | 0.29             | 4.03                | 25.153             | 3.172             | 7.93                  | 7.93                 |
| `trapezium`                    | 0.33             | 4.41                | 26.443             | 3.133             | 8.44                  | 8.44                 |
| `exponential`                  | 0.45             | 5.73                | 30.853             | 3.488             | 8.85                  | 8.85                 |
| `sigmoidal`                    | 0.37             | 5.73                | 34.723             | 4.189             | 8.29                  | 8.29                 |
| `desirability`                 | 0.50             | 8.14                | 45.697             | 3.847             | 11.88                 | 11.88                |
| `default_scale_classification` | 0.31             | 4.98                | 125.175            | 12.485            | 10.03                 | 10.03                |

### Prepared input (`evaluation`)

| Workload                       | Wall speedup, 16 | Wall speedup, 100,000 |
| ------------------------------ | ---------------: | --------------------: |
| `hyperbolic`                   | 0.22             | 26.38                 |
| `bell`                         | 0.12             | 26.65                 |
| `parabolic`                    | 0.17             | 46.83                 |
| `triangle`                     | 0.16             | 44.59                 |
| `trapezium`                    | 0.16             | 43.63                 |
| `exponential`                  | 0.26             | 34.09                 |
| `sigmoidal`                    | 0.22             | 21.71                 |
| `desirability`                 | 0.37             | 36.66                 |
| `default_scale_classification` | 0.19             | 29.52                 |

For this grid, all families already benefit at 1,024 coordinates with list
conversion included. The sampled sizes do not locate an exact break-even
point. Conversion, masks, output form, active branches and repeated use of
prepared arrays can move it substantially; an application must measure its
actual batch shape and representation.

## Memory results

These are separate fresh-process observations for the smallest and largest
size of each mode, not allocations measured during the timing loop. Before
and after one untraced operation, each Linux child reads its current address
space's `VmHWM`. Using `getrusage().ru_maxrss` here would retain a Linux
pre-exec launcher peak and conceal the actual worker footprint.

The table shows a single untraced total process peak, followed by a separately
traced operation peak for original-list input with 100,000 coordinates.

| Workload                       | Scalar RSS MiB | NumPy RSS MiB | Scalar traced peak MiB | NumPy traced peak MiB |
| ------------------------------ | -------------: | ------------: | ---------------------: | --------------------: |
| `hyperbolic`                   | 27.98          | 43.72         | 1.91                   | 3.15                  |
| `bell`                         | 27.69          | 43.15         | 1.68                   | 3.40                  |
| `parabolic`                    | 27.69          | 42.65         | 1.68                   | 2.79                  |
| `triangle`                     | 27.69          | 42.62         | 1.68                   | 2.86                  |
| `trapezium`                    | 27.37          | 42.40         | 1.45                   | 2.77                  |
| `exponential`                  | 29.52          | 44.09         | 3.05                   | 3.82                  |
| `sigmoidal`                    | 29.52          | 44.80         | 3.05                   | 4.41                  |
| `desirability`                 | 29.52          | 44.16         | 3.05                   | 3.91                  |
| `default_scale_classification` | 26.47          | 49.96         | 0.77                   | 7.64                  |

RSS includes interpreter, imports, prepared inputs and allocator behavior;
it is not an incremental allocation estimate. Before/after high-water
increases in JSON can be zero when input preparation already established a
larger peak. They do not imply zero allocation. Memory probes have one sample
per case and are observations, not statistical confidence bounds.

`tracemalloc` starts after input preparation and reports a separate operation
peak. It captures Python/NumPy allocations registered with Python's tracing
allocator, not all native allocator, mapped library, retained arena or OS
memory. It is not a substitute for RSS. Scalar grades outside active branches
can share constant float objects; their list footprint varies with branches.

One 100,000-element float64 output has a payload of 800,000 bytes; default-scale
indices use the same byte count here as NumPy int64. Python lists contain
references plus separately owned/shared objects. JSON keeps array `nbytes`,
shallow list/object sizes, tracing and RSS in distinct fields; none of these
are summed to manufacture a "total memory" figure.

## Optional dependency cost

| Observation                                     | Value                                   |
| ----------------------------------------------- | --------------------------------------: |
| Platform wheel download size                    | 16,597,350 bytes (15.83 MiB)            |
| Wheel uncompressed members                      | 57,505,893 bytes                        |
| Installed NumPy RECORD-listed files             | 57,505,983 bytes (54.84 MiB); 904 files |
| Fresh-process scalar module import, median wall | 12.93 ms                                |
| Fresh-process NumPy import, median wall         | 29.64 ms                                |
| Offline wheel installation, median wall         | 689.67 ms                               |
| Offline installation, median child CPU          | 687.59 ms                               |

Wheel SHA-256: `fffe29a1ef00883599d1dc2c51aa2e5d80afe49523c261a74933df395c15c520`.

Imports use seven fresh interpreters after common benchmark standard-library
startup; process-launch time is excluded. Module caches are fresh, filesystem
caches are not flushed. Scalar and NumPy import times are independent,
conditional import observations, not an application startup forecast.
Import RSS before/after values are retained in JSON.

Installation uses seven newly created venvs and the exact cached local wheel,
with pip `--python ... install --no-index --no-deps --no-compile`. Venv creation,
network download and bytecode compilation are excluded. Child CPU is the
change in `RUSAGE_CHILDREN` user plus system time around the installation
command. File size counts are logical bytes, not physical disk allocation;
installed RECORD does not necessarily include later generated caches.
No measured network download time is claimed.

## Numerical evidence and limits

All 72 cases passed before timing. Maximum observed grade discrepancy was
2.2204460492503131e-16,
against absolute tolerance $10^{-12}$ with zero relative tolerance. Every
batch classification decision matched exactly. The prototype's separate
boundary/alias/noncontiguous/extreme-coordinate tests remain required;
passing these finite grids alone does not prove global mathematical equality.

The deterministic benchmark tests cover workload parity, deliberate tie
selection, invalid measurement settings, rejection of wrong numerical
results, platform guards, Linux RSS source and metric schema. CI executes
these checks with the optional prototype on Python 3.13/3.14; timing has no
threshold and CI does not assert speedup.

The experiment and harness remain outside the built package. NumPy stays an
isolated requirement in `experiments/requirements-vectorized.txt`; no runtime
requirement, extra, public import or backend selection was added.
[ADR-0015](../adr/0015-optional-vectorized-execution-strategy.md) resolves
Tasks #109 and #14's strategy decision without promoting this prototype. The
measured source identity above remains authoritative for these observations;
future promotion must validate and measure its current scalar and array APIs.
