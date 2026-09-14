# Legacy Consumer and Protected-Name Inventory

This inventory records evidence-backed consumers of the historical FuzzyRoutines API before modernization.

The purpose is to distinguish **real compatibility obligations** from accidental implementation details.

## Evidence levels

- **Current source evidence** — directly observed in a currently accessible repository.
- **Historical evidence** — known from archived/historical usage identified during the FuzzyRoutines audit.
- **Unknown** — no evidence available; do not guess.

## Current source evidence

### Fuzzy-Technologies/TKSBrokerAPI

Repository:

https://github.com/Fuzzy-Technologies/TKSBrokerAPI

Direct source evidence:

https://github.com/Fuzzy-Technologies/TKSBrokerAPI/blob/b963c54039f013d432220186ae35a22359c5a773/tksbrokerapi/TradeRoutines.py

Observed dependencies:

- module path `fuzzyroutines.FuzzyRoutines`;
- class `UniversalFuzzyScale`;
- `UniversalFuzzyScale.levelsNames`;
- `UniversalFuzzyScale.levels`;
- `FuzzyScale.Fuzzy(realValue)` behavior inherited by `UniversalFuzzyScale`;
- returned level dictionaries containing at least the `"name"` key.

Observed application role:

- construction of a shared universal fuzzy risk scale;
- extraction of the historical level names `Min/Low/Med/High/Max`;
- classification of numeric risk values using `FUZZY_SCALE.Fuzzy(...)["name"]`.

Compatibility consequence:

These names and return-shape expectations are protected unless a deliberate breaking-change decision and downstream migration are approved.

## Historical consumer evidence

### FuzzyClassificator lineage

The project audit identified historical FuzzyClassificator usage of FuzzyRoutines, including direct use of:

- `UniversalFuzzyScale`;
- `FuzzyScale.Fuzzy()`;
- `FuzzySet.Defuz()`.

The currently accessible organization code search did not provide a canonical active repository location for that historical consumer. Therefore this entry is retained as **historical evidence**, not claimed as current active source evidence.

Compatibility consequence:

Do not remove or silently rename these historical entry points merely because their consumer is not currently active.

## Protected names/imports

The following compatibility surface has direct or historical consumer evidence and/or is explicitly documented by the FuzzyRoutines README:

### Import path

```python
fuzzyroutines.FuzzyRoutines
```

The README also documents:

```python
from fuzzyroutines.FuzzyRoutines import *
```

### Classes

- `MFunction`
- `FuzzySet`
- `FuzzyScale`
- `UniversalFuzzyScale`

### Core methods/properties

- `FuzzySet.Defuz()`
- `FuzzyScale.Fuzzy()`
- `FuzzyScale.GetLevelByName()`
- `UniversalFuzzyScale.levels`
- `UniversalFuzzyScale.levelsNames`
- `UniversalFuzzyScale.levelsNamesUpper`

### Fuzzy operators

- `FuzzyNOT`
- `FuzzyNOTParabolic`
- `FuzzyAND`
- `FuzzyOR`
- `TNorm`
- `TNormCompose`
- `SCoNorm`
- `SCoNormCompose`

### Historical membership identifiers

- `hyperbolic`
- `bell`
- `parabolic`
- `triangle`
- `trapezium`
- `exponential`
- `sigmoidal`
- `desirability`

## What is not protected merely by this inventory

A compatibility obligation does **not** require retaining known defects.

Examples:

- invalid mathematical edge results;
- stale cached defuzzification;
- non-terminating numerical search;
- silent exception-to-zero behavior;
- validation bugs.

The historical callable name should normally survive while the defect is corrected and documented.

## Unknown usage

Unknown external use must remain marked unknown.

Absence of code-search evidence is not evidence that nobody uses the package.

Before an intentional breaking release:

1. repeat organization/public consumer search;
2. inspect package download/current maintainer context;
3. review compatibility tests;
4. document migration impact;
5. obtain explicit approval for the break.
