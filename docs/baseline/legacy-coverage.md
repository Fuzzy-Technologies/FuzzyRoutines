# Legacy Coverage Baseline

This measurement captures statement and branch coverage produced by the **unmodified historical test module** `tests/test_routines.py`.

No tests are added by this Task.

## Measurement command

```bash
python -m pip install --disable-pip-version-check pytest coverage
python -m coverage run --branch -m pytest -q tests/test_routines.py
python -m coverage report --show-missing
python -m coverage json -o coverage.json
```

## Environment

```text
GitHub Actions
ubuntu-latest
Python 3.11
coverage: resolved from PyPI at workflow runtime
pytest: resolved from PyPI at workflow runtime
```

The workflow log is the human-readable evidence. The uploaded `coverage.json` artifact is the machine-readable evidence.

## Baseline result

The values below are filled from the first implementation-PR run.

| Metric                              | Result |
|-------------------------------------|-------:|
| Source statements                   |    380 |
| Missing source statements           |    226 |
| Source statement coverage           | 40.53% |
| Source branches                     |    134 |
| Missing source branches             |     75 |
| Partial source branches             |      3 |
| Source branch coverage              | 44.03% |
| Source combined coverage            | 41.44% |
| Whole measurement statements        |    454 |
| Whole measurement branch coverage   | 56.40% |
| Whole measurement combined coverage | 51.92% |

## Known measurement boundary

Only `tests/test_routines.py` is executed.

Modernization tests are deliberately excluded so this file remains a stable representation of the historical test suite's reach.

## Evidence

Workflow run:

https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/34830651049

Machine-readable artifact:

https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/34830651049/artifacts/10341594867

Artifact digest:

```text
sha256:c5a50e2d33c9c628d8d35240bba94d857a68c18aa5c217f68cd611f110dceb5a
```

Resolved measurement tools:

```text
Python 3.11.16
pytest 9.1.1
coverage 7.16.1
```

The historical suite itself passed: **11 passed, 1 pytest deprecation warning**.

## Uncovered mathematical areas

The report shows that the historical suite is concentrated on helper/operator behavior and leaves most of the domain model without direct coverage.

Major uncovered areas:

- **Membership functions / `MFunction`** — factory setup and essentially all membership-function implementations (`Hyperbolic`, `Bell`, `Parabolic`, `Triangle`, `Trapezium`, `Exponential`, `Sigmoidal`, `Desirability`) are largely uncovered.
- **`FuzzySet`** — construction/validation, mutation behavior, centroid implementation and backward-compatible `Defuz()` paths are largely uncovered.
- **`FuzzyScale`** — default construction, level validation, lookup maps, fuzzification and name lookup are largely uncovered.
- **`UniversalFuzzyScale`** — preset construction and exposed level-name properties are uncovered.
- **Composition edge paths** — `TNormCompose` and `SCoNormCompose` have uncovered branch transitions even though the basic operator families have legacy test coverage.

This baseline supports the planned expansion of reference/property tests before mathematical refactoring.
