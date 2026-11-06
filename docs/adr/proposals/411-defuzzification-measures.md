<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Defuzzification measures and maximum ties

- Status: Proposed for 2.2
- Task: [#411](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/411)
- Feature: [#366](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/366)
- Builds on: [ADR-0001](../0001-backward-compatibility-contract.md), [ADR-0002](../0002-universe-support-semantics.md), and [ADR-0005](../0005-numerical-defuzzification-policy.md)

## Decision

Use an explicit discrete operation for finite output universes. Keep the
continuous centroid's signature, dispatch, errors and default selection under
ADR-0005. New continuous methods require an explicit finite closed integration
domain contained in the continuous universe. A sample grid supplies data for
an explicitly sampled model and never changes the measure of an existing
continuous model. The historical Universal Fuzzy Scale and legacy Defuz()
retain their existing contracts.

### Discrete output

For increasing declared coordinates x_i and validated grades g_i, assign
mass g_i to x_i. The centroid is sum(x_i g_i) / sum(g_i). Coordinate
spacing affects the moment through x_i and contributes no width factors.
A centroid may lie between declared coordinates. Callers needing a declared
coordinate can choose the discrete bisector or one of the endpoint maxima.

Define the discrete bisector as the first coordinate whose cumulative mass
is at least half the total. An atom may straddle half the mass. If the
cumulative sum reaches half exactly and stays there through a gap, the
selected coordinate is the atom where it first reached half.

Find the maximum grade on the selected coordinates. Smallest and largest of
maxima return the corresponding extreme coordinates. Mean of maxima is the
unweighted arithmetic mean of all maximum-grade coordinates. This mean can
fall outside the maximizer set or between universe coordinates. Ties use
numeric equality and have no implicit tolerance.

A separately supplied subset, if supported by the implementation API, must
be nonempty, explicitly named and validated as a subset of the universe.
No interval clipping, interpolation, quadrature or implicit sampling occurs.

### Continuous output

Use membership as a density with respect to coordinate length. The
centroid and bisector use the positive integrated area over the declared
domain. The bisector is the leftmost coordinate where cumulative area reaches
half. This rule selects the start of a zero-area gap when the left component
contains exactly half the total. Truncation changes the area, moment and
maximizers because all three are computed on the declared domain.

Smallest and largest of maxima are the least and greatest points where the
domain's maximum grade is attained. If all maximizers are isolated, mean of
maxima is their unweighted arithmetic mean. If maximal plateaus have positive
total length, mean of maxima is the length-weighted mean of their midpoints.
Isolated points contribute zero measure in this case. Overlapping plateau
intervals must be unioned before calculating length. The mean may lie in a
gap. If the supremum is unattained, a maximum-selection result is undefined.
A method that needs a minimum or maximum of an attained set is undefined
when that extremum does not exist.

### Eligibility and errors

Discrete methods accept finite declared universes and evaluate their finite
points using existing scalar validation. Continuous bisector and maximum
selection initially accept only finite-window representations with trusted
piece geometry and a complete, finite partition into supported pieces.
A piecewise-linear model is eligible when its geometry, boundary policy and
window intersection are explicit. The implementation must state which
built-ins and composed models have complete geometry for each method.
Continuous bisector may solve a piece integral analytically or use a bounded
root solver inside an already identified piece. Plateaus and equal maxima
require proof from the supported representation. A dense grid cannot establish
global maximum ties for an arbitrary callback. Sampled diagnostics may
report estimates under a separate explicit contract; they are deferred here.

Undefined results include an all-zero discrete grade set, zero continuous
area for centroid/bisector, and no positive attained maximum for maximum
selection. A positive isolated point can define a discrete result and a
maximum for eligible continuous geometry even when its continuous area is
zero. Invalid grades and domains use existing validation errors. Working
precision that cannot establish a cumulative comparison, a tie, or a valid
result must trigger a safe exact/reference path or an explicit numerical
failure. A fixed global epsilon would merge distinct grades and is outside
the contract.

## Analytical acceptance cases

| Case | Expected result |
| ---- | --------------- |
| Discrete points (0, 2, 10), grades (1/4, 1, 1) | Centroid 16/3; bisector 2; maxima 2, 10 and mean 6 |
| Discrete points (0, 2, 10), grades (1, 0, 1) | Half-mass tie chooses 0; maximum mean is 5 |
| Continuous grade 1 on [0, 2] and [4, 6], zero in the gap | Centroid 3; bisector 2; maxima 0, 6 and mean 3 |
| Same profile truncated to [1, 6] | Centroid 23/6; bisector 9/2; maxima 1, 6 and mean 23/6 |
| Continuous positive maximum plateaus [0, 1] and [3, 5], isolated equal peak at 9 | Maximum endpoints 0 and 9; maximum mean 17/6 |
| Positive isolated point at 2, zero elsewhere on [0, 4] | Maximum 2; centroid and bisector undefined |
| All zero or no selected mass | Undefined result, including maximum selection for all-zero grades |

For supported nonconstant pieces, add independently derived cases that locate
the bisector inside a rising segment and distinguish a continuous integral from
a sampled weighted sum. Add adversarial checks for a half-mass tie near
roundoff, invalid grades, unsupported geometry and the unchanged continuous
centroid and historical scale. Update the canonical API guide and adapt EN,
RU and zh-CN examples when the public operations land in
[#412](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/412)
and [#413](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/413).
