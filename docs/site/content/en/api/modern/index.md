<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Modern API

The root [`fuzzyroutines`][fuzzyroutines] package re-exports the recommended
public symbols. Module pages preserve their architectural ownership and expose
stable fully qualified anchors:

| Module                                      | Responsibility                                              |
|---------------------------------------------|-------------------------------------------------------------|
| [`alphacuts`](alphacuts.md)                 | Exact discrete and sampled continuous alpha-cuts            |
| [`domain`](domain.md)                       | Declared universes and finite integration domains           |
| [`fuzzysets`](fuzzysets.md)                 | Scalar fuzzy sets, operators, policies, and normalization   |
| [`linguistic`](linguistic.md)               | Immutable linguistic terms and ordered scales               |
| [`properties`](properties.md)               | Exact or sampled support, core, boundary, and height        |
| [`relations`](relations.md)                 | Domain-explicit equality and inclusion comparisons          |

Use [package exports](package.md) for the authoritative root import surface.
