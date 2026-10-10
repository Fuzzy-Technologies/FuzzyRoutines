<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0014: Sampled Linguistic-Scale Diagnostics

- Status: Accepted on merge
- Date: 2026-09-28
- Related planning task: #85
- Related Feature: #27

## Context

A linguistic scale can classify an individual coordinate while still hiding
structural defects across its intended operating interval. Important defects
include regions with no active term, regions with several simultaneously active
terms, weak maximum membership, and failure to approximate a partition of
unity. These properties cannot be proved for arbitrary continuous membership
callables by inspecting a finite number of values.

Diagnostics must therefore expose their operational domain, grid, and
tolerances. They must also remain observational: evaluating a scale must never
retune membership-function coefficients or otherwise mutate the scale.

## Decision

`LinguisticScale.Diagnose()` accepts an explicit finite closed
`IntegrationDomain` and a `ScaleDiagnosticsPolicy`. Every term must use a
`ContinuousUniverse`, and the complete analysis domain must belong to every
term universe.

For $n\geq2$ samples on $D=[l,r]$, the endpoint-preserving grid is

$$
x_j=l+\frac{j}{n-1}(r-l), \qquad j=0,\ldots,n-1.
$$

The implementation records each ordered membership vector exactly once per
coordinate. For term $L_i$ and an explicit membership threshold
$\tau\in[0,1]$,

$$
s_{ij}=\mu_{L_i}(x_j),
\qquad
c_j=\max_i s_{ij},
\qquad
A_j=\{L_i\mid s_{ij}>\tau\}.
$$

The strict threshold produces the following classifications:

- a gap when $|A_j|=0$;
- an overlap when $|A_j|\geq2$;
- sampled coverage $c_j$ at every coordinate.

Optional partition-quality evidence uses

$$
e_j=\left|\sum_i s_{ij}-1\right|.
$$

The result exposes minimum, mean, and maximum sampled coverage; gap and overlap
fractions; maximum simultaneous active-term count; mean and maximum partition
error; and whether every sampled error is within the explicit partition
tolerance.

## Evidence boundary

The result is reproducible for the declared domain, sample count, membership
threshold, partition tolerance, term order, and membership definitions. It is
finite sampled evidence only. Absence of a sampled gap, overlap, or partition
error does not prove absence between grid coordinates.

Every membership function is evaluated exactly once per grid coordinate. The
diagnostic operation creates immutable result values and does not modify scale
terms, fuzzy sets, membership callables, or analytical coefficients.

## Consequences

- Scale defects become measurable instead of implicit.
- Threshold semantics are explicit and shared by gap and overlap detection.
- Endpoint inclusion and grid density are reproducible.
- Consumers can compare scale versions without relying on plots or hidden
  defaults.
- Discrete-universe diagnostics remain outside this operation; exhaustive
  discrete analysis can be added later under a distinct exactness contract.

## Rejected alternatives

- **Infer a domain from fuzzy-set support:** rejected because mathematical
  support and an operational analysis interval are different concepts.
- **Use an implicit epsilon:** rejected because activity and partition
  tolerances are caller policy.
- **Report only aggregate counts:** rejected because point-level membership
  evidence is required to reproduce and investigate a finding.
- **Describe finite sampling as continuous proof:** rejected because arbitrary
  callables may change between sampled coordinates.

## Acceptance and supersession

This ADR is **Accepted** on merge. Changing the grid endpoint rule, strict
activity comparison, gap or overlap definition, partition-error formula, or
sampled-evidence boundary requires a superseding decision.
