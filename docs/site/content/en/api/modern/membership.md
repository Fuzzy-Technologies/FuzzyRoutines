<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Membership functions

The focused membership module owns the scalar analytical formulas. Its
immutable callable definitions can be passed directly to `ScalarFuzzySet`.
`Triangle` takes the conventional left, peak, right order; `Trapezoid` takes
left, plateau start, plateau end, right. Historical `MFunction` identifiers
retain their parameter conventions through explicit adapters.

## Custom scalar evaluators

`MembershipCallable` is the typed structural contract for custom functions,
lambdas, bound methods, and callable objects. No inheritance, wrapper, or
registration is required. The evaluator accepts one positional finite
`numbers.Real` coordinate and returns a finite real grade in `[0, 1]`;
booleans are excluded from both sides of the contract.

For annotations, `MembershipScalar` explicitly includes `float | numbers.Real`;
static checkers also accept built-in integers through their numeric promotion
to `float`. This avoids treating runtime registration as static inheritance:
`numbers.Real` alone does not accept ordinary `float` values in common type
checkers. A custom function annotated only `float -> float` narrows the broader
contract and cannot promise support for every real scalar. Use
`MembershipScalar` for its input, and that alias or `float` for its output.

`ScalarFuzzySet` construction checks callability without executing the
function. `Membership` checks the coordinate against the declared universe
before invocation, then validates the returned grade without coercion or
clamping. Incorrect signatures fail when called; custom exceptions propagate.
The protocol supplies neither runtime validation nor signature inspection.
Direct calls to a custom evaluator use its own validation behavior.

```python
from fuzzyroutines.defuzzification import Centroid
from fuzzyroutines.domain import ContinuousUniverse, IntegrationDomain
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.membership import MembershipCallable, MembershipScalar


def RisingGrade(coordinate: MembershipScalar) -> MembershipScalar:
    """Return a linear grade for coordinates in the closed unit interval."""

    return coordinate


membershipFunction: MembershipCallable = RisingGrade
fuzzySet = ScalarFuzzySet(
    ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True),
    membershipFunction,
)
centroid = Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))
```

The centroid is `2 / 3`, using adaptive numerical integration over the explicit
bounded integration domain. Generic callables do not acquire exact continuous
support, core, height, or analytical moments from this protocol. A function must
be sufficiently regular for the selected integration policy, and its grades
must remain consistent during evaluation. Mutable bookkeeping, such as counting
calls, is permitted when it does not change the grades. No callable snapshot is
created automatically. See the executable
[`custom_membership.py`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/examples/migration/custom_membership.py)
example.

The isolated static consumer smoke is reproducible with an optional mypy
installation:

```bash
python -m mypy --python-version 3.13 --strict --follow-imports silent --warn-unused-ignores tests/typing/custom_membership.py
```

It checks built-in float and integer calls, analytical evaluators, bound methods,
and rejects narrow inputs, nonnumeric results, and missing positional arguments.
Imported-module diagnostics are intentionally hidden by `--follow-imports
silent`; this is a consumer contract check, not the project-wide typing gate
planned in Task #95. Runtime finiteness, boolean exclusion, and grade range
cannot be proved by these annotations.

::: fuzzyroutines.membership
    options:
      members:
        - MembershipCallable
        - MembershipScalar
        - MembershipFunction
        - Hyperbolic
        - Bell
        - SShoulder
        - Triangle
        - Trapezoid
        - Gaussian
        - Logistic
        - HarringtonDesirability
