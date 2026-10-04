<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0015: Optional Vectorized Execution Strategy

- Status: Accepted on merge
- Date: 2026-10-04
- Related planning tasks: [#109](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/109), [#14](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/14)
- Related Feature: [#34](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/34)
- Milestone: M5 performance experiments
- Evidence: [scalar/array comparison](../performance/vectorized-membership-comparison.md)

## Context and numbering

The planning issue #14 originally called the optional NumPy decision
"ADR-0007". The accepted repository
[ADR-0007](0007-parallel-test-execution.md) already defines process-parallel
test execution. This decision uses the next available number, ADR-0015, and
does not supersede or amend that test-runner contract.

Scalar evaluation is the dependency-free default and serves callers evaluating
individual coordinates, built-in families, and arbitrary membership callables.
The repository-only NumPy prototype tests whether batches of built-in family
evaluations justify a separate optional execution path. A faster array kernel
alone would not justify a mandatory dependency, implicit conversion, or changes
to existing scalar contracts.

## Decision

Retain the zero-dependency scalar implementation as the installed-package
default. Adopt optional, explicitly selected NumPy vectorization as the
strategy for large batches of supported built-in membership families, subject
to the implementation acceptance gates below. Reject mandatory NumPy and
automatic replacement of scalar evaluation.

The benchmark evidence is sufficient to resolve the strategy decision in
Tasks #109 and #14. Public backend implementation is separate future work.
This ADR adds no runtime dependency, distribution extra, public array API,
backend selector, or automatic batch-size threshold. The current
`experiments.vectorized_membership` interface remains a repository-only
prototype outside the built package.

A future implementation must keep NumPy imports lazy and confined to the
explicit optional path. Installing and importing the scalar package must work
without NumPy. Array inputs, result ownership, dtype, shape, validation and
failure behavior require a documented additive API; existing scalar signatures,
return values and parameter conventions remain protected.

Vectorization eligibility must be explicit for each built-in family. Arbitrary
custom membership callables remain scalar unless a separate supported array
contract is defined and verified. The benchmark's default-scale selector is
experimental evidence, not a public vectorized scale or inference engine.

## Evidence used

The [report](../performance/vectorized-membership-comparison.md) and
[raw JSON](../performance/evidence/vectorized-membership-python314-linux.json)
record a Linux/CPython 3.14.7 run with NumPy 2.3.5. The measured clean source
commit is
[`147694190ae7d07b659d4453faf3973efe1bb4fd`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/147694190ae7d07b659d4453faf3973efe1bb4fd).
The JSON SHA-256 is
`e6d725618bf2712fe073a2a832f03e019a9e936d03b803082216eaa38c5f360e`.
Later facade or module changes do not change that recorded source identity;
promotion must measure the implementation it proposes to ship.

- All 72 comparisons passed the absolute $10^{-12}$, zero-relative-tolerance
  parity gate. The maximum observed grade discrepancy was
  `2.2204460492503131e-16`; default-scale classification indices matched exactly.
- Each timing case has seven paired samples with alternating backend order.
  NumPy was slower at both 1 and 16 coordinates across the measured workloads.
- With original-list conversion included, built-in membership evaluation was
  4.03–8.14 times faster at 1,024 coordinates and 7.14–11.88 times faster at
  100,000. Default-scale classification was 10.03 times faster at 100,000.
- At 100,000 coordinates, prepared-array membership evaluation was
  21.71–46.83 times faster. Those numbers exclude original-list conversion;
  parameter validation, input copies and result allocation remain included.
- Original-list workloads at 100,000 coordinates had total process peak RSS
  of approximately 26–30 MiB for scalar execution and 42–50 MiB for NumPy.
  The operation's separately traced temporary peak was also higher with NumPy.
  Each memory case has one sample; RSS is not incremental allocation cost.
- NumPy's fresh-process import median was 29.64 ms, versus 12.93 ms for the
  scalar module. The measured wheel was 15.83 MiB and installed RECORD-listed
  files occupied 54.84 MiB of logical bytes. Imports exclude process startup;
  these observations do not predict application startup or download latency.

These are representative synthetic grids on a shared host, not an FMA consumer
trace or a cross-platform guarantee. No exact crossover point was measured.
The sampled gain at 1,024 coordinates is evidence for this environment, not a
portable dispatch threshold. Prepared-array gains cannot be used to promise
the same speedup for original-list inputs. Finite-grid parity does not prove
equivalence for every finite input or pathological parameter combination.

## Public implementation acceptance gates

A separate implementation task and PR must satisfy all of these gates before
promoting an optional backend:

1. Define the additive public batch API, eligible built-in families, supported
   Python/NumPy versions, explicit selection mechanism, and optional packaging
   boundary. Verify clean wheel installation, scalar imports and scalar use
   without NumPy, plus an actionable failure when an explicitly requested
   backend is unavailable.
2. Preserve the canonical scalar formulas and validation contract rather than
   introducing an independent source of mathematical truth. Verify parity
   against the current scalar implementation with absolute $10^{-12}$ and
   zero relative tolerance; check branch endpoints, adjacent floats, degenerate
   parameters, saturation, invalid inputs and explicit failure behavior.
3. Specify and test conversion, dtype, shape, empty/noncontiguous arrays,
   immutable parameter snapshots, fresh results, input nonmutation and ambient
   NumPy error-state restoration. Document any intentional exception
   differences instead of claiming universal scalar/array equivalence.
4. Reproduce time, peak process memory, temporary allocation, import and
   installation cost for the exact candidate and scalar baseline. Retain raw
   samples, at least seven paired timing repeats and separate prepared-array
   and conversion-inclusive results under the
   [benchmark protocol](../performance/benchmark-reproducibility-protocol.md).
   Include the intended consumer's representative batch shapes and data
   representation before making application or FMA throughput claims.
5. Establish that the intended workloads benefit enough to justify measured
   resource costs. Keep timing out of deterministic CI thresholds; enforce
   parity, compatibility and dependency isolation in CI. Document workload
   guidance without inventing a universal crossover or implicit fallback.

Scale or inference-engine vectorization needs its own declared scope and
evidence, including modern explicit tie/no-match policies and custom callable
handling. The historical later-level-wins benchmark selector is not sufficient
to establish those contracts.

## Alternatives and consequences

- **Mandatory NumPy or array-first scalar execution:** rejected because small
  batches regress and import, installation and memory costs are material.
- **Automatic selection at 1,024 coordinates:** rejected because the sparse
  sampled sizes do not locate a crossover and conversion costs vary by caller.
- **Promote the prototype immediately:** rejected because it is a research
  interface measured against a recorded historical source, not the current
  shipped API with the public acceptance gates satisfied.
- **Keep all execution scalar indefinitely:** rejected because large built-in
  batches show substantial conversion-inclusive gains and justify an optional
  path for callers who accept its measured costs.

The default remains portable and inexpensive for scalar use. Large-batch
callers gain a justified future option, while maintainers accept additional
parity, packaging and version-matrix responsibilities when implementing it.

## Acceptance and supersession

This ADR is **Accepted on merge** and resolves the vectorization strategy;
implementation remains future work under the gates above. Making NumPy
mandatory, changing the scalar default, introducing automatic dispatch, or
extending eligibility to arbitrary custom callables requires an amendment or
superseding decision with corresponding evidence.
