<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Maintenance warning zones

**Question:** how strongly is a temperature in the warning zone while outside
the critical zone? Both models describe the same 40–120 °C universe, so they
can be composed as fuzzy sets.

```python
from fuzzyroutines import (
    Complement, ContinuousUniverse, Difference, Intersection, NegationPolicy,
    ScalarFuzzySet, SNormPolicy, SShoulder, TNormPolicy, Union,
)

universe = ContinuousUniverse(40, 120, leftClosed=True, rightClosed=True)
warning = ScalarFuzzySet(universe, SShoulder(60, 100))
critical = ScalarFuzzySet(universe, SShoulder(90, 110))
negation = NegationPolicy("standard")
conjunction = TNormPolicy("logic")
warningWithoutCritical = Difference(warning, critical, conjunction, negation)
noncritical = Complement(critical, negation)
both = Intersection(warning, critical, conjunction)
either = Union(warning, critical, SNormPolicy("logic"))
assert warning.Membership(100) == 1
assert critical.Membership(100) == 0.5
assert warningWithoutCritical.Membership(100) == 0.5
assert noncritical.Membership(100) == both.Membership(100) == 0.5
assert either.Membership(100) == 1
print(warningWithoutCritical.Membership(100))
```

![Warning, critical, and directed fuzzy difference over temperature](../assets/figures/alarm.svg)

With standard negation and minimum conjunction,

$$
\mu_{W\setminus C}(x)=\min\{\mu_W(x),1-\mu_C(x)\}.
$$

At 100 °C this is $\min(1,1-0.5)=0.5$. The difference is **directed**:
reversing warning and critical changes its meaning. It is not ordinary
subtraction, and it does not implement arithmetic on fuzzy numbers. The
composition declines to zero when the critical grade reaches one.

**Use in your project:** retain the warning and critical grades as well as the
composed result so a dashboard can explain its decision. These demonstration
thresholds need application-specific validation before operational use.

```bash
python -I examples/guide.py --scenario alarm
```

Continue with [quality alpha cuts](alpha-cuts.md).
