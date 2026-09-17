# Typed Linguistic-Term Representation

## Scope

The modern API represents one linguistic term as an immutable association:

```text
LinguisticTerm(name, fuzzySet)
```

`name` is a non-empty string preserved exactly as declared. `fuzzySet` is a
modern `ScalarFuzzySet`; the representation does not silently adapt the
historical mutable `FuzzySet` class.

An ordered scale is represented by:

```text
LinguisticScale((term1, term2, ...))
```

The explicit tuple is retained without sorting or normalization. It must be
non-empty, contain only `LinguisticTerm` values, and use exact unique names.
Case-distinct names such as `Low` and `LOW` remain representable because name
matching policy is outside this representation contract.

## Deliberate boundary

`LinguisticScale` does not perform name lookup, compare membership grades,
choose a term on a tie, or fuzzify a scalar value. Those behaviors require
their own explicit policies and belong to subsequent roadmap tasks. In
particular, tuple position is data; it is not yet a tie-breaking rule.

## Compatibility

The historical `fuzzyroutines.FuzzyRoutines.FuzzyScale` remains available.
Its `levels` property continues to expose and accept the original mutable list
of dictionaries with `name` and `fSet` keys. The modern types are additions;
they do not replace or reinterpret that compatibility facade.

## Example

```python
from fuzzyroutines import (
    ContinuousUniverse,
    LinguisticScale,
    LinguisticTerm,
    ScalarFuzzySet,
)

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
low = LinguisticTerm("Low", ScalarFuzzySet(universe, lambda value: 1.0 - value))
high = LinguisticTerm("High", ScalarFuzzySet(universe, lambda value: value))
scale = LinguisticScale((low, high))
```
