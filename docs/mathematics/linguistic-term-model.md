<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

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
non-empty, contain only `LinguisticTerm` values, and use names that are unique
under Unicode case-insensitive comparison. Case-distinct declarations such as
`Low` and `LOW` are rejected because they make case-insensitive lookup
ambiguous.

`GetTermByName(termName, exactMatching=True)` performs complete-name lookup.
The default mode compares names exactly, including case. Passing
`exactMatching=False` compares Unicode case-folded names. Both modes return the
original declared `LinguisticTerm` object or `None`; neither performs substring,
prefix, approximate, or membership-based matching.

## Deliberate boundary

`LinguisticScale` does not compare membership grades, choose a term on a tie,
or fuzzify a scalar value. Those behaviors require their own explicit policies
and belong to subsequent roadmap tasks. In particular, tuple position is data;
it is not yet a tie-breaking rule.

## Compatibility

The historical `fuzzyroutines.FuzzyRoutines.FuzzyScale` remains available.
Its `levels` property continues to expose and accept the original mutable list
of dictionaries with both required `name` and `fSet` keys. Its protected
`GetLevelByName(levelName, exactMatching=True)` call shape remains available:
the default performs exact complete-name lookup, while `False` performs
case-insensitive complete-name lookup through the historical uppercase map.
Names that collide ignoring case are rejected so this lookup remains
unambiguous. The modern types are additions; they do not replace the mutable
dictionary compatibility facade.

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
assert scale.GetTermByName("Low") is low
assert scale.GetTermByName("high", exactMatching=False) is high
```
