<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Numerical edge-case policy

## Status

Implemented v2 contract. Task #64 established the policy, Task #66 removed
stale construction-time centroid state, and Tasks #79 and #80 implement the
[analytical and adaptive centroid strategy](centroid-defuzzification.md),
explicit precision, convergence failure, and zero-area behavior.

## Tolerances

No global epsilon is permitted. Each operation owns an explicit numerical contract:

- algebraic membership and fuzzy-operator identities use an exact result when the formula is exact in binary floating point, otherwise a test-specific absolute and relative tolerance;
- root or inverse membership operations declare their stopping criterion, maximum work, and residual bound;
- numerical integration declares an absolute and relative error target, an adaptive stopping criterion, and a deterministic failure mode.

## Degenerate inputs

A membership configuration is invalid when its required widths or ordered breakpoints are degenerate. Construction must raise ValueError before evaluation rather than rely on division by zero, a zero result, or a later cache failure.

Centroid defuzzification has no value for a zero-area membership over its support. It must raise ValueError; returning a support midpoint, zero, NaN, infinity, or a cached predecessor is forbidden.

Integration accuracy is an algorithm setting owned by the integration method. It is not a mutable membership-function configuration parameter and no hard-coded point count constitutes a correctness claim.

## Evidence

Tests in `tests/test_numerical_edge_policy.py` and
`tests/test_defuzzification.py` verify the implemented behavior. The legacy
1000-point right-endpoint implementation remains only as independently
reproduced historical baseline evidence in Task #78.
