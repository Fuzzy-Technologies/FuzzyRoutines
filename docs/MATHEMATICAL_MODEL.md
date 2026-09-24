<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Canonical Mathematical Model

This document is the entry point for the mathematical contract implemented by
FuzzyRoutines. It defines the shared vocabulary, records the formulas exposed
by the current public surfaces, and links each topic to its detailed contract
and executable evidence. The detailed pages remain authoritative for numerical
algorithms, compatibility exceptions, and proof boundaries.

The model is one-dimensional and scalar. Multidimensional fuzzy sets,
type-2 fuzzy sets, symbolic algebra, and implicit interpolation are outside the
current contract.

## Contract and evidence hierarchy

When sources appear to disagree, use this order:

1. accepted architecture decisions define the intended contract;
2. this document states the integrated mathematical model;
3. focused mathematics pages define topic-specific details and evidence limits;
4. public docstrings describe callable behavior;
5. executable tests prove the behavior of the current implementation.

The [current implementation status](current-status.md) distinguishes accepted
design from shipped behavior. The
[historical compatibility contract](compatibility/legacy-public-api-1.0.3.md)
protects existing names and signatures; it does not make historical terminology
mathematically canonical.

## Scalar fuzzy set and domains

A scalar fuzzy set is the ordered pair

$$
A=(X,\mu_A), \qquad \mu_A:X\to[0,1],
$$

where $X$ is an explicitly declared `ContinuousUniverse` or
`DiscreteUniverse`. Coordinates and grades are finite real scalars. Boolean,
non-finite, and out-of-range grades are rejected rather than coerced.

The following concepts are distinct:

| Concept              | Definition                                                       | Current representation                                      |
|----------------------|------------------------------------------------------------------|-------------------------------------------------------------|
| Universe             | Coordinates on which $\mu_A$ defines $A$                         | `ContinuousUniverse` or `DiscreteUniverse`                  |
| Integration domain   | Finite closed interval used by one numerical operation           | `IntegrationDomain`                                         |
| Positive support     | $\{x\in X\mid\mu_A(x)>0\}$                                       | Exact region or explicit sampled evidence                   |
| Support closure      | Closure of positive support relative to $X$                      | Exact region for supported representations                  |
| Core                 | $\{x\in X\mid\mu_A(x)=1\}$                                       | Exact region for supported representations                  |
| Boundary             | $\{x\in X\mid0<\mu_A(x)<1\}$                                     | Fuzzy transition region, not topological boundary           |
| Height               | $\sup\{\mu_A(x)\mid x\in X\}$                                    | Exact scalar only when the representation supports proof    |

An integration domain is never inferred to be support. In particular, the
historical `FuzzySet.supportSet` tuple is a compatibility spelling for a finite
integration interval. Exact and sampled property semantics are specified in
the [universe and support contract](mathematics/universe-support-contract.md)
and [ADR-0002](adr/0002-universe-support-semantics.md).

## Membership-function families

`MFunction` is the historical analytical-family registry. Let
$S_{a,b}$ denote the quadratic increasing shoulder

$$
S_{a,b}(x)=
\begin{cases}
0, & x\le a,\\
2\left(\dfrac{x-a}{b-a}\right)^2, & a<x\le\dfrac{a+b}{2},\\
1-2\left(\dfrac{x-b}{b-a}\right)^2, & \dfrac{a+b}{2}<x<b,\\
1, & x\ge b.
\end{cases}
$$

The triangle and trapezium families use the protected historical parameter
order even though their geometric breakpoint order is different:

$$
\operatorname{Tri}_{a,c,b}(x)=
\begin{cases}
0, & x\le a,\\
\dfrac{x-a}{c-a}, & a<x\le c,\\
\dfrac{b-x}{b-c}, & c<x\le b,\\
0, & x>b,
\end{cases}
$$

and

$$
\operatorname{Trap}_{a,c,d,b}(x)=
\begin{cases}
0, & x\le a,\\
\dfrac{x-a}{c-a}, & a<x<c,\\
1, & c\le x\le d,\\
\dfrac{b-x}{b-d}, & d<x\le b,\\
0, & x>b.
\end{cases}
$$

Every stored membership parameter is a finite built-in `int` or `float`;
Boolean values are rejected even though Python treats them as integers. The
family-specific constraints below are additional to that blanket scalar
contract. `desirability` stores no parameters, but its evaluation coordinate
must still be a finite built-in scalar.

The implemented families are:

| Historical identifier   | Mathematical function                                                                    | Valid parameters                                        | Exact aliases               |
|-------------------------|------------------------------------------------------------------------------------------|---------------------------------------------------------|-----------------------------|
| `hyperbolic`            | $1$ for $x\le c$; otherwise $1/(1+(a(x-c))^b)$                                           | $a>0$, $b>0$, finite $c$                                | None                        |
| `bell`                  | $S_{a,b}(x)$ for $x<b$; $1$ on $[b,c]$; $1-S_{c,c+b-a}(x)$ after $c$                     | $a<b\le c$                                              | None                        |
| `parabolic`             | $S_{a,b}(x)$                                                                             | $a<b$                                                   | `sShoulder`                 |
| `triangle`              | $\operatorname{Tri}_{a,c,b}(x)$                                                          | $a<c\le b$; legacy order is `a, b, c`                   | None                        |
| `trapezium`             | $\operatorname{Trap}_{a,c,d,b}(x)$                                                       | $a<c\le d<b$; legacy order is `a, b, c, d`              | None                        |
| `exponential`           | $\exp\!\left[-\tfrac12((x-a)/b)^2\right]$                                                | finite $a$, $b>0$                                       | `gaussian`                  |
| `sigmoidal`             | $1/(1+\exp[-a(x-b)])$                                                                    | $a\ne0$, finite $b$                                     | `logistic`                  |
| `desirability`          | $\exp[-\exp(-y)]$                                                                        | finite $y$; no stored parameters                        | `harringtonDesirability`    |

The exact piecewise triangle and trapezium equations, numerical branches, and
historical parameter order are frozen by the
[membership-function contract](mathematics/membership-function-contracts.md).
The legacy `bell` is a flat-top piecewise-quadratic family, not the generalized
bell commonly used in other libraries. Registry aliases share the same
implementation; they are not new families or permission to rename protected
parameters.

## Negations

Every negation maps $[0,1]$ to $[0,1]$. The modern set API requires an explicit
`NegationPolicy`; it has no process-wide default.

The standard complement is

$$
N(x)=1-x.
$$

The historical parametric strong negation has fixed point
$\alpha\in(0,1)$:

$$
N_\alpha(x)=
\begin{cases}
1+x\dfrac{\alpha-1}{\alpha}, & x\le\alpha,\\
(x-1)\dfrac{\alpha}{\alpha-1}, & x>\alpha.
\end{cases}
$$

The parabolic family is the valid branch of

$$
2\alpha-x-y=(2\alpha-1)(y-x)^2,
\qquad \alpha\in\left[\frac14,\frac34\right].
$$

With $D=1-8(2\alpha-1)(x-\alpha)$, the cancellation-resistant branch is

$$
N_\alpha(x)=x+\frac{4(\alpha-x)}{1+\sqrt{D}}.
$$

It satisfies $N(0)=1$, $N(1)=0$, $N(\alpha)=\alpha$, monotone decrease, and
involution on its accepted domain. The `epsilon` argument retained by
`FuzzyNOTParabolic` is compatibility-only and does not control the analytical
algorithm. See the [derivation](mathematics/parabolic-negation-derivation.md)
and [ADR-0004](adr/0004-operator-and-negation-contracts.md).

## T-norms and s-norms

For $x,y\in[0,1]$, the public scalar operators and modern policy values expose
four dual families:

| Family        | T-norm $T(x,y)$                                       | S-norm $S(x,y)$                                      |
|---------------|-------------------------------------------------------|------------------------------------------------------|
| `logic`       | $\min(x,y)$                                           | $\max(x,y)$                                          |
| `algebraic`   | $xy$                                                  | $x+y-xy$                                             |
| `boundary`    | $\max(x+y-1,0)$                                       | $\min(x+y,1)$                                        |
| `drastic`     | $y$ if $x=1$; $x$ if $y=1$; otherwise $0$             | $y$ if $x=0$; $x$ if $y=0$; otherwise $1$            |

The historical spelling is `SCoNorm`; the modern set policy is `SNormPolicy`.
Composition validates every operand before folding. The executable suite
checks closure, commutativity, associativity, identities, and both De Morgan
laws under standard negation.

## Fuzzy-set algebra

All modern binary operations require exactly equal universes. They never infer
a resampling grid, coordinate conversion, or universe reconciliation.

For sets $A$ and $B$ over the same universe:

$$
\begin{aligned}
\mu_{\neg A}(x) &= N(\mu_A(x)),\\
\mu_{A\cap B}(x) &= T(\mu_A(x),\mu_B(x)),\\
\mu_{A\cup B}(x) &= S(\mu_A(x),\mu_B(x)),\\
\mu_{A\setminus B}(x) &= T(\mu_A(x),N(\mu_B(x))).
\end{aligned}
$$

Difference is directed. Under general fuzzy grades,
$A\setminus A$ is not required to be empty. Symmetric difference is not yet a
public contract because it additionally requires an explicit s-norm and an
accepted composition policy. See
[explicit fuzzy-set operations](mathematics/fuzzy-set-operations.md).

Mathematical equality and inclusion are also explicit operations:

$$
\begin{aligned}
A=B &\iff \forall x\in X:\mu_A(x)=\mu_B(x),\\
A\subseteq B &\iff \forall x\in X:\mu_A(x)\le\mu_B(x).
\end{aligned}
$$

Discrete universes are checked exhaustively. Continuous arbitrary callables
require a declared finite `ComparisonDomain`, so a positive result is evidence
only on those coordinates, not a proof of global functional equality. Exact
and tolerance policies are never implicit. See
[equality and inclusion](mathematics/fuzzy-set-relations.md).

## Alpha-cuts, height, normalization, and convexity

FuzzyRoutines uses weak alpha-cuts:

$$
A_\alpha=\{x\in X\mid\mu_A(x)\ge\alpha\},
\qquad \alpha\in[0,1].
$$

Therefore $A_0=X$, $A_1$ is the core, and
$A_\beta\subseteq A_\alpha$ whenever $0\le\alpha\le\beta\le1$.
`AlphaCut` is exact for a declared finite `DiscreteUniverse`.
`SampleAlphaCut` records a finite continuous grid and always reports
`isExact == False`; its result is not continuous geometry.

For exact positive height $h(A)$, normalization is

$$
\mu_{\operatorname{Normalize}(A)}(x)=\frac{\mu_A(x)}{h(A)}.
$$

Zero height is rejected. Exact height is available for exhaustive discrete
sets and supported analytical continuous families; arbitrary continuous
callables fail closed rather than using a sampled maximum as proof. See the
[alpha-cut contract](mathematics/alpha-cuts.md) and
[normalization contract](mathematics/fuzzy-set-normalization.md).

The accepted one-dimensional convexity definition is quasiconcavity:

$$
\mu_A(\lambda x+(1-\lambda)y)
\ge\min(\mu_A(x),\mu_A(y)),
\qquad \lambda\in[0,1].
$$

Equivalently, every positive weak alpha-cut is convex. This definition is
accepted by [ADR-0009](adr/0009-fuzzy-set-convexity-semantics.md), but the
public convexity query and evidence-result API are **not implemented**. A
finite continuous grid can expose a counterexample; absence of a sampled
violation cannot prove global convexity. See the
[convexity design contract](mathematics/fuzzy-set-convexity.md).

## Linguistic terms and scales

The modern representation associates an exact non-empty name with one
`ScalarFuzzySet`:

$$
L=(\text{name},A).
$$

`LinguisticScale` stores a non-empty ordered tuple of uniquely named
`LinguisticTerm` values. Tuple order is data. The current type deliberately
does not define lookup, grade comparison, tie-breaking, or fuzzification.

The historical mutable `FuzzyScale.levels` list remains available as a
compatibility surface. Its existing `Fuzzy()` lookup behavior is not silently
promoted into the typed model. See the
[linguistic-term representation](mathematics/linguistic-term-model.md).

## Centroid defuzzification

For a continuous fuzzy set and explicit finite integration domain
$D=[l,r]$, the implemented centroid is

$$
C(A,D)=
\frac{\int_l^r x\mu_A(x)\,\mathrm{d}x}
     {\int_l^r \mu_A(x)\,\mathrm{d}x}.
$$

Polynomial families use analytical moments. Gaussian membership uses stable
closed forms when the finite area is resolvable. Other `MFunction` families
and generic callables use deterministic adaptive Simpson integration with an
explicit `CentroidPolicy`. A zero or non-finite area raises `ValueError`, and
exhausted adaptive work raises `CentroidConvergenceError`; no best-so-far or
fixed-grid estimate is returned as a converged result.

The compatibility method `FuzzySet.Defuz()` and the `defuzValue` property
delegate to this strategy on every access. They observe current parameters and
current `supportSet` integration bounds without a retained centroid cache. See the
[centroid contract](mathematics/centroid-defuzzification.md) and
[ADR-0005](adr/0005-numerical-defuzzification-policy.md).

## Implementation boundary

| Capability                                    | Status                      | Contract or evidence                                                                   |
|-----------------------------------------------|-----------------------------|----------------------------------------------------------------------------------------|
| Explicit continuous and discrete universes    | Implemented                 | [Universe and support](mathematics/universe-support-contract.md)                       |
| Historical analytical membership registry     | Implemented and protected   | [Membership functions](mathematics/membership-function-contracts.md)                   |
| Explicit negation, t-norm, and s-norm policy  | Implemented                 | [ADR-0004](adr/0004-operator-and-negation-contracts.md)                                |
| Complement, intersection, union, difference   | Implemented                 | [Fuzzy-set operations](mathematics/fuzzy-set-operations.md)                            |
| Equality and inclusion                        | Implemented                 | [Relations](mathematics/fuzzy-set-relations.md)                                        |
| Exact discrete and sampled continuous cuts    | Implemented                 | [Alpha-cuts](mathematics/alpha-cuts.md)                                                |
| Height and normalization                      | Implemented                 | [Normalization](mathematics/fuzzy-set-normalization.md)                                |
| Typed linguistic representation               | Implemented                 | [Linguistic terms](mathematics/linguistic-term-model.md)                               |
| Analytical and adaptive centroid              | Implemented                 | [Centroid defuzzification](mathematics/centroid-defuzzification.md)                    |
| Executable convexity result API               | Roadmap                     | [Accepted design](mathematics/fuzzy-set-convexity.md)                                  |
| Typed linguistic lookup and fuzzification     | Roadmap                     | [Current status](current-status.md#still-in-the-v2-roadmap)                            |
| Symmetric difference                          | Unsupported                 | [ADR-0008](adr/0008-fuzzy-set-difference-semantics.md)                                 |
| Multidimensional or type-2 fuzzy sets         | Out of scope                | Requires a separate architecture decision                                              |

## Detailed contract index

| Topic                          | Canonical detail                                                                            |
|--------------------------------|---------------------------------------------------------------------------------------------|
| Finite scalar values           | [Finite-number policy](mathematics/finite-number-policy.md)                                 |
| Numerical tolerances           | [Numerical edge policy](mathematics/numerical-edge-policy.md)                               |
| Domains and derived geometry   | [Universe and support](mathematics/universe-support-contract.md)                            |
| Membership families            | [Formula and parameter contracts](mathematics/membership-function-contracts.md)             |
| Stable numerical branches      | [Source formula and algorithm invariants](mathematics/source-algorithm-invariants.md)       |
| Negations                      | [Parabolic derivation](mathematics/parabolic-negation-derivation.md)                        |
| Set operations                 | [Complement, intersection, union, and difference](mathematics/fuzzy-set-operations.md)      |
| Relations                      | [Equality and inclusion](mathematics/fuzzy-set-relations.md)                                |
| Alpha-cuts                     | [Exact and sampled alpha-cuts](mathematics/alpha-cuts.md)                                   |
| Height and normalization       | [Fuzzy-set normalization](mathematics/fuzzy-set-normalization.md)                           |
| Convexity                      | [Fuzzy-set convexity](mathematics/fuzzy-set-convexity.md)                                   |
| Linguistic model               | [Typed linguistic-term representation](mathematics/linguistic-term-model.md)                |
| Defuzzification                | [Centroid defuzzification](mathematics/centroid-defuzzification.md)                         |
| Compatibility                  | [Historical-to-modern migration](migration/historical-to-modern.md)                         |

## License

This documentation is licensed under the
[Apache License 2.0](../LICENSE). Redistributions must preserve the license,
copyright, and attribution notices described in [NOTICE](../NOTICE).
