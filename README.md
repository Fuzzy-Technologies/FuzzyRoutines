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

The current `develop` branch already provides:

- the historical membership families and public import path, protected by compatibility tests;
- strict parameter validation and transitional `gaussian`, `logistic`, `sShoulder`, and `harringtonDesirability` registry names in the historical factory;
- verified classical t-norm and s-norm families, with validation of every composed operand;
- finite-domain validation for parameterized `FuzzyNOT`;
- analytical parabolic negation without an epsilon-driven scan;
- reentrant Bell evaluation without temporary mutation of shared parameters;
- immutable scalar universe and numerical integration-domain value objects;
- an explicit compatibility mapping from legacy `supportSet` tuples to
  `IntegrationDomain`;
- `FuzzySet` centroid access that reflects current membership parameters and integration interval;
- deterministic scale lookup with one membership evaluation per term and an explicit later-term tie policy;
- reproducible command-line benchmarks and diagnostic reports.

Derived support/core properties, fuzzy-set algebra, alpha-cuts,
analytical/adaptive defuzzification strategy, the complete typed module API,
optional vectorization, and free-threaded execution remain roadmap work. See the
[current implementation status](docs/current-status.md) for the exact boundary
and evidence.

The focused typed modules will become the default API for new users. The
historical `FuzzyRoutines.py` entry point will remain a compatibility facade:
old names and parameter conventions will delegate to or explicitly adapt the
same mathematically correct core rather than own duplicate implementations.

## Install from source

    git clone https://github.com/Fuzzy-Technologies/FuzzyRoutines.git
    cd FuzzyRoutines
    python -m pip install .

## Current compatibility API example

    from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction, TNorm, UniversalFuzzyScale

    membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
    fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0), linguisticName="Medium")
    scale = UniversalFuzzyScale()

    print(TNorm(0.4, 0.7, normType="algebraic"))
    print(fuzzySet.Defuz())
    print(scale.Fuzzy(0.5)["name"])

This example uses the current historical facade. Its triangle argument order is
`a, b, c`, where `c` is the apex. New v2 examples will default to the focused
modern API after its parameter contracts are implemented.

## Modern domain API

    from fuzzyroutines import ContinuousUniverse, DiscreteUniverse, IntegrationDomain

    universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
    integrationDomain = IntegrationDomain(0.1, 0.9).ValidateWithin(universe)
    sampledUniverse = DiscreteUniverse((0.0, 0.5, 1.0))

Universes are part of fuzzy-set identity. An `IntegrationDomain` is only a
finite operational interval for a numerical method; it is never mathematical
support. See the universe/support contract for the exact semantics.

## Mathematics and compatibility

- Membership-function contracts: docs/mathematics/membership-function-contracts.md
- Membership-function ADR: docs/adr/0003-membership-function-contracts.md
- Universe/support contract: docs/mathematics/universe-support-contract.md
- Universe/support ADR: docs/adr/0002-universe-support-semantics.md
- Operator and negation ADR: docs/adr/0004-operator-and-negation-contracts.md
- Parabolic-negation derivation: docs/mathematics/parabolic-negation-derivation.md
- Compatibility ledger: docs/compatibility/corrected-bug-ledger.md
- Benchmark protocol: docs/performance/benchmark-reproducibility-protocol.md
- Current implementation status: docs/current-status.md

## Development

    python -m pip install -e .
    python -m tools.test_runner
    ruff check .

The project intentionally does not use ruff format. See docs/development-evidence-protocol.md for the review, evidence, and Python-style rules.

The canonical runner discovers the complete suite, uses process workers by
default, caps automatic parallelism at 12, and executes tests marked `serial`
in a separate sequential phase. Use `--jobs N`, `--timeout N`, `--serial`, or
`--fail-fast` to override one run. It never retries failures automatically.
