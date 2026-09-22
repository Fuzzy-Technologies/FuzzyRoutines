# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic contracts for the canonical installed-package API reference."""

import ast
import re
import subprocess
from pathlib import Path

from tools import build_api_reference

PROJECTROOT = Path(__file__).parents[1]
SITEROOT = PROJECTROOT / "docs" / "site"
CONFIGPATH = SITEROOT / "mkdocs.yml"


def test_CanonicalReferenceHasCompleteOrderedNavigation():
    configurationText = CONFIGPATH.read_text(encoding="utf-8")
    expectedPages = (
        "api/modern/package.md",
        "api/modern/alphacuts.md",
        "api/modern/domain.md",
        "api/modern/fuzzysets.md",
        "api/modern/linguistic.md",
        "api/modern/properties.md",
        "api/modern/relations.md",
        "api/legacy/index.md",
    )

    offsets = []
    for pagePath in expectedPages:
        offsets.append(configurationText.index(pagePath))
        assert (SITEROOT / "content" / "en" / pagePath).is_file()

    assert offsets == sorted(offsets)


def test_CanonicalReferenceLinksEveryRootExportToItsCanonicalObject():
    packageModule = ast.parse(
        (PROJECTROOT / "fuzzyroutines" / "__init__.py").read_text(encoding="utf-8")
    )
    canonicalTargets = {}
    rootExports = None

    for statement in packageModule.body:
        if isinstance(statement, ast.ImportFrom):
            for importedName in statement.names:
                publicName = importedName.asname or importedName.name
                canonicalTargets[publicName] = (
                    f"{statement.module}.{importedName.name}"
                )

        elif isinstance(statement, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in statement.targets
        ):
            rootExports = ast.literal_eval(statement.value)

    assert rootExports is not None
    expectedLinks = {
        exportName: canonicalTargets[exportName] for exportName in rootExports
    }
    packagePage = (
        SITEROOT / "content" / "en" / "api" / "modern" / "package.md"
    ).read_text(encoding="utf-8")
    renderedLinks = {
        linkText: target
        for linkText, target in re.findall(
            r"\[`([^`]+)`\]\[([^\]]+)\]",
            packagePage,
        )
        if linkText in expectedLinks
    }

    assert renderedLinks == expectedLinks


def test_CanonicalReferenceUsesInstalledStaticDiscoveryAndStrictBuilds():
    configurationText = CONFIGPATH.read_text(encoding="utf-8")
    builderText = (PROJECTROOT / "tools" / "build_api_reference.py").read_text(
        encoding="utf-8"
    )

    assert "!ENV FUZZYROUTINES_INSTALLED_PACKAGES" in configurationText
    assert build_api_reference.CONFIGPATH == CONFIGPATH
    assert '"--strict"' in builderText
    assert '"--no-deps"' in builderText
    assert "cwd=buildRoot" in builderText
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
    tablePages = (
        SITEROOT / "content" / "en" / "api" / "modern" / "index.md",
        SITEROOT / "content" / "en" / "api" / "modern" / "package.md",
    )

    for tablePage in tablePages:
        tableLines = [
            line
            for line in tablePage.read_text(encoding="utf-8").splitlines()
            if line.startswith("|")
        ]
        assert tableLines
        assert len({len(line) for line in tableLines}) == 1
