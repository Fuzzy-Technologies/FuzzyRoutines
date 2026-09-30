<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Focused modern module ownership

Task #89 implements the modern-core-first direction accepted in
[ADR-0001](../adr/0001-backward-compatibility-contract.md) and the explicit
membership conventions of
[ADR-0003](../adr/0003-membership-function-contracts.md). It does not introduce
a new compatibility guarantee or change accepted mathematical formulas.

The package already has focused domain, set, defuzzification, linguistic,
property, alpha-cut, and relation modules. Their existing names remain stable;
adding `sets.py` or `scales.py` solely to duplicate those boundaries is
unnecessary.

- `numeric.py` owns internal finite-real and membership-grade validation.
- `membership.py` owns analytical scalar evaluation and immutable modern
  membership definitions with semantic parameter names.
- `operators.py` owns scalar negation and norm policies.
- `domain.py` owns declared universes and numerical integration domains.
- `fuzzysets.py` owns immutable scalar sets and set algebra.
- `defuzzification.py` owns analytical moments and adaptive quadrature.
- `linguistic.py` owns terms, ordered scales, fuzzification, and sampled
  diagnostics.
- `properties.py`, `alphacuts.py`, and `relations.py` retain their existing
  evidence boundaries.

Modern modules do not import `FuzzyRoutines.py`. The historical membership
object adapts its protected names and parameter conventions to shared modern
evaluation. Internal analytical snapshots let exact property, normalization,
and centroid operations consume a supported formula without depending on the
historical class. Those snapshots are copied evidence, not transparent caches
over mutable legacy state or arbitrary callables.

The historical module still owns its mutable compatibility classes and utility
surface. Task #90 completes its facade work; Task #91 reviews the curated
root exports. New membership factories are available through explicit imports
from `fuzzyroutines.membership` in this stage.

## Modern usage

```python
from fuzzyroutines import Centroid, ContinuousUniverse, IntegrationDomain, ScalarFuzzySet
from fuzzyroutines.membership import Triangle

membership = Triangle(left=0.0, peak=0.5, right=1.0)
universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
fuzzy_set = ScalarFuzzySet(universe, membership)

assert fuzzy_set.Membership(0.25) == 0.5
assert abs(Centroid(fuzzy_set, IntegrationDomain(0.0, 1.0)) - 0.5) < 1e-12
```

The module extraction is validated by historical compatibility tests,
modern/legacy numerical parity, exact-property and centroid tests, a legacy
import blocker for modern operations, and the installed-wheel strict API build.
