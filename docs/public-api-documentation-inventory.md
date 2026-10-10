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
surface. Every export below has English source documentation and is re-exported
from `fuzzyroutines`:

| Module            | Public symbols                                                                                                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `alphacuts`       | `AlphaCut`, `SampleAlphaCut`, `SampledAlphaCut`                                                                                                                                      |
| `defuzzification` | `Centroid`, `CentroidConvergenceError`, `CentroidPolicy`                                                                                                                             |
| `domain`          | `ContinuousUniverse`, `DiscreteUniverse`, `IntegrationDomain`                                                                                                                        |
| `fuzzysets`       | `Complement`, `Difference`, `Height`, `Intersection`, `IsNormal`, `Normalize`, `ScalarFuzzySet`, `Union`                                                                             |
| `linguistic`      | `FuzzificationPolicy`, `FuzzificationResult`, `LinguisticScale`, `LinguisticTerm`, `ScaleDiagnosticPoint`, `ScaleDiagnosticsPolicy`, `ScaleDiagnosticsResult`, `TermMembership`      |
| `membership`      | `Bell`, `Gaussian`, `HarringtonDesirability`, `Hyperbolic`, `Logistic`, `MembershipCallable`, `MembershipFunction`, `MembershipScalar`, `SShoulder`, `Trapezoid`, `Triangle`         |
| `operators`       | `NegationPolicy`, `SNormPolicy`, `TNormPolicy`                                                                                                                                       |
| `properties`      | `ContinuousFuzzyProperties`, `ContinuousInterval`, `ContinuousRegion`, `DeriveProperties`, `DiscreteFuzzyProperties`, `DiscreteRegion`, `SampleProperties`, `SampledFuzzyProperties` |
| `relations`       | `ComparisonDomain`, `ComparisonPolicy`, `EqualOnDomain`, `IncludedOnDomain`                                                                                                          |

## Historical compatibility facade

`fuzzyroutines.FuzzyRoutines.__all__` explicitly defines the fifteen supported
historical names. Its wildcard import retains every supported function and class
while excluding imported helpers. The documented legacy API comprises:

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
- Imported modules formerly exposed by historical wildcard behavior (`copy`,
  `math`) are observed baseline artifacts, not project-owned API symbols; the
  curated facade no longer imports them.
- PEP 695 aliases such as `MembershipScalar` use the immediately following
  source string as their documentation. Static discovery checks their coverage
  and hashes both the alias definition and documentation for translation drift.
  Their runtime `__doc__` describes Python's `TypeAliasType`, not the alias.
- Dataclass-generated methods are documented through their owning class and
  public attributes; generated callables are not separate authored symbols.

## Verification boundary

`tests/test_public_api_documentation.py` checks the packaged public surface,
including public legacy members, for non-empty English docstrings and
period-terminated summaries. The clean-install workflow runs that test against
both wheel and source-distribution artifacts.

Task #204 established `docs/site/api-coverage.toml` as the machine-readable reviewed
surface and exclusion manifest. Its deterministic validator compares the
manifest with statically discovered source symbols and the tracked
mkdocstrings directives, then reports missing coverage with source file, line,
and qualified symbol. Generated HTML remains disposable under ADR-0010, so the
gate rejects committed generated output instead of maintaining a drift-prone
generated snapshot.
