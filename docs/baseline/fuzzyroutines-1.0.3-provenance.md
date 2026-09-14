# FuzzyRoutines 1.0.3 Canonical Provenance Baseline

This record freezes the legacy baseline used by the modernization plan.

It describes the historical state **before** current modernization commits on `develop`.

## Repository provenance

Canonical repository:

https://github.com/Fuzzy-Technologies/FuzzyRoutines

Historical baseline recorded during the 2026-09-12 audit:

| Ref | Commit |
| --- | --- |
| `master` | `ceb9403d44c19ba73fd351e1b05091d337280864` |
| `develop` | `db335f3661402c2300676fd9131dc1bba8e4d675` |
| tag `1.0.3` | `ceb9403d44c19ba73fd351e1b05091d337280864` |

At that baseline, `master` was two commits ahead of `develop`.

The live `develop` branch now advances as modernization work is merged. Do not use the moving branch head as a substitute for the frozen legacy revision.

## Historical package metadata

Package:

https://pypi.org/project/fuzzyroutines/1.0.3/

PyPI release:

- version: `1.0.3`;
- release date: 2019-09-01;
- latest release at the time of this provenance record;
- maintainer shown by PyPI: `devopshq`;
- author metadata: Timur Gilmullin;
- license: MIT;
- classifier: Python 3.6.

## Published artifact

PyPI exposes one artifact for 1.0.3:

```text
fuzzyroutines-1.0.3-py3-none-any.whl
```

Metadata:

- size: 10.5 kB;
- uploaded: 2019-09-01;
- source distribution: none;
- Trusted Publishing: no;
- upload client included CPython 3.6.7 / twine 1.13.0.

Published hashes:

```text
SHA256      5febdfab36109c7055374c217ec8d8b6fe2c5a1b1e44a90868513b8bb38c1333
MD5         01ddee9a8b9dd662d332c6dc25641f1b
BLAKE2b-256 71679174ab0b741bb615bb80876dcd0eff6f92107d0cd8e2f86941b7b4f7a3af
```

The SHA-256 value is the canonical artifact-integrity value for reproducibility checks.

## Legacy release/build lineage

The repository's historical packaging path is coupled to Travis CI:

- Python 3.6;
- dynamic version generation from Travis environment variables;
- legacy `devopshq` project URLs;
- encrypted Travis/PyPI deployment configuration.

This provenance record preserves that lineage as evidence. It does **not** endorse reusing the old publication mechanism.

## Reproduction commands

Repository revision:

```bash
git fetch --tags origin
git checkout ceb9403d44c19ba73fd351e1b05091d337280864
git rev-parse HEAD
```

Expected:

```text
ceb9403d44c19ba73fd351e1b05091d337280864
```

Tag relationship:

```bash
git rev-list -n 1 1.0.3
```

Expected:

```text
ceb9403d44c19ba73fd351e1b05091d337280864
```

Artifact verification after downloading the PyPI wheel:

```bash
python - <<'PY'
from hashlib import sha256
from pathlib import Path

path = Path("fuzzyroutines-1.0.3-py3-none-any.whl")
print(sha256(path.read_bytes()).hexdigest())
PY
```

Expected:

```text
5febdfab36109c7055374c217ec8d8b6fe2c5a1b1e44a90868513b8bb38c1333
```

## Environment caveat

The legacy package declares Python 3.6 metadata, but this document does not claim that 1.0.3 has been successfully executed on every candidate modern Python version.

Execution/test-matrix evidence belongs to the dedicated legacy test-baseline Task.

## Source of truth

This file is the human-readable provenance record.

The immutable Git commit/tag and PyPI artifact hash remain the machine-verifiable source evidence.
