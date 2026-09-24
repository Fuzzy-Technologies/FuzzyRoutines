<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Compatibility and migration

- Status: current `develop` contract for `2.0.0.dev0`
- Governing decision: [ADR-0001](adr/0001-backward-compatibility-contract.md)
- Observed 1.0.3 surface: [legacy public API snapshot](compatibility/legacy-public-api-1.0.3.md)
- Implemented v2 surface: [public API inventory](public-api-documentation-inventory.md)

This page is the canonical entry point for choosing an API surface and moving
existing FuzzyRoutines code forward. Compatibility means that protected
historical names and call shapes remain available. It does not mean that a
known mathematical, numerical, validation, or stale-state defect remains
available.

## Choose a surface

| Situation                                     | Supported entry point                                   | Guidance                                                                                            |
|-----------------------------------------------|---------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Existing 1.0.3-style application              | `fuzzyroutines.FuzzyRoutines`                           | Keep the historical calls until a focused modern path supplies every behavior the application uses. |
| New code with explicit mathematical contracts | Root exports from `fuzzyroutines`                       | Prefer immutable universes, fuzzy sets, policies, result types, and explicit numerical domains.     |
| Incremental migration                         | Modern root exports plus selected compatibility objects | Migrate one operation at a time; using `MFunction` as a callable source is currently supported.     |

The modern package API is recommended for new code, but it is not a mandatory
rename layer for existing callers. Historical names remain supported under
[ADR-0001](adr/0001-backward-compatibility-contract.md) unless a later approved
ADR deliberately changes that contract.

## Protected historical surface

The protected compatibility import is:

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction, TNorm
```

The supported historical surface comprises:

- functions `DiapasonParser`, `IsNumber`, `IsCorrectFuzzyNumberValue`,
  `FuzzyNOT`, `FuzzyNOTParabolic`, `FuzzyAND`, `FuzzyOR`, `TNorm`,
  `TNormCompose`, `SCoNorm`, and `SCoNormCompose`;
- classes `MFunction`, `FuzzySet`, `FuzzyScale`, and `UniversalFuzzyScale`;
- `MFunction` members `name`, `parameters`, `mju`, `accuracy`, `Hyperbolic()`,
  `Bell()`, `Parabolic()`, `Triangle()`, `Trapezium()`, `Exponential()`,
  `Sigmoidal()`, and `Desirability()`;
- `FuzzySet` members `name`, `mFunction`, `supportSet`, `defuzValue`, and
  `Defuz()`;
- `FuzzyScale` members `name`, `levels`, `Fuzzy()`, and `GetLevelByName()`;
- inherited `UniversalFuzzyScale` behavior plus `levelsNames` and
  `levelsNamesUpper`;
- historical membership identifiers `hyperbolic`, `bell`, `parabolic`,
  `triangle`, `trapezium`, `exponential`, `sigmoidal`, and `desirability`;
- the historical membership keyword names, parameter meaning, and parameter
  ordering recorded by the
  [membership-function contract](mathematics/membership-function-contracts.md).

Exact signatures and the observed wildcard-import boundary are recorded in the
[1.0.3 snapshot](compatibility/legacy-public-api-1.0.3.md) and enforced by
[`test_legacy_public_api.py`](../tests/test_legacy_public_api.py) and
[`test_legacy_import_compatibility.py`](../tests/test_legacy_import_compatibility.py).
Imported helper modules accidentally visible through wildcard import are not
project-owned compatibility symbols.

`sShoulder`, `gaussian`, `logistic`, and `harringtonDesirability` are accepted
additional `MFunction` identifiers. They select the same implementations as
their corresponding historical identifiers. They are optional conveniences,
not replacements that existing callers must adopt.

## Modern paths available now

| Need                        | Historical path                         | Implemented modern path                                                                     | Boundary                                                                               |
|-----------------------------|-----------------------------------------|---------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| Binary scalar operators     | `FuzzyNOT`, `TNorm`, `SCoNorm`          | `NegationPolicy`, `TNormPolicy`, `SNormPolicy`                                              | The policy objects expose `Evaluate()` and are immutable.                              |
| Variadic scalar composition | `TNormCompose`, `SCoNormCompose`        | No focused n-ary replacement                                                                | Keep the historical functions when n-ary folding is required.                          |
| Membership functions        | `MFunction`                             | No focused factory                                                                          | `MFunction.mju` may supply a callable to the modern set API.                           |
| Fuzzy-set representation    | Mutable `FuzzySet`                      | `ScalarFuzzySet` with `ContinuousUniverse` or `DiscreteUniverse`                            | `supportSet` is an integration interval, not a mathematical universe or exact support. |
| Set algebra                 | Scalar operators applied by caller code | `Complement`, `Intersection`, `Union`, and `Difference` with explicit policy objects        | Binary operations require exactly compatible universes.                                |
| Derived set information     | No unified historical result            | `DeriveProperties`, `SampleProperties`, `AlphaCut`, `SampleAlphaCut`, `Height`, `Normalize` | Exact and sampled evidence use distinct result contracts.                              |
| Relations                   | No focused historical surface           | `EqualOnDomain`, `IncludedOnDomain`, `ComparisonPolicy`, `ComparisonDomain`                 | Comparison tolerance and inspection domain are explicit.                               |
| Linguistic representation   | `FuzzyScale`, `UniversalFuzzyScale`     | `LinguisticTerm`, `LinguisticScale`                                                         | Modern lookup, tie-breaking, and fuzzification policies are not implemented yet.       |
| Centroid defuzzification    | `FuzzySet.Defuz()`, `defuzValue`        | `Centroid` with `ScalarFuzzySet`, `IntegrationDomain`, and optional `CentroidPolicy`        | The integration interval is explicit and finite.                                       |

The root-package export list in
[`fuzzyroutines/__init__.py`](../fuzzyroutines/__init__.py) is authoritative for
which modern symbols are implemented. The [current implementation status](current-status.md)
separates that surface from roadmap work.

## Corrected behavior is not a compatibility promise

The compatibility contract preserves valid usage, not defective results. The
following implemented corrections can therefore change failure modes or
outputs while retaining historical names and call shapes:

| Corrected area                | Current behavior                                                                                          |
|-------------------------------|-----------------------------------------------------------------------------------------------------------|
| Scalar and composed operators | Reject invalid, non-finite, Boolean, empty, and unknown-family inputs with explicit `ValueError`.         |
| Parametric negation           | Enforces the proved parameter domains; parabolic negation uses a bounded analytical branch.               |
| Membership construction       | Requires exact finite parameter sets and valid family geometry.                                           |
| Bell evaluation               | Does not mutate the caller-visible parameter mapping.                                                     |
| Centroid state                | Recalculates from current membership parameters and integration bounds rather than returning stale state. |
| Scale lookup                  | Evaluates each term once and preserves the documented later-term tie policy.                              |

The [corrected-bug ledger](compatibility/corrected-bug-ledger.md) supplies the
change history and merged evidence. A future correction must be added there;
an intentional removal or signature change instead requires the explicit ADR
and consumer-impact process defined by ADR-0001. Known downstream evidence is
tracked separately in the [consumer inventory](compatibility/legacy-consumers.md).

## Migration examples

Existing code remains valid:

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0))
centroid = fuzzySet.Defuz()
```

The same membership definition can move to the implemented modern set and
defuzzification contracts without inventing a future membership factory:

```python
from fuzzyroutines import Centroid, ContinuousUniverse, IntegrationDomain, ScalarFuzzySet
from fuzzyroutines.FuzzyRoutines import MFunction

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, membershipFunction.mju)
centroid = Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))
```

Detailed, area-by-area guidance is in the
[historical-to-modern migration guide](migration/historical-to-modern.md).
Its complete executable scenarios are:

- [`historical_compatibility.py`](../examples/migration/historical_compatibility.py);
- [`modern_supported.py`](../examples/migration/modern_supported.py).

Run them against an installed package with:

```console
python examples/migration/historical_compatibility.py
python examples/migration/modern_supported.py
```

[`test_migration_examples.py`](../tests/test_migration_examples.py) verifies
their imports and deterministic results. Repository documentation gates also
validate the local links and Markdown table alignment on this page.
