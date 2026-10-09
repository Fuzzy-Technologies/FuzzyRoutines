<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Exceptions

Import the modern categories explicitly from `fuzzyroutines.exceptions`.
`FuzzyRoutinesError` catches failures deliberately raised by the mathematical
core. Existing handlers for `TypeError`, `ValueError`, and `ArithmeticError`
continue to work.

| Category                    | Meaning                                                            | Built-in handler                |
| --------------------------- | ------------------------------------------------------------------ | ------------------------------- |
| `InvalidParameterTypeError` | An object has the wrong kind, including boolean scalar inputs      | `TypeError`                     |
| `InvalidParameterError`     | A value, grade, family, or policy violates its contract            | `ValueError`                    |
| `InvalidDomainError`        | Interval geometry, coordinate ordering, or universes conflict      | `ValueError`                    |
| `NumericalError`            | A mathematical operation cannot resolve its result                 | `ArithmeticError`               |
| `UndefinedResultError`      | Zero-area centroid, zero-height normalization, or nonfinite result | `ValueError`, `ArithmeticError` |

`InvalidDomainError` is an `InvalidParameterError`. Scalar finiteness checks
use `InvalidParameterError`; domain errors describe geometry and relationships
between otherwise validated values. `UndefinedResultError` is a `NumericalError`
and also preserves historical `ValueError` handlers for undefined results.
[CentroidConvergenceError][fuzzyroutines.defuzzification.CentroidConvergenceError]
remains defined in `fuzzyroutines.defuzzification` and retains its existing root
export and identity; it is now a `NumericalError` as well as an `ArithmeticError`.

```python
from fuzzyroutines.domain import IntegrationDomain
from fuzzyroutines.exceptions import InvalidDomainError

try:
    IntegrationDomain(1.0, 0.0)

except InvalidDomainError:
    pass
```

User membership evaluators keep their own exception objects, even if an
exception happens to belong to this hierarchy. Neither modern operations nor
historical centroid adapters wrap arbitrary callback failures.

The historical membership geometry validator retains concrete `ValueError`.
The historical fuzzy-set interval constructor and setter explicitly translate
only owned domain validation failures to concrete `TypeError` or `ValueError`.
The historical centroid adapter selects concrete `ValueError` only for the
engine's zero-area and nonfinite-result checks. It preserves callback errors
and `CentroidConvergenceError` unchanged. Other historical validation contracts,
including documented generic `Exception` errors, remain protected.

## Worked examples

[Undefined-result handling](../../guides/api-recipes.md#handle-a-mathematically-undefined-result) handles zero membership area.

::: fuzzyroutines.exceptions
    options:
      members:
        - FuzzyRoutinesError
        - InvalidParameterTypeError
        - InvalidParameterError
        - InvalidDomainError
        - NumericalError
        - UndefinedResultError
