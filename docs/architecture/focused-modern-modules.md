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

- `exceptions.py` owns modern input, domain, and numerical error categories.
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

Task #90 makes `FuzzyRoutines.py` an explicit compatibility facade. The private
`_legacy` package has separate boundaries for utilities, operator call shapes,
mutable membership functions, mutable sets, and historical scale defaults. Each
adapter delegates formulas and numerical policies to the focused modern core.
The facade retains the original class/function module paths for serialized
objects, including pickles created before extraction.

Historical scale lookup still compares uppercase names, preserves mutable level
dictionaries, and chooses the last maximum even when all memberships are zero.
These are compatibility policies; modern scales use Unicode case folding and
an explicit no-match/tie policy. The adapters preserve these distinct contracts
without rebuilding an immutable modern scale on every historical call.

Task #91 defines the curated root `__all__`, including modern membership
factories and their typing contracts. The historical facade `__all__` contains
the fifteen supported names and excludes the old `math` and `copy` helper
leaks. The [public API inventory](../public-api-documentation-inventory.md)
records both surfaces and the source-documentation policy for type aliases.

## Modern usage

```python
from fuzzyroutines import Centroid, ContinuousUniverse, IntegrationDomain, ScalarFuzzySet, Triangle

membership = Triangle(left=0.0, peak=0.5, right=1.0)
universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, membership)

assert fuzzySet.Membership(0.25) == 0.5
assert abs(Centroid(fuzzySet, IntegrationDomain(0.0, 1.0)) - 0.5) < 1e-12
```

The module extraction is validated by historical compatibility tests,
modern/legacy numerical parity, exact-property and centroid tests, a legacy
import blocker for modern operations, and the installed-wheel strict API build.


## Error boundaries

Task #94 introduces the explicit `fuzzyroutines.exceptions` import surface.
Modern errors preserve built-in catch compatibility while distinguishing wrong
object kinds, invalid values, invalid domain geometry, and unresolved numerical
results. The existing `CentroidConvergenceError` stays in its defining module
and joins the numerical category without changing its public import identity.

The legacy interval adapter translates only controlled domain constructor
failures to the protected concrete built-in error types. A private centroid
engine accepts an explicit result-error class: modern calls select
`UndefinedResultError`, and historical calls select `ValueError`. This selection
applies only to engine-owned result checks, so evaluator failures and convergence
errors propagate unchanged. The shared historical membership geometry validator
continues to raise concrete `ValueError`.
