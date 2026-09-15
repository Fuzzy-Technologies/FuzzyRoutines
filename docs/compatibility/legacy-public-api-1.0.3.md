# Legacy Public API Snapshot — FuzzyRoutines 1.0.3

This document records the observed historical public surface before modernization.

It is a **baseline snapshot**, not a promise to preserve mathematically incorrect behavior. The compatibility rule is:

> Preserve historical public names and import paths. Correct mathematical, logical, numerical, and theoretical defects under those names where possible.

## Historical import path

The README documents:

```python
from fuzzyroutines.FuzzyRoutines import *
```

The module does not currently define `__all__`. Therefore wildcard import
follows normal Python behavior and also exposes imported module names such as
`math` and `copy`. The historical `traceback` leak disappeared when Task #63
removed print-and-zero exception handling. These helper modules are observed
behavior, but they are **not** protected domain API.

## Protected top-level functions

- `DiapasonParser(diapason)`
- `IsNumber(value)`
- `IsCorrectFuzzyNumberValue(value)`
- `FuzzyNOT(fuzzyNumber, alpha=0.5)`
- `FuzzyNOTParabolic(fuzzyNumber, alpha=0.5, epsilon=0.001)`
- `FuzzyAND(aNumber, bNumber)`
- `FuzzyOR(aNumber, bNumber)`
- `TNorm(aFuzzyNumber, bFuzzyNumber, normType='logic')`
- `TNormCompose(*fuzzyNumbers, normType='logic')`
- `SCoNorm(aFuzzyNumber, bFuzzyNumber, normType='logic')`
- `SCoNormCompose(*fuzzyNumbers, normType='logic')`

## Protected classes

### MFunction

Constructor:

```text
MFunction(userFunc, **membershipFunctionParams)
```

Historical public members include:

- `name`
- `parameters`
- `mju`
- `accuracy`
- `Hyperbolic(x)`
- `Bell(x)`
- `Parabolic(x)`
- `Triangle(x)`
- `Trapezium(x)`
- `Exponential(x)`
- `Sigmoidal(x)`
- `Desirability(y)`

Historical membership-function identifiers:

```text
hyperbolic
bell
parabolic
triangle
trapezium
exponential
sigmoidal
desirability
```

Parameter ordering/meaning is legacy API. In particular, Triangle and Trapezium conventions must not be silently reinterpreted during modernization.

### FuzzySet

Constructor:

```text
FuzzySet(membershipFunction, supportSet=(0.0, 1.0), linguisticName='FuzzySet')
```

Historical public members:

- `name`
- `mFunction`
- `supportSet`
- `defuzValue`
- `Defuz()`

### FuzzyScale

Constructor:

```text
FuzzyScale()
```

Historical public members:

- `name`
- `levels`
- `Fuzzy(realValue)`
- `GetLevelByName(levelName, exactMatching=True)`

### UniversalFuzzyScale

Constructor:

```text
UniversalFuzzyScale()
```

Historical public members include the inherited FuzzyScale API plus:

- `levelsNames`
- `levelsNamesUpper`

## Compatibility boundary

This snapshot protects **names, import paths, callable shape, and documented parameter conventions**.

It does not protect known defects. Examples already identified for later correction include:

- invalid edge behavior in fuzzy negation;
- brute-force/parabolic negation failure modes;
- stale `FuzzySet.Defuz()` derived state;
- weak validation in scale/operator composition code;
- mutation inside Bell evaluation.

Any intentional public-contract change requires an explicit compatibility decision and corresponding migration evidence.
