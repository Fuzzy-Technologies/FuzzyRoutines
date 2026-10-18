# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Published-baseline evidence and usable candidate installation instructions."""

import importlib.metadata
import re
import shlex
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from tools.locale_documentation import ProtectedPageParts

ROOT = Path(__file__).resolve().parents[1]
MIGRATION_PATHS = (
    "docs/migration/1.0.3-to-2.0.0.md",
    "docs/site/content/ru/migration/1.0.3-to-2.0.0.md",
    "docs/site/content/zh-CN/migration/1.0.3-to-2.0.0.md",
)
PYPI_RELEASE = "https://pypi.org/project/fuzzyroutines/2.0.0/"
GITHUB_RELEASE = "https://github.com/Fuzzy-Technologies/FuzzyRoutines/releases/tag/v2.0.0"


def test_ReadmeLinksRemainUsableFromThePackageIndex():
    """Keep package-description links independent of GitHub's relative URL rules."""

    text = (ROOT / "README.md").read_text(encoding="utf-8")
    targets = re.findall(r"\]\(([^)]+)\)", text)
    assert targets, "The README must provide a documentation route"
    assert all(urlsplit(target).scheme == "https" and urlsplit(target).netloc for target in targets), "README links must work when rendered as the PyPI package description"


@pytest.mark.parametrize("relativePath", (
    "README.md", "docs/index.html", "docs/ru/index.html", "docs/zh-CN/index.html", "docs/llms.txt",
    *(f"docs/site/content/{locale}/{guide}.md" for locale in ("en", "ru", "zh-CN")
      for guide in ("quick-start", "agent-quickstart", "guides/numpy-batches")),
))
def test_ProductEntryPointsInstallTheDocumentedSourceVersion(relativePath):
    """Prevent a new release's onboarding from silently installing its older baseline."""

    text = (ROOT / relativePath).read_text(encoding="utf-8")
    sourceVersion = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    pins = re.findall(r"fuzzyroutines(?:\[numpy\])?==([0-9.]+)", text)
    assert pins and set(pins) == {sourceVersion}, "Primary installation commands must match the release source"
    assert "2.0.0" in text and "PyPI" in text, "Keep the published baseline distinct from conditional release availability"


@pytest.mark.parametrize("locale", ("en", "ru", "zh-CN"))
@pytest.mark.parametrize("installedVersion", ("2.1.0", "2.0.0", "2.1.0rc1"))
def test_BatchGuideChecksTheInstalledCandidateBeforeUsingItsApi(locale, installedVersion, monkeypatch):
    """Exercise the copyable version guard against the candidate and wrong versions."""

    text = (ROOT / "docs/site/content" / locale / "guides/numpy-batches.md").read_text(encoding="utf-8")
    recipe = next(block for block in re.findall(r"```bash\n(.*?)\n```", text, re.DOTALL) if "$FUZZYROUTINES_WHEEL" in block)
    commands = [shlex.split(line) for line in recipe.splitlines()]
    guard = next(command for command in commands if "-c" in command)
    guardIndex = commands.index(guard)
    installIndex = next(index for index, command in enumerate(commands) if command[:4] == ["python", "-m", "pip", "install"])
    assert installIndex < guardIndex, "Check the package that was just installed"
    assert "$FUZZYROUTINES_WHEEL" in commands[installIndex], "Install the reviewed local wheel rather than the published 2.0 baseline"
    assert "-I" in guard, "A checkout must not shadow the installed candidate"
    monkeypatch.setattr(importlib.metadata, "version", lambda package: installedVersion)
    with pytest.raises(SystemExit) as outcome:
        exec(guard[guard.index("-c") + 1], {})  # noqa: S102 - Execute the reviewed local documentation fixture.
    assert (outcome.value.code == 0) == (installedVersion == "2.1.0"), "Only the documented exact candidate may proceed"
    canonical = (ROOT / "docs/site/content/en/guides/numpy-batches.md").read_text(encoding="utf-8")
    assert ProtectedPageParts(text) == ProtectedPageParts(canonical), "Translations must preserve executable and mathematical fragments"


@pytest.mark.parametrize("relativePath", MIGRATION_PATHS)
def test_MigrationLocalesPointToThePublishedBaseline(relativePath):
    """Keep release-specific migration claims tied to actual published artifacts."""

    text = (ROOT / relativePath).read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+)\)", text)
    assert PYPI_RELEASE in links and GITHUB_RELEASE in links, "Every migration locale must link its published PyPI baseline and verified release artifacts"
    staleStatements = ("prepared `2.0.0` candidate", "подготовленный кандидат `2.0.0`", "已准备好的 `2.0.0` 候选版本")
    assert not any(statement in text for statement in staleStatements), "Published 2.0 must not be presented as an unreleased candidate"
    canonical = (ROOT / MIGRATION_PATHS[0]).read_text(encoding="utf-8")
    assert ProtectedPageParts(text) == ProtectedPageParts(canonical), "Publication-status edits must preserve every protected mathematical and executable fragment"
    assert "{#migration-notes-103-to-the-planned-200-release}" in text, "Keep the historical explicit anchor stable for existing migration links"


def test_ReadinessSeparatesProductionEvidenceFromNewCandidateAcceptance():
    """Retain immutable 2.0 publication evidence and an independent future gate."""

    text = (ROOT / "docs/release-readiness.md").read_text(encoding="utf-8")
    assert PYPI_RELEASE in text and GITHUB_RELEASE in text, "Living readiness must identify the published baseline"
    assert "actions/runs/38087564208" in text and "49c9aee67a60cad74bc9494943b8745b72d2f43c" in text, "Publication claims need the successful production run and its exact source"
    assert "blob/v2.0.0/docs/release-readiness.md" in text, "Historical preparation evidence must remain available at its immutable tag"
    assert "issues/337" in text and "## Current 2.1 development gate" in text, "Current candidate acceptance must have its own explicitly separate owner"
    assert "## Audit follow-ups" in text, "Existing audit-follow-up links must remain navigable"


@pytest.mark.parametrize("version", ("2.0.0", "2.1.0.dev0", "2.1.0rc1"))
def test_PackagingRecipeSelectsTheWheelThatWasJustBuilt(tmpPath, version):
    """Resolve the documented install operand against stable and candidate builds."""

    text = (ROOT / "docs/release-packaging-notes.md").read_text(encoding="utf-8")
    operand = re.search(r"^python -m pip install --force-reinstall (\S+)$", text, re.MULTILINE).group(1)
    distribution = tmpPath / "dist" / f"fuzzyroutines-{version}-py3-none-any.whl"
    distribution.parent.mkdir()
    distribution.touch()
    assert list(tmpPath.glob(operand)) == [distribution], "The clean-output recipe must select the actual candidate wheel rather than a hard-coded 2.0 filename"
