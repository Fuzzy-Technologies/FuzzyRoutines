<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

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

ADR-0002 defines the legacy `supportSet` as an integration-domain compatibility
name, not mathematical support. Modern numerical operations consume an
explicit integration domain and must not infer one from sampled membership
values.

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

### Audit amendment — 2026-10-16

Compositions owned by the inference engine retain trusted built-in knots and
linear minimum-clipping points as private initial quadrature partitions.
Generic user callback attributes do not authorize such hints. The sum of all
active-panel Simpson error estimates must meet the same global area and
first-moment targets; partitions do not each receive a fresh tolerance.
Refinement prioritizes estimated error and preserves `maximumDepth` per initial
interval. These remain conditional numerical estimates, not rigorous error
certificates for arbitrary functions.

For supported piecewise-polynomial analytical sources, unsafe floating-point
moments are recomputed with exact rational representations of the binary64
coordinates before taking the ratio. The shared polynomial formulas and at
most five pieces are reused; no new numerical backend or runtime dependency
is introduced. This prevents tiny/huge intermediate moments from erasing a
representable centroid. A genuinely zero area still raises the existing
undefined-result error. Gaussian and arbitrary-callback underflow limits are
not silently promoted to symbolic guarantees.

This ADR is **Accepted**. A different default numerical method, tolerance
policy, or zero-area contract requires an amendment or a new ADR.

The global adaptive pass preserves wholly rational coordinates and panel sums.
Zero-error panels are not subdivided after another panel exhausts its depth;
otherwise an isolated discontinuity could trigger irrelevant exponential work.
A quarter of each moment target reserves margin for the final ratio. If a
nonzero adaptive sample or same-sign area/moment estimate is rounded to zero,
raise `NumericalError`; generic compositions do not acquire the bounded
polynomial rational fallback merely by retaining geometry.

### Release acceptance amendment — 2026-10-19

Clipped polynomial panels are integrated in distance from their left endpoint.
Subtracting nearby powers of two endpoints can destroy significant digits and
return a centroid outside a narrow integration window even for an ordinary
triangle. Independent exact monomial integrals cover every polynomial branch.

The bounded rational path preserves original `Rational` parameters and domain
endpoints before any binary64 conversion. Distinct rational vertices or large
integers must not collapse into a zero-width segment. When supplied geometry
is not exactly representable in binary64, return its exact rational centroid;
some valid rational integration windows contain no binary64 coordinate at all.
Ordinary float geometry retains the floating-point path and the existing
single final rounding on exceptional rational recomputation. This refines the
analytical implementation without changing historical scale coefficients,
the centroid definition, adaptive tolerances or optional dependencies.

Trusted inference knots likewise retain distinct original rational coordinates.
This prevents a known positive-area built-in consequent from disappearing
during binary64 conversion; it does not turn Mamdani quadrature into symbolic
integration. If working-precision rounding puts the final numerical centroid
outside its original integration domain, raise `NumericalError` instead of
returning an invalid coordinate or clamping it to an endpoint.

The adaptive queue updates compensated moment/error totals when a panel is
replaced. Acceptance (or depth exhaustion) always recomputes the complete
active partition before checking the global targets. This removes quadratic
per-refinement rescans without treating accumulated rounding as acceptance
evidence. Overflow guards apply to engine sums, not callback exceptions.
