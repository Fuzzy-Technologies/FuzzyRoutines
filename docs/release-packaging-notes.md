<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Packaging and release notes

## 2.0.0 release candidate

The build baseline is intentionally separate from the mathematical
modernisation work. It adopts the PEP 517/518 build interface and stores the
candidate version, `2.0.0`, in `pyproject.toml`. Publication remains subject
to final human acceptance and the protected release workflow.

The [version decision](release-version-decision.md) reaffirms `2.0.0` as the
first stable target under ADR-0006, based on the CPython support floor and
observed helper-import changes. It does not change package metadata or approve
publication. See the [development changelog](../CHANGELOG.md) and
[1.0.3 migration notes](migration/1.0.3-to-2.0.0.md) for user-visible impact.

- The package supports CPython 3.13 and 3.14.
- `setuptools.build_meta` is the build backend.
- Package metadata uses the SPDX expression `Apache-2.0`; both `LICENSE` and
  `NOTICE` are included in source and wheel distributions.
- `setup.py` remains only as a legacy command-line compatibility shim; it owns
  neither package metadata nor versioning.
- Routine CI must build and install artifacts but cannot publish a release.
- The former Travis deployment configuration was retired after the protected
  Trusted Publishing replacement was verified under Task #46.
- Any future numerical dependency must support the declared CPython matrix;
  legacy interpreter compatibility is not a dependency-selection constraint.

### Local verification

Ordinary PEP 517 builds remain supported. To reproduce the CI candidates for a
committed source revision, use a new environment with the checked-in build
requirements and a new output directory:

```bash
python -m pip install -r requirements-build.txt
python -m tools.reproducible_artifacts --output-directory dist
(cd dist && sha256sum --check SHA256SUMS)
python -m pip install --force-reinstall dist/fuzzyroutines-2.0.0-py3-none-any.whl
python -c "from fuzzyroutines.FuzzyRoutines import MFunction; print(MFunction('triangle', a=0, b=1, c=0.5))"
python -m tools.check_license_headers
```

The comparison command builds the current **Git HEAD**, so uncommitted changes
are excluded. The command rejects an existing output directory instead of
overwriting previous evidence. Development runs may use focused tests; full
builds, clean-install checks, and regressions run in pull-request CI.

### Artifact byte reproducibility

Task #278 addresses the source archive timestamp difference found by the M6
packaging audit. `SOURCE_DATE_EPOCH` alone makes setuptools wheels reproducible,
but upstream setuptools does not normalize every sdist tar member and gzip
timestamp. The backend remains `setuptools.build_meta` under ADR-0006. A narrow
`sdist` command extension writes the prepared source tree directly with stable
timestamps, owner fields, permissions, member order, and an unnamed gzip header.
It preserves payload bytes and executable files. There is no archive rewriting
after the build. The extension is included in the source distribution, so a
wheel can also be built from the sdist without a Git checkout.

Both the package and protected release workflows use `requirements-build.txt`
and the same comparison command. They export the source revision into two new
directories, deliberately vary source filesystem timestamps, and build a wheel
and sdist independently in the active locked build environment. The source epoch
is the Git commit timestamp. Artifact names and SHA-256 hashes must agree before
any candidates are selected. The first build's unchanged bytes then pass through
the existing clean-install checks; the protected release uses those same bytes
for provenance and publication.

`dist/reproducibility.json` records the source revision, source epoch, interpreter,
platform, build tool versions, two source timestamp offsets, and both hashes for
each distribution. `SHA256SUMS` hashes only distributions; the JSON report and
source revision are evidence files. A mismatch fails CI and blocks publication.

This is a promise for the same source, source epoch, interpreter, platform, and
locked build tools. Hash equality across different Python or tool versions is
not required. These CI builds share a controlled tool environment; they do not
claim that operating systems or future dependency releases are interchangeable.
An ordinary build without `SOURCE_DATE_EPOCH` retains upstream setuptools
behavior and makes no byte reproducibility claim. Set an explicit source epoch
when building manually with `python -m build`; malformed values fail the sdist
command instead of falling back to wall-clock timestamps.

The upstream limitation and supported command customization are documented in
[setuptools issue #2133](https://github.com/pypa/setuptools/issues/2133) and the
[setuptools extension guide](https://setuptools.pypa.io/en/latest/userguide/extension.html).

The protected publication mechanics and required manual platform configuration
are defined in the [PyPI Trusted Publishing runbook](trusted-publishing-runbook.md).
Routine CI still cannot publish artifacts. A production release additionally
requires the complete human-reviewed readiness checklist, a protected annotated
tag, and approval through the `pypi` GitHub environment.
