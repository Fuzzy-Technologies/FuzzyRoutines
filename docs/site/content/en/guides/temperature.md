<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Temperature comfort

**Question:** how compatible is a 24 °C measurement with the concepts
*Comfort* and *Warm*? Follow the self-contained
[quick start](../quick-start.md) to construct the scale and compute both grades.

On the descending side of `Triangle(16, 22, 28)`, the comfort grade is

$$
\mu_{\mathrm{Comfort}}(24)=\frac{28-24}{28-22}=\frac{2}{3}.
$$

The first half of the quadratic shoulder gives

$$
\mu_{\mathrm{Warm}}(24)=2\left(\frac{24-22}{30-22}\right)^2=\frac{1}{8}.
$$

[![Temperature model and measured membership grades](../assets/figures/temperature.svg)](../assets/figures/temperature.svg)

The strongest grade selects *Comfort*. The result does not claim that comfort
has a 66.7% probability. Both grades describe the same measurement under two
definitions. Their sum is not constrained to one.

**Engineering check:** the universe includes both endpoints, so membership at
0 and 40 °C is legal. Coordinates outside it raise a domain error. This minimal
scale leaves a low-temperature gap: both grades are zero below or at 16 °C.
Add a cold term and audit the scale if complete coverage is required.

**Use in your project:** retain the full membership vector for a dashboard or
subsequent policy calculation; use `selectedTerms` only when a single label is
useful. Do not discard a weak winning grade. The next scenario shows abstention.

```bash
python -I examples/guide.py --scenario temperature
```

Continue with [severity labels and abstention](risk.md).
