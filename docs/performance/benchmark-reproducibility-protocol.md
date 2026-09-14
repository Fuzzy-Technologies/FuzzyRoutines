# Benchmark Reproducibility Protocol

- Status: Protocol for Task #103
- Applies to: membership functions, fuzzy operators, `FuzzySet`, centroids,
  and linguistic scales

## Purpose

A performance claim is valid only when another developer can reproduce the
workload, environment, command, and summary statistic. Benchmarks do not
justify a mathematical or compatibility change without independent parity
evidence.

## Required benchmark record

Every benchmark result records:

- Git commit, dirty-state status, and package version;
- CPython implementation and exact version;
- operating system, CPU model, logical CPU count, and memory;
- dependency versions and installation command;
- the exact benchmark command and any environment variables;
- deterministic input generator, seed, and input size;
- warm-up count, measured repeat count, and timer;
- raw sample values plus median, minimum, and interquartile range;
- numerical-parity reference, tolerance, and pass/fail result.

## Measurement rules

- Use `time.perf_counter_ns()` or an equivalent monotonic high-resolution
  timer.
- Keep benchmark data local and deterministic. A benchmark must not call an
  external online service.
- Separate process-startup, import, construction, evaluation, and
  defuzzification workloads; do not collapse them into one opaque number.
- Run a warm-up before measurement. Record at least seven measured samples and
  report the median as the primary timing result.
- Pin the workload and seed. If CPU affinity, performance governor, or process
  priority is changed, record it; do not claim cross-machine comparability.
- Compare proposed changes against a named baseline commit in the same
  environment whenever possible.
- A faster result is rejected if mathematical parity or public-contract
  compatibility fails.

## Reporting template

```text
Workload:
Baseline commit:
Candidate commit:
Environment:
Command:
Input and seed:
Warm-up / measured samples:
Timer:
Raw samples:
Median / minimum / IQR:
Numerical parity reference and tolerance:
Result:
```

## Scope boundary

This protocol preserves the dependency-free scalar core. Optional NumPy or
other vectorized execution remains an ADR-0007 decision and requires memory,
installation-cost, and numerical-parity evidence in addition to timing data.
