<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Choose how grades combine

**Question:** should two partially satisfied criteria require the weaker grade,
or should their partial satisfaction compound? The choice is a model policy.
First measure each physical quantity with its own membership function; combine
the resulting dimensionless grades. For set composition, both sets must share
the same universe.

For two grades $a,b\in[0,1]$, the illustrated policies are

$$
T_{\mathrm{minimum}}(a,b)=\min(a,b),\qquad
T_{\mathrm{product}}(a,b)=ab,
$$

$$
S_{\mathrm{maximum}}(a,b)=\max(a,b),\qquad
S_{\mathrm{algebraic}}(a,b)=a+b-ab.
$$

[![Minimum and product conjunction, maximum and algebraic disjunction, with the second grade fixed at 0.6](../assets/figures/operators.svg)](../assets/figures/operators.svg)

The horizontal coordinate varies the first grade from zero to one; the second
is fixed at 0.6. On the left, minimum saturates at 0.6 while product scales the
first grade by 0.6. On the right, maximum stays at least 0.6 while algebraic
disjunction rises continuously to one. These are explicit fuzzy policies, not
an assumption that the measurements are statistically independent.

```python
from math import isclose
from fuzzyroutines import NegationPolicy, SNormPolicy, TNormPolicy

first, second = 0.4, 0.6
assert TNormPolicy("logic").Evaluate(first, second) == 0.4
assert isclose(TNormPolicy("algebraic").Evaluate(first, second), 0.24)
assert SNormPolicy("logic").Evaluate(first, second) == 0.6
assert isclose(SNormPolicy("algebraic").Evaluate(first, second), 0.76)
assert NegationPolicy("standard").Evaluate(first) == 0.6
print(0.4, 0.24, 0.6, 0.76)
```

Standard negation is $N(a)=1-a$. A directed difference uses conjunction with
the negated second grade: for minimum conjunction,
$\mu_{A\setminus B}(x)=\min(\mu_A(x),1-\mu_B(x))$. It is not ordinary subtraction.
The [alarm scenario](alarm.md) shows the resulting curve. Boundary and drastic
alternatives, plus parametric and parabolic negations, have executable examples
in the [API recipes](api-recipes.md#choose-scalar-operator-families-deliberately).

**Use in your project:** retain the selected policy with your model and compare
intermediate grades before changing it. A product can lower an AND result
substantially; that does not mean the implementation is slower or less accurate.
The choice expresses how partial compatibility should combine.
