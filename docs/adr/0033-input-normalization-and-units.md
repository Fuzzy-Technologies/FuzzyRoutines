<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0033: Explicit input normalization and units

- Status: Proposed
- Date: 2026-11-06
- Related Task: [#403](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/403)
- Related Feature: [#363](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/363)

## Context

A measurement and the coordinate used to evaluate its linguistic scale may
have different units and bounds. For example, an application can map an
operating temperature in degrees Celsius to the historical scale's closed
$[0,1]$ universe. The application owns the operating range. The scale owns the
membership functions and selection policy.

## Decision

Use an immutable affine mapping defined by four finite bounds and two unit
labels. Let $a<b$ be the closed source bounds and $c<d$ the closed target
bounds. Both unit labels are nonblank, case-sensitive strings. Declare
dimensionless coordinates with the unit label `1`. A caller supplies an
observation in the declared source unit. An observation in a different unit
requires an explicit conversion at the caller boundary.

When a mapping is bound to a model input, its target bounds must equal the
bounds of the input scale's finite closed continuous universe. The mapping
accepts finite binary64 values and integers exactly representable as binary64.
Reject booleans, numeric strings, nonfinite values and integers that lose
precision on conversion. Reject equal or reversed bounds during construction.
At evaluation, report a missing observation separately from an invalid
number. Reject observations outside the source interval, including the first
representable value beyond either endpoint. A caller can apply an explicit
missing-value policy before invoking the mapping.

For an admitted source observation $x$ and an admitted target coordinate
$y$, the forward and inverse maps are

$$
y=c+(d-c)\frac{x-a}{b-a},\qquad
x=a+(b-a)\frac{y-c}{d-c}.
$$

The inverse applies the same missing-value, numeric, and bounds checks to
the target coordinate. Each endpoint maps directly to its corresponding
declared endpoint, retaining its stored representation. The exact map is
strictly increasing and bijective between the two closed intervals. Evaluate
the interior expression over exact ratios of the admitted values, then round
the result once to nearest binary64 with ties to even. In particular, extreme
finite bounds can have a span larger than the largest binary64 value and
still define a valid mapping. Binary64 rounding preserves nondecreasing
order, and adjacent inputs can share one mapped coordinate. Inverse
round-trips after rounding therefore have precision limits that depend on
both ranges. The exact map has inverse sensitivity $(b-a)/(d-c)$, which
determines how forward rounding error scales in source units.

### Analytical examples

- **Temperature.** Map $[10,50]$ °C to $[0,1]$. At $30$ °C the target
  coordinate is $1/2$, and inverse evaluation at $1/2$ returns $30$ °C.
- **Load.** Map $[0,80]$ kN to a scale on $[-1,1]$. At $60$ kN the target
  coordinate is $1/2$, and inverse evaluation at $1/2$ returns $60$ kN.
- **Risk score.** Map $[200,1000]$ points to $[0,1]$. At $400$ points the
  target coordinate is $1/4$, and inverse evaluation at $1/4$ returns
  $400$ points. The target coordinate is a model input with unit `1`.

Each displayed coordinate and inverse result is exactly representable in
binary64. The examples specify application ranges independently of
membership shapes and inference.

### Project configuration

[ADR-0021](0021-versioned-project-configuration.md) defines v1 presentation
units as labels and scenario inputs as model coordinates. A caller can
evaluate the mapping explicitly before writing a v1 scenario and record the
physical bounds and units in its own application. A future project
representation needs a separate schema decision with an explicit binding
to a model input, validated bounds, both unit labels, and a defined place
for physical observations. The v1 representation retains its current
meaning. The original historical-scale coefficients, centroid windows, and
selection behavior remain governed by
[ADR-0016](0016-linguistic-encodings-and-historical-preset.md) and the
[2.x compatibility contract](0001-backward-compatibility-contract.md).

## Output

This proposal specifies the numerical and configuration boundary. The
implementation should verify the three analytical examples, endpoint and
inverse endpoint behavior, adjacent out-of-range values, extreme finite
spans, and the distinct missing-value and invalid-number outcomes. An
installed example should demonstrate how a physical observation becomes
the coordinate evaluated by the existing scale API.
