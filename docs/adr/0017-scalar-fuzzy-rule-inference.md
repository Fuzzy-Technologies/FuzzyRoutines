<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0017: Explicit scalar fuzzy-rule inference

## Status

Accepted on 2026-10-14 for Tasks #330, #331 and #332 after independent
mathematical, implementation and documentation review. The 54 focused inference
and figure tests verify analytical references, edge policies and reproducible
plots. This additive contract preserves every 2.0 operation and historical preset.

## Context

Membership functions and set operations do not by themselves execute a rule
base. Applications need separate, inspectable choices for antecedent logic,
rule weighting, output activation, aggregation and numerical defuzzification.
The same rule text can produce different numerical results under those choices.

## Decision

Models have one or more named scalar input variables and exactly one scalar
output. A `FuzzyVariable` owns an ordered tuple of uniquely named terms with
equal universes. Inputs may have continuous or discrete universes. Mamdani's
output universe is continuous; Sugeno declares a continuous output universe
without requiring output terms. Names are exact and case-sensitive.

`TermCondition`, `AllOf`, `AnyOf` and `NotCondition` form a finite expression
tree. AND and OR require at least two children. `InferencePolicy` explicitly
supplies t-norm, s-norm and negation policies from ADR-0004. Child order is
preserved; no expressions, strings or Python source are evaluated dynamically.
Rule weights are degrees in $[0,1]$ and use product weighting:

$$
\alpha_i = w_i A_i(\mathbf{x}).
$$

All model containers and result records are frozen dataclasses and tuples.
Membership callbacks are retained by reference: purity is the caller's
responsibility, as for `ScalarFuzzySet`. No hidden mutable evaluation cache is
retained. Each input term is evaluated once per invocation, in declared order.
Trace records preserve all input grades, rule names, antecedent grades, weights,
firing strengths and output contributions. Membership grades are not
probabilities and need not sum to one.

### Mamdani

`MamdaniModel` supplies a separate t-norm `activation` and s-norm `aggregation`.
"Activation" means applying the firing degree to the consequent set, not a
claim that every selected t-norm is a formal fuzzy implication operator:

$$
\mu_i(y)=T_{\rm activation}(\alpha_i,\mu_{B_i}(y)),\qquad
\mu_{\rm out}(y)=S_{\rm aggregation}(\mu_1(y),\ldots,\mu_n(y)).
$$

Evaluation returns every activated set and their aggregated `ScalarFuzzySet`.
An optional explicit `IntegrationDomain` requests `Centroid` using ADR-0005;
otherwise the scalar value is absent. Composed callbacks carry no analytical
certificate, so their centroid uses adaptive Simpson integration with the
existing tolerance/depth policy. Convergence is numerical evidence under the
regularity assumption; arbitrarily narrow features may evade sampling.

The 2026-10-16 audit amendment preserves trusted built-in geometry through
engine-owned activation and aggregation wrappers. Initial quadrature partitions
include family knots and minimum-clipping points of piecewise-linear terms;
all panels share one global estimated-error budget. A priority queue refines
the largest estimated error, retaining the configured maximum depth per initial
interval. These hints are not analytical certificates, and arbitrary callback
attributes are not trusted. The disjoint audit triangles have independent
areas `0.02`, `0.15` and centroid `1161/1700`, rather than the large term's `0.75`.

### Sugeno

`SugenoRule` accepts `ConstantConsequent(c)` or
`AffineConsequent(b, ((inputName, coefficient), ...))`:

$$
z_i=b_i+\sum_j a_{ij}x_j,\qquad
\bar\alpha_i=\frac{\alpha_i}{\sum_k\alpha_k},\qquad
z=\sum_i\bar\alpha_i z_i.
$$

Normalization scales firing strengths by their maximum before summation to
avoid needless underflow. Each trace reports $z_i$, $\bar\alpha_i$ and its
contribution $\bar\alpha_i z_i$. Rounded contributions can reconstruct the
final value only up to round-off. If their sum escapes the finite consequent
convex hull or overflows, the engine recomputes the weighted ratio using exact
rational representations of the finite strengths and consequences (retaining
exact rational inputs rather than underflowing them through a float cast),
then rounds once. This preserves constant endpoints without clamping user
inputs or the output. The normal calculation stays on the floating-point path.
This is a weighted scalar average, not the
centroid of an aggregated fuzzy set and not a call to the legacy `Defuz()`.
Every consequent, including inactive ones, must be finite and belong to the
declared output universe at the supplied inputs; values are never clamped.
No gradient, parameter training or tensor support is implied.

The audit amendment also retains an exact `Fraction` for a positive normalized
strength in the binary64 subnormal range. Its contribution is rounded only
after the exact normalized ratio is multiplied by the consequent; otherwise
a huge finite consequent could lose a representable contribution. This uses
the existing `MembershipScalar` real-number field contract, adds no field or
public type, and keeps ordinary traces on floats. The exact denominator is
computed at most once per evaluation. Positive antecedent/weight products
that already underflowed to zero cannot be faithfully represented by the
existing firing snapshot: they raise `NumericalError`, separately from true
no-fire. No sentinel or silent redefinition of a trace is allowed.

### Validation and failure policy

- Empty rules/inputs, duplicate names, unknown references, non-tuple containers
  and invalid operator/consequent types fail at construction.
- Evaluation requires exactly the declared input keys. Missing and extra keys
  fail. Booleans, non-real/non-finite values and out-of-universe inputs fail.
- All zero firing strengths raise `UndefinedResultError`; there is no fallback,
  previous-result reuse or invented zero prediction.
- Positive firing but zero integrated Mamdani area raises `UndefinedResultError`.
  Exceeded quadrature depth propagates `CentroidConvergenceError`.
- Sugeno non-finite intermediate arithmetic raises `NumericalError`; invalid
  finite output coordinates raise `InvalidDomainError`. Callback errors retain
  their original exceptions. Binary64 round-off and underflow remain explicit
  numerical limitations; this engine does not promise exact symbolic results.

## Independent reference cases

Let input $x\in[0,1]$ have terms $\mu_L(x)=1-x$ and $\mu_H(x)=x$.
At $x=1/4$ and unit rule weights, firing strengths are $(3/4,1/4)$.
For Mamdani, use output sets $\mu_{B_L}(y)=1-y$ and $\mu_{B_H}(y)=y$,
minimum activation and maximum aggregation on $[0,1]$:

$$
\mu_{\rm out}(y)=
\begin{cases}
3/4,&0\le y\le1/4,\\
1-y,&1/4<y<3/4,\\
1/4,&3/4\le y\le1.
\end{cases}
$$

The area is $1/2$, first moment is $37/192$ and centroid is $37/96$.
For zero-order Sugeno consequences $(1/5,4/5)$, the output is $7/20$.
For affine consequences $(x/2,1/2+x/2)$, it is $1/4$.
These different answers illustrate different output models, not disagreement
between equivalent algorithms. Tests also cover product activation, sum
aggregation, contradictory and repeated rules, endpoint/no-fire cases,
overflow, invalid models and numerical nonconvergence.

## Output

A dependency-free `fuzzyroutines.inference` public module, typed reusable
models, executable monitoring example, and EN/RU/zh-CN guide with reproducible
stage plots. Neural integrations may reuse fixed parameters but trainable
Sugeno models remain a separate research contract.
