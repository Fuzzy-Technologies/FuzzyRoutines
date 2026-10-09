<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Finite scalar input policy

## Status

Implemented scalar contract. Task #62 defined the policy and Task #63 removed
the silent sentinel and exception-to-zero paths from public scalar operators
and built-in membership evaluation.

## Rule

Every validated scalar input must be finite; a fuzzy degree must additionally
lie in the closed interval `[0, 1]`. Boolean values are never accepted as scalar
numbers. The historical facade accepts built-in `int` and `float` values.
The modern API uses the broader `numbers.Real` contract, including `Fraction`,
without converting a valid input merely for type checking. Its public typing
alias is `MembershipScalar`.

Invalid scalar inputs include NaN, positive infinity, negative infinity,
`True`, `False`, and non-numeric values. Historical operators and membership
evaluators raise `ValueError` with a human-readable diagnostic. Modern scalar
validation distinguishes `InvalidParameterTypeError` (also `TypeError`) from
`InvalidParameterError` (also `ValueError`); analytical-family constructors
retain their documented `ValueError`-compatible parameter validation.
Invalid inputs never produce NaN, infinity, or a silent `None` sentinel.

## Scope

- FuzzyNOT, FuzzyNOTParabolic, FuzzyAND, FuzzyOR, TNorm, and SCoNorm apply the fuzzy-degree rule.
- Composition helpers validate every supplied fuzzy degree before evaluation.
- Membership functions accept finite real coordinates and finite, function-specific parameters; their domain constraints are defined with the individual membership contracts.
- This policy does not coerce strings, booleans, `Decimal` values, or arrays.
  A direct call to a user-supplied evaluator retains that evaluator's own
  behavior; `ScalarFuzzySet.Membership` validates its input and returned grade.
  Exceptions raised inside user callbacks propagate unchanged.

## Evidence

The tests in `tests/test_finite_number_policy.py` exercise public operator and
membership boundaries, explicit error behavior, extreme finite coordinates,
and propagation of internal programming errors. Composition-specific coverage
is retained in `tests/test_composition_validation.py`. Modern contracts,
registered real scalars, and error categories are covered by
`tests/test_public_typing_runtime.py`, `tests/test_fuzzy_set_operations.py`, and
`tests/test_domain_exceptions.py`.
