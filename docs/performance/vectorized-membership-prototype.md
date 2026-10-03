<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Optional Vectorized Membership Prototype

Task [#107](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/107)
implements a repository-only experiment for array evaluation. It does not change
the scalar API, package exports, mandatory dependencies, or distribution extras.
The `experiments/` directory is excluded by the existing package discovery rule
(`fuzzyroutines*`). NumPy is imported lazily on array evaluation; importing either
the scalar package or this experimental module does not require NumPy.

## Reproduce the experiment

Use a supported Python 3.13 or 3.14 environment at the repository root:

```bash
python -m pip install -r requirements.txt -r experiments/requirements-vectorized.txt
python -m pytest -q tests/test_vectorized_membership.py tests/test_vectorized_optional_boundary.py
```

The optional requirement is pinned to NumPy 2.3.5 for repeatable parity checks.
The dedicated `Optional vectorized prototype parity` workflow checks both
supported Python versions. The normal scalar test suite skips the NumPy parity
module when NumPy is absent and still exercises dependency isolation in a fresh
process that blocks NumPy imports.

```python
from experiments.vectorized_membership import EvaluateMembership

grades = EvaluateMembership("gaussian", [-2.0, 0.0, 2.0], a=0.0, b=1.0)
```

This import is a research interface, not a supported installed-package API.
Parameters retain the historical `MFunction` names and geometric conventions;
in particular, `triangle(a, b, c)` uses `c` as the apex. All eight historical
families and their existing exact aliases are covered. Custom callables,
operators, centroids, arbitrary precision, GPU execution, and vectorized fuzzy
set objects are outside this prototype.

## Numerical and ownership boundary

- Inputs are non-scalar real integer or floating arrays/sequences. Coordinates
  are copied to binary64; shape is preserved, including empty dimensions.
- Boolean, complex, string, object, scalar, and non-finite coordinates are
  rejected. The prototype does not silently coerce string/object data to numbers.
- Integer and float32 inputs use their float64-converted coordinates as the
  scalar reference. This does not promise exact preservation of arbitrary large
  integers or extended precision inputs.
- `MFunction` validates a fresh parameter snapshot before calculation, so the
  scalar family registry and parameter validation remain authoritative.
- Results are fresh float64 arrays with finite grades in $[0,1]$. Inputs and
  parameter mappings are not changed. Ambient NumPy error settings are restored.
- Active branch masks avoid computing invalid unused branches. This includes
  the supported triangle boundary `c == b`, fractional hyperbolic powers on the
  active positive tail, and stable logistic saturation.
- Gaussian and logistic overflow-to-saturation and desirability underflow limits
  match scalar behavior in the tested extreme cases. Unrepresentable power or
  piecewise intermediates fail explicitly; squared denominator underflow fails
  with `ZeroDivisionError`. Scalar/NumPy exception identity is not guaranteed for
  all pathological finite parameter combinations. No all-finite-input guarantee
  is made.

## Parity evidence and next gate

The numerical reference is `MFunction(...).mju(float(x))` at each converted
coordinate. The acceptance tolerance is absolute $10^{-12}$ with zero relative
tolerance, matching the existing scalar benchmark protocol. Tests cover seeded
random inputs, dense grids, branch endpoints and adjacent representable floats,
plateau/apex degeneracies, multidimensional/noncontiguous arrays, invalid
configurations, empty arrays, and stable saturation cases. Passing these sampled
checks is evidence for those workloads, not a proof of equivalence everywhere.

No speedup, memory-efficiency, installation-cost, or adoption claim is made in
Task #107. Array allocation and intermediate masks have costs that require
measurement. Task #108 must apply the
[benchmark reproducibility protocol](benchmark-reproducibility-protocol.md) and
record timing samples, peak memory, dependency/installation cost, input shape,
dtype, and scalar parity in the same environment. Task #109 must decide whether
an optional public backend is justified; this experiment makes no such decision.

The [scalar/array comparison](vectorized-membership-comparison.md) provides
Task #108's reproducible timing, isolated memory, optional dependency cost,
and parity evidence. Its observations apply to the recorded environment and
workloads; the public backend decision remains Task #109.
