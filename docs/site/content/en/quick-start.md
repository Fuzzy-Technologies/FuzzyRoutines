<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Quick start

Turn a measured temperature into interpretable linguistic grades, then choose a
label. FuzzyRoutines provides scalar fuzzy sets, eight membership families,
explicit combination policies, linguistic scales, alpha cuts, and continuous
centroids. The modern API requires **CPython 3.13 or 3.14** and has no mandatory
NumPy or plotting dependency.

## Install

Create an isolated environment:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

This guide targets **2.1.0**. When that version is available on PyPI, install it
with the exact pin:

```bash
python -m pip install fuzzyroutines==2.1.0
```

If 2.1.0 is not yet available on PyPI, obtain the matching reviewed CI wheel
from the [agent guide](agent-quickstart.md), set its absolute local path in
`FUZZYROUTINES_WHEEL`, and use this installation route instead:

```bash
: "${FUZZYROUTINES_WHEEL:?Set the absolute path to the reviewed 2.1.0 wheel}"
python -m pip install --no-deps "$FUZZYROUTINES_WHEEL" &&
python -I -c "from importlib.metadata import version; import sys; actual = version('fuzzyroutines'); sys.exit(0 if actual == '2.1.0' else f'Expected 2.1.0; found {actual}')"
```

The [published 2.0.0 baseline](https://pypi.org/project/fuzzyroutines/2.0.0/)
and its [tagged documentation](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/site/content/en/quick-start.md)
remain available for reproducing earlier results. Older 1.x releases do not
provide this modern API. Preserve the wheel hash and matching source revision
when reporting candidate results.

## Measure and classify in a few lines

Suppose a room is at 24 °C. We define an illustrative *Comfort* triangle with
full membership at 22 °C, declining to zero at 16 and 28 °C. *Warm* rises
smoothly from 22 to 30 °C. Choose these thresholds with the people who understand
your application; they are model assumptions, not parameters learned by the
library.

```python
from math import isclose
from fuzzyroutines import (
    ContinuousUniverse, LinguisticScale, LinguisticTerm,
    ScalarFuzzySet, SShoulder, Triangle,
)

universe = ContinuousUniverse(0, 40, leftClosed=True, rightClosed=True)
scale = LinguisticScale((
    LinguisticTerm("Comfort", ScalarFuzzySet(universe, Triangle(16, 22, 28))),
    LinguisticTerm("Warm", ScalarFuzzySet(universe, SShoulder(22, 30))),
))
result = scale.Fuzzify(24)
grades = {item.term.name: item.grade for item in result.memberships}
assert isclose(grades["Comfort"], 2 / 3)
assert grades["Warm"] == 0.125
assert result.selectedTerms[0].name == "Comfort"
print(grades, result.selectedTerms[0].name)
```

The result is `Comfort ≈ 0.667`, `Warm = 0.125`, and the selected label is
`Comfort`. A grade describes compatibility with a defined concept. It is
**not a probability**, and the grades need not sum to one. `Fuzzify` reports all
grades; selection follows an explicit policy, with the first strongest term
selected by default.

[![Comfort and Warm membership curves with the 24 °C observation marked](assets/figures/temperature.svg)](assets/figures/temperature.svg)

The curves show the model on the declared 0–40 °C universe. The dashed line is
the measurement, and the dots are the two computed grades. This two-label
example deliberately leaves some temperatures uncovered. Check coverage before
using it as a complete operational scale.

## Combine, inspect, and explain a result

Continue with the [nine worked scenarios](guides/index.md). They cover
physical measurements, policy choices, abstention, directed fuzzy difference,
alpha cuts, centroids, scale diagnosis, and custom models. Each includes
self-contained code, expected numbers, and a figure. The
[membership gallery](guides/membership-families.md) helps choose a curve.

The script
[`examples/guide.py`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/examples/guide.py)
runs all nine scenarios and checks independent numerical expectations. From a
checkout with the package installed:

```bash
python -I examples/guide.py
python -I examples/guide.py --scenario centroid
```

You can copy a scenario into your project. Its scalar computations use only
FuzzyRoutines and the Python standard library; the checked-in SVGs require no
plotting package to view. To regenerate the figures from a checkout, install
`docs/requirements-plots.txt` and run `tools/generate_guide_figures.py` as
described in the [figure provenance guide](guides/figures.md).

For older `MFunction`, `FuzzySet`, and `FuzzyScale` code, start with the
[historical facade](api/legacy/index.md). Modern sets and policies are immutable;
the historical facade deliberately preserves its mutable compatibility contract.
