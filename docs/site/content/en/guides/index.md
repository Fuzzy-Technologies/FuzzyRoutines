<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Worked scenarios

Start with [installation and the temperature quick start](../quick-start.md).
Then choose the question that matches your application:

1. [Temperature comfort](temperature.md): define a physical universe and read every grade.
2. [Severity labels and abstention](risk.md): decline a weak classification.
3. [Two sensor criteria](sensors.md): combine grades from different measurements.
4. [Maintenance warning zones](alarm.md): compose sets on the same universe.
5. [Quality alpha cuts](alpha-cuts.md): distinguish exact discrete results from samples.
6. [Centroids and numerical accuracy](centroid.md): verify area moments independently.
7. [Scale audit](scale-audit.md): reveal ties, gaps, and unbalanced partitions.
8. [Custom quality model](custom.md): use a typed callable and normalize discrete data.
9. [Historical Universal Fuzzy Scale](universal-fuzzy-scale.md): preserve the five original levels and reconstruct them with the modern API.

Every scenario defines its units or score range, shows intermediate values,
and asserts an expected result. Parameters are illustrative expert choices, except for the explicitly frozen historical preset.
These examples demonstrate fuzzy calculations, not a validated controller,
trained statistical model, or complete rule-based inference engine.

## Read the mathematics consistently

For a fuzzy set $A$, the membership function maps a coordinate to a grade:

$$
\mu_A: U \longrightarrow [0,1].
$$

The **universe** $U$ declares allowed coordinates. The **positive support**
contains coordinates with strictly positive membership; it may be much smaller
than the universe. Its closure includes limit points. The **core** has grade
one. None of these terms means a probability distribution.

For two grades $a,b$, a T-norm expresses conjunction and an S-norm expresses
disjunction. Minimum/maximum and algebraic policies have different numerical
meaning. Choose them deliberately and record that choice with the model.

A weak alpha cut includes grades equal to the threshold. Exact discrete
operations inspect every declared coordinate. Continuous sampling reports
observations on a stated grid; it cannot prove what happens between points.

The continuous centroid is a ratio of area moments over an explicit finite
integration domain. Analytical formulas and adaptive integration have different
evidence and failure modes. A centroid is a representative coordinate, not an
expected value of a probability distribution unless a separate probabilistic
model justifies that interpretation.

See the [API reference](../api/index.md) for signatures, supported families,
validation rules, errors, and immutable result fields; the
[membership gallery](membership-families.md) for all eight curve families; and
[figure provenance](figures.md) for rendering and numerical limitations.

Follow the [computation paths](workflow.md) to choose classification or centroid
integration. Compare [operator policies](operators.md), inspect and reconstruct
[result records](results.md), handle [errors](errors.md), or maintain
[historical integrations](historical-recipes.md). The
[public example index](example-index.md) links every inventoried symbol to
executed usage. Open a linked SVG at full size on narrow screens.

The foundational set interpretation follows L. A. Zadeh,
[“Fuzzy sets” (1965), DOI 10.1016/S0019-9958(65)90241-X](https://doi.org/10.1016/S0019-9958(65)90241-X).
The examples and policy choices here are specific to FuzzyRoutines.
