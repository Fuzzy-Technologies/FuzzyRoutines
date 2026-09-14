# Finite scalar input policy

## Status

Target v2 contract. The current legacy implementation has inconsistent handling of non-finite values; this document and its executable tests define the correction target for Tasks #62 and #63.

## Rule

Every public scalar fuzzy operator and membership evaluator accepts only finite instances of int or float. Boolean values are never scalar numbers. A fuzzy degree must additionally lie in the closed interval [0, 1].

Invalid scalar inputs include NaN, positive infinity, negative infinity, True, False, and non-numeric values. Public APIs must raise ValueError with a stable human-readable message; they must never return NaN, infinity, or a silent None sentinel for these inputs.

## Scope

- FuzzyNOT, FuzzyNOTParabolic, FuzzyAND, FuzzyOR, TNorm, and SCoNorm apply the fuzzy-degree rule.
- Composition helpers validate every supplied fuzzy degree before evaluation.
- Membership functions accept finite real coordinates and finite, function-specific parameters; their domain constraints are defined with the individual membership contracts.
- This policy does not coerce strings, booleans, Decimal values, or array-like values.

## Evidence

The pending tests in tests/test_finite_number_policy.py encode the public correction target. Task #63 will implement it consistently in the shared validation path.
