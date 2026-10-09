<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Choose a membership family

Choose the curve from the meaning of the concept: a tolerance band, a smooth
transition, a central preference, or a monotone tail. The factories return
immutable `MembershipFunction` objects; they do not fit parameters to data.
All coordinates and parameters must satisfy the documented finite real
contracts. Booleans are not accepted as numbers.

![Eight membership families evaluated by the scalar API](../assets/figures/membership-families.svg)

Each curve displays 401 observations over −3 to 3. The displayed interval is
not a claim about mathematical support. Gaussian, logistic, desirability, and
hyperbolic tails extend beyond it. Numerical underflow at a distant coordinate
does not redefine an analytical family's positive support.

## Hyperbolic: saturation followed by a decreasing tail

`Hyperbolic(scale, exponent, cutoff)` is one at and below `cutoff` and decreases
after it. Positive scale and exponent determine the tail. For an illustrative
penalty, use `Hyperbolic(1, 2, 0)`; at coordinate 1 its grade is 0.5.

## Bell: a smooth finite tolerance band

`Bell(left, plateauStart, plateauEnd)` has quadratic shoulders and a flat
plateau. Its right foot is `plateauEnd + plateauStart - left`; it is not a
Gaussian. For `Bell(-2, -1, 1)`, the plateau is [−1, 1] and the right foot is 2.

## S-shoulder: a smooth transition to saturation

`SShoulder(left, right)` is zero at and below `left`, one at and above `right`,
and quadratic between. Its midpoint grade is 0.5. Use it when an increasing
quantity gradually becomes fully compatible with a concept.

## Triangle: a preferred value with linear tolerance

`Triangle(left, peak, right)` uses the conventional left–peak–right order.
`left < peak <= right`; a peak at the right endpoint is supported. A symmetric
triangle is convenient for a preferred setting, but asymmetric tolerances are
equally valid. The quality scenario uses `Triangle(10, 12, 14)`.

## Trapezoid: a fully acceptable interval

`Trapezoid(left, plateauStart, plateauEnd, right)` has linear shoulders and a
grade-one interval. `plateauStart == plateauEnd` is permitted. Use it when a
range of settings is equally acceptable, rather than one preferred point.

## Gaussian: smooth preference around a center

`Gaussian(center, scale)` evaluates the unnormalized membership curve

$$
\mu(x)=\exp\left[-\frac12\left(\frac{x-\mathrm{center}}{\mathrm{scale}}\right)^2\right].
$$

The scale is positive and the peak is one. This is a membership function, not
a probability-density normalization; its area is not constrained to one.

## Logistic: a monotone sigmoid

`Logistic(slope, midpoint)` has grade 0.5 at its midpoint. The slope must be
nonzero: positive slopes increase, negative slopes decrease. No finite
coordinate reaches the mathematical limiting grades zero or one, although
floating-point evaluation can round or underflow to an endpoint.

## Harrington desirability: a fixed asymmetric sigmoid

`HarringtonDesirability()` has no parameters and evaluates

$$
\mu(x)=\exp[-\exp(-x)].
$$

Its input is a dimensionless transformed desirability coordinate. Define that
transformation in your model before passing a physical measurement. At zero
its grade is $\exp(-1)$, approximately 0.367879.

## Execute every family and inspect an immutable definition

```python
from math import exp, isclose
from fuzzyroutines import (
    Bell, Gaussian, HarringtonDesirability, Hyperbolic, Logistic,
    MembershipFunction, SShoulder, Trapezoid, Triangle,
)

assert Hyperbolic(1, 2, 0)(1) == 0.5
assert Bell(-2, -1, 1)(0) == 1
assert SShoulder(-2, 2)(0) == 0.5
assert Triangle(-2, 0, 2)(0) == 1
assert Trapezoid(-2, -1, 1, 2)(0) == 1
assert Gaussian(0, 1)(0) == 1
assert Logistic(2, 0)(0) == 0.5
assert isclose(HarringtonDesirability()(0), exp(-1))
definition = MembershipFunction("triangle", left=-2, peak=0, right=2)
assert definition.Evaluate(0) == definition(0) == 1
assert definition.family == "triangle" and definition.parameters["peak"] == 0
print(definition.family, dict(definition.parameters))
```

Factory functions are the easiest entry point. The generic constructor requires
the exact canonical family identifier and parameter names, including
`"s_shoulder"` and `"harrington_desirability"`. Those string values are data,
not Python declaration names. See the
[membership API](../api/modern/membership.md) for all validity constraints.

For a model these families cannot express, use a
[typed custom evaluator](custom.md). Continuous exact properties require
analytical evidence; an arbitrary callable does not gain such evidence simply
by resembling a familiar curve.
