<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Centroids and numerical accuracy

**Question:** how can we replace a continuous fuzzy profile with one
representative coordinate, and verify the number independently?

For a finite integration domain $[a,b]$ with positive membership area,

$$
c=\frac{\int_a^b x\mu(x)\,\mathrm{d}x}{\int_a^b \mu(x)\,\mathrm{d}x}.
$$

```python
from math import isclose
from fuzzyroutines import (
    Centroid, ContinuousUniverse, IntegrationDomain,
    ScalarFuzzySet, SNormPolicy, Triangle, Union,
)

universe = ContinuousUniverse(0, 8, leftClosed=True, rightClosed=True)
triangle = ScalarFuzzySet(universe, Triangle(0, 2, 8))
centroid = Centroid(triangle, IntegrationDomain(0, 8))
assert isclose(centroid, (0 + 2 + 8) / 3, abs_tol=1e-12)

combinedUniverse = ContinuousUniverse(0, 10, leftClosed=True, rightClosed=True)
left = ScalarFuzzySet(combinedUniverse, Triangle(0, 1, 3))
right = ScalarFuzzySet(combinedUniverse, Triangle(4, 6, 10))
combined = Union(left, right, SNormPolicy("logic"))
combinedCentroid = Centroid(combined, IntegrationDomain(0, 10))
assert isclose(combinedCentroid, 44 / 9, abs_tol=1e-9, rel_tol=1e-9)
print(centroid, combinedCentroid)
```

For the first triangle, the geometric centroid is
$(0+2+8)/3=10/3\approx3.333333$. This is an independent analytical oracle.
The library uses analytical moments for the recognized triangular family.

![Triangle centroid and a separate four-point trapezoidal approximation](../assets/figures/centroid.svg)

The cyan dashed line joins four user-side samples at
$0,8/3,16/3,8$, whose grades are $0,8/9,4/9,0$. Applying the trapezoidal rule
separately to area and first moment gives

$$
A_4=\frac{32}{9},\qquad M_4=\frac{1024}{81},\qquad
c_4=\frac{M_4}{A_4}=\frac{32}{9}\approx3.555556.
$$

The absolute difference is $c_4-c=2/9$; the relative difference is
$(c_4-c)/c=1/15$, about 6.67%. The executable scenario implements this
calculation explicitly. **Library `Centroid` does not use that fixed grid.**
The picture shows why a coarse sampled representation can change a result.

For the two disjoint triangles, areas are $3/2$ and $3$, while their
centroids are $4/3$ and $20/3$. Because their positive supports are
disjoint, maximum union adds their area moments without overlap correction:

$$
c=\frac{(3/2)(4/3)+3(20/3)}{3/2+3}=\frac{44}{9}\approx4.888889.
$$

The composed callable uses adaptive quadrature. Its observed result agrees
with this oracle within the asserted $10^{-9}$ tolerance.

**Engineering checks:** an integration domain must lie within the continuous
universe. Zero area raises `UndefinedResultError`. Exhausting the adaptive
depth raises `CentroidConvergenceError`, rather than returning a silent fallback.
The policy's tolerances govern moment integration; they are not a proven
absolute bound on centroid-coordinate error. Generic functions must be
sufficiently regular: narrow features missed by quadrature cannot be ruled out
by finite evaluation alone. Choose domain and model accordingly.

**Use in your project:** record units, finite integration limits, policy, and
an independent reference when a representative coordinate influences a
decision. Truncating a curve changes the centroid being requested.

```bash
python -I examples/guide.py --scenario centroid
```

Continue with [scale auditing](scale-audit.md).
