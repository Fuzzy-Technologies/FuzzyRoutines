# ADR-0006: Packaging, Versioning, and Release Policy

- Status: Accepted on merge
- Date: 2026-09-14
- Related planning task: #13
- Release execution milestone: M6

## Context

FuzzyRoutines 1.0.3 is built through a Travis-coupled `setup.py` path with
dynamic CI-derived version text and historical DevOpsHQ/PyPI metadata. The
modernization release must produce reproducible wheels and source distributions
without coupling routine test CI to package publication.

The legacy release provenance is recorded in
`docs/baseline/fuzzyroutines-1.0.3-provenance.md`.

## Decision

### Build standard

The supported build interface is PEP 517/518 with a checked-in
`pyproject.toml`. The initial backend is `setuptools.build_meta`; changing
the backend requires a separate ADR.

`setup.py` may remain temporarily as a compatibility shim for legacy tooling,
but it must not be a second owner of project version or release metadata once
the PEP 517 baseline lands.

### Version ownership

The canonical package version is the PEP 621
`[project].version` value in `pyproject.toml`.

- Versions comply with PEP 440.
- The first modernization development line is `2.0.0.devN`.
- The first public modernization release is `2.0.0`.
- Routine CI must build and install artifacts but must never publish them.
- A runtime `__version__` is not introduced by packaging work alone; if it
  becomes public API, it must be covered by the compatibility contract.

A release artifact and Git tag must carry the same normalized version.

### Supported Python policy

FuzzyRoutines 2.x will require Python 3.9 or later. The release matrix must
verify Python 3.9, 3.11, and the newest supported CPython version available in
CI. The historical Python 3.6 claim remains provenance, not a 2.x support
promise.

Raising the floor later is an intentional compatibility change and requires
release-note and version-policy review.

### Release flow

1. A release candidate is built from `develop` or the approved release branch.
2. CI verifies tests, wheel build, sdist build, and clean-install import smoke.
3. A human approves the release version and changelog.
4. An annotated `vX.Y.Z` tag identifies the exact source.
5. The release workflow builds the tagged source, verifies artifact metadata,
   creates GitHub release evidence, and publishes through PyPI Trusted
   Publishing.
6. Artifact hashes, tag, workflow run, and GitHub release URL are recorded.

Publication is unavailable to ordinary pull-request workflows.

### Credentials and legacy CI

PyPI API tokens and Travis encrypted secrets are obsolete credential paths.
They must not be copied to GitHub secrets or source. The Travis deployment
configuration remains only until its replacement mechanics are verified by
Tasks #44 and #45; Task #46 then removes or disables it safely.

## Consequences

- Task #44 implements the packaging baseline on a fresh branch from
  `develop`; the existing exploratory packaging branch is evidence only and
  must be reconciled, not merged blindly.
- Task #45 adds artifact build and clean-install verification without
  publication.
- Task #46 retires the old Travis deployment path only after replacement
  evidence exists.
- M6 owns actual release execution, GitHub release, and PyPI publication.

## Acceptance and supersession

This ADR is **Proposed** until the review PR is approved and merged. Any
different build backend, version source, supported-Python floor, or publication
mechanism must amend or supersede this ADR before implementation.