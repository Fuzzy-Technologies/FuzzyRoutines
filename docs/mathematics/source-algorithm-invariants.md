<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Source Formula and Algorithm Invariants

- Status: Executable traceability contract for Task #201
- Scope: currently implemented scalar formulas and finite algorithms
- Source of truth: executable code plus the focused mathematical contracts

## Traceability map

This map connects each non-trivial implementation family to its definition,
boundary contract, numerical argument, and executable evidence. It is an index,
not a second copy of the detailed proofs.

| Implementation area                       | Definition or derivation                                                                                                | Required invariant                                                                  | Executable evidence                                                     |
|-------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| Historical membership families            | [Membership-function contracts](membership-function-contracts.md)                                                       | Validated geometry; stable families saturate; formulas expose overflow bounds       | `tests/test_formula_algorithm_invariants.py`, membership contract tests |
| Parametric and parabolic negations        | [Operator contracts](../adr/0004-operator-and-negation-contracts.md) and [derivation](parabolic-negation-derivation.md) | Endpoint reversal, fixed point, monotone decrease, and involution                   | negation and formula-invariant tests                                    |
| T-norms, s-norms, and set operations      | [Explicit fuzzy-set operations](fuzzy-set-operations.md)                                                                | Closure, boundary identities, associativity, commutativity, and De Morgan duality   | operator algebraic and reference tests                                  |
| Exact height and normalization            | [Height and normalization](fuzzy-set-normalization.md)                                                                  | Exact evidence only; positive height scales to one; zero height fails closed        | normalization and derived-property tests                                |
| Analytical and sampled derived properties | [Universe and support contract](universe-support-contract.md)                                                           | Analytical geometry is exact; finite sampling remains provenance-rich evidence      | derived-property and formula-invariant tests                            |
| Weak alpha-cuts and uniform sampling      | [Alpha-cut contract](alpha-cuts.md)                                                                                     | `>=` boundary, nested cuts, exact discrete scan, explicit sampled approximation     | alpha-cut and formula-invariant tests                                   |
| Equality and inclusion                    | [Equality and inclusion](fuzzy-set-relations.md)                                                                        | Exhaustive discrete comparison; bounded continuous claim; explicit tolerance        | fuzzy-set relation tests                                                |
| Centroid defuzzification                  | [Numerical policy](../adr/0005-numerical-defuzzification-policy.md)                                                     | Analytical moments or deterministic adaptive quadrature                             | analytical, convergence, edge, and legacy-reference tests               |

## Numerically sensitive branches

### Parabolic negation

The implicit relation is quadratic in $d=y-x$. Evaluating the direct root

$$
d = \frac{-1 + \sqrt{D}}{2(2\alpha-1)}
$$

would cancel near $\alpha=1/2$ and divides by zero at the standard-complement
case. Rationalization gives the implemented continuous form

$$
y = x + \frac{4(\alpha-x)}{1+\sqrt{D}}.
$$

The two discriminant expressions in source are algebraically equivalent
forms selected on opposite sides of $\alpha=1/2$. They keep their additive
terms non-negative on the accepted domain. Exact endpoint returns protect the
boundary contract from avoidable round-off.

### Logistic membership

For $z=a(x-b)$, the direct expression $1/(1+e^{-z})$ overflows when $z$ is a
large negative finite value. The implementation therefore uses

$$
\sigma(z) =
\begin{cases}
1/(1+e^{-z}), & z \ge 0, \\
e^z/(1+e^z), & z < 0.
\end{cases}
$$

Both exponents are non-positive, so `math.exp` cannot overflow. Binary64 may
still round the mathematical open-interval result to exactly `0.0` or `1.0`;
that is representational saturation, not clamping.

### Harrington desirability

The formula $d(y)=e^{-e^{-y}}$ has the mathematical range $(0,1)$. For very
negative finite $y$, evaluating the inner exponential first would overflow
even though the final representable result is already `0.0`. The guarded
branch compares $y$ with the logarithm of Python's greatest finite binary64
value and returns that deterministic underflow limit. For large positive
finite $y$, ordinary rounding may produce `1.0`.

### Historical intermediate overflow

Finite parameters and a finite input do not imply that every intermediate
binary64 result is finite. The retained `Hyperbolic`, `Bell`, and `Parabolic`
expressions are evaluated directly and do not rescale extreme powers or
squares. They may therefore raise `OverflowError` at sufficiently large
magnitudes even though their parameters and input passed finite-value
validation. This is a documented current numerical limitation, not a claim
that all finite binary64 inputs produce a grade. The stable logistic branches
and the Harrington guard above address their own known exponential overflow
paths; they do not generalize that guarantee to the other historical families.

### Uniform grids

For a closed interval $[l,r]$ and $n\ge2$, sampled operations use

$$
h=\frac{r-l}{n-1}, \qquad x_i=l+ih.
$$

The final coordinate is assigned from `r` instead of recomputed. This makes
the closed-domain endpoint invariant exact even when repeated binary64
arithmetic would produce a neighboring value. Construction and evaluation are
$O(n)$ time and $O(n)$ retained provenance.

### Retired legacy centroid evidence

For `accuracy = n`, legacy defuzzification evaluates right endpoints
$x_i=l+i(r-l)/n$, $i=1,\ldots,n$, and returns

$$
\frac{\sum_i x_i\mu(x_i)}{\sum_i\mu(x_i)}.
$$

The common rectangle width cancels from the quotient. This is $O(n)$ time and
$O(1)$ auxiliary space, but it is not an adaptive quadrature or a convergence
claim. Tests preserve this algorithm independently as Task #78 provenance; it
is no longer the production implementation.

### Current centroid

The current strategy evaluates analytical area and first moment for supported
piecewise-polynomial and stable Gaussian paths. Other continuous callables use
adaptive Simpson quadrature with immutable per-operation tolerances and a
finite recursion limit. Zero area raises `ValueError`, and exhausted adaptive
work raises `CentroidConvergenceError`; neither condition produces a cached,
fixed-grid, or best-so-far result. The complete contract and evidence map are
in [Centroid defuzzification](centroid-defuzzification.md).

### Finite relations

Equality and inclusion consume each declared comparison coordinate at most
once and stop at the first counterexample. They are $O(n)$ in the worst case
and $O(1)$ auxiliary space. Tolerance equality follows Python's documented
criterion

$$
|a-b| \le \max(r\max(|a|,|b|), A),
$$

where $r$ and $A$ are the explicit relative and absolute tolerances. Inclusion
first accepts exact order and uses closeness only for a small violating pair;
it never widens every grade by an implicit epsilon.

## Reference hierarchy

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- E. P. Klement, R. Mesiar, and E. Pap, *Triangular Norms*, Springer, 2000.
  <https://doi.org/10.1007/978-94-015-9540-7>
- Python documentation, [`math` — Mathematical functions](https://docs.python.org/3/library/math.html),
  for `exp`, finite-number behavior, and the exact `isclose` criterion.
- C. Barker, [PEP 485 — A Function for testing approximate equality](https://peps.python.org/pep-0485/),
  the accepted Python specification behind `math.isclose`.
- IEEE Std 754-2019, *IEEE Standard for Floating-Point Arithmetic*.
  <https://standards.ieee.org/ieee/754/6210/>

The historical membership shapes and parabolic relation remain
project-specific compatibility contracts where no verified source establishes
the exact formula under the retained name. The repository documents that fact
instead of manufacturing external provenance.
