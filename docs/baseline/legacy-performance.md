# Legacy Performance Baseline

This record is the informational timing baseline for the historical
FuzzyRoutines implementation. It implements Task #42 without changing source
mathematics or applying an optimization.

## Baseline identity

| Item                             | Value                                                    |
|----------------------------------|----------------------------------------------------------|
| Source branch                    | `develop`                                                |
| Source commit                    | `6282544f269c15490dd2c5874463367f4f708432`               |
| Historical mathematical baseline | `ceb9403d44c19ba73fd351e1b05091d337280864` / tag `1.0.3` |
| Measurement tool                 | `tools/benchmark_legacy_baseline.py`                     |
| Timing clock                     | `time.perf_counter()`                                    |
| Samples per benchmark            | 7                                                        |
| Statistic                        | median microseconds per operation                        |

The source diff between the historical baseline and this `develop` revision
contains baseline/documentation/CI work only; this Task does not claim a
cross-machine performance comparison.

## Reproduction

Run from a checkout of the recorded revision:

```bash
python --version
python tools/benchmark_legacy_baseline.py --repeats 7
python -m pytest -q
```

The tool prints machine-readable JSON. It performs one warm-up invocation per
benchmark, then records seven per-operation wall-clock samples. The median is
the reported baseline; min/max show local run variability.

## Measurement environment

| Item       | Value                                                   |
|------------|---------------------------------------------------------|
| Python     | CPython 3.12.14                                         |
| Platform   | Linux 6.18.44, x86_64, glibc 2.39                       |
| Processor  | x86_64                                                  |
| Test suite | PASS — 23 passed, 1 recorded pytest deprecation warning |

## Results

| Operation                                  | Iterations per sample |       Median |                  Range |
|--------------------------------------------|----------------------:|-------------:|-----------------------:|
| Bell membership evaluation                 |               200,000 |     0.416 µs |         0.412–0.424 µs |
| FuzzySet construction plus legacy centroid |                   100 |   354.704 µs |     352.184–383.716 µs |
| UniversalFuzzyScale construction           |                    25 | 2,493.754 µs | 2,444.431–2,575.673 µs |
| UniversalFuzzyScale lookup                 |               100,000 |     1.854 µs |         1.832–2.308 µs |

The lookup benchmark constructs the scale once before measurement and measures
only `scale.Fuzzy(0.5)`. Construction benchmarks include their legacy
centroid work.

## Interpretation boundary

These results are reproducible observations for this environment, not
portability claims or optimization targets. Future performance work must:

- use the same tool and report its revision/environment;
- establish numerical and observable-behavior parity;
- record before/after medians and ranges;
- avoid attributing a cross-machine difference solely to code changes.

The benchmark protocol and any optimization decision remain separate planned
work.
