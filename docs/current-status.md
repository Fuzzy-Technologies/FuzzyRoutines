# Current implementation status

This page records the public boundary of the active `develop` branch. It
separates implemented and tested behavior from the FuzzyRoutines 2 roadmap. The
first stable modernization release remains planned as `2.0.0`; current package
metadata uses `2.0.0.dev0`.

## Implemented and verified

- Historical imports and public names remain covered by compatibility tests.
- Built-in membership families have documented formula and parameter contracts. Strict construction-time validation is not yet complete for every family.
- Classical logic, algebraic, bounded, and drastic t-norm/s-norm families have reference and property tests.
- `TNormCompose` and `SCoNormCompose` validate every operand before evaluation.
- `FuzzyNOT` requires a finite real `alpha` in the open interval `(0, 1)`.
- Bell membership evaluation does not mutate its parameter mapping and has a concurrent reentrancy regression test.
- `FuzzySet.Defuz()` and `defuzValue` recalculate from the current membership parameters and integration interval.
- `FuzzyScale.Fuzzy()` evaluates each term once and deliberately selects the later term when memberships tie.
- `UniversalFuzzyScale` no longer constructs and discards the default three-level scale.
- Benchmark and diagnostic tools emit machine-readable JSON and have end-to-end command-line tests.

The corresponding accepted changes are
[#184](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/184),
[#185](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/185),
[#186](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/186),
[#187](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/187),
[#188](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/188),
[#189](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/189), and
[#190](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/190).

## Still in the v2 roadmap

- strict parameter-domain validation for all membership families;
- the proved closed-form parabolic-negation implementation;
- explicit universe, integration-domain, mathematical-support, core, and height semantics;
- fuzzy-set complement, union, intersection, equality, and inclusion;
- alpha-cuts and derived fuzzy-set properties;
- analytical centroid moments where stable closed forms exist;
- deterministic adaptive quadrature with explicit tolerance and convergence errors elsewhere;
- a focused typed module API with the historical module retained as a compatibility facade;
- optional vectorized execution, subject to numerical-parity, time, memory, and dependency evidence;
- free-threaded CPython support, subject to race-safety and scaling evidence.

## Performance and concurrency claims

Performance changes are accepted only with reproducible before/after
measurements and numerical-parity tests. Current scalar optimizations remove
known duplicate work; they do not establish a universal speed claim.

Ordinary independent Python processes can execute independent models.
Thread-safe or free-threaded execution is not yet a supported contract for the
complete library. Individual paths may receive reentrancy tests before that
broader claim is made.

## Release status

Routine pull-request workflows build and clean-install packages but cannot
publish them. Release candidates, signed tags, GitHub Releases, and PyPI Trusted
Publishing belong to the release milestone and require the complete
human-reviewed readiness gate.
