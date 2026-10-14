<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0018: Explicit public NumPy batches

- Status: Accepted on merge
- Date: 2026-10-14
- Tasks: [#333](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/333), [#334](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/334), [#335](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/335)
- Extends: [ADR-0015](0015-optional-vectorized-execution-strategy.md)

## Decision

Add `fuzzyroutines.batches.EvaluateMembershipBatch`, `FuzzifyBatch` and
`ScaleBatchResult`. A call to these separately imported operations explicitly
selects optional NumPy execution; `backend="numpy"` documents that selection.
Reject every other backend value. Scalar APIs never dispatch to these functions.
The extra `fuzzyroutines[numpy]` installs `numpy>=2.3.5,<3`; the baseline matrix is
CPython 3.13/3.14 with NumPy 2.3.5. CI must also exercise the current compatible
NumPy release before expanding a supported-version claim. Importing the package
or the batch module must work without NumPy. A missing dependency is reported
only when array evaluation is requested, with the installation command.

## Mathematical source and eligibility

All eight modern built-in families are eligible. Parameter validation and
immutable snapshots use `membership._AnalyticalSource`; array kernels explicitly
lower its canonical branches to masks. They are not an additional public formula
registry. Every branch is checked against the scalar evaluator, including
adjacent floats, permitted degeneracies, and the corrected extreme Gaussian,
logistic and linear-ramp cases. Parameters must be `int`/`float` values exactly
representable in binary64. Rational/custom real parameters remain scalar-only.
Accepted integer parameters retain their original type during intermediate
endpoint arithmetic; exact representability alone does not justify replacing
an integer sum by a potentially overflowing floating-point sum.

Unmodified inherited built-in evaluators are eligible; overridden evaluators,
generic functions, legacy mutable objects, composed and normalized membership
callables are rejected. Users can assemble any modern scale from eligible terms,
including the historical five-level preset. Continuous and discrete universes
are supported, with exactly representable binary64 bounds/points. Universe
subclasses and overridden fuzzy-set/scale evaluators are rejected: batch
execution must not bypass custom scalar semantics. Every input
coordinate must belong to every term universe; no clipping is performed.

## Array contract

| Concern                 | Contract                                                                                       |
| ----------------------- | ---------------------------------------------------------------------------------------------- |
| Input                   | Rectangular real numeric sequence or ndarray, rank at least one                                |
| Conversion              | Copy into C-order float64; parity refers to converted coordinates                              |
| Rejection               | Boolean coordinates, complex/string/object dtype, scalar/0-D input, nonfinite converted values |
| Shapes                  | Any positive rank; empty dimensions and noncontiguous input are valid                          |
| Ownership               | Inputs never mutated/retained; membership output is fresh and writable                         |
| Scale grades            | Shape `input_shape + (term_count,)`, declared term order                                       |
| Scale confidence        | Shape `input_shape`, maximum grade                                                             |
| Tie and selection masks | Boolean arrays with the same shape as scale grades                                             |
| Scale result ownership  | All four arrays independently copied and read-only; explicit `copy()` produces writable arrays |
| Normalization           | No coordinate or grade normalization; grades are not probabilities                             |

Input integer arrays may lose precision when converted to float64. A caller who
needs exact integer/rational arithmetic must use the scalar API. Extended-float
arrays are accepted only if every converted coordinate remains finite. Python
sequences containing booleans are rejected before NumPy can coerce them. Already
converted numeric arrays carry their existing dtype/value meaning.

## Selection and numerical failure

`FuzzifyBatch` uses `FuzzificationPolicy`. Exact ties compare grades directly;
positive float tolerances retain the scalar `math.isclose` boundary allowance
(`rel_tol=1e-12`, `abs_tol=0`). `first`, `last`, and `all` operate in declared term
order. A maximum grade less than or equal to `minimumConfidence` is a no-match:
both masks are entirely false. Policy thresholds must be int/float values.

Parity acceptance is absolute `1e-12`, relative zero, at the documented grids and
edge cases; selected names and tie masks must match the scalar reference there.
This is finite evidence, not a proof for every possible binary64 parameter set.
No speed threshold belongs in CI. A failed array operation returns no partial
result and never silently falls back to a scalar loop.

Active squared-width underflow raises `ZeroDivisionError`. NumPy arithmetic
overflow/invalid/divide failures are translated to `OverflowError`; a resulting
invalid grade raises `InvalidParameterError`. These are deliberate batch failure
categories, not a promise of identical exception messages or failure ordering
across scalar iteration and array evaluation. Inactive branches are not evaluated.
NumPy error state is restored on success and failure; positive tails may underflow
to zero just as in the scalar core.

## Acceptance and costs

The PR must demonstrate installed-wheel execution with and without the extra,
the supported runtime matrix, static consumer typing, the historical preset,
invalid inputs, immutable snapshots, ownership, empty/noncontiguous arrays and
ambient error-state restoration. Three-language guides and API pages describe
the same surface. Source benchmarks must not be presented as released-wheel data.

The reproducible comparison retains at least seven paired timing samples,
separate prepared-array/conversion-inclusive cases, process and traced memory,
fresh-process imports and cached-wheel installation costs. Synthetic grids and
matrix shapes are identified as such. Actual FMA/robot throughput claims require
owner-authorized consumer shapes and traces; their absence remains explicit.
The scalar default, no automatic crossover, and no mandatory dependency decisions
in ADR-0015 remain unchanged. Array inference, tensor gradients and arbitrary
callable vectorization are outside this decision.
