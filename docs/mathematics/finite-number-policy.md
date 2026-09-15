# Finite scalar input policy

## Status

Implemented scalar contract. Task #62 defined the policy and Task #63 removed
the silent sentinel and exception-to-zero paths from public scalar operators
and built-in membership evaluation.

## Rule

Every public scalar fuzzy operator and membership evaluator accepts only finite instances of int or float. Boolean values are never scalar numbers. A fuzzy degree must additionally lie in the closed interval [0, 1].

Invalid scalar inputs include NaN, positive infinity, negative infinity, True, False, and non-numeric values. Public APIs must raise ValueError with a stable human-readable message; they must never return NaN, infinity, or a silent None sentinel for these inputs.

## Scope

- FuzzyNOT, FuzzyNOTParabolic, FuzzyAND, FuzzyOR, TNorm, and SCoNorm apply the fuzzy-degree rule.
- Composition helpers validate every supplied fuzzy degree before evaluation.
- Membership functions accept finite real coordinates and finite, function-specific parameters; their domain constraints are defined with the individual membership contracts.
- This policy does not coerce strings, booleans, Decimal values, or array-like values.

## Evidence

The tests in `tests/test_finite_number_policy.py` exercise public operator and
membership boundaries, explicit error behavior, extreme finite coordinates,
and propagation of internal programming errors. Composition-specific coverage
is retained in `tests/test_composition_validation.py`.
