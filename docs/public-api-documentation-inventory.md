<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Public API documentation inventory

This inventory records the reviewed Python surface for Task #200. It separates
the modern immutable API from the historical compatibility facade so generated
reference pages can describe both without presenting legacy aliases as the
recommended design.

## Modern package exports

The root `fuzzyroutines.__all__` list is the authoritative modern public
surface. Every export below has an English source docstring and is re-exported
from `fuzzyroutines`:

| Module       | Public symbols                                                                                                                                                                       |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `alphacuts`  | `AlphaCut`, `SampleAlphaCut`, `SampledAlphaCut`                                                                                                                                      |
| `domain`     | `ContinuousUniverse`, `DiscreteUniverse`, `IntegrationDomain`                                                                                                                        |
| `fuzzysets`  | `Complement`, `Difference`, `Height`, `Intersection`, `IsNormal`, `NegationPolicy`, `Normalize`, `ScalarFuzzySet`, `SNormPolicy`, `TNormPolicy`, `Union`                             |
| `linguistic` | `LinguisticScale`, `LinguisticTerm`                                                                                                                                                  |
| `properties` | `ContinuousFuzzyProperties`, `ContinuousInterval`, `ContinuousRegion`, `DeriveProperties`, `DiscreteFuzzyProperties`, `DiscreteRegion`, `SampledFuzzyProperties`, `SampleProperties` |
| `relations`  | `ComparisonDomain`, `ComparisonPolicy`, `EqualOnDomain`, `IncludedOnDomain`                                                                                                          |

## Historical compatibility facade

`fuzzyroutines.FuzzyRoutines` intentionally has no `__all__`: its wildcard
behavior is part of the observed 1.0.3 compatibility baseline. The documented
legacy API comprises:

- Functions: `DiapasonParser`, `IsNumber`, `IsCorrectFuzzyNumberValue`,
  `FuzzyNOT`, `FuzzyNOTParabolic`, `FuzzyAND`, `FuzzyOR`, `TNorm`,
  `TNormCompose`, `SCoNorm`, and `SCoNormCompose`.
- Classes: `MFunction`, `FuzzySet`, `FuzzyScale`, and `UniversalFuzzyScale`,
  including their public methods and properties.
- Compatibility family aliases accepted by `MFunction`: `sShoulder`,
  `gaussian`, `logistic`, and `harringtonDesirability`. These are string
  identifiers, not separate Python symbols; the `MFunction` class docstring
  documents them explicitly.

## Reviewed exclusions

- Names beginning with `_` are implementation details rather than public API.
  They still retain source docstrings when they encode a mathematical or
  architectural boundary, as required by `docs/python-code-style.md`.
- `fuzzyroutines.Examples` is executable demonstration code, not a production
  API module. Its migration and executable documentation belong to Task #202.
- Imported modules exposed by the historical wildcard behavior (`copy`,
  `math`) are observed compatibility artifacts, not project-owned API symbols.
- Dataclass-generated methods are documented through their owning class and
  public attributes; generated callables are not separate authored symbols.

## Verification boundary

`tests/test_public_api_documentation.py` checks the packaged public surface,
including public legacy members, for non-empty English docstrings and
period-terminated summaries. The clean-install workflow runs that test against
both wheel and source-distribution artifacts. Documentation-rendering and
reference-drift enforcement remain the separate scope of Task #204.
