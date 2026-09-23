# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Compose the product page and generated API reference for GitHub Pages.

The command copies only reviewed static inputs into a disposable Pages root.
English is the canonical API reference. Reserved Russian and Simplified
Chinese routes render explicit fallback pages until reviewed translations
exist; they never masquerade English content as translated documentation.
"""

import argparse
import html
import shutil
import tomllib
from pathlib import Path

PROJECTROOT = Path(__file__).parents[1]
DEFAULTAPISITE = PROJECTROOT / "_build" / "api-reference" / "site"
DEFAULTOUTPUT = PROJECTROOT / "_build" / "pages" / "site"
PRODUCTROOT = PROJECTROOT / "docs"
PROJECTMETADATA = PROJECTROOT / "pyproject.toml"
PUBLICROOT = "https://fuzzy-technologies.github.io/FuzzyRoutines"
LOCALES = {
    "ru": ("Русский", "Перевод пока не опубликован."),
    "zh-CN": ("简体中文", "翻译尚未发布。"),
}


def ParseArguments(arguments=None):
    """Parse explicit composition inputs and the disposable output path."""

    parser = argparse.ArgumentParser(
        description="Compose the complete FuzzyRoutines GitHub Pages artifact.",
    )
    parser.add_argument(
        "--api-site",
        dest="apiSite",
        type=Path,
        default=DEFAULTAPISITE,
        help="Generated strict API-reference site.",
    )
    parser.add_argument(
        "--output",
        dest="outputRoot",
        type=Path,
        default=DEFAULTOUTPUT,
        help="Disposable Pages artifact root.",
    )
    return parser.parse_args(arguments)


def ReadPackageVersion():
    """Return the canonical PEP 621 package version without importing code."""

    with PROJECTMETADATA.open("rb") as metadataFile:
        metadata = tomllib.load(metadataFile)

    return metadata["project"]["version"]


def ValidateApiSite(apiSite):
    """Reject incomplete generated API input before copying any output."""

    requiredPaths = (
        apiSite / "index.html",
        apiSite / "api" / "index.html",
        apiSite / "objects.inv",
        apiSite / "search" / "search_index.json",
    )
    for requiredPath in requiredPaths:
        if not requiredPath.is_file():
            raise FileNotFoundError(
                f"generated API reference is incomplete: {requiredPath}"
            )


def RecreateOutput(outputRoot):
    """Replace only the selected disposable output directory."""

    resolvedOutput = outputRoot.resolve()
    if resolvedOutput in {PROJECTROOT.resolve(), PRODUCTROOT.resolve()}:
        raise ValueError(f"refusing to replace source directory: {resolvedOutput}")

    if resolvedOutput.exists():
        shutil.rmtree(resolvedOutput)

    resolvedOutput.mkdir(parents=True)
    return resolvedOutput


def WriteLocaleFallback(routeRoot, locale, languageName, statusText):
    """Write an accessible locale placeholder linked to canonical English."""

    canonicalUrl = f"{PUBLICROOT}/api/latest/{locale}/"
    englishUrl = f"{PUBLICROOT}/api/latest/en/"
    versionsUrl = f"{PUBLICROOT}/api/versions/"
    productUrl = f"{PUBLICROOT}/"
    pageText = f"""<!doctype html>
<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->
<html lang="{html.escape(locale)}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="FuzzyRoutines {html.escape(languageName)} documentation status." />
    <link rel="canonical" href="{canonicalUrl}" />
    <link rel="stylesheet" href="../../../assets/site.css" />
    <title>FuzzyRoutines documentation — {html.escape(languageName)}</title>
  </head>
  <body>
    <a class="skip-link" href="#content">Skip to content</a>
    <main id="content">
      <header class="site-header">
        <a class="site-title" href="{productUrl}">◒ FuzzyRoutines</a>
      </header>
      <section class="hero" aria-labelledby="fallback-title">
        <div class="hero-copy">
          <p class="eyebrow">{html.escape(languageName)} · reserved route</p>
          <h1 id="fallback-title">{html.escape(statusText)}</h1>
          <p class="hero-lead" lang="en">
            Reviewed documentation is not available for this locale yet.
            Use the canonical English API reference; this route will remain
            stable when reviewed translations are published.
          </p>
          <div class="hero-actions">
            <a class="button primary" href="{englishUrl}" hreflang="en">English API reference</a>
            <a class="button" href="{versionsUrl}">Documentation versions</a>
          </div>
        </div>
      </section>
    </main>
  </body>
</html>
"""
    routeRoot.mkdir(parents=True)
    (routeRoot / "index.html").write_text(pageText, encoding="utf-8")


def WriteApiEntry(apiRoot):
    """Write the stable API entry point with locale and version navigation."""

    pageText = """<!doctype html>
<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="FuzzyRoutines API reference languages and versions." />
    <link rel="canonical" href="https://fuzzy-technologies.github.io/FuzzyRoutines/api/" />
    <link rel="stylesheet" href="../assets/site.css" />
    <title>FuzzyRoutines API reference</title>
  </head>
  <body>
    <a class="skip-link" href="#content">Skip to content</a>
    <main id="content">
      <header class="site-header">
        <a class="site-title" href="../">◒ FuzzyRoutines</a>
      </header>
      <section class="hero" aria-labelledby="api-title">
        <div class="hero-copy">
          <p class="eyebrow">Canonical documentation</p>
          <h1 id="api-title">API reference</h1>
          <p class="hero-lead">Choose the current language route or inspect immutable release documentation.</p>
          <div class="hero-actions">
            <a class="button primary" href="latest/en/" hreflang="en">English</a>
            <a class="button" href="latest/ru/" hreflang="ru">Русский</a>
            <a class="button" href="latest/zh-CN/" hreflang="zh-CN">简体中文</a>
            <a class="button" href="versions/">Versions</a>
          </div>
        </div>
      </section>
    </main>
  </body>
</html>
"""
    (apiRoot / "index.html").write_text(pageText, encoding="utf-8")


def WriteVersionIndex(apiRoot, packageVersion):
    """Describe latest versus immutable releases without inventing a release."""

    pageText = f"""<!doctype html>
<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="FuzzyRoutines API reference version policy." />
    <link rel="canonical" href="{PUBLICROOT}/api/versions/" />
    <link rel="stylesheet" href="../../assets/site.css" />
    <title>FuzzyRoutines documentation versions</title>
  </head>
  <body>
    <a class="skip-link" href="#content">Skip to content</a>
    <main id="content">
      <header class="site-header">
        <a class="site-title" href="../../">◒ FuzzyRoutines</a>
      </header>
      <section class="hero" aria-labelledby="versions-title">
        <div class="hero-copy">
          <p class="eyebrow">Documentation lifecycle</p>
          <h1 id="versions-title">Latest and immutable releases</h1>
          <p class="hero-lead">
            <a href="../latest/en/">Latest English documentation</a> tracks the approved
            default branch and currently describes package version
            <code>{html.escape(packageVersion)}</code>.
          </p>
          <p>
            No stable 2.x release documentation has been published yet.
            Stable releases will appear under <code>/api/versions/&lt;version&gt;/</code>
            and will never be relabelled as another version.
          </p>
        </div>
      </section>
    </main>
  </body>
</html>
"""
    versionsRoot = apiRoot / "versions"
    versionsRoot.mkdir()
    (versionsRoot / "index.html").write_text(pageText, encoding="utf-8")


def ComposeSite(apiSite, outputRoot):
    """Create and verify one complete disposable Pages directory."""

    apiSite = apiSite.resolve()
    ValidateApiSite(apiSite)
    outputRoot = RecreateOutput(outputRoot)

    shutil.copy2(PRODUCTROOT / "index.html", outputRoot / "index.html")
    shutil.copytree(PRODUCTROOT / "assets", outputRoot / "assets")

    apiRoot = outputRoot / "api"
    englishRoot = apiRoot / "latest" / "en"
    englishRoot.parent.mkdir(parents=True)
    shutil.copytree(apiSite, englishRoot)

    for locale, (languageName, statusText) in LOCALES.items():
        WriteLocaleFallback(
            apiRoot / "latest" / locale,
            locale,
            languageName,
            statusText,
        )

    WriteApiEntry(apiRoot)
    WriteVersionIndex(apiRoot, ReadPackageVersion())

    requiredOutput = (
        outputRoot / "index.html",
        englishRoot / "index.html",
        apiRoot / "latest" / "ru" / "index.html",
        apiRoot / "latest" / "zh-CN" / "index.html",
        apiRoot / "versions" / "index.html",
    )
    for requiredPath in requiredOutput:
        if not requiredPath.is_file():
            raise AssertionError(f"Pages artifact is missing route: {requiredPath}")

    return outputRoot


def Main(arguments=None):
    """Compose the Pages site and report its verified disposable location."""

    options = ParseArguments(arguments)
    outputRoot = ComposeSite(options.apiSite, options.outputRoot)
    print(f"GitHub Pages composition: PASS ({outputRoot})")
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
