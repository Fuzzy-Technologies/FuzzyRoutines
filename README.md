# FuzzyRoutines

FuzzyRoutines is a Python library for fuzzy membership functions, fuzzy sets, fuzzy scales, and common t-norm and s-norm operators. It is maintained by [Fuzzy Technologies](https://fuzzy-technologies.github.io/).

> Technologies · Knowledge · Science

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
