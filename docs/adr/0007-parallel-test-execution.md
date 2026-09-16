# ADR-0007: Deterministic Process-Parallel Test Execution

- Status: Accepted
- Date: 2026-09-16
- Related planning task: #212
- Related Feature: #211

## Context

The suite is growing from a small historical regression set into a mathematical,
compatibility, packaging, performance, and documentation gate. A single-process
default wastes independent CPU capacity, while unconstrained parallelism can
hide order dependencies, reuse mutable files, collide on ports or databases,
and turn timeouts into nondeterministic hangs.

The test runner must use the same Python SDK selected by the developer, IDE, or
CI job. It must not create a second dependency resolver or add test tooling to
the runtime package.

## Decision

### Canonical entry point

The canonical repository test command is:

```text
python -m tools.test_runner
```

The runner invokes pytest through `sys.executable`. Therefore the caller's
active Python SDK and installed test dependencies remain authoritative.

### Worker policy

Parallel-safe tests run in pytest-xdist worker processes with
`--dist=loadscope`. Automatic worker count is:

```text
min(os.cpu_count() or 1, configured_max_workers)
```

The repository default maximum is 12. An explicit `--jobs N` must be a positive
integer no greater than the configured maximum. `--serial` runs the complete
selection with `-n 0` for debugging and explicitly incompatible environments;
it is not the normal execution path.

### Serial-resource policy

A test that cannot own its mutable resources is marked `serial`. Normal runs
have two phases:

1. `not serial` through isolated xdist processes;
2. `serial` through one separate pytest subprocess.

When `--fail-fast` observes a failure or timeout, later phases do not start.
No failed test is automatically retried. A manual rerun is diagnostic evidence,
not a mechanism for manufacturing a passing gate.

### Isolation policy

Every invocation owns a new session root. Pytest `--basetemp` and xdist create
worker-specific trees beneath it. An autouse fixture gives each test a unique
temporary directory, mutable-state root, and database path. Tests needing a
network endpoint reserve an ephemeral loopback port through the shared fixture
instead of probing a hard-coded port.

The canonical runner disables pytest's repository cache and Python bytecode
writes, so parallel workers do not use `.pytest_cache` or shared `__pycache__`
files as mutable coordination points. Strict marker validation prevents a typo
from silently moving a shared-resource test into the parallel phase.

Module and process globals remain the responsibility of the test that mutates
them: restore them through fixtures or mark the test serial. Test correctness
must not depend on collection or completion order.

### Timeout and result policy

pytest-timeout enforces the configured per-test deadline. The CI job retains an
outer timeout for runner or infrastructure failures outside an individual test.

Each phase writes JUnit XML. The runner parses test cases and emits exactly one
sorted `TEST_SUMMARY` JSON object with:

- `total`;
- `passed`;
- `failed`;
- `skipped` (including expected xfail outcomes reported as skipped by JUnit);
- `timeout`;
- `duration`;
- `process_errors` for collection errors and worker/process failures that have
  no ordinary failed test case.

Any phase return code other than success or an empty marker selection makes the
runner return non-zero.

## Consequences

- `pytest`, `pytest-xdist`, and `pytest-timeout` are test-only dependencies.
- Direct `python -m pytest` remains available for focused diagnostics, but it is
  not the canonical full-suite gate.
- Test authors must request the isolation fixtures rather than inventing shared
  root directories, database files, or fixed ports.
- Process startup overhead is accepted in exchange for isolation and scalable
  execution; the 12-worker cap prevents workstation oversubscription.
- The acceptance benchmark for the 356-result suite measured a median of
  `4.152 s` in serial mode and `4.571 s` with nine workers. Parallel execution
  therefore increased current wall time by `10.1%`; the decision is justified
  by isolation and future scalability, not by a present-day speedup claim.

## Acceptance and supersession

This ADR was accepted when implementation PR #216 was reviewed and merged on
2026-09-16. A change to the default concurrency model, retry policy, isolation
boundary, or result schema requires an amendment or superseding ADR.
