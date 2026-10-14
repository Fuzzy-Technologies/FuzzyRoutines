# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Structural and link contracts for the project Pages site."""

import contextlib
import posixpath
import re
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path
from urllib.parse import urlsplit

import pytest

PROJECT_ROOT = Path(__file__).parents[1]
SITE_ROOT = PROJECT_ROOT / "docs"
LOCALES = ("en", "ru", "zh-CN")


class PageParser(HTMLParser):
    """Collect page metadata, anchors and links without executing JavaScript."""

    def __init__(self):
        """Initialize independent metadata, anchor and link collections."""

        super().__init__()
        self.ids = set()
        self.links = []
        self.metaNames = set()
        self.hasTitle = False
        self.elements = []

    def handle_starttag(self, tag, attributes):
        """Record title presence, metadata names, anchors and navigational links."""

        attributeMap = dict(attributes)
        self.elements.append((tag, attributeMap))
        if "id" in attributeMap:
            self.ids.add(attributeMap["id"])
        if tag in {"a", "link"} and "href" in attributeMap:
            self.links.append(attributeMap["href"])
        if tag == "meta" and "name" in attributeMap:
            self.metaNames.add(attributeMap["name"])
        if tag == "title":
            self.hasTitle = True


def LandingPath(locale):
    """Resolve each authored product landing route, independently of API locales."""

    return SITE_ROOT / "index.html" if locale == "en" else SITE_ROOT / locale / "index.html"


def ParsePage(pagePath):
    """Parse one tracked UTF-8 HTML page for structural and link assertions."""

    parser = PageParser()
    parser.feed(pagePath.read_text(encoding="utf-8"))
    return parser


@pytest.mark.parametrize("locale", LOCALES)
def test_PagesEntryPointHasRequiredMetadata(locale):
    """Verify that pages entry point has required metadata."""

    pagePath = LandingPath(locale)
    parser = ParsePage(pagePath)

    assert parser.hasTitle
    assert {"description", "viewport"} <= parser.metaNames


@pytest.mark.parametrize("locale", LOCALES)
def test_PagesLocalLinksAndFragmentsResolve(locale):
    """Verify that pages local links and fragments resolve."""

    pagePath = LandingPath(locale)
    parser = ParsePage(pagePath)

    for link in parser.links:
        parsedLink = urlsplit(link)
        if parsedLink.scheme or parsedLink.netloc:
            assert parsedLink.scheme == "https"
            continue

        if parsedLink.path:
            assetPrefix = "api/latest/en/assets/"
            relativeDirectory = "" if locale == "en" else locale
            relativePath = posixpath.normpath(posixpath.join(relativeDirectory, parsedLink.path))

            if relativePath.startswith(assetPrefix):
                relativePath = "site/content/en/assets/" + relativePath[len(assetPrefix):]

            targetPath = (SITE_ROOT / relativePath).resolve()
            assert targetPath.is_relative_to(SITE_ROOT.resolve())
            assert targetPath.exists(), link

        if parsedLink.fragment:
            assert parsedLink.fragment in parser.ids, link


@pytest.mark.parametrize("locale", LOCALES)
def test_PagesSiteKeepsInteractionsLocal(locale):
    """Keep copy and image interactions available without remote scripts."""

    pageText = LandingPath(locale).read_text(encoding="utf-8")
    prefix = "" if locale == "en" else "../"

    assert f'<script defer src="{prefix}assets/site.js"></script>' in pageText
    assert f'<script defer src="{prefix}api/latest/en/assets/javascripts/lightbox.js"></script>' in pageText
    assert '<script src="http' not in pageText.lower()
    assert "http://" not in pageText.lower()


def test_PagesSiteSeparatesImplementedBehaviorFromRoadmap():
    """Verify that pages site separates implemented behavior from roadmap."""

    pageText = (SITE_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'data-status="implemented"' in pageText
    assert 'data-status="roadmap"' in pageText
    assert "Implemented in 2.0" in pageText
    assert "Future work" in pageText
    assert "current-status.md" in pageText


@pytest.mark.parametrize("locale", LOCALES)
def test_PagesQuickstartProducesDisplayedOutput(locale):
    """Execute the user-facing example and compare its advertised result."""

    from xml.etree import ElementTree

    pageText = LandingPath(locale).read_text(encoding="utf-8")
    blocks = {
        match.group(1): ElementTree.fromstring(match.group(0)).text
        for match in re.finditer(r'<code id="([^"]+)">.*?</code>', pageText, re.DOTALL)
    }
    output = StringIO()

    with contextlib.redirect_stdout(output):
        exec(compile(blocks["quickstart-code"], "homepage-quickstart", "exec"), {})  # noqa: S102 -- Execute the repository-owned tutorial contract.

    assert output.getvalue().strip() == blocks["quickstart-output"]
    assert "git+" not in pageText


def test_LandingLocalesPreserveLayoutAndExecutableContent():
    """Keep one product design and numerical example across independently reviewed prose."""

    canonical = ParsePage(LandingPath("en"))
    protectedAttributes = {"id", "class", "role", "type", "data-copy-target", "width", "height", "loading", "fetchpriority"}
    canonicalLayout = [(tag, {key: value for key, value in attributes.items() if key in protectedAttributes})
                       for tag, attributes in canonical.elements]
    english = LandingPath("en").read_text(encoding="utf-8")
    codePattern = r'<code id="([^\"]+)">(.*?)</code>'

    for locale in ("ru", "zh-CN"):
        translated = ParsePage(LandingPath(locale))
        layout = [(tag, {key: value for key, value in attributes.items() if key in protectedAttributes})
                  for tag, attributes in translated.elements]
        assert layout == canonicalLayout, f"{locale} must preserve the shared product layout and interactions."
        text = LandingPath(locale).read_text(encoding="utf-8")
        assert re.findall(codePattern, text, re.DOTALL) == re.findall(codePattern, english, re.DOTALL)
        assert "Quick start" not in text and "Expected output" not in text


@pytest.mark.parametrize("locale", LOCALES)
def test_LandingLanguageLinksAndApiDestinationsAreExplicit(locale):
    """Support direct locale URLs and route ordinary documentation links to that locale."""

    parser = ParsePage(LandingPath(locale))
    pageRoute = "/FuzzyRoutines/" if locale == "en" else f"/FuzzyRoutines/{locale}/"
    assert next(attributes["lang"] for tag, attributes in parser.elements if tag == "html") == locale
    canonical = next(attributes["href"] for tag, attributes in parser.elements
                     if tag == "link" and attributes.get("rel") == "canonical")
    assert urlsplit(canonical).path == pageRoute
    languageLinks = [(tag, attributes) for tag, attributes in parser.elements
                     if tag == "a" and "hreflang" in attributes and "/api/" not in attributes["href"]]
    assert len(languageLinks) == 3

    for _, attributes in languageLinks:
        target = attributes["hreflang"]
        targetRoute = "/FuzzyRoutines/" if target == "en" else f"/FuzzyRoutines/{target}/"
        assert urlsplit(attributes["href"]).path == targetRoute
        assert attributes.get("aria-current") == ("page" if target == locale else None)

    for tag, attributes in parser.elements:
        if tag != "a" or "href" not in attributes or "hreflang" in attributes:
            continue

        path = urlsplit(attributes["href"]).path

        if path.startswith("/FuzzyRoutines/api/latest/") and "/assets/" not in path:
            assert path.startswith(f"/FuzzyRoutines/api/latest/{locale}/"), attributes["href"]


@pytest.mark.parametrize("locale", LOCALES)
def test_LandingAssetsRemainSharedAndResolveFromNestedRoutes(locale):
    """Prevent relative styles, scripts and images from breaking after direct navigation."""

    parser = ParsePage(LandingPath(locale))
    resolved = []

    for tag, attributes in parser.elements:
        reference = attributes.get("src") or (attributes.get("href") if tag == "link" else None)

        if not reference or urlsplit(reference).scheme:
            continue

        relativeDirectory = "" if locale == "en" else locale
        path = posixpath.normpath(posixpath.join(relativeDirectory, reference))
        resolved.append(path)
        sourcePath = path.replace("api/latest/en/assets/", "site/content/en/assets/", 1)
        assert (SITE_ROOT / sourcePath).is_file(), f"{locale}: missing shared asset {reference}"

    assert "assets/landing.css" in resolved
    assert "assets/site.js" in resolved
    assert "api/latest/en/assets/stylesheets/fonts.css" in resolved
    assert "api/latest/en/assets/javascripts/lightbox.js" in resolved
