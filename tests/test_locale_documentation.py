# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Executable contracts for multilingual manifests and source-drift gates."""

from pathlib import Path

from tools.locale_documentation import (
    CanonicalHash,
    CanonicalUnit,
    ValidateLocales,
)

PROJECTROOT = Path(__file__).parents[1]


def _Write(path, text):
    """Write one UTF-8 fixture below its prepared temporary root."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _Glossary(locale, preferred):
    """Return one minimal locale glossary with a shared stable concept ID."""

    return f'''schemaVersion = 1
locale = "{locale}"

[[terms]]
id = "concept:fuzzy-set.core"
english = "core"
preferred = "{preferred}"
avoid = []
note = "Coordinates whose membership grade equals the set height."
references = ["docs/reference.md"]
'''


def _PrepareFixture(
    projectRoot,
    ruState="missing",
    includeUnit=True,
    includeReviews=True,
):
    """Create a complete one-page multilingual validation fixture."""

    sourcePath = projectRoot / "docs" / "site" / "content" / "en" / "index.md"
    sourceText = "# Canonical English\n"
    _Write(sourcePath, sourceText)
    _Write(projectRoot / "docs" / "reference.md", "# Reference\n")
    _Write(
        projectRoot / "docs" / "site" / "api-coverage.toml",
        "schemaVersion = 1\nsurfaces = []\n",
    )
    _Write(
        projectRoot / "docs" / "i18n" / "project.toml",
        '''schemaVersion = 1
projectId = "fixture"
projectName = "Fixture"
sourceLocale = "en"
locales = ["en", "ru", "zh-CN"]
packageNames = ["fixture"]
contentRoot = "docs/site/content"
unitManifest = "docs/i18n/units.toml"
buildRoot = "_build/docs"
apiCoverageManifest = "docs/site/api-coverage.toml"

[branding]
organization = "Fuzzy Technologies"
assetRoot = "docs/site/assets"

[glossaries]
ru = "docs/i18n/glossaries/ru.toml"
zh-CN = "docs/i18n/glossaries/zh-CN.toml"
''',
    )
    _Write(
        projectRoot / "docs" / "i18n" / "glossaries" / "ru.toml",
        _Glossary("ru", "ядро"),
    )
    _Write(
        projectRoot / "docs" / "i18n" / "glossaries" / "zh-CN.toml",
        _Glossary("zh-CN", "核"),
    )

    unit = CanonicalUnit(
        identifier="page:index",
        kind="page",
        sourcePath="docs/site/content/en/index.md",
        signature="",
        body=sourceText,
    )
    sourceHash = CanonicalHash(unit)
    records = ""

    if includeUnit:
        ruPath = ""
        reviews = ""

        if ruState != "missing":
            _Write(
                projectRoot / "docs" / "site" / "content" / "ru" / "index.md",
                "# Русский перевод\n",
            )
            ruPath = 'path = "docs/site/content/ru/index.md"\n'

        if ruState == "approved" and includeReviews:
            reviews = f'''
[[units.translations.ru.reviews]]
role = "editorial"
reviewedSourceHash = "{sourceHash}"
reviewer = "editor"
reviewedAt = "2026-09-24T00:00:00Z"

[[units.translations.ru.reviews]]
role = "mathematical"
reviewedSourceHash = "{sourceHash}"
reviewer = "reviewer"
reviewedAt = "2026-09-24T00:00:00Z"
'''

        records = f'''
[[units]]
id = "page:index"
kind = "page"
sourcePath = "docs/site/content/en/index.md"
sourceHash = "{sourceHash}"
reviewClass = "mathematical"

[units.translations.ru]
{ruPath}state = "{ruState}"
{reviews}
[units.translations.zh-CN]
state = "missing"
'''

    _Write(
        projectRoot / "docs" / "i18n" / "units.toml",
        f"schemaVersion = 1\n{records}",
    )

    return sourcePath


def test_CurrentLocaleManifestsMatchCanonicalEnglishInventory():
    """Keep every canonical page and public symbol represented exactly once."""

    assert ValidateLocales(PROJECTROOT).diagnostics == ()


def test_MissingCanonicalUnitHasActionableCompletenessDiagnostic(tmp_path):
    """Name the absent stable ID and source when inventory is incomplete."""

    _PrepareFixture(tmp_path, includeUnit=False)

    report = ValidateLocales(tmp_path)
    expectedDiagnostic = (
        "docs/i18n/units.toml: missing canonical unit page:index "
        "source=docs/site/content/en/index.md action=add exactly one manifest record"
    )

    assert report.diagnostics == (expectedDiagnostic,)


def test_PageIdentifierSurvivesAnExplicitManifestPathMove(tmp_path):
    """Preserve a stable page ID when its canonical English path changes."""

    originalPath = _PrepareFixture(tmp_path)
    movedPath = tmp_path / "docs" / "site" / "content" / "en" / "guide.md"
    movedPath.write_text(originalPath.read_text(encoding="utf-8"), encoding="utf-8")
    originalPath.unlink()
    manifestPath = tmp_path / "docs" / "i18n" / "units.toml"
    manifestText = manifestPath.read_text(encoding="utf-8").replace(
        "docs/site/content/en/index.md",
        "docs/site/content/en/guide.md",
    )
    manifestPath.write_text(manifestText, encoding="utf-8")

    report = ValidateLocales(tmp_path)

    assert report.diagnostics == ()
    assert "page:index" in report.states


def test_ApprovedTranslationBecomesStaleAfterCanonicalEnglishChange(tmp_path):
    """Fail closed with exact hashes when approved English source drifts."""

    sourcePath = _PrepareFixture(tmp_path, ruState="approved")
    sourcePath.write_text("# Changed canonical English\n", encoding="utf-8")

    report = ValidateLocales(tmp_path)

    assert report.states["page:index"]["ru"] == "stale"
    assert any("canonical source drift" in value for value in report.diagnostics)
    assert any(
        "unit=page:index locale=ru" in value
        and "translation=docs/site/content/ru/index.md" in value
        and "action=set state=stale" in value
        for value in report.diagnostics
    )


def test_ApprovedTranslationRequiresAllHumanReviewRoles(tmp_path):
    """Reject false approval without editorial and mathematical reviewers."""

    _PrepareFixture(tmp_path, ruState="approved", includeReviews=False)

    report = ValidateLocales(tmp_path)

    assert any(
        "ru approved state lacks review roles editorial, mathematical" in value
        for value in report.diagnostics
    )


def test_TranslationStateAndPathFailuresRemainExplicit(tmp_path):
    """Reject malformed states and locale content without an accountable state."""

    _PrepareFixture(tmp_path, ruState="unexpected")

    report = ValidateLocales(tmp_path)

    assert any("invalid ru state 'unexpected'" in value for value in report.diagnostics)


def test_GlossaryConceptInventoriesMustMatchAcrossLocales(tmp_path):
    """Prevent locale glossaries from silently describing different concepts."""

    _PrepareFixture(tmp_path)
    _Write(
        tmp_path / "docs" / "i18n" / "glossaries" / "zh-CN.toml",
        '''schemaVersion = 1
locale = "zh-CN"
terms = []
''',
    )

    report = ValidateLocales(tmp_path)

    assert "docs/i18n/glossaries: ru and zh-CN concept IDs must match" in (
        report.diagnostics
    )
