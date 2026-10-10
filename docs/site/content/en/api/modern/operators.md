<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Scalar operators

The operator module owns immutable negation, t-norm, and s-norm policies and
their scalar formulas. Existing imports from `fuzzyroutines.fuzzysets` retain
the same policy class objects. Set algebra uses these policies without global
configuration.

## Worked examples

[Sensor criteria](../../guides/sensors.md) compares combinations; [operator recipes](../../guides/api-recipes.md#choose-scalar-operator-families-deliberately) executes every family.
[Operator curves](../../guides/operators.md) show how the chosen policy changes
conjunction and disjunction.

::: fuzzyroutines.operators
    options:
      members:
        - NegationPolicy
        - TNormPolicy
        - SNormPolicy
