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
chunk_size=4096)`. The operation and result are design names; this ADR does
not ship a callable. Calling this operation opts into NumPy. The sole
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

| Concern       | Contract |
| ------------- | -------- |
| Observations  | A rank-two numeric ndarray or rectangular list/tuple of rows with shape `(N, F)`. No scalar, rank-one, broadcast, transposed or implicit flattening semantics. |
| Feature axis  | A required tuple of exactly `F` unique, case-sensitive names, one per supplied column. It must be a permutation of the model input names; bind by name, not by physical column position or dictionary order. A square input is still interpreted as rows of observations. |
| Empty input   | A shaped `(0, F)` ndarray or the empty outer sequence `[]`/`()` with valid `feature_names`. Reject `(0, G)` for `G != F` and reject a rank-one empty ndarray. Shape, model and options are validated even when `N = 0`. |
| Single row    | Use `(1, F)`, including `(1, 1)` for one feature. All output arrays retain a row axis. |
| Array dtype   | Signed/unsigned integer or real floating dtype; allow non-contiguous, negative-stride, read-only and non-native-endian inputs. Reject Boolean, complex, string, object, structured and masked arrays. Reject array subclasses that would discard custom input semantics on conversion. |
| Sequence data | Validate shape and real numeric cells before execution; reject Boolean cells even in mixed numeric rows. Accept built-in `int`/`float` and NumPy integer/real-floating scalars. Reject ragged input, implicit coercions from other cell types, iterators and mappings. |
| Conversion    | Work on a private C-order float64 chunk in model feature order. Precision may change (including large integers); scalar parity is against the resulting binary64 coordinates. A non-finite converted coordinate is a bad row. Input data is never mutated or retained in the result. |
| Base result   | `values`: float64 `(N,)` in output units; `valid_mask`: bool `(N,)`; `status`: uint8 `(N,)`. Valid values are finite, failed values are `NaN`, and `valid_mask` is true exactly where `status == 0`. |
| Ownership     | Fresh, independent arrays exposed read-only, with an explicit array copy for writable use. Row order follows the source, including failed rows; row indices are zero based. |

Raggedness, wrong shape/dtype or cell type, bad feature bindings, invalid
options, unsupported model data and dependency errors are whole-call
failures; they cannot be masked. A missing feature column is a call error
even when every row would be empty. An array already converted to numeric
dtype conveys only its current dtype and values.

### Row failures

In `"raise"` mode, raise on the lowest original row index with a row
failure and return no result. Include that index and, when known, the
feature or rule name in the diagnostic. In `"mask"` mode, return all rows
with the same classifications. The operation uses the following stage
order within a row. Errors at the same stage need not match scalar message
text; check features, terms and rules in model order for diagnostics.

| Stage                         | Status | Error in `"raise"` mode     |
| ----------------------------- | -----: | --------------------------- |
| Valid result                  |      0 | —                           |
| Non-finite coordinate before or after float64 conversion (including conversion overflow) | 1 | `InvalidParameterError` |
| Finite coordinate outside its input universe | 2 | `InvalidDomainError` |
| Membership/antecedent arithmetic failure, invalid grade, or positive weighted firing underflowing to zero | 5 | `NumericalError` |
| All weighted firings truly zero |     3 | `UndefinedResultError`      |
| Non-finite affine or output arithmetic | 5 | `NumericalError`          |
| Finite consequent or final value outside the output universe | 4 | `InvalidDomainError` |

After firing succeeds, evaluate and validate every consequent in rule
order, including inactive rules, before validating the final output.
For a row with multiple bad consequents, the first failing rule determines
the code. Arithmetic failure in a lower level membership kernel is wrapped
with its cause when available. These are explicit batch row categories;
scalar exception types and ordering are unchanged. A model defect or
unexpected engine/resource error is a call failure, never a bad row. The
engine must restore the ambient NumPy error policy on success and failure.

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

| Mode         | Retained evidence |
| ------------ | ----------------- |
| `"off"`     | No trace arrays or per-row trace objects. |
| `"summary"` | Also retain `fired_rule_count` (int64 `(N,)`) and `max_firing_strength` (float64 `(N,)`). True no-fire rows have count and maximum zero; other failed rows use `-1` and `NaN`. |
| `"full"`    | Summary plus `input_grades` (float64 `(N, T)`), and five float64 `(N, R)` arrays for antecedent grade, firing, consequent, normalized strength and contribution. One float64 `(R,)` vector stores static rule weights. Include a bool `(N, R)` mask marking where the scalar exact normalized ratio is used. |

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
a final partial chunk. Empty input needs no kernel invocation. Preserve
identical values, masks and traces across chunk sizes and layouts; do not
reduce across rows. Under `"raise"`, failures in later rows or stages
cannot take precedence over an earlier failing row. Validate structure
and prepare model metadata once. Avoid a whole-batch conversion or reorder
copy: normalize one chunk at a time, then write results directly into
their final buffers.

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
  the model/input sizes, layout, software and host details. Follow the
  [benchmark protocol](../performance/benchmark-reproducibility-protocol.md).
  Accept a throughput claim only for measured workloads with a repeatable
  conversion-inclusive gain and acceptable memory for the intended caller.
  Timing is not a CI threshold; do not infer a portable crossover or
  consumer throughput from synthetic data.
- Verify installed execution with and without the optional dependency on
  the ADR-0018 support matrix. Update API and EN/RU/zh-CN guides when the
  batch operation is implemented; released scalar and membership/scale
  guides retain their current contracts.

## Output

The proposed contract specifies a single-output batch, error and trace
semantics, and the gates a public implementation must pass. Scalar
inference, existing NumPy operations and package dependencies are
unchanged by this decision record.
