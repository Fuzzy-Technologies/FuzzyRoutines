<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Handle invalid input and unresolved mathematics

Catch the category your application can handle. Invalid object types differ
from invalid values or domains; an undefined result differs from exhausted
numerical refinement. Preserve these distinctions in logs and user feedback.
Error categories live in `fuzzyroutines.exceptions`; `CentroidConvergenceError`
also belongs to the defuzzification API.

## Understand the category hierarchy

The following explicit instances demonstrate catch relationships; they do not
claim to trigger a real integration failure.

```python
from fuzzyroutines import CentroidConvergenceError
from fuzzyroutines.exceptions import (
    FuzzyRoutinesError, InvalidDomainError, InvalidParameterError,
    InvalidParameterTypeError, NumericalError, UndefinedResultError,
)

errors = (
    FuzzyRoutinesError("project error"), InvalidParameterTypeError("wrong kind"),
    InvalidParameterError("invalid value"), InvalidDomainError("invalid domain"),
    NumericalError("unresolved calculation"), UndefinedResultError("undefined result"),
    CentroidConvergenceError("refinement exhausted"),
)
assert all(isinstance(error, FuzzyRoutinesError) for error in errors)
assert isinstance(errors[1], TypeError) and isinstance(errors[2], ValueError)
assert isinstance(errors[3], InvalidParameterError)
assert isinstance(errors[5], ValueError) and isinstance(errors[5], NumericalError)
assert isinstance(errors[6], ArithmeticError)
print(tuple(type(error).__name__ for error in errors))
```

`UndefinedResultError` covers zero area or a result that cannot be represented
under the requested operation. It preserves both `ValueError` and numerical
catch contracts. User callbacks keep their own exceptions; the library does
not relabel arbitrary application failures as its own categories.

## Observe a real convergence failure without accepting a fallback

```python
from math import exp
from fuzzyroutines import (
    Centroid, CentroidConvergenceError, CentroidPolicy, ContinuousUniverse,
    IntegrationDomain, ScalarFuzzySet,
)


def DecayingGrade(coordinate: float) -> float:
    """Return a smooth valid grade on the declared nonnegative interval."""

    return exp(-coordinate)


fuzzySet = ScalarFuzzySet(ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True), DecayingGrade)
policy = CentroidPolicy(absoluteTolerance=1e-14, relativeTolerance=1e-14, maximumDepth=1)
try:
    Centroid(fuzzySet, IntegrationDomain(0, 1), policy)
except CentroidConvergenceError:
    print("Refinement exhausted: revise the domain or numerical policy")
else:
    raise AssertionError("the deliberately shallow integration unexpectedly converged")
```

This smooth callback requests tight tolerances with deliberately insufficient
depth. A real project should choose a justified domain and refinement budget,
then verify against an independent reference. Increasing depth alone cannot
prove that finite evaluations detected every narrow feature. For zero-area
handling see the [API recipe](api-recipes.md#handle-a-mathematically-undefined-result).
