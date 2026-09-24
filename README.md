<!--
SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

<p align="center">
  <img src="docs/site/content/en/assets/brand/fuzzyroutines-horizontal.svg" alt="FuzzyRoutines by Fuzzy Technologies" width="720">
</p>

<p align="center">
  A mathematically explicit Python foundation for fuzzy sets, membership
  functions, linguistic models, and compatibility-safe modernization.
</p>

<p align="center">
  <a href="https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/workflows/quick-gate.yml"><img alt="Quick deterministic gate" src="https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/workflows/quick-gate.yml/badge.svg?branch=develop"></a>
  <a href="https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/workflows/api-reference.yml"><img alt="API reference build" src="https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/workflows/api-reference.yml/badge.svg?branch=develop"></a>
  <img alt="CPython 3.13 and 3.14" src="https://img.shields.io/badge/CPython-3.13%20%7C%203.14-3776AB?logo=python&amp;logoColor=white">
  <a href="LICENSE"><img alt="Apache License 2.0" src="https://img.shields.io/badge/license-Apache--2.0-blue"></a>
</p>

> **Development status:** version 2 is an active correctness-focused
> modernization. The historical API remains protected, while the modern typed
> surface grows through small, executable contracts. See the
> [current implementation boundary](docs/current-status.md).

## At a glance

| Area              | Current contract                                                                                                                          |
|---                |---                                                                                                                                        |
| Runtime           | CPython 3.13 and 3.14                                                                                                                     |
| Package version   | `2.0.0.dev0`; not yet a stable release promise                                                                                            |
| Modern API        | Root exports from [`fuzzyroutines`](docs/public-api-documentation-inventory.md#modern-package-exports)                                    |
| Compatibility API | [`fuzzyroutines.FuzzyRoutines`](docs/COMPATIBILITY.md) preserves the ADR-protected contract and documents the wider observed 1.0.3 facade |
| API reference     | [Published English reference](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/) built from the installed package         |
| License           | [Apache License 2.0](LICENSE) with attribution details in [NOTICE](NOTICE)                                                                |

FuzzyRoutines targets scientific-grade behavior within fuzzy computing:
explicit domains, traceable formulas, analytical results where practical,
controlled numerical methods elsewhere, and executable evidence for important
boundaries and invariants. It is a focused library, not a computer-algebra
system or notebook environment.

Start with the [canonical mathematical model](docs/MATHEMATICAL_MODEL.md) for
the integrated definitions, formulas, compatibility spellings, and explicit
implemented-versus-roadmap boundary.

## Install

```console
git clone --branch develop https://github.com/Fuzzy-Technologies/FuzzyRoutines.git
cd FuzzyRoutines
python -m pip install .
```

## Choose the API surface

| Surface                  | Use it for                                                        | Start here                                                                                 |
|---                       |---                                                                |---                                                                                         |
| Modern typed API         | New code with explicit universes, policies, and evidence strength | [Modern API inventory](docs/public-api-documentation-inventory.md#modern-package-exports)  |
| Historical compatibility | Existing software written against the 1.0.3-style facade          | [Protected and observed surfaces](docs/COMPATIBILITY.md#adr-protected-historical-contract) |
| Migration boundary       | Moving one supported scenario at a time                           | [Canonical migration guide](docs/COMPATIBILITY.md#migration-examples)                      |

### Modern example

```python
from fuzzyroutines import ContinuousUniverse, DeriveProperties, ScalarFuzzySet
from fuzzyroutines.FuzzyRoutines import MFunction

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
fuzzySet = ScalarFuzzySet(universe, membershipFunction.mju)
properties = DeriveProperties(membershipFunction, universe)

assert fuzzySet.Membership(0.5) == 1.0
assert properties.core.Contains(0.5)
assert properties.height == 1.0
```

A declared [`ContinuousUniverse`](docs/mathematics/universe-support-contract.md)
is part of fuzzy-set identity. An
[`IntegrationDomain`](docs/adr/0005-numerical-defuzzification-policy.md) is only
a finite interval used by a numerical method; it is never mathematical
support.

### Historical compatibility example

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction, TNorm

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
fuzzySet = FuzzySet(
    membershipFunction,
    supportSet=(0.0, 1.0),
    linguisticName="Medium",
)

print(TNorm(0.4, 0.7, normType="algebraic"))
print(fuzzySet.Defuz())
```

The legacy triangle order is `a, b, c`, where `c` is the apex. Protected
names and corrected historical defects are tracked in the
[compatibility ledger](docs/compatibility/corrected-bug-ledger.md).

## Core contracts

| Concept                     | Mathematical contract                                                                          | Architecture decision                                                              |
|-----------------------------|------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| Membership functions        | [Families, formulas, and parameter domains](docs/mathematics/membership-function-contracts.md) | [ADR-0003](docs/adr/0003-membership-function-contracts.md)                         |
| Universes and support       | [Universe, support, core, boundary, and height](docs/mathematics/universe-support-contract.md) | [ADR-0002](docs/adr/0002-universe-support-semantics.md)                            |
| Negations and scalar norms  | [Formula and algorithm invariants](docs/mathematics/source-algorithm-invariants.md)            | [ADR-0004](docs/adr/0004-operator-and-negation-contracts.md)                       |
| Fuzzy-set operations        | [Complement, intersection, union, and difference](docs/mathematics/fuzzy-set-operations.md)    | [ADR-0008](docs/adr/0008-fuzzy-set-difference-semantics.md)                        |
| Alpha-cuts                  | [Exact and sampled alpha-cut evidence](docs/mathematics/alpha-cuts.md)                         | [Universe semantics](docs/adr/0002-universe-support-semantics.md)                  |
| Height and normalization    | [Exact evidence and fail-closed normalization](docs/mathematics/fuzzy-set-normalization.md)    | [Numerical policy](docs/adr/0005-numerical-defuzzification-policy.md)              |
| Equality and inclusion      | [Explicit comparison domains and policies](docs/mathematics/fuzzy-set-relations.md)            | [Modern domain boundary](docs/current-status.md#implemented-modern-domain-surface) |
| Linguistic terms and scales | [Immutable typed representation](docs/mathematics/linguistic-term-model.md)                    | [Roadmap boundary](docs/current-status.md#still-in-the-v2-roadmap)                 |

## Documentation map

| Need                                  | Canonical source                                                                                                                                         |
|---------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| What exists now                       | [Current implementation status](docs/current-status.md)                                                                                                  |
| Public symbols                        | [Public API inventory](docs/public-api-documentation-inventory.md)                                                                                       |
| Mathematical definitions              | [`docs/mathematics`](docs/mathematics/)                                                                                                                  |
| Compatibility and migration           | [Canonical guide](docs/COMPATIBILITY.md) · [Corrected-bug ledger](docs/compatibility/corrected-bug-ledger.md)                                            |
| Benchmarks and performance claims     | [Results](docs/BENCHMARKS.md) · [Protocol](docs/performance/benchmark-reproducibility-protocol.md)                                                       |
| Tests, tools, examples, and artifacts | [Executable documentation](docs/executable-tests-tools-and-examples.md)                                                                                  |
| Contribution and evidence rules       | [Development evidence protocol](docs/development-evidence-protocol.md) · [Python style](docs/python-code-style.md)                                       |
| API documentation architecture        | [ADR-0010](docs/adr/0010-api-documentation-architecture.md) · [Reproducible build](docs/site/README.md)                                                  |

## Development

```console
python -m pip install -e .
python -m tools.test_runner
ruff check .
python tools/build_api_reference.py
```

The canonical runner discovers the complete suite, uses independent
`pytest-xdist` worker **processes** by default, caps automatic parallelism at
12, and moves tests marked `serial` into a separate sequential phase. Use
`--jobs N`, `--timeout N`, `--serial`, or `--fail-fast` for an explicit run.
It never retries failures automatically.

The project intentionally does not use `ruff format`. Markdown tables are
source-aligned and checked automatically. Generated API HTML is disposable
output under `_build/api-reference/`; annotations, English Google-style
Markdown docstrings, and tracked Markdown remain the sources of truth.

## Roadmap boundary

The current typed surface already includes explicit scalar universes, immutable
fuzzy sets, operations, derived properties, alpha-cuts, comparison policies,
and linguistic representations. Symmetric difference, executable convexity,
defuzzification methods beyond the implemented centroid contract, typed
linguistic lookup, vectorized backends, and free-threaded CPython support remain
roadmap work. Performance and concurrency claims require numerical-parity,
timing, memory, and race-safety evidence.

The generated reference is composed with the
[FuzzyRoutines GitHub Pages site](https://fuzzy-technologies.github.io/FuzzyRoutines/).
Pull requests and `develop` produce preview artifacts; production deployment
occurs only from the approved `master` branch. Stable routes separate the
moving English reference from reserved translation and release-version paths.

## License

Source code, tests, documentation, examples, tools, workflows, and
project-owned site assets are licensed under the
[Apache License 2.0](LICENSE). Redistributions must preserve the license,
copyright, and attribution notices, including [NOTICE](NOTICE).

The license does not grant permission to use Fuzzy Technologies trade names or
marks beyond reasonable attribution and the NOTICE requirements. See the
[licensing and provenance policy](docs/licensing.md).
