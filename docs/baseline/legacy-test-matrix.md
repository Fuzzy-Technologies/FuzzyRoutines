# Legacy Test Matrix Baseline

This baseline executes the **unmodified historical test module** `tests/test_routines.py` against explicitly recorded Python candidates.

It intentionally excludes tests added by the modernization effort so that later regression growth does not rewrite the legacy baseline.

## Candidate runtimes

| Python | Container |
| --- | --- |
| 3.6 | `python:3.6-slim` |
| 3.8 | `python:3.8-slim` |
| 3.11 | `python:3.11-slim` |
| 3.13 | `python:3.13-slim` |

Python 3.6 is included because the historical package metadata declared Python 3.6.

Python 3.8, 3.11 and 3.13 provide progressively newer compatibility probes without changing the legacy tests.

## Exact command

Each matrix entry runs:

```bash
python --version
python -m pip --version
python -m pip install --disable-pip-version-check --no-cache-dir pytest
python -m pytest -q tests/test_routines.py
```

inside the corresponding official Python container image.

## Environment

Shared GitHub runner:

```text
ubuntu-latest
```

The Python runtime itself is supplied by the recorded official container tag.

## Result policy

- every candidate runs independently;
- matrix fail-fast is disabled;
- failures remain visible and are not converted into PASS;
- a runtime failure caused by environment/tooling is recorded separately from a test assertion failure;
- no source or mathematical behavior changes are allowed in this baseline Task.

## Baseline results

Results are filled from the first successful execution of this workflow on the implementation PR.

| Python | Result | Evidence |
| --- | --- | --- |
| 3.6 | pending | pending |
| 3.8 | pending | pending |
| 3.11 | pending | pending |
| 3.13 | pending | pending |
