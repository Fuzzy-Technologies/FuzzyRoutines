<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines documentation

![FuzzyRoutines with Alice in the Fuzzy Technologies research laboratory](assets/brand/fuzzyroutines-alice.png){ .fr-project-art }

Start with the [quick start](quick-start.md) to install the modern API and
classify a physical measurement. The [nine worked scenarios](guides/index.md)
explain inputs, policies, calculations, expected results, and figures. Browse
the [membership gallery](guides/membership-families.md) to choose a curve, or
use the [practical API recipes](guides/api-recipes.md) for smaller operations.

Start with the [modern API](api/modern/index.md) for new code. Use the
[historical compatibility facade](api/legacy/index.md) only when maintaining
software written against FuzzyRoutines 1.0.3.

The modern API separates fuzzy sets, declared universes, alpha-cuts, derived
properties, linguistic structures, and comparison policies into explicit
modules. For example, a scalar fuzzy set is declared over a
[`ContinuousUniverse`][fuzzyroutines.domain.ContinuousUniverse] or a
[`DiscreteUniverse`][fuzzyroutines.domain.DiscreteUniverse].

A directed difference uses

$$
\mu_{A \setminus B}(x)
= T\left(\mu_A(x), N\left(\mu_B(x)\right)\right).
$$
