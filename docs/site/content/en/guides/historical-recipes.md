<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Maintain historical integrations

Use these recipes for existing 1.x consumers. The historical facade is
`fuzzyroutines.FuzzyRoutines`; new integrations should start with the immutable
[modern API](../api/modern/index.md). The supported interpreter is still Python
3.13 or 3.14. Compatibility preserves reviewed calls and names, while the
[migration notes](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/migration/1.0.3-to-2.0.0.md)
explain corrected mathematics and removed helper imports. Each block is
standalone and is tested against installed distributions.

## Parse ranges and validate historical scalar values

```python
from fuzzyroutines.FuzzyRoutines import DiapasonParser, IsCorrectFuzzyNumberValue, IsNumber

assert DiapasonParser("1-3,5,3") == [1, 2, 3, 5]
assert IsNumber(0.5) and not IsNumber(True)
assert IsCorrectFuzzyNumberValue(0.5) and not IsCorrectFuzzyNumberValue(1.5)
print(DiapasonParser("1-3,5,3"))
```

These historical scalar predicates accept built-in `int` and `float`, excluding
booleans. `IsNumber` is a type predicate, not a finite-value guarantee. The
parser retains its historical diagnostic-and-empty-list result for malformed
text; validate that result if an empty range is unacceptable in your project.

## Combine historical grades

```python
from math import isclose
from fuzzyroutines.FuzzyRoutines import (
    FuzzyAND, FuzzyNOT, FuzzyNOTParabolic, FuzzyOR,
    SCoNorm, SCoNormCompose, TNorm, TNormCompose,
)

assert FuzzyAND(0.4, 0.7) == 0.4 and FuzzyOR(0.4, 0.7) == 0.7
assert isclose(FuzzyNOT(0.4), 0.6) and isclose(FuzzyNOTParabolic(0.4), 0.6)
expectedAnd = {"logic": 0.4, "algebraic": 0.28, "boundary": 0.1, "drastic": 0}
expectedOr = {"logic": 0.7, "algebraic": 0.82, "boundary": 1, "drastic": 1}
for family in expectedAnd:
    assert isclose(TNorm(0.4, 0.7, normType=family), expectedAnd[family], abs_tol=1e-12)
    assert isclose(SCoNorm(0.4, 0.7, normType=family), expectedOr[family], abs_tol=1e-12)
assert isclose(TNormCompose(0.4, 0.7, 0.9, normType="algebraic"), 0.252)
assert isclose(SCoNormCompose(0.4, 0.7, 0.9, normType="algebraic"), 0.982)
print(TNormCompose(0.4, 0.7, 0.9, normType="algebraic"))
```

Composition folds from left to right. One valid operand returns that operand;
zero operands fail. Every operand and policy is validated, including the unary
case. `FuzzyNOT` is the historical parametric negation; its default alpha 0.5
reduces to the standard complement. The parabolic adapter keeps `epsilon` as a
validated compatibility argument; it does not change the result's precision.

## Evaluate all historical membership families and aliases

```python
from math import exp, isclose
from fuzzyroutines.FuzzyRoutines import MFunction

cases = (
    ("hyperbolic", {"a": 1, "b": 2, "c": 0}, 1),
    ("bell", {"a": -2, "b": -1, "c": 1}, 1),
    ("parabolic", {"a": -2, "b": 2}, 0.5),
    ("triangle", {"a": -2, "b": 2, "c": 0}, 1),
    ("trapezium", {"a": -2, "b": 2, "c": -1, "d": 1}, 1),
    ("exponential", {"a": 0, "b": 1}, 1),
    ("sigmoidal", {"a": 2, "b": 0}, 0.5),
    ("desirability", {}, exp(-1)),
)
for family, parameters, expected in cases:
    model = MFunction(family, **parameters)
    assert isclose(model.mju(0), expected)
    assert model.name == model.mju.__name__ and model.parameters == parameters
for alias, canonical, parameters in (
    ("sShoulder", "parabolic", {"a": -2, "b": 2}),
    ("gaussian", "exponential", {"a": 0, "b": 1}),
    ("logistic", "sigmoidal", {"a": 2, "b": 0}),
    ("harringtonDesirability", "desirability", {}),
):
    assert MFunction(alias, **parameters).mju(0) == MFunction(canonical, **parameters).mju(0)
triangle = MFunction("triangle", a=0, b=2, c=1)
triangle.parameters = {"a": 0, "b": 4, "c": 2}
assert triangle.mju(2) == 1
print(triangle.name, triangle.parameters)
```

`mju` is bound to the selected public family method (`Hyperbolic`, `Bell`,
`Parabolic`, `Triangle`, `Trapezium`, `Exponential`, `Sigmoidal`, or
`Desirability`). Call it with one coordinate. The aliases select those same
methods; they do not define new mathematics. Historical triangle order is
**a = left foot, b = right foot, c = peak**; modern `Triangle` uses
**left, peak, right**. Historical trapezium uses **a = left foot, b = right
foot, c = plateau start, d = plateau end**; modern `Trapezoid` uses their
geometric left-to-right order. The mutable parameter setter revalidates the whole
mapping. Do not replace `mju` and expect stock analytical certificates to apply.

## Recompute a mutable set after changing its model or window

```python
from math import isclose
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

model = MFunction("triangle", a=0, b=2, c=1)
fuzzySet = FuzzySet(model, supportSet=(0, 2), linguisticName="Preferred")
assert fuzzySet.name == "Preferred" and fuzzySet.mFunction is model
assert fuzzySet.supportSet == (0, 2)
assert isclose(fuzzySet.Defuz(), 1) and isclose(fuzzySet.defuzValue, 1)
replacement = MFunction("triangle", a=0, b=4, c=2)
fuzzySet.name = "Updated preference"
fuzzySet.mFunction = replacement
fuzzySet.supportSet = (0, 4)
assert fuzzySet.mFunction is replacement and fuzzySet.name == "Updated preference"
assert isclose(fuzzySet.Defuz(), 2) and isclose(fuzzySet.defuzValue, 2)
print(fuzzySet.name, fuzzySet.Defuz())
```

Despite its historical name, `supportSet` is a finite **integration window**;
it is not analytical positive support. `Defuz()` recomputes the centroid using
the reviewed modern numerical policy. Reading `defuzValue` also recomputes the
current result; both access paths observe changes to the model and window.
`MFunction.accuracy` is retained for compatibility but does not configure modern
centroid quadrature.

## Read and replace scale levels deliberately

```python
from fuzzyroutines.FuzzyRoutines import FuzzyScale, FuzzySet, MFunction, UniversalFuzzyScale

first = FuzzySet(MFunction("triangle", a=0, b=2, c=1), supportSet=(0, 2))
second = FuzzySet(MFunction("triangle", a=0, b=2, c=1), supportSet=(0, 2))
scale = FuzzyScale()
scale.name = "Two identical preferences"
scale.levels = [{"name": "First", "fSet": first}, {"name": "Second", "fSet": second}]
assert scale.name == "Two identical preferences" and len(scale.levels) == 2
assert scale.Fuzzy(1)["name"] == "Second"
assert scale.GetLevelByName("First")["fSet"] is first
assert scale.GetLevelByName("SECOND", exactMatching=False)["fSet"] is second
universal = UniversalFuzzyScale()
assert len(universal.levels) == len(universal.levelsNames) == len(universal.levelsNamesUpper)
assert universal.Fuzzy(0.5)["name"] in universal.levelsNames
assert {name.upper() for name in universal.levelsNames} == set(universal.levelsNamesUpper)
print(scale.Fuzzy(1)["name"], tuple(universal.levelsNames))
```

Historical ties favor the **later** level; the modern default favors the first
term, with an explicit policy for alternatives. A historical scale always
returns a winning level, including zero-coverage cases; modern results can
abstain. The universal preset preserves its historical geometry and known
coverage limitations. Diagnose a new operational scale rather than treating a
preset name as evidence of complete coverage.
