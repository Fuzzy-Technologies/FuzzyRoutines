<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Historical-to-Modern API Migration Examples

- Status: current `develop` implementation boundary
- Related Task: #99
- Canonical entry point: [compatibility and migration](../COMPATIBILITY.md)
- Compatibility decision: [ADR-0001](../adr/0001-backward-compatibility-contract.md)
- Exact implementation boundary: [current status](../current-status.md)

## Migration rule

Historical names remain supported. Existing users do not need to rename
`MFunction`, `FuzzySet`, `FuzzyScale`, `UniversalFuzzyScale`, `Defuz`, or the
scalar operator functions merely to adopt version 2. Migrate one area at a
time when the focused API already provides the behavior the application
needs.

The current modern API covers explicit domains, immutable scalar fuzzy sets,
set algebra, relations, derived properties, alpha-cuts, exact height-aware
normalization, and typed linguistic-term and ordered-scale representations. A
focused membership-function factory, typed scale lookup and fuzzification
policies remain roadmap work. Modern centroid defuzzification is available
through an explicit integration domain and numerical policy. The examples
below keep remaining gaps visible instead of inventing future call shapes.

| Area                 | Historical API remains supported                                   | Preferred path available today                                                                                                   |
|----------------------|--------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Operators            | `FuzzyNOT`, `TNorm`, `SCoNorm`, and compose functions              | `NegationPolicy`, `TNormPolicy`, and `SNormPolicy`; set operations require policies explicitly                                   |
| Membership functions | `MFunction` and every protected historical identifier              | No focused factory yet; use `MFunction` directly or as a callable source for `ScalarFuzzySet`                                    |
| Fuzzy sets           | Mutable `FuzzySet` with a legacy `supportSet` integration interval | Immutable `ScalarFuzzySet` with an explicit `ContinuousUniverse` or `DiscreteUniverse`                                           |
| Scales               | `FuzzyScale` and `UniversalFuzzyScale`                             | Typed representation via `LinguisticTerm` and `LinguisticScale`; legacy classes remain required for lookup and fuzzification     |
| Derived operations   | No equivalent unified modern surface                               | `DeriveProperties`, `AlphaCut`, `SampleAlphaCut`, `Height`, and `Normalize` preserve explicit exactness boundaries               |
| Defuzzification      | `FuzzySet.Defuz()` and `defuzValue`                                | `Centroid()` with explicit `ScalarFuzzySet`, `IntegrationDomain`, and optional `CentroidPolicy`                                  |

## Operators

Historical scalar calls select a family with a string:

```python
from fuzzyroutines.FuzzyRoutines import FuzzyNOT, SCoNorm, TNorm

conjunction = TNorm(0.4, 0.7, normType="algebraic")
disjunction = SCoNorm(0.4, 0.7, normType="logic")
negated = FuzzyNOT(0.4)
```

The modern scalar and fuzzy-set paths make the selected policy an immutable
value:

```python
from fuzzyroutines import NegationPolicy, SNormPolicy, TNormPolicy

conjunction = TNormPolicy("algebraic").Evaluate(0.4, 0.7)
disjunction = SNormPolicy("logic").Evaluate(0.4, 0.7)
negated = NegationPolicy("standard").Evaluate(0.4)
```

`TNormCompose` and `SCoNormCompose` do not yet have focused modern
counterparts. Keep those historical names when n-ary composition is required;
do not replace them with an undocumented API.

## Membership functions

The historical factory and parameter conventions remain the executable API:

```python
from fuzzyroutines.FuzzyRoutines import MFunction

# Historical order is preserved: a = left foot, c = apex, b = right foot.
membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
grade = membershipFunction.mju(0.25)
```

There is no focused modern membership-function factory yet. When adopting the
modern set model, reuse the protected evaluator as a callable:

```python
from fuzzyroutines import ContinuousUniverse, ScalarFuzzySet
from fuzzyroutines.FuzzyRoutines import MFunction

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, membershipFunction.mju)
```

Additive registry names such as `gaussian`, `logistic`, `sShoulder`, and
`harringtonDesirability` are available, but migration does not require
renaming `exponential`, `sigmoidal`, `parabolic`, or `desirability`. See the
[membership-function contract](../mathematics/membership-function-contracts.md)
before changing any identifier because some historical parameter orders are
deliberately preserved.

## Fuzzy sets

Historical construction combines a membership object, a mutable name, and a
tuple historically called `supportSet`:

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
fuzzySet = FuzzySet(
    membershipFunction,
    supportSet=(0.0, 1.0),
    linguisticName="Medium",
)
```

For new set algebra, declare the universe separately and pass a membership
callable:

```python
from fuzzyroutines import (
    Complement,
    ContinuousUniverse,
    NegationPolicy,
    ScalarFuzzySet,
)

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, membershipFunction.mju)
complement = Complement(fuzzySet, NegationPolicy("standard"))

assert complement.Membership(0.25) == 0.5
```

`ScalarFuzzySet` has no linguistic-name field and no numerical integration
interval. `IntegrationDomain` is a separate operational value and is not
mathematical support.

## Scales

Continue to use the protected historical classes:

```python
from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale

scale = UniversalFuzzyScale()
level = scale.Fuzzy(0.5)
assert level["name"] == "Med"
```

The modern API can represent names, fuzzy sets, and explicit term order without
silently inheriting the historical dictionary shape:

```python
from fuzzyroutines import LinguisticScale, LinguisticTerm

modernScale = LinguisticScale((LinguisticTerm("Medium", fuzzySet),))
```

This representation deliberately has no `Fuzzy()` or `GetLevelByName()`
method, tie-breaking rule, case-matching rule, or scalar fuzzification policy.
There is therefore no truthful behavioral replacement yet for those historical
operations. Keep `FuzzyScale` or `UniversalFuzzyScale` when lookup or
fuzzification is required; use `LinguisticTerm` and `LinguisticScale` when an
immutable typed representation is sufficient.

## Defuzzification

Existing code may continue to use the recalculating compatibility entry point:

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0))
centroid = fuzzySet.Defuz()
```

`Defuz()` now uses the modern analytical/adaptive strategy and ignores the
retained compatibility attribute `MFunction.accuracy`. The historical
`supportSet` tuple is a finite numerical integration interval, not exact
positive support. New code can express the same operation explicitly:

```python
from fuzzyroutines import Centroid, ContinuousUniverse, IntegrationDomain, ScalarFuzzySet

integrationDomain = IntegrationDomain.FromLegacyInterval(fuzzySet.supportSet)
modernSet = ScalarFuzzySet(ContinuousUniverse(), membershipFunction.mju)
centroid = Centroid(modernSet, integrationDomain)
```

See [Centroid defuzzification](../mathematics/centroid-defuzzification.md) for
analytical families, adaptive tolerances, zero-area behavior, and convergence
failure.

## Executable examples

Both examples import only public package entry points and contain no source
tree path manipulation:

```bash
python examples/migration/historical_compatibility.py
python examples/migration/modern_supported.py
```

- [`historical_compatibility.py`](../../examples/migration/historical_compatibility.py)
  exercises all five historical areas.
- [`modern_supported.py`](../../examples/migration/modern_supported.py) exercises
  explicit operator policies and immutable fuzzy sets while clearly using the
  historical membership factory as the current interoperability path.

The example tests execute each script from a temporary working directory. The
package workflow independently installs the wheel and source distribution,
removes `PYTHONPATH`, proves the import origin is inside the clean environment,
and runs the same scripts through the shell-visible entry points. See
[`Executable Tests, Tools, Benchmarks, and Examples`](../executable-tests-tools-and-examples.md)
for the complete artifact and exit-code contract.
