<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Centroid defuzzification

## Contract

For a continuous scalar fuzzy set $A$ and an explicit finite integration
domain $D=[l,r]$, FuzzyRoutines defines the centroid as

$$
C(A,D)=\frac{\int_l^r x\mu_A(x)\;\mathrm{d}x}{\int_l^r \mu_A(x)\;\mathrm{d}x}.
$$

The integration domain is operational input, not the mathematical support of
the set. It must lie inside the declared `ContinuousUniverse`. A zero or
non-finite denominator has no centroid and raises `ValueError`.

## Evaluation paths

`Centroid` selects a method from evidence carried by the membership callable:

| Membership source                             | Method                                                                        |
| --------------------------------------------- | ----------------------------------------------------------------------------- |
| Triangle, trapezium, parabolic, bell          | Analytical piecewise-polynomial area and first moment                         |
| Gaussian-shaped exponential                   | Analytical `erf`/`erfc` area and stable exponential boundary difference       |
| Other analytical families or generic callable | Deterministic adaptive Simpson integration of area and first moment           |

The Gaussian path uses complementary error functions for same-sided tails.
Writing $u=(l-c)/s$ and $v=(r-c)/s$ for centre $c$ and positive scale $s$, its
standardized area is

$$
I=\sqrt{\frac{\pi}{2}}
\begin{cases}
\mathrm{erfc}(u/\sqrt{2})-\mathrm{erfc}(v/\sqrt{2}), & u\ge0,\\
\mathrm{erfc}(-v/\sqrt{2})-\mathrm{erfc}(-u/\sqrt{2}), & v\le0,\\
\mathrm{erf}(v/\sqrt{2})-\mathrm{erf}(u/\sqrt{2}), & u\lt0\lt v.
\end{cases}
$$

The area is $sI$, and the centroid is
$c+s(e^{-u^2/2}-e^{-v^2/2})/I$. The boundary difference uses `expm1` to retain
precision when the exponentials are close. This avoids subtracting two `erf`
values that have both rounded close to one.

A first-order estimate of normalization and special-function rounding must
fit the caller's `relativeTolerance` before the analytical result is used.
This estimate is a method-selection guard, not an exact error certificate.
Non-positive or non-finite area, non-finite moments, an unresolved subtraction,
or an out-of-domain analytical centroid delegates to adaptive integration with
the same policy. Results are never clamped to an endpoint, and no path silently
falls back to a fixed sampling grid.

## Precision and failure

`CentroidPolicy` owns the adaptive configuration for one operation. Its
defaults are an absolute area tolerance of `1e-12`, a relative tolerance of
`1e-10`, and at most 20 recursive bisections per interval. The absolute
first-moment target scales with the largest absolute domain coordinate.
These are moment error targets, rather than a direct bound on centroid error.
When tiny membership weights force Gaussian fallback, callers can lower the
absolute tolerance explicitly so it does not dominate their requested relative
accuracy.

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
remain test provenance, with a declared absolute compatibility bound of
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

## References

- W. Van Leekwijck and E. E. Kerre, “Defuzzification: Criteria and
  Classification,” *Fuzzy Sets and Systems*, 108(2), 159–178, 1999.
  <https://doi.org/10.1016/S0165-0114(97)00337-0>
