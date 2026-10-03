<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Scalar operators

The operator module owns immutable negation, t-norm, and s-norm policies and
their scalar formulas. Existing imports from `fuzzyroutines.fuzzysets` retain
the same policy class objects. Set algebra uses these policies without global
configuration.

::: fuzzyroutines.operators
    options:
      members:
        - NegationPolicy
        - TNormPolicy
        - SNormPolicy
