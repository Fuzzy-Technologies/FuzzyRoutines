# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Render all user-documentation locales from source-bound translation records.

Run inside the installed-wheel documentation environment. Drafts may be built
as labelled review artifacts, but only completely approved locales can replace
public fallback routes. The stable release gate separately requires all locales.
"""

from __future__ import annotations

import argparse
import inspect
import json
import posixpath
import re
import shutil
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from tools.locale_documentation import DiscoverCanonicalUnits, ValidateLocales

PROJECTROOT = Path(__file__).resolve().parents[1]
CONTENTROOT = "docs/site/content/en"
LANGUAGES = {"en": "en", "ru": "ru", "zh-CN": "zh"}
CATEGORIES = {
    "ru": {"Worked scenarios": "Практические сценарии", "API reference": "Справочник API", "Modern API": "Современный API", "Historical API": "Исторический API", "Mathematics": "Математические основы", "Migration": "Миграция", "API contracts": "Контракты API", "Product overview": "О проекте", "Languages and versions": "Языки и версии"},
    "zh-CN": {"Worked scenarios": "应用场景", "API reference": "API 参考", "Modern API": "现代 API", "Historical API": "历史 API", "Mathematics": "数学基础", "Migration": "迁移", "API contracts": "API 契约", "Product overview": "项目概览", "Languages and versions": "语言与版本"},
}
PREVIEWBANNERS = {
    "ru": "Предварительная версия для рецензирования. Переводы ещё не утверждены; отсутствующие разделы показаны на английском. Это не принятая русская документация релиза.",
    "zh-CN": "供审阅的预览版本。译文尚未获得批准；缺失部分以英文显示。此版本并非发布版的已批准中文文档。",
}


def ReadInputs(projectRoot):
    """Validate all hashes and return canonical units, records and project metadata."""

    report = ValidateLocales(projectRoot)

    if report.diagnostics:
        raise ValueError("\n".join(report.diagnostics))

    project = tomllib.loads((projectRoot / "docs/i18n/project.toml").read_text(encoding="utf-8"))
    records = tomllib.loads((projectRoot / project["unitManifest"]).read_text(encoding="utf-8"))["units"]
    units = DiscoverCanonicalUnits(projectRoot, project, {
        record["sourcePath"]: record["id"] for record in records if record["kind"] == "page"
    })
    return project, units, {record["id"]: record for record in records}, report


def PageDestination(unit, project):
    """Resolve one stable page route independently of language or translated title."""

    for page in project.get("externalPages", ()):
        if page["id"] == unit.identifier:
            return page["destination"]

    return Path(unit.sourcePath).relative_to(CONTENTROOT).as_posix()


def RewriteExternalLinks(text, sourcePath, destination, destinations):
    """Keep staged mathematical/migration references linked to their real sources."""

    def Replace(match):
        """Resolve relative Markdown links before moving a canonical external page."""

        label, target = match.groups()
        parsed = urlsplit(target)

        if parsed.scheme or parsed.netloc or not parsed.path or target.startswith("/"):
            return match.group(0)

        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(sourcePath), parsed.path))
        suffix = f"#{parsed.fragment}" if parsed.fragment else ""

        if resolved in destinations:
            rewritten = posixpath.relpath(destinations[resolved], posixpath.dirname(destination))
            return f"[{label}]({rewritten}{suffix})"

        return f"[{label}](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/{resolved}{suffix})"

    return re.sub(r"\[([^\]]+)\]\(([^\s)]+)\)", Replace, text)


def AuthoredSymbolPath(unit):
    """Resolve root/facade aliases to their physical Griffe object identity."""

    if unit.kind == "module":
        return unit.identifier.removeprefix("module:")

    modulePath = Path(unit.sourcePath).with_suffix("")
    moduleName = ".".join(modulePath.parts)
    publicPath = unit.identifier.removeprefix("symbol:")
    components = publicPath.split(".")
    definitionIndex = 2 if components[1] == "FuzzyRoutines" else next(
        index for index, part in enumerate(components) if part[:1].isupper()
    )
    return moduleName + "." + ".".join(components[definitionIndex:])


def StageLocale(projectRoot, outputRoot, locale, project, units, records, report):
    """Prepare disposable Markdown, shared assets and a static API translation map."""

    contentRoot = outputRoot / locale / "content"
    contentRoot.mkdir(parents=True)
    shutil.copytree(projectRoot / project["branding"]["assetRoot"], contentRoot / "assets")
    destinations = {
        unit.sourcePath: PageDestination(unit, project) for unit in units if unit.kind == "page"
    }
    symbolTranslations = {}
    statuses = {}

    for unit in units:
        record = records[unit.identifier]
        translation = record.get("translations", {}).get(locale, {})
        state = report.states[unit.identifier].get(locale, "canonical")
        translatedPath = translation.get("path")
        body = unit.body
        linkSourcePath = unit.sourcePath

        if locale != "en" and translatedPath and state in {"draft", "review", "approved"}:
            body = (projectRoot / translatedPath).read_text(encoding="utf-8")
            linkSourcePath = translatedPath

        statuses[unit.identifier] = state

        if unit.kind == "page":
            destination = destinations[unit.sourcePath]
            assetPrefix = posixpath.relpath("assets", posixpath.dirname(destination)) + "/"
            body = re.sub(r"(?<=\]\()(?:(?:\.\./)+en/assets/)", assetPrefix, body)

            if not unit.sourcePath.startswith(CONTENTROOT + "/"):
                body = RewriteExternalLinks(body, linkSourcePath, destination, destinations)

            pagePath = contentRoot / destination
            pagePath.parent.mkdir(parents=True, exist_ok=True)
            pagePath.write_text(body, encoding="utf-8")

        elif locale != "en" and translatedPath:
            symbolPath = AuthoredSymbolPath(unit)
            translated = inspect.cleandoc(body).strip()
            existing = symbolTranslations.get(symbolPath)

            if existing is not None and existing != translated:
                raise ValueError(f"conflicting alias translations: {symbolPath}")

            symbolTranslations[symbolPath] = translated

    mapPath = outputRoot / locale / "docstrings.json"
    mapPath.write_text(json.dumps(symbolTranslations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    approved = locale == "en" or all(state == "approved" for state in statuses.values())
    return contentRoot, mapPath, {"approved": approved, "states": statuses}


def LocalizeNavigation(navigation, locale, contentRoot):
    """Translate labels while retaining every canonical page route and ordering."""

    localized = []

    for entry in navigation:
        for title, value in entry.items():
            label = CATEGORIES.get(locale, {}).get(title, title)

            if isinstance(value, list):
                value = LocalizeNavigation(value, locale, contentRoot)

            elif value.endswith(".md") and (contentRoot / value).is_file():
                text = (contentRoot / value).read_text(encoding="utf-8")
                match = re.search(r"^# (.+?)(?:\s*\{#[^}]+\})?$", text, re.MULTILINE)

                if match:
                    label = match.group(1)

            localized.append({label: value})

    return localized


def BuildLocale(projectRoot, outputRoot, locale, project, units, records, report):
    """Render a strict locale site with static installed-wheel discovery."""

    from mkdocs.commands.build import build
    from mkdocs.config import load_config as LoadConfig
    from mkdocs.utils.yaml import yaml_load as LoadYaml

    contentRoot, mapPath, evidence = StageLocale(projectRoot, outputRoot, locale, project, units, records, report)
    configPath = projectRoot / "docs/site/mkdocs.yml"

    with configPath.open(encoding="utf-8") as configFile:
        settings = LoadYaml(configFile)

    navigation = [entry for entry in settings["nav"] if "Mathematics guides" not in entry]

    for section, prefix in (("Mathematics", "mathematics/"), ("Migration", "migration/"), ("API contracts", "contracts/")):
        pages = [{page["title"]: page["destination"]} for page in project.get("externalPages", ()) if page["destination"].startswith(prefix)]
        if pages:
            navigation.append({section: pages})

    settings["nav"] = LocalizeNavigation(navigation, locale, contentRoot)
    settings["docs_dir"] = str(contentRoot)
    settings["site_dir"] = str(outputRoot / locale / "site")
    settings["site_url"] = f"https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/{locale}/"
    settings["edit_uri"] = f"edit/develop/docs/site/content/{locale}/"
    settings["theme"]["language"] = LANGUAGES[locale]
    settings["hooks"] = [str(projectRoot / "tools/locale_site_hook.py")]
    settings["extra"] = {
        "localeRoot": "/FuzzyRoutines/api/latest",
        "localePreviewBanner": "" if evidence["approved"] else PREVIEWBANNERS[locale],
    }
    settings["extra"]["localePreviewTitle"] = {"ru": "Версия для рецензирования", "zh-CN": "审阅版本"}.get(locale, "Review preview")
    settings["markdown_extensions"].append("admonition")

    for plugin in settings["plugins"]:
        if isinstance(plugin, dict) and "mkdocstrings" in plugin:
            plugin["mkdocstrings"]["locale"] = LANGUAGES[locale]
            options = plugin["mkdocstrings"]["handlers"]["python"]["options"]

            if locale != "en":
                options["extensions"] = [{str(projectRoot / "tools/locale_griffe_extension.py"): {"translationMap": str(mapPath)}}]

    configuration = LoadConfig(str(configPath), **settings)
    build(configuration)
    siteRoot = Path(settings["site_dir"])

    for unit in units:
        if unit.kind == "page":
            destination = Path(PageDestination(unit, project))
            route = destination.parent / "index.html" if destination.name == "index.md" else destination.with_suffix("") / "index.html"
            if not (siteRoot / route).is_file():
                raise AssertionError(f"missing {locale} route: {route}")

    for artifact in ("objects.inv", "search/search_index.json"):
        if not (siteRoot / artifact).is_file():
            raise AssertionError(f"missing {locale} artifact: {artifact}")

    searchIndex = json.loads((siteRoot / "search/search_index.json").read_text(encoding="utf-8"))
    if locale == "zh-CN" and not any("\u200b" in entry["text"] for entry in searchIndex["docs"]):
        raise AssertionError("Chinese search needs segmented text; install the pinned jieba documentation dependency")

    sourceAssets = projectRoot / project["branding"]["assetRoot"]
    for asset in sourceAssets.rglob("*"):
        if asset.is_file() and (siteRoot / "assets" / asset.relative_to(sourceAssets)).read_bytes() != asset.read_bytes():
            raise AssertionError(f"shared asset changed in {locale}: {asset.name}")

    (outputRoot / locale / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Locale reference: {locale} PASS ({len(evidence['states'])} units; approved={evidence['approved']})")


def Main(arguments=None):
    """Build the requested locale into a fresh, explicitly disposable directory."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", choices=tuple(LANGUAGES), required=True)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args(arguments)
    project, units, records, report = ReadInputs(PROJECTROOT)
    BuildLocale(PROJECTROOT, options.output.resolve(), options.locale, project, units, records, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
