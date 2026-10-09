# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Executable contracts for multilingual manifests and source-drift gates."""

from pathlib import Path

from tools.locale_documentation import (
    CanonicalHash,
    CanonicalUnit,
    DiscoverCanonicalUnits,
    ProtectedApiContract,
    ProtectedPageParts,
    TranslationHash,
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
note = "Coordinates whose membership grade equals one."
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
publicationPath = "/fixture"

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
    translationHash = TranslationHash("# Русский перевод\n")
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
reviewedTranslationHash = "{translationHash}"
reviewer = "editor"
reviewedAt = "2026-09-24T00:00:00Z"

[[units.translations.ru.reviews]]
role = "mathematical"
reviewedSourceHash = "{sourceHash}"
reviewedTranslationHash = "{translationHash}"
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


def test_ReleaseGateRejectsMissingOrDraftTranslations(tmpPath):
    """Ordinary development validation must not imply stable multilingual readiness."""

    _PrepareFixture(tmpPath, ruState="draft")
    assert not ValidateLocales(tmpPath).diagnostics
    report = ValidateLocales(tmpPath, requireApproved=True)
    assert any("ru release requires approved, got draft" in item for item in report.diagnostics)
    assert any("zh-CN release requires approved, got missing" in item for item in report.diagnostics)


def test_TranslationEditInvalidatesHumanReviewEvenWhenEnglishIsUnchanged(tmpPath):
    """Approval must bind translated wording as well as its English source."""

    _PrepareFixture(tmpPath, ruState="approved")
    assert not ValidateLocales(tmpPath).diagnostics
    translation = tmpPath / "docs/site/content/ru/index.md"
    translation.write_text("# Изменённый перевод\n", encoding="utf-8")
    report = ValidateLocales(tmpPath)
    assert report.states["page:index"]["ru"] == "stale"
    assert any("translation changed" in item for item in report.diagnostics)


def test_TranslationProtectionDetectsChangedCodeAndFormulaButAllowsProse():
    """A fluent translation must not silently alter executable examples or equations."""

    source = "# English\nValue $x/2$\n\n$$\na+b\n$$\n\n```python\nvalue = 1\n```\n"
    translated = source.replace("English", "Русский").replace("Value", "Значение")
    assert ProtectedPageParts(source) == ProtectedPageParts(translated)
    assert ProtectedPageParts(source) != ProtectedPageParts(translated.replace("x/2", "x/3"))
    assert ProtectedPageParts(source) != ProtectedPageParts(translated.replace("value = 1", "value = 2"))


def test_ApiTranslationProtectsIndentedExamplesAndEveryDocumentedField():
    """Indented docstring examples and contract names need the same protection as pages."""

    source = 'English.\n\nArgs:\n    **parameters: Input.\n\nAttributes:\n    value: Result.\n\nRaises:\n    ValueError: Invalid.\n\nExamples:\n    ```python\n    value = 1\n    ```\n'
    translated = source.replace("English.", "Русский текст.").replace("Input.", "Параметры.")
    assert ProtectedApiContract(source) == ProtectedApiContract(translated)
    assert ProtectedApiContract(source) != ProtectedApiContract(translated.replace("**parameters:", "**параметры:"))
    assert ProtectedApiContract(source) != ProtectedApiContract(translated.replace("ValueError:", "TypeError:"))
    assert ProtectedPageParts(source) == ProtectedPageParts(translated)
    assert ProtectedPageParts(source) != ProtectedPageParts(translated.replace("value = 1", "value = 2"))


def test_CurrentGlossariesUseReviewedMathematicalTerminology():
    """Protect the reviewed Russian and Simplified Chinese terminology."""

    russianGlossary = (
        PROJECTROOT / "docs" / "i18n" / "glossaries" / "ru.toml"
    ).read_text(encoding="utf-8")
    chineseGlossary = (
        PROJECTROOT / "docs" / "i18n" / "glossaries" / "zh-CN.toml"
    ).read_text(encoding="utf-8")

    for requiredTerm in (
        'preferred = "универсальное множество"',
        'preferred = "множество поддержки"',
        'preferred = "ядро нечёткого множества"',
        'preferred = "область интегрирования"',
    ):
        assert requiredTerm in russianGlossary, (
            f"Russian glossary lost the reviewed term: {requiredTerm}"
        )

    for requiredTerm in (
        'preferred = "论域"',
        'preferred = "模糊集的支集"',
        'preferred = "模糊集的核"',
        'preferred = "积分域"',
    ):
        assert requiredTerm in chineseGlossary, (
            f"Simplified Chinese glossary lost the reviewed term: {requiredTerm}"
        )

    assert 'preferred = "正支撑集"' not in chineseGlossary
    assert "equals the set height" not in chineseGlossary


def test_MissingCanonicalUnitHasActionableCompletenessDiagnostic(tmpPath):
    """Name the absent stable ID and source when inventory is incomplete."""

    _PrepareFixture(tmpPath, includeUnit=False)

    report = ValidateLocales(tmpPath)
    expectedDiagnostic = (
        "docs/i18n/units.toml: missing canonical unit page:index "
        "source=docs/site/content/en/index.md action=add exactly one manifest record"
    )

    assert report.diagnostics == (expectedDiagnostic,)


def test_PageIdentifierSurvivesAnExplicitManifestPathMove(tmpPath):
    """Preserve a stable page ID when its canonical English path changes."""

    originalPath = _PrepareFixture(tmpPath)
    movedPath = tmpPath / "docs" / "site" / "content" / "en" / "guide.md"
    movedPath.write_text(originalPath.read_text(encoding="utf-8"), encoding="utf-8")
    originalPath.unlink()
    manifestPath = tmpPath / "docs" / "i18n" / "units.toml"
    manifestText = manifestPath.read_text(encoding="utf-8").replace(
        "docs/site/content/en/index.md",
        "docs/site/content/en/guide.md",
    )
    manifestPath.write_text(manifestText, encoding="utf-8")

    report = ValidateLocales(tmpPath)

    assert report.diagnostics == ()
    assert "page:index" in report.states


def test_ApprovedTranslationBecomesStaleAfterCanonicalEnglishChange(tmpPath):
    """Fail closed with exact hashes when approved English source drifts."""

    sourcePath = _PrepareFixture(tmpPath, ruState="approved")
    sourcePath.write_text("# Changed canonical English\n", encoding="utf-8")

    report = ValidateLocales(tmpPath)

    assert report.states["page:index"]["ru"] == "stale"
    assert any("canonical source drift" in value for value in report.diagnostics)
    assert any(
        "unit=page:index locale=ru" in value
        and "translation=docs/site/content/ru/index.md" in value
        and "action=set state=stale" in value
        for value in report.diagnostics
    )


def test_PublicClassFieldAnnotationParticipatesInCanonicalHash(tmpPath):
    """Make dataclass-like public field changes invalidate symbol translations."""

    _PrepareFixture(tmpPath)
    coveragePath = tmpPath / "docs" / "site" / "api-coverage.toml"
    _Write(
        coveragePath,
        '''schemaVersion = 1

[[surfaces]]
module = "fixture"
source = "fixture.py"
mode = "authored"
''',
    )
    sourcePath = tmpPath / "fixture.py"
    _Write(
        sourcePath,
        '''class Record:
    """Represent one documented record."""

    value: int
''',
    )
    projectManifest = {
        "contentRoot": "docs/site/content",
        "apiCoverageManifest": "docs/site/api-coverage.toml",
        "packageNames": ["fixture"],
    }
    originalUnits = DiscoverCanonicalUnits(tmpPath, projectManifest)
    originalUnit = next(
        unit for unit in originalUnits if unit.identifier == "symbol:fixture.Record"
    )
    sourcePath.write_text(
        sourcePath.read_text(encoding="utf-8").replace("value: int", "value: float"),
        encoding="utf-8",
    )
    changedUnits = DiscoverCanonicalUnits(tmpPath, projectManifest)
    changedUnit = next(
        unit for unit in changedUnits if unit.identifier == "symbol:fixture.Record"
    )

    assert CanonicalHash(originalUnit) != CanonicalHash(changedUnit)


def test_ModuleOverviewHashIsOptInAndIndependentOfCallableInventory(tmpPath):
    """Overview-only edits must invalidate translations without inventing API symbols."""

    _PrepareFixture(tmpPath)
    _Write(tmpPath / "docs/site/api-coverage.toml", 'schemaVersion = 1\n[[surfaces]]\nmodule = "fixture"\nsource = "fixture.py"\nmode = "authored"\n')
    sourcePath = tmpPath / "fixture.py"
    _Write(sourcePath, '"""Canonical overview."""\n\ndef Calculate():\n    """Return a value."""\n    return 1\n')
    projectManifest = {"contentRoot": "docs/site/content", "apiCoverageManifest": "docs/site/api-coverage.toml", "packageNames": ["fixture"]}
    defaultUnits = DiscoverCanonicalUnits(tmpPath, projectManifest)
    assert all(unit.kind != "module" for unit in defaultUnits)
    projectManifest["includeModuleDocstrings"] = True
    originalUnits = {unit.identifier: unit for unit in DiscoverCanonicalUnits(tmpPath, projectManifest)}
    assert {unit.identifier for unit in defaultUnits} == set(originalUnits) - {"module:fixture"}
    sourcePath.write_text(sourcePath.read_text().replace("Canonical overview.", "Changed overview."))
    changedUnits = {unit.identifier: unit for unit in DiscoverCanonicalUnits(tmpPath, projectManifest)}
    assert CanonicalHash(originalUnits["module:fixture"]) != CanonicalHash(changedUnits["module:fixture"])
    assert CanonicalHash(originalUnits["symbol:fixture.Calculate"]) == CanonicalHash(changedUnits["symbol:fixture.Calculate"])


def test_ApprovedTranslationRequiresAllHumanReviewRoles(tmpPath):
    """Reject false approval without editorial and mathematical reviewers."""

    _PrepareFixture(tmpPath, ruState="approved", includeReviews=False)

    report = ValidateLocales(tmpPath)

    assert any(
        "ru approved state lacks review roles editorial, mathematical" in value
        for value in report.diagnostics
    )


def test_TranslationStateAndPathFailuresRemainExplicit(tmpPath):
    """Reject malformed states and locale content without an accountable state."""

    _PrepareFixture(tmpPath, ruState="unexpected")

    report = ValidateLocales(tmpPath)

    assert any("invalid ru state 'unexpected'" in value for value in report.diagnostics)


def test_GlossaryConceptInventoriesMustMatchAcrossLocales(tmpPath):
    """Prevent locale glossaries from silently describing different concepts."""

    _PrepareFixture(tmpPath)
    _Write(
        tmpPath / "docs" / "i18n" / "glossaries" / "zh-CN.toml",
        '''schemaVersion = 1
locale = "zh-CN"
terms = []
''',
    )

    report = ValidateLocales(tmpPath)

    assert "docs/i18n/glossaries: target locale concept IDs must match" in (
        report.diagnostics
    )
