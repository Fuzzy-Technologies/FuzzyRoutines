<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines API reference

![FuzzyRoutines](assets/brand/fuzzyroutines-horizontal.svg){ .fr-brand-lockup }

This is the canonical English reference for the installed FuzzyRoutines
package. It is generated from Python annotations and English Google-style
docstrings using static Griffe discovery.

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

The rendered formula and qualified links above are part of the strict build
contract.
