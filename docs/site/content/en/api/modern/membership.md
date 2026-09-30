<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Membership functions

The focused membership module owns the scalar analytical formulas. Its
immutable callable definitions can be passed directly to `ScalarFuzzySet`.
`Triangle` takes the conventional left, peak, right order; `Trapezoid` takes
left, plateau start, plateau end, right. Historical `MFunction` identifiers
retain their parameter conventions through explicit adapters.

::: fuzzyroutines.membership
    options:
      members:
        - MembershipFunction
        - Hyperbolic
        - Bell
        - SShoulder
        - Triangle
        - Trapezoid
        - Gaussian
        - Logistic
        - HarringtonDesirability
