# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Optional packaging and executable documentation scope invariants."""

import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_NumpyExtraDoesNotAddAScalarRuntimeDependency():
    """Keep the accepted NumPy range opt-in while preserving zero core dependencies."""

    metadata = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = metadata["project"]
    assert not project.get("dependencies", []), "Scalar installations must retain zero mandatory dependencies"
    assert project["optional-dependencies"]["numpy"] == ["numpy>=2.3.5,<3"]


def test_OptionalCoverageDeclaresTheGuidesAndTheirPublicModules():
    """Make omitted example evidence explicit without hiding the public API surface."""

    manifest = tomllib.loads((PROJECT_ROOT / "docs/site/api-coverage.toml").read_text(encoding="utf-8"))
    scopes = {scope["extra"]: scope for scope in manifest["optionalExamples"]}
    assert scopes["numpy"]["pages"] == ["guides/numpy-batches.md", "guides/sugeno-batches.md"]
    assert scopes["numpy"]["modules"] == ["fuzzyroutines.batches", "fuzzyroutines.sugeno_batches"]
    assert set(scopes["numpy"]["modules"]) <= {surface["module"] for surface in manifest["surfaces"]}

    for locale in ("en", "ru", "zh-CN"):
        contentRoot = PROJECT_ROOT / "docs/site/content" / locale

        for page in (*scopes["numpy"]["pages"], "api/modern/batches.md", "api/modern/sugeno-batches.md"):
            assert (contentRoot / page).is_file()
