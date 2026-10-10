<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Historical Universal Fuzzy Scale

The **Universal Fuzzy Scale** is the historical five-level preset used by
FuzzyRoutines consumers: **Min → Low → Med → High → Max**. This page preserves
its original coefficients and shows how to reconstruct its classifier with the
modern immutable API. “Universal” is the preset's historical name, not a claim
that these coefficients fit every application. It is not the three-level default
`FuzzyScale`, nor a set of five equally spaced triangles.

[![Five historical membership curves and their modern reconstruction, shown side by side on zero to one; both retain the weak region near 0.17.](../assets/figures/universal-fuzzy-scale.svg)](../assets/figures/universal-fuzzy-scale.svg)

Both panels use the same coefficients. The left panel evaluates the historical
facade; the right evaluates the explicit modern construction. The Min curve drops sharply around 0.125; Low, Med and
High have flat tops and quadratic shoulders; Max rises between 0.77 and 0.95.
The small Min tail remains positive even where it is invisible at this scale.

## Cybersecurity and risk levels

The scale can turn a normalized score into linguistic levels for cybersecurity
and risk assessment: for example, the risk of an asset, the severity of a
security finding, or the effectiveness of protective controls. First define
how observations or expert assessments produce a score in `[0, 1]`, and what
an increase means. Higher risk and stronger protection have opposite meanings
for decisions, even when both use the labels Min, Low, Med, High and Max.

For an illustrative risk score of `0.75`, the historical scale selects `High`
with membership `1`. This means full membership in the High term under this
model; neither number is a probability of an incident. Keep the membership
grades alongside the selected label to expose transitions between levels.
Choose normalization, aggregation and response rules for the application,
validate them against domain evidence, and handle weak coverage explicitly as
shown below. The scale supplies linguistic interpretation of an input score;
it does not by itself measure risk or define an incident-response policy.

## The historical definition

| Level | Historical family / modern constructor | Historical `supportSet` |
| ----- | -------------------------------------- | ----------------------- |
| Min   | `hyperbolic` / `Hyperbolic(8, 20, 0)`  | `[0, 0.23]`             |
| Low   | `bell` / `Bell(0.17, 0.23, 0.34)`      | `[0.17, 0.40]`          |
| Med   | `bell` / `Bell(0.34, 0.40, 0.60)`      | `[0.34, 0.66]`          |
| High  | `bell` / `Bell(0.60, 0.66, 0.77)`      | `[0.60, 0.83]`          |
| Max   | `parabolic` / `SShoulder(0.77, 0.95)`  | `[0.77, 1]`             |

Here `supportSet` is the **historical finite centroid integration window**.
`UniversalFuzzyScale.Fuzzy(x)` evaluates each raw `mFunction.mju(x)` and does
**not clip** the membership curve to that window. In particular, Min remains
positive beyond 0.23. The modern reconstruction therefore gives every term the
same closed universe `[0, 1]`; assigning those five windows as term universes
would change behavior and make classification fail for most coordinates.

For normalized coordinates $0\le x\le1$, define the quadratic rising shoulder:

$$
s_{a,b}(x)=\begin{cases}
0,&x\le a,\\
2\left(\frac{x-a}{b-a}\right)^2,&a\lt x\le\frac{a+b}{2},\\
1-2\left(\frac{b-x}{b-a}\right)^2,&\frac{a+b}{2}\lt x\lt b,\\
1,&x\ge b.
\end{cases}
$$

$$
\mu_{\mathrm{Min}}(x)=\frac{1}{1+(8x)^{20}}
$$

$$
\mu_{\mathrm{Bell}(a,b,c)}(x)=\min\left\lbrace s_{a,b}(x),1-s_{c,c+b-a}(x)\right\rbrace
$$

$$
\mu_{\mathrm{Max}}(x)=s_{0.77,0.95}(x).
$$

A bell's right foot is $c+b-a$; its core is the entire interval $[b,c]$.
The scale is not a partition of unity: grades need not sum to one and are not
probabilities. The independent formulas above are evaluated in the executable
example and plot tests without calling the membership API.

## Existing historical code

```python
from math import isclose
from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale

scale = UniversalFuzzyScale()
assert [level["name"] for level in scale.levels] == ["Min", "Low", "Med", "High", "Max"]
grades = {level["name"]: level["fSet"].mFunction.mju(0.2) for level in scale.levels}
assert isclose(grades["Low"], 0.5)
assert scale.Fuzzy(0.2)["name"] == "Low"
assert scale.GetLevelByName("Med")["fSet"].supportSet == (0.34, 0.66)
assert scale.GetLevelByName("Min")["fSet"].mFunction.mju(0.5) > 0
print(grades, scale.Fuzzy(0.2)["name"])
```

The compatibility facade retains the old names and constructor. This example
runs on version 2.0; it does not assert that every numerical bug in 1.0.3 is
preserved. In particular, the reviewed centroid corrections are documented in
the [migration notes](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/migration/1.0.3-to-2.0.0.md).

## Explicit construction with the modern API

```python
from math import isclose
from fuzzyroutines import (
    Bell, ContinuousUniverse, FuzzificationPolicy, Hyperbolic,
    LinguisticScale, LinguisticTerm, ScalarFuzzySet, SShoulder,
)
from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale

universe = ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True)
models = (
    ("Min", Hyperbolic(8, 20, 0)),
    ("Low", Bell(0.17, 0.23, 0.34)),
    ("Med", Bell(0.34, 0.40, 0.60)),
    ("High", Bell(0.60, 0.66, 0.77)),
    ("Max", SShoulder(0.77, 0.95)),
)
scale = LinguisticScale(tuple(
    LinguisticTerm(name, ScalarFuzzySet(universe, model))
    for name, model in models
))
legacy = UniversalFuzzyScale()
policy = FuzzificationPolicy(tiePolicy="last", tieTolerance=0)
for coordinate in (0, 0.125, 0.17, 0.2, 0.37, 0.5, 0.63, 0.81, 0.86, 1):
    result = scale.Fuzzify(coordinate, policy)
    for item, previous in zip(result.memberships, legacy.levels, strict=True):
        assert isclose(item.grade, previous["fSet"].mFunction.mju(coordinate), abs_tol=1e-12)
    assert result.selectedTerms[0].name == legacy.Fuzzy(coordinate)["name"]
assert isclose(scale.Fuzzify(0.125).confidence, 0.5)
assert not scale.Fuzzify(0.17, FuzzificationPolicy(minimumConfidence=0.1)).isMatch
assert not scale.Fuzzify(0.125, FuzzificationPolicy(minimumConfidence=0.5)).isMatch
print([(item.term.name, item.grade) for item in scale.Fuzzify(0.2).memberships])
```

The historical `parabolic` membership is the modern `SShoulder`, not a parabola
extending without bounds. Keep the original level order and `tiePolicy="last"`
for historical winner selection. The default modern policy chooses the first
exact maximum; both APIs agree on the five curves, but policy choices must be
explicit in a migration.

## Values, boundaries, and decisions

| Coordinate | Result / grade                               |
| ---------- | -------------------------------------------- |
| 0          | Min = 1; included left boundary              |
| 0.125      | Min = 0.5                                    |
| 0.17       | Min ≈ 0.002129589894; Low = 0: weak coverage |
| 0.20       | Low = 0.5; Min ≈ 0.000082711220              |
| 0.50       | Med = 1; Min ≈ 9.094947018 × 10⁻¹³           |
| 0.81       | High ≈ 2/9, Max ≈ 8/81; select High          |
| 0.86       | Max ≈ 0.5                                    |
| 1          | Max = 1; included right boundary             |

The model intentionally retains weak coverage around the transition from Min
to Low; the graph must not be “fixed” by moving coefficients. At 0.17 the
historical classifier selects Min, while an explicit modern threshold of 0.1
returns no match. `minimumConfidence` is strict: a maximum grade equal to the
threshold also yields no match. The threshold is a membership requirement,
not a probability of a correct decision.

In exact real arithmetic the adjacent bells tie at 0.37 and 0.63. Floating-point
evaluation need not produce exact equality: at 0.37 the current evaluations are
Low ≈ 0.5000000000000009 and Med ≈ 0.4999999999999991, so historical selection
is **Low**. Do not assert that a mathematically symmetric midpoint must select
the later level. `tieTolerance=0` preserves the exact comparison; setting a
positive tolerance intentionally changes near-tie behavior.

The modern example rejects values outside `[0,1]`. The historical facade
accepts other finite coordinates (for example −0.1 selects Min and 1.1 selects
Max). Validate/normalize physical inputs before classification; do not silently
clamp them. Historical centroids also require their original per-level
integration windows, rather than integrating every modern term over `[0,1]`.

## Reproduce and verify

```bash
python examples/guide.py --scenario universal-fuzzy-scale
```

The scenario compares both APIs with independent piecewise formulas on **1001
coordinates** `0, 0.001, …, 1`, checks selected labels and weak-coverage policy,
and preserves the small positive Min tail. The two plotted panels independently
verify all **401 coordinates per curve**, ten curves in total. These finite grids
are regression evidence, not a proof over every real input. See
[figure reproduction](figures.md) for the pinned SVG toolchain and
[the frozen provenance](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/baseline/universal-fuzzy-scale-provenance.md)
for the original coefficients and centroid windows.
