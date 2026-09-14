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

| Metric | Result |
| --- | ---: |
| Statements | pending |
| Missing statements | pending |
| Statement coverage | pending |
| Branches | pending |
| Partial branches | pending |
| Branch coverage / combined report | pending |

## Known measurement boundary

Only `tests/test_routines.py` is executed.

Modernization tests are deliberately excluded so this file remains a stable representation of the historical test suite's reach.

## Uncovered mathematical areas

To be populated from the first coverage report. Areas are classified by mathematical/domain responsibility rather than by line count alone.
