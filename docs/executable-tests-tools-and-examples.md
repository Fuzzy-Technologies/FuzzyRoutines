<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Executable Tests, Tools, Benchmarks, and Examples

This page defines the user-visible execution boundary outside the importable
library. The Python package remains side-effect free on import. Examples,
benchmarks, maintenance commands, and test orchestration run only through an
explicit command.

## Test documentation

Every test module identifies the contract or evidence family it covers. Every
test function, helper, class and method has a concise English docstring stating
the invariant, regression or fixture boundary it verifies. Nested helpers and
framework callbacks follow the same rule. Meaningless placeholders such as
“test that the function works” do not satisfy editorial review.

The existing static documentation gate checks declarations without importing
or collecting tests:

```console
python -m tools.documentation_gates test-docstrings
```

This check also runs in the documentation CI `all` gate. Embedded Python
fixtures remain test data and do not require source-declaration docstrings.

Comments inside tests explain non-obvious matters such as:

- why a mathematical boundary value is representative;
- why a tolerance is valid for that specific numerical method;
- which historical regression a surprising expected value preserves;
- why a fixture must own an isolated process, port, path, or mutable state;
- what invariant a parameter grid spans.

The default test command is:

```console
python -m tools.test_runner --jobs auto --timeout 60
```

The runner creates its JUnit files and temporary directories below an
operating-system temporary directory and removes the complete session after
the run. Optional `--evidence-directory PATH` retains phase JUnit XML in a new
explicit directory and rejects an existing directory. Collection-level module
skips, observed before marker filtering in both phases, count once in the
aggregate summary. It returns `0` only when all parallel and serial phases pass, `1` for
test failures or process errors, and `2` for invalid runner configuration.

The mathematical coverage workflow measures every library module with
`coverage.py` branch tracing on CPython 3.13 and 3.14. It then compares actual
sequential and process-based JUnit test identities and outcomes using
`tools/release_test_audit.py`. Equal totals alone cannot establish parity.
Duplicate executed tests, changed outcomes, missing module reports and line-only
coverage fail. JSON evidence includes missing lines and branches for review;
percentages do not establish mathematical correctness. These full runs belong
to CI; routine development continues to use affected tests only.

## Worked user scenarios and figures

The canonical [English quick start](site/content/en/quick-start.md) and
[scenario collection](site/content/en/guides/index.md) are backed by
`examples/guide.py`. Its default executes eight scenarios, checks independent
expected results, and emits deterministic JSON to stdout. It creates no files
and imports no optional plotting or numerical dependency. `--scenario NAME`
selects one scenario; `--help` returns `0`, malformed arguments return `2`, and
a failed calculation assertion returns nonzero.

```console
python -I examples/guide.py
python -I examples/guide.py --scenario alpha-cuts
```

The installed verifier extracts every Python fence in `docs/site/content/en`,
including API-page examples, and runs each independently with `python -I`.
Package CI repeats this against both wheel and sdist on supported Python
versions. Documentation CI also executes the examples against its installed
wheel. An example must not depend on variables or imports from another fence.

`tools/generate_guide_figures.py` executes the same scenario assertions and
renders ten SVGs from scalar API evaluations. Install the pinned
`docs/requirements-plots.txt` documentation dependencies, then supply
`--output-directory`. `--check` verifies bytes without writes; the optional
`--preview-directory` owns PNG review artifacts. The tool returns `0` on a
complete rendering or comparison and nonzero on drift or failure. See
[figure provenance](site/content/en/guides/figures.md) for the exact sample
grids and numerical limits. CI verifies committed figures with the pinned
Python 3.14 toolchain; ordinary library installation remains dependency-free.

`tools/guide_example_coverage.py` executes the same published Python fences
and records actual public calls, property reads and constructors. Imports alone
do not count; typing contracts require annotations, and built-in exception
constructors require retained instances. Root aliases must resolve to their
canonical module objects. Its default prints a compact JSON summary to stdout;
`--output PATH` explicitly writes full JSON evidence, `--write-index` updates
the reader index, and `--check-index` rejects drift without writes. Exit `0`
means no coverage gaps; execution failures, gaps or drift return nonzero.
`--require-installed` rejects package origins outside the active environment.
There are no default artifacts to clean up. Installed wheel/sdist CI runs this
gate in isolated mode. For a source checkout, use:

```console
PYTHONPATH=. python tools/guide_example_coverage.py --check-index
```

## Migration examples

The two focused migration examples emit one JSON object to stdout and create no
files. They use deterministic scalar inputs and perform no network access.

| Command                                                         | Scenario                                        | Output keys                                              |
| --------------------------------------------------------------- | ----------------------------------------------- | -------------------------------------------------------- |
| `python examples/migration/historical_compatibility.py`         | Protected historical API                        | membership, operator, fuzzy set, scale, defuzzification  |
| `python examples/migration/modern_supported.py`                 | Supported modern API plus one legacy factory    | membership, operator, overlap, integration domain        |
| `python -m fuzzyroutines.Examples`                              | Broad historical compatibility demonstration    | Human-readable stdout                                    |

The package workflow executes all three from a temporary working directory
after installing both the wheel and source distribution. The verifier removes
`PYTHONPATH`, disables the user site, and rejects an import that does not come
from the active virtual environment. It also extracts every Python fence from
[`docs/COMPATIBILITY.md`](COMPATIBILITY.md) and executes each snippet with
Python isolated mode from the same temporary directory. This prevents the
checkout, user site, or environment overrides from satisfying an undocumented
import.

## Benchmark commands

Benchmarks print their complete JSON report to stdout. `--output PATH` writes
the same JSON to a caller-selected artifact path; parent directories are never
created implicitly. This makes ownership and cleanup explicit and prevents
silent `benchmark-*.json` files in the repository root.

| Command                                                  | Required evidence and workload                                        | Main options                                          |
| -------------------------------------------------------- | --------------------------------------------------------------------- | ----------------------------------------------------- |
| `python -m tools.benchmark_fuzzyset_centroid`            | Construction, centroid recalculation, timing, allocation, host        | `--samples`, `--output`                               |
| `python -m tools.benchmark_legacy_baseline`              | Historical membership, set, scale construction and lookup baseline    | `--repeats`, `--output`                               |
| `python -m tools.benchmark_membership_operators`         | Every membership/operator family, parity, raw timing, environment     | `--iterations`, `--repeats`, `--warmups`, `--output`  |
| `python -m tools.benchmark_scale_lookup`                 | Default/universal construction and repeated lookup                    | `--samples`, `--output`                               |

All benchmark commands return `0` after a complete report. Argument parsing
returns `2` for malformed CLI input. Invalid reproducibility limits, failed
parity, or output I/O errors return nonzero and do not constitute benchmark
evidence. Use `--help` for current defaults and lower bounds.

The dependency-free scalar benchmark protocol is defined in
[`benchmark-reproducibility-protocol.md`](performance/benchmark-reproducibility-protocol.md).
Timing observations are not performance claims until a named baseline and
candidate are measured in the same environment with numerical parity.

Example with an explicit disposable artifact directory:

```console
artifactDirectory="$(mktemp -d)"
python -m tools.benchmark_membership_operators \
  --iterations 10000 \
  --repeats 7 \
  --warmups 1 \
  --output "$artifactDirectory/membership-operators.json" \
  > "$artifactDirectory/membership-operators.stdout.json"
python -m json.tool "$artifactDirectory/membership-operators.json" > /dev/null
```

The caller owns `artifactDirectory` and may remove it after retaining any
review evidence required by the development protocol.

## Maintenance and diagnostic commands

| Command                                                  | Inputs                                       | Outputs and side effects                                        | Exit contract                           |
| -------------------------------------------------------- | -------------------------------------------- | --------------------------------------------------------------- | --------------------------------------- |
| `python -m tools.check_license_headers`                  | Tracked repository files                     | PASS on stdout or violations on stderr; no writes               | `0` valid, `1` drift                    |
| `python -m tools.report_universal_scale_coverage`        | Grid size, weak threshold, optional output   | JSON stdout and optional explicit JSON artifact                 | `0` complete, nonzero invalid/failure   |
| `python -m tools.evaluate_api_documentation`             | Tool names, Python version, output roots     | Explicit disposable environments, sites, logs, evidence JSON    | `0` complete, nonzero build/failure     |
| `python -m tools.pr_merge_links`                         | `PR_BODY` environment variable               | Closing issue numbers on stdout; no writes                      | `0` after deterministic parsing         |
| `python tools/verify_installed_executables.py ...`       | New explicit artifact directory              | Captured streams, reports, and a JSON summary in that directory | `0` complete, nonzero contract failure  |

`evaluate_api_documentation` refuses to replace an existing environment or
output directory unless its documented reuse mode is selected. Its default
`_build/` tree is ignored and disposable. The clean-install verifier likewise
requires a new artifact directory so stale output cannot be mistaken for
current evidence.

## Clean-install evidence

The package workflow builds a wheel and source distribution independently. For
each artifact and supported Python version it then:

1. creates a clean virtual environment;
2. installs the artifact without resolving runtime dependencies;
3. proves `fuzzyroutines` resolves under that environment prefix;
4. executes every compatibility-guide and canonical English Python snippet in isolated mode, recording public-symbol usage and checking the example index;
5. runs all eight worked scenarios and historical, modern, and bundled examples from a temporary directory;
6. runs every benchmark entry point with bounded realistic inputs;
7. parses redirected JSON stdout and compares each benchmark `--output` file;
8. leaves generated evidence only under the explicit temporary artifact tree.

This shell-visible check complements unit tests of report builders. A unit test
that calls `BuildReport()` directly does not prove argument parsing, installed
imports, exit status, stdout serialization, or artifact ownership.
