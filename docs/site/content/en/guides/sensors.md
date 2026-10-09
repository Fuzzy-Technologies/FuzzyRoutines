<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Combine two sensor criteria

**Question:** how strongly do an 80 °C temperature and 10 mm/s vibration
satisfy two illustrative warning criteria? Convert each physical measurement to
its own dimensionless grade before combining them. The model does not infer a
failure probability.

```python
from fuzzyroutines import SNormPolicy, SShoulder, TNormPolicy, Triangle

temperatureGrade = SShoulder(60, 100)(80)
vibrationGrade = Triangle(0, 8, 16)(10)
minimumAnd = TNormPolicy("logic").Evaluate(temperatureGrade, vibrationGrade)
productAnd = TNormPolicy("algebraic").Evaluate(temperatureGrade, vibrationGrade)
maximumOr = SNormPolicy("logic").Evaluate(temperatureGrade, vibrationGrade)
algebraicOr = SNormPolicy("algebraic").Evaluate(temperatureGrade, vibrationGrade)
assert (temperatureGrade, vibrationGrade) == (0.5, 0.75)
assert (minimumAnd, productAnd, maximumOr, algebraicOr) == (0.5, 0.375, 0.75, 0.875)
print(minimumAnd, productAnd, maximumOr, algebraicOr)
```

[![Two input grades and four explicitly selected combination results](../assets/figures/sensors.svg)](../assets/figures/sensors.svg)

Minimum conjunction retains the weaker grade: $\min(0.5,0.75)=0.5$.
Product conjunction gives $0.5\times0.75=0.375$. Maximum disjunction gives
0.75; algebraic disjunction gives

$$
0.5+0.75-0.5\times0.75=0.875.
$$

These are different fuzzy operator choices, not competing performance modes.
Using a product T-norm does not establish probabilistic independence.

**Engineering check:** the inputs have different units and universes, so use
scalar policy `Evaluate` here. Set-level `Intersection` and `Union` require
sets on the same universe. A full temperature–vibration rule base would need
an explicitly defined multivariate inference layer, which this example does
not implement.

**Use in your project:** record the chosen policy alongside the criterion
thresholds. The four values show why changing a policy can change a downstream
decision even when the measurements remain identical.

```bash
python -I examples/guide.py --scenario sensors
```

Continue with [maintenance warning zones](alarm.md).
