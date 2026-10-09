# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Focused rendering-boundary tests for source-owned multilingual documentation."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.build_locale_reference import (
    AuthoredSymbolPath,
    BuildLocale,
    RewriteExternalLinks,
    StageLocale,
)
from tools.locale_documentation import CanonicalUnit, ValidationReport
from tools.locale_site_hook import on_page_context as OnPageContext
from tools.locale_site_hook import on_page_markdown as OnPageMarkdown

PROJECTROOT = Path(__file__).resolve().parents[1]


def test_AliasTranslationsResolveToOnePhysicalObject():
    """Root exports and the historical facade must attach to the real static source."""

    for identifier, source, expected in (
        ("symbol:fuzzyroutines.Gaussian", "fuzzyroutines/membership.py", "fuzzyroutines.membership.Gaussian"),
        ("symbol:fuzzyroutines.FuzzyRoutines.MFunction.parameters", "fuzzyroutines/_legacy/membership.py", "fuzzyroutines._legacy.membership.MFunction.parameters"),
    ):
        assert AuthoredSymbolPath(CanonicalUnit(identifier, "symbol", source, "", "")) == expected


def test_ExternalPageLinksFollowStableRoutesAndRetainSourceReferences():
    """Moving a source page into the site must not break its mathematical references."""

    text = "[model](../MATHEMATICAL_MODEL.md#scalar) [test](../../tests/test_domain.py) [local](#note)"
    result = RewriteExternalLinks(text, "docs/mathematics/alpha-cuts.md", "mathematics/alpha-cuts.md", {"docs/MATHEMATICAL_MODEL.md": "mathematics/model.md"})
    assert "[model](model.md#scalar)" in result
    assert "https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/tests/test_domain.py" in result
    assert "[local](#note)" in result


def test_PreviewBannerAndLanguageSwitchKeepTheCurrentPage():
    """A translation preview cannot look approved or send a language switch home."""

    configuration = SimpleNamespace(extra={"localeRoot": "/FuzzyRoutines/api/latest", "localePreviewBanner": "Draft translation"})
    page = SimpleNamespace(url="guides/alpha-cuts/")
    context = {"page": page}
    assert OnPageContext(context, page=page, config=configuration, nav=None) is context
    assert all(item["link"].endswith("/guides/alpha-cuts/") for item in configuration.extra["alternate"])
    rendered = OnPageMarkdown("# Page", page=page, config=configuration, files=None)
    assert "Draft translation" in rendered
    assert rendered.endswith("# Page")


def test_StagingRetainsSharedFigureBytesAndNeverApprovesADraft(tmpPath):
    """Use the translated prose and the exact same scientific asset without promotion."""

    sourceRoot = tmpPath / "source"
    assets = sourceRoot / "docs/site/content/en/assets"
    assets.mkdir(parents=True)
    (assets / "figure.svg").write_bytes(b"<svg>English labels</svg>")
    translation = sourceRoot / "docs/site/content/ru/index.md"
    translation.parent.mkdir(parents=True)
    translation.write_text("# Русский текст\n", encoding="utf-8")
    unit = CanonicalUnit("page:index", "page", "docs/site/content/en/index.md", "", "# English\n")
    record = {"translations": {"ru": {"path": "docs/site/content/ru/index.md", "state": "draft"}}}
    report = ValidationReport((), {"page:index": {"ru": "draft"}})
    content, _, evidence = StageLocale(sourceRoot, tmpPath / "output", "ru", {"branding": {"assetRoot": "docs/site/content/en/assets"}}, (unit,), {"page:index": record}, report)
    assert (content / "index.md").read_text(encoding="utf-8") == "# Русский текст\n"
    assert (content / "assets/figure.svg").read_bytes() == (assets / "figure.svg").read_bytes()
    assert evidence["approved"] is False


def test_GriffeTranslationChangesDocumentationWithoutExecutingOrChangingTheApi(tmpPath):
    """Static discovery must preserve signatures/source and never execute project code."""

    griffe = pytest.importorskip("griffe")
    source = tmpPath / "sample.py"
    source.write_text('raise RuntimeError("project import is forbidden")\n\ndef Calculate(value: float = 1.0) -> float:\n    """Canonical English documentation."""\n    return value\n', encoding="utf-8")
    translationMap = tmpPath / "translations.json"
    translationMap.write_text(json.dumps({"sample.Calculate": "Русское описание."}), encoding="utf-8")
    extensions = griffe.load_extensions({str(PROJECTROOT / "tools/locale_griffe_extension.py"): {"translationMap": str(translationMap)}})
    module = griffe.load("sample", search_paths=[tmpPath], extensions=extensions, allow_inspection=False)
    function = module["Calculate"]
    assert function.docstring.value == "Русское описание."
    assert function.parameters["value"].default == "1.0"
    assert str(function.returns) == "float"
    assert "Canonical English documentation." in function.source


def test_OnePageLocaleBuildRendersTranslatedApiAndPreservesStableAnchors(tmpPath):
    """Exercise real MkDocs/Griffe wiring on one small page instead of a full local gate."""

    pytest.importorskip("mkdocs")
    sourceRoot = tmpPath / "source"
    assets = sourceRoot / "docs/site/content/en/assets"
    assets.mkdir(parents=True)
    (assets / "figure.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
    toolRoot = sourceRoot / "tools"
    toolRoot.mkdir()
    for name in ("locale_site_hook.py", "locale_griffe_extension.py"):
        (toolRoot / name).write_bytes((PROJECTROOT / "tools" / name).read_bytes())
    modulePath = sourceRoot / "sample.py"
    modulePath.write_text('raise RuntimeError("forbidden import")\n\ndef Calculate(value: float = 1.0) -> float:\n    """Canonical explanation."""\n    return value\n', encoding="utf-8")
    configuration = sourceRoot / "docs/site/mkdocs.yml"
    configuration.write_text(f'''site_name: Fixture
repo_url: https://github.com/Fuzzy-Technologies/FuzzyRoutines
strict: true
theme:
  name: material
nav:
  - Overview: index.md
markdown_extensions: [attr_list, toc]
plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [{sourceRoot.as_posix()}]
          options:
            show_root_heading: true
''', encoding="utf-8")
    pageTranslation = sourceRoot / "docs/site/content/ru/index.md"
    pageTranslation.parent.mkdir(parents=True)
    pageTranslation.write_text("# Расчёт {#calculation}\n\n![Общая фигура](../en/assets/figure.svg)\n\n::: sample.Calculate\n", encoding="utf-8")
    symbolTranslation = sourceRoot / "docs/i18n/ru-calculate.md"
    symbolTranslation.parent.mkdir()
    symbolTranslation.write_text("Вычислить значение без изменения входных данных.", encoding="utf-8")
    units = (
        CanonicalUnit("page:index", "page", "docs/site/content/en/index.md", "", "# Calculation\n\n::: sample.Calculate\n"),
        CanonicalUnit("symbol:sample.Calculate", "symbol", "sample.py", "", "Canonical explanation."),
    )
    records = {
        unit.identifier: {"translations": {"ru": {"path": path.relative_to(sourceRoot).as_posix(), "state": "draft"}}}
        for unit, path in zip(units, (pageTranslation, symbolTranslation), strict=True)
    }
    report = ValidationReport((), {unit.identifier: {"ru": "draft"} for unit in units})
    outputRoot = tmpPath / "output"
    BuildLocale(sourceRoot, outputRoot, "ru", {"branding": {"assetRoot": "docs/site/content/en/assets"}}, units, records, report)
    rendered = (outputRoot / "ru/site/index.html").read_text(encoding="utf-8")
    assert 'id="calculation"' in rendered
    assert 'id="sample.Calculate"' in rendered
    assert "Вычислить значение без изменения входных данных." in rendered
    assert "Предварительная версия для рецензирования" in rendered
    assert 'src="assets/figure.svg"' in rendered
    search = json.loads((outputRoot / "ru/site/search/search_index.json").read_text(encoding="utf-8"))
    assert any("Вычислить значение" in item["text"] for item in search["docs"])
