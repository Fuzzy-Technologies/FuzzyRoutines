<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0023: Explicit Sugeno rule batches

- Status: Proposed for 2.2
- Date: 2026-11-05
- Task: [#405](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/405)
- Feature: [#364](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/364)
- Builds on: [ADR-0017](0017-scalar-fuzzy-rule-inference.md) and [ADR-0018](0018-public-numpy-batches.md)

## Context

A rule model maps named observations to one output per observation. The
existing NumPy membership and scale operations evaluate coordinates, but
do not bind features to a rule model or distinguish one failed row from
the rest of a batch. Scalar Sugeno is the reference for both arithmetic and
validation. The batch design must keep the cost of retaining rule traces
separate from the cost of evaluating rules.

## Decision

Propose a separate operation, `EvaluateSugenoBatch(model, values, *,
feature_names, backend="numpy", on_error="raise", trace="off",
chunk_size=4096)`. The spelling is illustrative; this ADR does not ship
a callable. Calling this operation opts into NumPy. The sole
accepted backend is `"numpy"`; there is no `"auto"`, scalar dispatch or
fallback through `model.Evaluate`. NumPy loads on request via the existing
`fuzzyroutines[numpy]` extra. If absent, the call raises `ImportError` with
the install command, including for empty input. Ordinary imports and
scalar evaluation remain dependency free.

### Eligibility

Use a standard `SugenoModel` with one continuous output universe and the
existing ordered `TermCondition`, `AllOf`, `AnyOf` and `NotCondition` trees.
Fold children from left to right with the configured t-norm and s-norm.
Support the `logic`, `algebraic`, `boundary` and `drastic` norm families and
`standard`, `parametric` and `parabolic` negation. Use multiplication for
rule weights. Each rule may use `ConstantConsequent` (zero order) or
`AffineConsequent` (first order); mixed orders are valid in one model.
Affine coefficients bind by name, in declared coefficient order; omitted
coefficients contribute zero.

Reuse the eight analytical families eligible under ADR-0018: `Hyperbolic`,
`Bell`, `SShoulder`, `Triangle`, `Trapezoid`, `Gaussian`, `Logistic` and
`HarringtonDesirability`. The same built-in evaluator and parameter
eligibility rules apply, including the distinction between exact integer
parameter arithmetic and coordinate conversion. Input universes may be
standard continuous or discrete. Finite domain endpoints and discrete
points, rule weights, negation parameters and consequent coefficients
must be built-in `int`/`float` exactly representable in binary64. Preserve
open/closed bounds and discrete membership; no clipping or imputation.

Reject the whole call for Mamdani, legacy mutable objects, non-analytical
or user callbacks, overridden evaluators (including rule, set, policy and
universe semantics), rational/custom-real model data and tensor or device
inputs. New table and piecewise membership objects require their own batch
eligibility evidence before they can be supported. The historical Universal
Fuzzy Scale and its coefficients remain unchanged.

### Input and result shapes

Let `N` be the number of observations, `F > 0` the number of model inputs,
`T` the number of declared input terms across all variables, and `R` the
number of model rules.

Input is a rank-two numeric ndarray or rectangular list/tuple of rows.
Each row is an observation, even in a square matrix. There is no
broadcasting, transposing or implicit flattening. `feature_names` is a
tuple of exactly `F` unique, case-sensitive names, one per supplied
column and a permutation of the model input names. Bind columns by name
and evaluate in model declaration order.

| Case             | Shape or dtype                                   |
| ---------------- | ------------------------------------------------ |
| Observations     | `(N, F)`                                         |
| Empty input      | `(0, F)`, or `[]`/`()` with valid feature names  |
| Single row       | `(1, F)`, including `(1, 1)` for one feature     |
| `values`         | float64 `(N,)` in the model's output units       |
| `valid_mask`     | bool `(N,)`, true exactly where `status == 0`    |
| `status`         | uint8 `(N,)`, preserving source row order        |

Reject rank-one inputs, including empty ndarrays, and wrong widths,
including `(0, G)` for `G != F`. Validate shape, model and options even
when `N = 0`. Array dtypes may be signed/unsigned integer or real floating;
allow non-contiguous, negative-stride, read-only and non-native-endian
inputs. Reject Boolean, complex, string, object and structured dtypes,
and ndarray subclasses including masked arrays. For sequences, accept
built-in `int`/`float` and NumPy integer/real-floating scalars. Reject
Boolean cells before mixed numeric coercion, and reject ragged rows,
iterators, mappings and implicit coercion from other cell types.

Convert to private C-order float64 chunks in model feature order.
Precision may change, including for large integers; compare parity
against the converted coordinates. A non-finite converted coordinate is
a bad row. A failed output value is `NaN`; valid values are finite.
Return fresh independent arrays exposed read-only. Callers can request
writable copies using the array copy operation. Do not mutate input data
or retain it in the result. Row indices are zero based.

Use `InvalidParameterTypeError` for unsupported input kinds, dtypes,
cell types or model types, and `InvalidParameterError` for malformed
shape, name bindings or option values. Such validation errors and
dependency errors fail the whole call; they cannot be masked. A missing
feature column is a call error even when every row would be empty. An
array already converted to numeric dtype conveys its current dtype and
values.

### Row failures

In `"raise"` mode, raise on the lowest original row index with a row
failure and return no result. Include that index and, when known, the
feature or rule name in the diagnostic. In `"mask"` mode, return all rows
with the same classifications. The operation uses the following stage
order within a row. Errors at the same stage need not match scalar message
text; check features, terms and rules in model order for diagnostics.

| Stage                                   | Status | Error in `"raise"` mode |
| --------------------------------------- | -----: | ----------------------- |
| Valid result                            | 0      | —                       |
| Non-finite input or conversion overflow | 1      | `InvalidParameterError` |
| Input outside its universe              | 2      | `InvalidDomainError`    |
| Membership, antecedent or firing error  | 5      | `NumericalError`        |
| All weighted firings truly zero         | 3      | `UndefinedResultError`  |
| Non-finite affine or output arithmetic  | 5      | `NumericalError`        |
| Consequent or output outside universe   | 4      | `InvalidDomainError`    |

After firing succeeds, evaluate and validate every consequent in rule
order, including inactive rules, before validating the final output.
For a row with multiple bad consequents, the first failing rule determines
the code. Invalid grades and a positive weighted firing rounded to zero
are numerical errors. Preserve the cause of a lower level membership
failure when available. These are explicit batch row categories;
scalar exception types and ordering are unchanged. In a row with both
an invalid domain and a failing membership, the batch reports the
domain first because it validates every input domain before evaluating
terms. Differential tests isolate scalar failures; combined failures
use the batch precedence table. A model defect or unexpected engine or
resource error is a call failure. Restore the ambient NumPy error policy
on success and failure.

### Scalar parity

Evaluate every declared input term once per row, including unreferenced
terms. Compute normalized strengths using the scalar maximum-scaled
denominator and preserve the scalar finite-sum and exact-ratio safeguards
for affine and weighted sums. A plain dot product, clamping, replacing
`math.fsum` with an unchecked reduction, or treating near-zero values as
no firing can change the result or its failure category. Per-row numeric
corrections using shared scalar primitives are allowed inside the NumPy
engine; a hidden model-level fallback is not. The implementation must
prove any fast path's guard for boundary, underflow, cancellation and
overflow behavior or use the canonical arithmetic on those paths.

Check finite grades, strengths and normalized weights within absolute
`1e-12` and zero relative tolerance, as in ADR-0018. Compare values,
consequences and contributions using
`abs(candidate - reference) <= max(1e-12, 8 * ulp(reference))` on the
acceptance corpus. Also require exact row status, validity, branch
decisions (including exact zero and one where they govern a branch),
domain inclusion and constant/single-firing endpoints. Require exact
expected values for analytical subnormal and cancellation witnesses;
the absolute floor alone cannot check them. Firing underflow is numerical
failure, while a representable positive firing must not be reported as
no fire. Preserve the scalar exact-ratio path when a normalized strength
is subnormal but its contribution is representable. These tolerances are
test acceptance criteria, not thresholds used during inference.

### Trace and chunking

All modes return the base result. Changing trace level cannot change a
value, status or error index. Result metadata uses the model's variable,
term and rule declaration order, independent of supplied column order.

| Mode        | Retained evidence                                         |
| ----------- | --------------------------------------------------------- |
| `"off"`     | Base result; no trace arrays or per-row trace objects.    |
| `"summary"` | Base result, fired rule count and maximum firing.         |
| `"full"`    | Summary, input grades, rule traces, weights and mask.     |

Summary stores `fired_rule_count` as int64 `(N,)` and
`max_firing_strength` as float64 `(N,)`. True no-fire rows have count and
maximum zero; other failed rows use `-1` and `NaN`. Full adds
`input_grades` as float64 `(N, T)`, and five float64 `(N, R)` arrays for
antecedent grade, firing, consequent, normalized strength and
contribution. Static rule weights occupy one float64 `(R,)` vector. A
bool `(N, R)` mask marks where the exact normalized ratio is used.

Full trace preserves inactive rules on successful rows. Grades and the
five per-rule fields are `NaN` on failed rows, with a false exact-ratio
mask. Normalized strengths are the rounded view; a marked entry can be
recovered exactly by dividing that rule's exact binary64 firing ratio by
the exact sum of that row's firing ratios. Compute its contribution before
rounding the strength; a contribution may be nonzero even if the displayed
strength is zero. Keep names once and do not copy input coordinates into
the trace. Rounded contributions may not sum exactly to the reported value.

`chunk_size` is a positive integer number of rows (not Boolean), with a
default of 4096. Process consecutive chunks of up to that size, including
a final partial chunk. Empty input needs no kernel invocation. For
identical converted coordinates, preserve masks, statuses and trace
ordering exactly across chunk sizes and layouts, and meet the same
numeric parity bounds. Do not reduce across rows. Under `"raise"`,
failures in later rows or stages cannot take precedence over an earlier
failing row. Validate structure and prepare model metadata once. Avoid
a whole-batch conversion or reorder copy: normalize one chunk at a time,
then write results directly into their final buffers.

## Validation and resource budget

- The implementation must check zero-order, first-order and mixed models
  against per-row `SugenoModel.Evaluate` on binary64 coordinates and against
  independent analytical witnesses. Cover all supported term and operator
  families, open and discrete domain boundaries, adjacent floats, unused
  terms, inactive affine domain failures, no-fire and firing underflow.
  Include subnormal normalized strengths, cancellation, overflow and
  constant endpoints.
- Run each failure witness in both policies with bad rows on opposite sides
  of a chunk boundary. Include empty and single rows, mismatched/duplicate
  names, permuted columns, ragged/Boolean/object input, float32/integers,
  post-conversion nonfinite rows, and non-contiguous/read-only arrays.
  Compare all trace modes and chunk sizes `1`, a non-divisor of `N` and a
  size larger than `N`; verify ownership and ambient NumPy error policy.
- Excluding model metadata and array headers, the retained dense payload
  is `10N` bytes for off, `26N` for summary and
  `26N + 8NT + 41NR + 8R` for full. With `B = min(chunk_size, N)`, bound
  working memory to `O(B(F + T + R + L) + M)`, where `L` is the maximum
  number of simultaneously live expression/affine scratch vectors and
  `M` is prepared model metadata. Do not allocate a row-by-domain-grid
  matrix for discrete lookup. Measure retained payload and incremental
  temporary peak separately, alongside fresh-process peak RSS. At fixed
  model and chunk size, doubling `N` may grow the retained arrays but must
  not grow chunk scratch with `N`. Reducing the chunk size must reduce the
  bound; full trace still grows with the rows returned.
- Benchmark complete installed calls including validation, conversion,
  computation, masks and result allocation. Use a scalar loop over the
  same observations as the reference; include mapping creation and normal
  scalar trace work, retaining only the scalar evidence corresponding to
  the selected batch mode. Record prepared array and original sequence
  workloads separately, small batches (`1`, `16`), `1024` and `100000`
  rows, both orders, all modes and at least two chunk sizes. Retain at
  least seven paired alternating time samples, raw memory evidence, and
  the model/input sizes, layout, software and host details. Record fresh
  process import costs separately, with and without the optional extra. Follow the
  [benchmark protocol](../performance/benchmark-reproducibility-protocol.md).
  Accept a throughput claim only for measured workloads with a repeatable
  conversion-inclusive gain and acceptable memory for the intended caller.
  Timing is not a CI threshold; do not infer a portable crossover or
  consumer throughput from synthetic data.
- Verify installed execution with and without the optional dependency on
  the ADR-0018 support matrix. Update API and EN/RU/zh-CN guides when the
  batch operation is implemented; released scalar and membership/scale
  guides retain their current contracts.

## Bounded evidence

Run `python -m experiments.sugeno_batch_contract_probe` from the checkout
with NumPy available. The [probe](../../experiments/sugeno_batch_contract_probe.py)
independently computes a two-input, two-rule model on ten rows. The case
at `(risk, exposure) = (1/4, 1/4)`
has normalized strengths `(3/5, 2/5)` and exact weighted means `9/20`,
`67/160` and `7/16` for the constant, affine and mixed cases. The probe
checks those means, then compares the NumPy witness with scalar traces
on ordinary finite rows and tests no-fire, bad input and a bad inactive
consequent at different chunk boundaries. It exercises empty, single,
strided/reordered, integer, non-native-endian and float32 inputs. If
extended precision is available, it also checks conversion overflow.

On Python 3.13.17 with NumPy 2.5.4, the maximum observed absolute
output difference was zero in all three model orders. The ten-row
case (`T = 4`, `R = 2`) retained 100, 260 and 1416 array payload bytes
for off, summary and full respectively. Separate scalar witnesses show
why true zero firing and positive product underflow are different,
why a rounded-zero normalized ratio can still contribute `2**-52`,
and why affine cancellation must preserve a unit residual. The probe
does not implement general model validation or numerical repair, and
its payload counts do not measure temporary memory, RSS or throughput.

## Output

The proposed contract specifies a single-output batch, error and trace
semantics, and the gates a public implementation must pass. Implement
the batch engine in [#406](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/406)
and measure it in [#407](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/407).
Scalar inference, existing NumPy operations and package dependencies
are unchanged by this decision record.
