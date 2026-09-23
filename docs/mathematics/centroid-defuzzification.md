<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Centroid defuzzification

## Contract

For a continuous scalar fuzzy set $A$ and an explicit finite integration
domain $D=[l,r]$, FuzzyRoutines defines the centroid as

$$
C(A,D)=\frac{\int_l^r x\mu_A(x)\,dx}{\int_l^r \mu_A(x)\,dx}.
$$

The integration domain is operational input, not the mathematical support of
the set. It must lie inside the declared `ContinuousUniverse`. A zero or
non-finite denominator has no centroid and raises `ValueError`.

## Evaluation paths

`Centroid` selects a method from evidence carried by the membership callable:

| Membership source                      | Method                                                                      |
|----------------------------------------|-----------------------------------------------------------------------------|
| Triangle, trapezium, parabolic, bell   | Analytical piecewise-polynomial area and first moment                       |
| Gaussian-shaped exponential            | Analytical `erf` area and exponential boundary term when numerically stable |
| Other `MFunction` or generic callable  | Deterministic adaptive Simpson integration of area and first moment         |

The Gaussian path delegates to adaptive integration if subtracting the two
`erf` values cannot resolve a positive finite area. No path silently falls
back to a fixed sampling grid.

## Precision and failure

`CentroidPolicy` owns the adaptive configuration for one operation. Its
defaults are an absolute area tolerance of `1e-12`, a relative tolerance of
`1e-10`, and at most 20 recursive bisections per interval. The absolute
first-moment target scales with the largest absolute domain coordinate.

Adaptive integration raises `CentroidConvergenceError` when the configured
depth cannot meet both moment targets. Increasing the limit is an explicit
caller decision; failure never returns the best-so-far estimate as if it were
converged.

Generic callables are assumed sufficiently regular for adaptive quadrature.
No finite black-box sampler can discover a feature located between all of its
evaluation coordinates. Such a membership requires an analytical family or a
future explicitly partitioned-domain contract.

## Compatibility facade

`FuzzySet.Defuz()` and `defuzValue` delegate to the same strategy on every
access. They therefore observe current membership parameters and current
`supportSet` integration bounds without a retained centroid cache.
`MFunction.accuracy` remains writable for source compatibility but no longer
controls correctness or work. The retired 1000-point right-endpoint outputs
remain test provenance, with an approved absolute compatibility tolerance of
`5e-4` for the Task #78 reference cases.

## Evidence

- `tests/test_defuzzification.py` covers independent analytical references,
  adaptive convergence, explicit non-convergence, domain validation,
  mutation, narrow analytical sets, and low-membership sets;
- `tests/test_legacy_centroid_reference.py` preserves the retired algorithm's
  observations independently from production code;
- `tests/test_numerical_edge_policy.py` proves explicit zero-area failure.

The governing decisions are [ADR-0002](../adr/0002-universe-support-semantics.md)
and [ADR-0005](../adr/0005-numerical-defuzzification-policy.md).
