# ADR-0005: Numerical Precision and Defuzzification Policy

- Status: Accepted on merge
- Date: 2026-09-14
- Related planning task: #12
- Related Features: #21 and #26

## Context

The legacy centroid stores a precomputed value on `FuzzySet` and evaluates a
fixed 1000-point right-endpoint Riemann sum using mutable
`MFunction.accuracy`. It has no explicit finite-number, tolerance, zero-area,
or convergence contract.

The historical outputs must first be captured as evidence; they are not by
themselves the future numerical specification.

## Decision

### Numeric inputs and intermediate values

Public numerical inputs and membership evaluations used in mathematical
operations must be finite real values. NaN and infinities are invalid, not
zero-like values.

No repository-wide magic epsilon is permitted. Each approximate algorithm owns
a named tolerance with a documented mathematical purpose.

### Test tolerances

- Exact operator and piecewise-membership results use exact assertions where
  representable.
- Stable floating-point formula checks use an explicit absolute tolerance of
  `1e-12` unless a narrower task justifies another value.
- Numerical integration tests state their method, resolution or convergence
  tolerance, and reference value in the test itself.

### Centroid contract

The supported default defuzzification method is centroid:

```text
centroid = integral(x * mu(x)) / integral(mu(x))
```

The integration domain is the explicit legacy `supportSet` until ADR-0002
defines the new universe and support model.

The legacy right-endpoint, 1000-sample behavior is captured by Task #78 as a
reference observation. A later implementation may replace it only when it
preserves the approved centroid contract, documents its numerical method, and
supplies reference/convergence evidence.

Numerical policy must not remain mutable hidden state on `MFunction`. A later
implementation may provide explicit immutable or per-operation configuration
while preserving historical public attributes until a compatibility decision
says otherwise.

### Zero-area and degenerate behavior

A centroid is undefined when its membership area is zero or non-finite.
Returning a cached number, infinity, or an arbitrary endpoint is invalid.

The implementation must raise a clear domain error for zero area. Before the
minimal exception hierarchy exists, it may be a documented `ValueError`;
a later domain-specific subtype must preserve that meaning.

## Consequences

- Task #62 defines finite/NaN/infinity behavior in code.
- Task #64 owns degenerate-domain and zero-area implementation detail.
- Task #78 records legacy centroid outputs without declaring them correct.
- Tasks #79–#81 implement the decoupled centroid and any additional methods.
- Task #94 may refine the error type without changing the zero-area contract.

## Acceptance and supersession

This ADR is **Proposed** until review and merge. A different default numerical
method, tolerance policy, or zero-area contract requires an amendment or a new
ADR.