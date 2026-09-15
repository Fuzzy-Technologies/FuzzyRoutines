# FuzzyRoutines

FuzzyRoutines is a Python library for fuzzy membership functions, fuzzy sets, fuzzy scales, and common t-norm and s-norm operators. It is maintained by [Fuzzy Technologies](https://fuzzy-technologies.github.io/).

> Technologies · Knowledge · Science

## Vision and positioning

FuzzyRoutines is being developed as a focused, mathematically reliable fuzzy-computing foundation for Python — not as a general-purpose computer algebra system or notebook environment.

The long-term goal is to make fuzzy models convenient to define, inspect, test, calculate, and embed in real software:

- validated membership-function families with explicit parameter domains;
- fuzzy-set operations, alpha-cuts, derived properties, and linguistic variables;
- mathematically specified negations, t-norms, s-norms, and defuzzification strategies;
- fuzzy scales with explicit coverage, overlap, tie, and confidence semantics;
- high-performance scalar and batch execution, with optional vectorized backends where benchmark evidence justifies them;
- parallel execution across CPU cores through independent Python worker processes and interpreters, without hidden shared mutable state;
- stable historical entry points alongside a small modern typed API.

Within fuzzy computing, the target is scientific-grade behavior: formulas traceable to authoritative sources, analytical solutions where practical, controlled numerical methods elsewhere, and executable evidence for boundaries and invariants. Python scripts, applications, and notebook systems are intended host environments; FuzzyRoutines supplies the specialized fuzzy-mathematics layer.

Performance is a first-class requirement, not a marketing claim. The target is low-overhead scalar evaluation and efficient batch workloads: eliminate duplicated computation, prefer validated analytical fast paths, allow caching only when results cannot become stale, and introduce vectorized or accelerated backends when measurements justify their complexity and dependency cost. Every optimization must preserve the mathematical contract and provide numerical-parity, timing, and memory evidence.

Concurrency is an explicit design target. The mathematical core should be deterministic, reentrant, process-safe, and free of hidden global mutable state; models and configurations should be serializable where practical. This allows callers to distribute independent workloads across multiple CPU cores using separate supported Python processes or interpreters on the same machine. FuzzyRoutines does not hide a global worker pool or force one orchestration framework. Thread-based and free-threaded CPython execution will be claimed only after race-safety, numerical-parity, and scaling benchmarks pass.

The library is also the reusable fuzzy foundation for Fuzzy Technologies research, expert systems, trading systems, decision models, and future products.

## Status

Version 2 is an active correctness-focused modernization. The historical public API remains available while documented defects are repaired through small, reviewable changes. Do not treat the current branch as a stable release promise.

Supported runtimes are CPython 3.13 and 3.14.

## Install from source

    git clone https://github.com/Fuzzy-Technologies/FuzzyRoutines.git
    cd FuzzyRoutines
    python -m pip install .

## Quick start

    from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction, TNorm, UniversalFuzzyScale

    membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
    fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0), linguisticName="Medium")
    scale = UniversalFuzzyScale()

    print(TNorm(0.4, 0.7, normType="algebraic"))
    print(fuzzySet.Defuz())
    print(scale.Fuzzy(0.5)["name"])

The legacy triangle argument order is a, b, c, where c is the apex. See the compatibility documentation before porting an external fuzzy model.

## Mathematics and compatibility

- Membership-function contracts: docs/mathematics/membership-function-contracts.md
- Membership-function ADR: docs/adr/0003-membership-function-contracts.md
- Operator and negation ADR: docs/adr/0004-operator-and-negation-contracts.md
- Parabolic-negation derivation: docs/mathematics/parabolic-negation-derivation.md
- Compatibility ledger: docs/compatibility/corrected-bug-ledger.md
- Benchmark protocol: docs/performance/benchmark-reproducibility-protocol.md

## Development

    python -m pip install -e .
    python -m pytest
    ruff check .

The project intentionally does not use ruff format. See docs/development-evidence-protocol.md for the review, evidence, and Python-style rules.
