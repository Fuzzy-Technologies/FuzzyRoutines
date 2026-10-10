<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Legacy Test Matrix Baseline

This baseline executes the **unmodified historical test module** `tests/test_routines.py` against explicitly recorded Python candidates.

It intentionally excludes tests added by the modernization effort so that later regression growth does not rewrite the legacy baseline.
The workflow materializes the immutable pre-baseline source commit
`8e739c1665aa9894ede556e3f3f4cb20174d14ff` before entering the runtime
matrix; it does not execute the evolving current package under legacy Python.

## Candidate runtimes

| Python | Container          |
|--------|--------------------|
| 3.6    | `python:3.6-slim`  |
| 3.8    | `python:3.8-slim`  |
| 3.11   | `python:3.11-slim` |
| 3.13   | `python:3.13-slim` |

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
The working directory is an archive of the pinned historical source commit
rather than the pull-request checkout.

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

| Python | Result                                         | Evidence                                                                            |
|--------|------------------------------------------------|-------------------------------------------------------------------------------------|
| 3.6    | PASS — 11 passed                               | [run](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/34830382303) |
| 3.8    | PASS — 11 passed                               | [run](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/34830382303) |
| 3.11   | PASS — 11 passed, 1 pytest deprecation warning | [run](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/34830382303) |
| 3.13   | PASS — 11 passed, 1 pytest deprecation warning | [run](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/34830382303) |

## Resolved runtime details

| Candidate | Resolved Python | pip    | pytest | Container digest                                                          |
|-----------|-----------------|--------|--------|---------------------------------------------------------------------------|
| 3.6       | 3.6.15          | 21.2.4 | 7.0.1  | `sha256:2cfebc27956e6a55f78606864d91fe527696f9e32a724e6f9702b5f9602d0474` |
| 3.8       | 3.8.20          | 23.0.1 | 8.3.5  | `sha256:1d52838af602b4b5a831beb13a0e4d073280665ea7be7f69ce2382f29c5a613f` |
| 3.11      | 3.11.16         | 24.0   | 9.1.1  | `sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534` |
| 3.13      | 3.13.15         | 26.2.1 | 9.1.1  | `sha256:9d2e5553305c7c7b0097999bb17187c69b921ccd6bc9d40e4bb5ebe652c00285` |

The Python 3.11 and 3.13 runs expose a pytest deprecation warning for the class-scoped fixture implemented as an instance method in the historical tests. This does not fail the legacy suite, but it is recorded as test-infrastructure debt rather than hidden.
