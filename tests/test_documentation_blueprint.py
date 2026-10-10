# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Executable contracts for the reusable documentation blueprint."""

import builtins
import shutil
import tomllib
from pathlib import Path

from tools.locale_documentation import ValidateLocales

PROJECTROOT = Path(__file__).parents[1]
BLUEPRINTROOT = PROJECTROOT / "docs" / "documentation-blueprint"
FIXTUREROOT = (
    PROJECTROOT
    / "tests"
    / "fixtures"
    / "documentation-blueprint"
    / "sampleproject"
)


def test_SecondProjectDryRunDoesNotImportFuzzyRoutines(tmpPath, monkeypatch):
    """Validate a foreign package and locale set without runtime imports."""

    projectRoot = tmpPath / "sampleproject"
    shutil.copytree(FIXTUREROOT, projectRoot)
    importedNames = []
    originalImport = builtins.__import__

    def GuardedImport(name, globals=None, locals=None, fromlist=(), level=0):
        """Reject a FuzzyRoutines import during the independent dry-run."""

        importedNames.append(name)

        if name == "fuzzyroutines" or name.startswith("fuzzyroutines."):
            raise AssertionError(f"blueprint imported product package {name}")

        return originalImport(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", GuardedImport)

    report = ValidateLocales(projectRoot)

    assert report.diagnostics == ()
    assert report.states == {
        "page:index": {"de": "missing"},
        "symbol:sampleproject.ForecastTemperature": {"de": "missing"},
    }
    assert not any(name.startswith("fuzzyroutines") for name in importedNames)


def test_BlueprintManifestMakesEveryProjectInputExplicit():
    """Keep identity, packages, locales, branding, and URL path configurable."""

    manifestPath = BLUEPRINTROOT / "templates" / "project.toml"
    manifest = tomllib.loads(manifestPath.read_text(encoding="utf-8"))

    assert manifest["projectName"] == "SampleProject"
    assert manifest["packageNames"] == ["sampleproject"]
    assert manifest["locales"] == ["en", "de"]
    assert manifest["branding"] == {
        "organization": "Fuzzy Technologies",
        "assetRoot": "docs/site/content/en/assets",
    }
    assert manifest["publicationPath"] == "/SampleProject"


def test_BlueprintRejectsApiSurfacesOutsideDeclaredPackages(tmpPath):
    """Bind static discovery to the explicit package-name input."""

    projectRoot = tmpPath / "sampleproject"
    shutil.copytree(FIXTUREROOT, projectRoot)
    coveragePath = projectRoot / "docs" / "site" / "api-coverage.toml"
    coveragePath.write_text(
        coveragePath.read_text(encoding="utf-8").replace(
            'module = "sampleproject"',
            'module = "undeclared"',
        ),
        encoding="utf-8",
    )

    report = ValidateLocales(projectRoot)

    assert len(report.diagnostics) == 1
    assert "module 'undeclared' is outside declared packageNames" in report.diagnostics[0]


def test_BlueprintKeepsGeneratedHtmlOutsideTrackedTemplates():
    """Provide source configuration without creating a second HTML authority."""

    trackedFiles = tuple(path for path in BLUEPRINTROOT.rglob("*") if path.is_file())

    assert trackedFiles
    assert not any(path.suffix == ".html" for path in trackedFiles)
    assert (BLUEPRINTROOT / "templates" / "mkdocs.yml") in trackedFiles
    assert (BLUEPRINTROOT / "templates" / "documentation-gates.yml") in trackedFiles
    assert (BLUEPRINTROOT / "templates" / "requirements-api.txt") in trackedFiles


def test_BlueprintWorkflowKeepsBuildAndPublicationSeparated():
    """Allow previews on reviews but production deployment only from master."""

    workflowText = (
        BLUEPRINTROOT / "templates" / "documentation-gates.yml"
    ).read_text(encoding="utf-8")

    assert "pull_request:" in workflowText
    assert "github.event_name == 'push'" in workflowText
    assert "github.ref == 'refs/heads/master'" in workflowText
    assert "actions/upload-pages-artifact@v3" in workflowText
    assert "actions/deploy-pages@v4" in workflowText
