<!--
SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

<p align="center">
  <img src="https://raw.githubusercontent.com/Fuzzy-Technologies/FuzzyRoutines/master/docs/site/content/en/assets/brand/fuzzyroutines-alice.png" alt="FuzzyRoutines with Alice in the Fuzzy Technologies research laboratory" width="960">
</p>

<p align="center">
  A mathematically explicit Python foundation for fuzzy sets, membership
  functions, linguistic models, and compatibility-safe modernization.
</p>

<p align="center">
  <a href="https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/workflows/quick-gate.yml"><img alt="Quick deterministic gate" src="https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/workflows/quick-gate.yml/badge.svg?branch=master"></a>
  <a href="https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/workflows/api-reference.yml"><img alt="API reference build" src="https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/workflows/api-reference.yml/badge.svg?branch=master"></a>
  <img alt="CPython 3.13 and 3.14" src="https://img.shields.io/badge/CPython-3.13%20%7C%203.14-3776AB?logo=python&amp;logoColor=white">
  <a href="https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/LICENSE"><img alt="Apache License 2.0" src="https://img.shields.io/badge/license-Apache--2.0-blue"></a>
</p>

> **FuzzyRoutines 2.0** combines a modern typed API with the protected
> historical API. See the
> [current implementation boundary](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/current-status.md).

## At a glance

| Area                | Current contract                                                                                                                                                                                           |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Runtime             | CPython 3.13 and 3.14                                                                                                                                                                                      |
| Package version     | `2.0.0`                                                                                                                                                                                                    |
| Modern API          | Root exports from [`fuzzyroutines`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/public-api-documentation-inventory.md#modern-package-exports)                                     |
| Compatibility API   | [`fuzzyroutines.FuzzyRoutines`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/COMPATIBILITY.md) preserves the ADR-protected contract and documents the wider observed 1.0.3 facade  |
| API reference       | [Published English reference](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/) built from the installed package                                                                          |
| License             | [Apache License 2.0](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/LICENSE) with attribution details in [NOTICE](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/NOTICE) |

FuzzyRoutines targets scientific-grade behavior within fuzzy computing:
explicit domains, traceable formulas, analytical results where practical,
controlled numerical methods elsewhere, and executable evidence for important
boundaries and invariants. It is a focused library, not a computer-algebra
system or notebook environment.

Start with the [canonical mathematical model](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/MATHEMATICAL_MODEL.md) for
the integrated definitions, formulas, compatibility spellings, and explicit
implemented-versus-roadmap boundary.

## Install

Use CPython 3.13 or 3.14:

```console
python -m pip install fuzzyroutines==2.0.0
```

Historical 1.x packages do not provide the modern API shown below. For a
source checkout, see [Development](#development).

The [quick start](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/site/content/en/quick-start.md) explains installation
and classifies a 24 °C measurement.
Explore [nine worked scenarios](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/site/content/en/guides/index.md), with
independent numerical checks and eleven reproducible scientific figures, or
reconstruct the [historical Universal Fuzzy Scale](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/site/content/en/guides/universal-fuzzy-scale.md), or
browse the [membership gallery](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/site/content/en/guides/membership-families.md).
The [computation diagrams](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/site/content/en/guides/workflow.md) explain the
different workflows; the [public example index](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/site/content/en/guides/example-index.md)
links all 193 inventoried public symbols to executed examples.
From a checkout with the package installed, `python -I examples/guide.py` runs
every scenario without NumPy, Matplotlib, network access, or file creation.

## Choose the API surface

| Surface                    | Use it for                                                          | Start here                                                                                                                                                 |
| -------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Modern typed API           | New code with explicit universes, policies, and evidence strength   | [Modern API inventory](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/public-api-documentation-inventory.md#modern-package-exports)  |
| Historical compatibility   | Existing software written against the 1.0.3-style facade            | [Protected and observed surfaces](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/COMPATIBILITY.md#adr-protected-historical-contract) |
| Migration boundary         | Moving one supported scenario at a time                             | [Canonical migration guide](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/COMPATIBILITY.md#migration-examples)                      |

### Modern example

```python
from fuzzyroutines import ContinuousUniverse, DeriveProperties, ScalarFuzzySet, Triangle

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
membership = Triangle(left=0.0, peak=0.5, right=1.0)
fuzzySet = ScalarFuzzySet(universe, membership)
properties = DeriveProperties(membership, universe)

assert fuzzySet.Membership(0.5) == 1.0
assert properties.core.Contains(0.5)
assert properties.height == 1.0
```

A declared [`ContinuousUniverse`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/mathematics/universe-support-contract.md)
is part of fuzzy-set identity. An
[`IntegrationDomain`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/adr/0005-numerical-defuzzification-policy.md) is only
a finite interval used by a numerical method; it is never mathematical
support.

### Historical compatibility example

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction, TNorm

membership = MFunction("triangle", a=0.0, b=1.0, c=0.5)
fuzzySet = FuzzySet(
    membership,
    supportSet=(0.0, 1.0),
    linguisticName="Medium",
)

print(TNorm(0.4, 0.7, normType="algebraic"))
print(fuzzySet.Defuz())
```

The legacy triangle order is `a, b, c`, where `c` is the apex. Protected
names and corrected historical defects are tracked in the
[compatibility ledger](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/compatibility/corrected-bug-ledger.md).

## Core contracts

| Concept                       | Mathematical contract                                                                                                                                          | Architecture decision                                                                                                                              |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Membership functions          | [Families, formulas, and parameter domains](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/mathematics/membership-function-contracts.md) | [ADR-0003](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/adr/0003-membership-function-contracts.md)                         |
| Universes and support         | [Universe, support, core, boundary, and height](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/mathematics/universe-support-contract.md) | [ADR-0002](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/adr/0002-universe-support-semantics.md)                            |
| Negations and scalar norms    | [Formula and algorithm invariants](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/mathematics/source-algorithm-invariants.md)            | [ADR-0004](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/adr/0004-operator-and-negation-contracts.md)                       |
| Fuzzy-set operations          | [Complement, intersection, union, and difference](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/mathematics/fuzzy-set-operations.md)    | [ADR-0008](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/adr/0008-fuzzy-set-difference-semantics.md)                        |
| Alpha-cuts                    | [Exact and sampled alpha-cut evidence](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/mathematics/alpha-cuts.md)                         | [Universe semantics](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/adr/0002-universe-support-semantics.md)                  |
| Height and normalization      | [Exact evidence and fail-closed normalization](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/mathematics/fuzzy-set-normalization.md)    | [Numerical policy](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/adr/0005-numerical-defuzzification-policy.md)              |
| Equality and inclusion        | [Explicit comparison domains and policies](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/mathematics/fuzzy-set-relations.md)            | [Modern domain boundary](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/current-status.md#implemented-modern-domain-surface) |
| Linguistic terms and scales   | [Immutable typed representation](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/mathematics/linguistic-term-model.md)                    | [Roadmap boundary](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/current-status.md#still-in-the-v2-roadmap)                 |

## Documentation map

| Need                                      | Canonical source                                                                                                                                                                                                                                                                                                                                    |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| What exists now                           | [Current implementation status](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/current-status.md)                                                                                                                                                                                                                             |
| Audited contracts and release limits      | [Project readiness audit](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/audits/2026-10-05-project-audit.md)                                                                                                                                                                                                                  |
| Public symbols                            | [Public API inventory](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/public-api-documentation-inventory.md)                                                                                                                                                                                                                  |
| Static types and custom callbacks         | [Public modern typing](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/public-typing.md)                                                                                                                                                                                                                                       |
| Mathematical definitions                  | [`docs/mathematics`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/tree/master/docs/mathematics/)                                                                                                                                                                                                                                             |
| Compatibility and migration               | [Canonical guide](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/COMPATIBILITY.md) · [Corrected-bug ledger](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/compatibility/corrected-bug-ledger.md)                                                                                                       |
| Release changes and version decision      | [Development changelog](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/CHANGELOG.md) · [1.0.3 migration](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/migration/1.0.3-to-2.0.0.md) · [Version rationale](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/release-version-decision.md) |
| Benchmarks and performance claims         | [Results](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/BENCHMARKS.md) · [Protocol](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/performance/benchmark-reproducibility-protocol.md)                                                                                                                  |
| Tests, tools, examples, and artifacts     | [Executable documentation](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/executable-tests-tools-and-examples.md)                                                                                                                                                                                                             |
| Contribution and evidence rules           | [Development evidence protocol](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/development-evidence-protocol.md) · [Python style](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/python-code-style.md)                                                                                                  |
| Optional vectorization strategy           | [ADR-0015](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/adr/0015-optional-vectorized-execution-strategy.md) · [Scalar/array evidence](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/performance/vectorized-membership-comparison.md)                                                                 |
| API documentation architecture            | [ADR-0010](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/adr/0010-api-documentation-architecture.md) · [Reproducible build](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/site/README.md)                                                                                                             |

## Development

For an editable source checkout:

```console
git clone --branch master https://github.com/Fuzzy-Technologies/FuzzyRoutines.git
cd FuzzyRoutines
python -m pip install -e .
python -m pip install -r requirements.txt
python -m pytest -q tests/test_membership_function_contracts.py
python -m ruff check fuzzyroutines/membership.py
```

Choose the tests and lint paths for the files and contracts being changed.
PR CI runs the complete deterministic suite, typing, documentation builds,
and package installation gates. Full local regression and build runs are
reserved for an explicit maintainer request.

The canonical full-suite runner, `python -m tools.test_runner`, discovers the complete suite, uses independent
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
and linguistic representations. Inline modern annotations, `py.typed`, strict
source checks, and installed-wheel consumer checks are implemented; see the
[typing contract](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/public-typing.md). Symmetric difference, executable
convexity, defuzzification methods beyond the implemented centroid contract,
vectorized backends, and free-threaded CPython support remain roadmap work.
Performance and concurrency claims require numerical-parity,
timing, memory, and race-safety evidence.

The generated reference is composed with the
[FuzzyRoutines GitHub Pages site](https://fuzzy-technologies.github.io/FuzzyRoutines/).
Pull requests and `develop` produce preview artifacts; production deployment
occurs only from the approved `master` branch. Stable routes separate the
moving references in English, Russian and Simplified Chinese. The version index
links to tagged sources for historical versions. Separately hosted documentation
snapshots for individual releases are not currently provided.

## License

Source code, tests, documentation, examples, tools, workflows, and
project-owned site assets are licensed under the
[Apache License 2.0](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/LICENSE). Redistributions must preserve the license,
copyright, and attribution notices, including [NOTICE](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/NOTICE).

The license does not grant permission to use Fuzzy Technologies trade names or
marks beyond reasonable attribution and the NOTICE requirements. See the
[licensing and provenance policy](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/master/docs/licensing.md).
