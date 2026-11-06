<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0032: Supported Python matrix for FuzzyRoutines 2.2

- Status: Proposed
- Date: 2026-11-06
- Related Task: [#380](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/380)
- Related Feature: [#356](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/356)
- Retains the runtime boundary in [ADR-0006](0006-packaging-versioning-release-policy.md)

## Context

The current [package metadata](../../pyproject.toml) sets `Requires-Python` to
`>=3.13`. The documented and tested release matrix covers CPython 3.13 and
3.14. The open-ended metadata bound does not establish support for a future
interpreter, a free-threaded build, or an alternative implementation.

### Consumer evidence

- **TKSBrokerAPI.** At `b963c54039f013d432220186ae35a22359c5a773`, the
  [package declaration](https://github.com/Fuzzy-Technologies/TKSBrokerAPI/blob/b963c54039f013d432220186ae35a22359c5a773/setup.py)
  permits Python 3.9 and later. The
  [container recipe](https://github.com/Fuzzy-Technologies/TKSBrokerAPI/blob/b963c54039f013d432220186ae35a22359c5a773/deploy/Dockerfile)
  specifies Python 3.11. Its
  [requirements](https://github.com/Fuzzy-Technologies/TKSBrokerAPI/blob/b963c54039f013d432220186ae35a22359c5a773/requirements.txt)
  permit FuzzyRoutines 1.0.3 and later, subject to resolver compatibility.
  FuzzyRoutines 2.x requires a newer interpreter than the container recipe
  supplies. Deployment versions and migration results on either supported
  Python remain unknown.
- **FuzzyRoutines public TKSBrokerAPI replay.** The
  [pinned replay](../performance/public-consumer-batch-replay.md) ran on
  CPython 3.14.8 with NumPy 2.3.5 and matched all 30 upstream expected
  labels and rounded percentages. It exercises extracted test inputs.
  Production runtime and application-level behavior remain unknown.
- **Private FMA and robot consumers.** The
  [migration record](../migration/consumer-scale-boundary.md) identifies
  the integration gap. Runtime versions, dependency locks, and
  application-level results are unavailable.
- **FuzzyClassificator lineage.** The
  [consumer inventory](../compatibility/legacy-consumers.md) records
  historical API use. Runtime versions, current maintenance, and
  installation evidence remain unknown.

## Language and dependency constraints

- The package uses [PEP 695](https://peps.python.org/pep-0695/) type alias and
  type-parameter syntax, including in [membership](../../fuzzyroutines/membership.py)
  and [inference](../../fuzzyroutines/inference.py). Python 3.11 and earlier
  cannot parse those modules. Lowering metadata to accommodate the
  container recipe would require source and typing changes as well as
  application-level testing.
- On the reviewed base `81992dddd8417588072d60ce2c03e0b94a2a9f88`,
  CPython 3.12.14 compiled all 24 package files and passed a narrow
  dependency-free source check. CPython 3.13.17 passed the same source
  check. The check constructs the modern historical scale, imports the
  historical facade, classifies 0.5 as `Med`, and confirms that the imports
  leave NumPy unloaded. A source smoke does not exercise wheel installation,
  the full mathematical and compatibility gates, or consumer environments.
- An offline wheel built from that base with setuptools 84.0.0 retained
  `Requires-Python: >=3.13`. A standard pip dry-run on CPython 3.12.14
  rejected the wheel on this requirement. A clean offline install on
  CPython 3.13.17 passed the same scalar smoke from outside the checkout.
- The scalar package declares no mandatory runtime dependencies. The optional
  NumPy floor is 2.3.5, whose [upstream release notes](https://numpy.org/doc/stable/release/2.3.5-notes.html)
  include Python 3.12. The minimum alone does not establish coverage for the
  resolver-selected version, wheels on every platform, typing, or development
  and documentation tooling.
- The [2.1 release evidence](../audits/2026-10-19-release-acceptance.md) records
  isolated builds and installs on both supported Python versions. This
  historical evidence identifies working release gates. A 2.2 candidate
  needs its own results.

## Decision

Keep CPython 3.13 and 3.14 as the supported 2.2 matrix and retain
`Requires-Python >=3.13`. The known Python 3.11 consumer recipe and the
CPython 3.12 source smoke do not justify changing either boundary. Maintain
the historical public API and scale semantics in accordance with
[ADR-0001](0001-backward-compatibility-contract.md) and
[ADR-0016](0016-linguistic-encodings-and-historical-preset.md).

A separate matrix expansion proposal should identify a maintained consumer
with an exact interpreter, platform, and dependency lock that requires the
new cell. Record isolated sdist and wheel builds and installs, the base and
optional-dependency matrices, strict typing, deterministic scalar and
historical-scale tests, and a reproducible consumer integration run. Review
those results before changing metadata, classifiers, documentation, or CI.

## Reproduce the source check

Run from the reviewed checkout under each interpreter. This checks source
behavior only and does not require a package install.

```bash
python - <<'PY'
import sys
from pathlib import Path

from fuzzyroutines import CreateUniversalFuzzyScale
from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale

paths = sorted(Path("fuzzyroutines").rglob("*.py"))
for path in paths:
    compile(path.read_bytes(), str(path), "exec")

assert CreateUniversalFuzzyScale().terms
assert UniversalFuzzyScale().Fuzzy(0.5)["name"] == "Med"
assert "numpy" not in sys.modules
print(sys.version.split()[0], len(paths))
PY
```

For an equivalent installed check, run the import and assertions from
outside the checkout with the supported interpreter in a clean environment.
On 3.12, `python -m pip install --no-index --no-deps --dry-run <wheel>`
checks the declared floor without modifying the environment.
