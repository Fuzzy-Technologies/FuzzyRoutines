<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Linguistic inputs and numeric predictions

A linguistic label, a membership vector and a numeric representative carry
different information. The 2.1 `LinguisticCodec` makes those conversions explicit
without requiring a neural-network framework. It operates on one sample at a
time; convert tuples to your framework's arrays or tensors outside the core.

## Encode observations and decode predictions

For term $i$, $D_i$ is its declared centroid integration window and $\mu_i$
is its membership function. The scalar representative and full feature vector are

$$
c_i=\frac{\int_{D_i}x\mu_i(x)\,\mathrm{d}x}{\int_{D_i}\mu_i(x)\,\mathrm{d}x},
\qquad
\mathbf{g}(x)=(\mu_1(x),\ldots,\mu_N(x)).
$$

Centroids can represent input labels or training targets. They are **not network
weights**: training learns those separately. Numeric observations and predictions
must already use the scale's units. For the historical preset this is the closed
interval `[0, 1]`; application-specific normalization must be explicit and, if
fitted, learned only from the training split.

```python
from math import isclose
from fuzzyroutines import (
    CreateUniversalFuzzyScale, LinguisticCodec,
    UniversalFuzzyScaleDomains, UniversalFuzzyScalePolicy,
)

codec = LinguisticCodec(
    CreateUniversalFuzzyScale(),
    UniversalFuzzyScaleDomains(),
    UniversalFuzzyScalePolicy(),
)
assert codec.termNames == ("Min", "Low", "Med", "High", "Max")
representative = codec.EncodeLabel("Low")
assert isclose(representative, 0.285, abs_tol=1e-12)
grades = codec.EncodeMemberships(0.17)
assert 0 < sum(grades) < 0.003
prediction = codec.DecodePrediction(0.75)
assert prediction.selectedTerms[0].name == "High"
print(representative, grades, prediction.selectedTerms[0].name)
```

The output has one scalar near `0.285`, five grades in Min/Low/Med/High/Max order,
and the label `High`. At `0.17`, the small total grade is retained: it is weak
coverage, not a probability distribution to renormalize. A prediction returns
all grades and tie/no-match evidence. Use a declared `FuzzificationPolicy` to
change tie handling or abstain below a confidence threshold.

`EncodeLabel` accepts complete case-sensitive names. Unknown names raise an
error, never a zero representative. Scalar operations reject arrays, non-finite
values and coordinates outside any term universe. `AverageRepresentatives`
accepts exactly one tuple of N grades; nested vectors and implicit batch shapes
are rejected. The codec never clamps predictions or hides fitted state.

## Representative averaging and aggregate centroids

These two operations answer different questions:

$$
y_{\mathrm{rep}}=\frac{\sum_i g_i c_i}{\sum_i g_i}
\qquad\text{and}\qquad
y_{\mathrm{set}}=\frac{\int_D x\mu_{\mathrm{aggregate}}(x)\,\mathrm{d}x}
{\int_D\mu_{\mathrm{aggregate}}(x)\,\mathrm{d}x}.
$$

The first averages representative coordinates using supplied grades. The second
finds the centre of area of an explicitly constructed fuzzy set. Even grades
`(1, 1)` do not make the two results equal when term areas differ.

[![Two disjoint triangles have centres 1 and 4 and areas 1 and 2; equal-grade representative averaging gives 2.5, while the centroid of their maximum-union is 3.](../assets/figures/linguistic-encoding.svg)](../assets/figures/linguistic-encoding.svg)

```python
from math import isclose
from fuzzyroutines import (
    Centroid, ContinuousUniverse, FuzzificationPolicy, IntegrationDomain,
    LinguisticCodec, LinguisticScale, LinguisticTerm, ScalarFuzzySet,
    SNormPolicy, Triangle, Union,
)

universe = ContinuousUniverse(0, 6, leftClosed=True, rightClosed=True)
small = ScalarFuzzySet(universe, Triangle(0, 1, 2))
large = ScalarFuzzySet(universe, Triangle(2, 4, 6))
codec = LinguisticCodec(
    LinguisticScale((LinguisticTerm("Small", small), LinguisticTerm("Large", large))),
    (IntegrationDomain(0, 2), IntegrationDomain(2, 6)),
    FuzzificationPolicy(),
)
representative = codec.AverageRepresentatives((1, 1))
aggregate = Union(small, large, SNormPolicy("logic"))
aggregateCentroid = Centroid(aggregate, IntegrationDomain(0, 6))
assert representative == 2.5
assert isclose(aggregateCentroid, 3, abs_tol=1e-10)
print(representative, aggregateCentroid)
```

The triangles have analytical areas 1 and 2, so the aggregate centroid is
$(1\cdot1+2\cdot4)/3=3$. The representative average is $(1+4)/2=2.5$.
`AverageRepresentatives` accepts grades whose sum differs from one. All-zero
grades raise `UndefinedResultError`; a positive-grade term with zero area also
fails explicitly. A zero-grade term contributes zero and needs no centroid.
Aggregation policies, their domain and zero-area handling remain the caller's
explicit choice when computing `Centroid` of an aggregated set.

## Why the conversions are not inverses

Selecting a label discards other membership grades; replacing a label by its
centroid reduces an entire curve to one coordinate. The selected label may even
change after that conversion. A triangle with vertices `0, 1, 6` has centroid
`7/3`. Another term can have its peak at `7/3` and win when that centroid is
classified. This is an expected limitation, not a round-trip guarantee.

Keep the full membership vector when those distinctions matter. Fixed fuzzy
preprocessing around a neural network does not itself create trainable fuzzy
rules or preserve automatic-differentiation gradients.

## Reproduce the figure

Install the pinned `docs/requirements-plots.txt` toolchain and the candidate
package, then run:

```bash
python -m tools.generate_encoding_figure --output-directory docs/site/content/en/assets/figures
python -m tools.generate_encoding_figure --output-directory docs/site/content/en/assets/figures --check
```

The curve coordinates come from the public scalar API; the two reported centres
are checked against the independent analytical references above. See the
[historical preset](universal-fuzzy-scale.md) for its original windows and the
[API reference](../api/modern/linguistic.md) for all codec contracts.
