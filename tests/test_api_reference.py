# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic contracts for the canonical installed-package API reference."""

import subprocess
from pathlib import Path

import yaml

from tools import build_api_reference

PROJECTROOT = Path(__file__).parents[1]
SITEROOT = PROJECTROOT / "docs" / "site"
CONFIGPATH = SITEROOT / "mkdocs.yml"


def test_CanonicalReferenceHasCompleteOrderedNavigation():
    configuration = yaml.safe_load(
        CONFIGPATH.read_text(encoding="utf-8").replace(
            "!ENV FUZZYROUTINES_INSTALLED_PACKAGES",
            '"installed-packages"',
        )
    )
    navigationText = repr(configuration["nav"])

    for pagePath in (
        "api/modern/package.md",
        "api/modern/alphacuts.md",
        "api/modern/domain.md",
        "api/modern/fuzzysets.md",
        "api/modern/linguistic.md",
        "api/modern/properties.md",
        "api/modern/relations.md",
        "api/legacy/index.md",
    ):
        assert pagePath in navigationText
        assert (SITEROOT / "content" / "en" / pagePath).is_file()


def test_CanonicalReferenceUsesInstalledStaticDiscoveryAndStrictBuilds():
    configurationText = CONFIGPATH.read_text(encoding="utf-8")
    builderText = (PROJECTROOT / "tools" / "build_api_reference.py").read_text(
        encoding="utf-8"
    )

    assert "!ENV FUZZYROUTINES_INSTALLED_PACKAGES" in configurationText
    assert build_api_reference.CONFIGPATH == CONFIGPATH
    assert '"--strict"' in builderText
    assert '"--no-deps"' in builderText
    assert "FuzzyRoutinesImportGuard" in builderText
    assert "import fuzzyroutines" not in builderText


def test_CanonicalReferenceDependenciesRemainExactlyPinnedAndDocsOnly():
    requirements = (PROJECTROOT / "docs" / "requirements-api.txt").read_text(
        encoding="utf-8"
    )
    projectMetadata = (PROJECTROOT / "pyproject.toml").read_text(encoding="utf-8")

    dependencyLines = [
        line for line in requirements.splitlines() if line and not line.startswith("#")
    ]
    assert dependencyLines
    assert all(line.count("==") == 1 for line in dependencyLines)
    for packageName in (
        "mkdocs",
        "mkdocs-material",
        "mkdocstrings",
        "mkdocstrings-python",
        "griffelib",
    ):
        assert f"{packageName}==" in requirements
        assert packageName not in projectMetadata


def test_CanonicalReferenceDoesNotTrackGeneratedHtml():
    trackedPaths = subprocess.check_output(
        ["git", "ls-files"],
        cwd=PROJECTROOT,
        text=True,
    ).splitlines()

    assert not any(path.startswith("_build/") for path in trackedPaths)
    assert not any(path.endswith(".html") for path in trackedPaths if path.startswith("docs/site/"))


def test_CanonicalReferenceMarkdownTablesHavePaddedColumns():
    modernIndexLines = (
        SITEROOT / "content" / "en" / "api" / "modern" / "index.md"
    ).read_text(encoding="utf-8").splitlines()
    tableLines = [line for line in modernIndexLines if line.startswith("|")]

    assert tableLines
    assert len({len(line) for line in tableLines}) == 1
