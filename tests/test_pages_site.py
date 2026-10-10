# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Structural and link contracts for the project Pages site."""

import contextlib
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path
from urllib.parse import urlsplit

PROJECT_ROOT = Path(__file__).parents[1]
SITE_ROOT = PROJECT_ROOT / "docs"


class PageParser(HTMLParser):
    """Collect page metadata, anchors and links without executing JavaScript."""

    def __init__(self):
        """Initialize independent metadata, anchor and link collections."""

        super().__init__()
        self.ids = set()
        self.links = []
        self.metaNames = set()
        self.hasTitle = False

    def handle_starttag(self, tag, attributes):
        """Record title presence, metadata names, anchors and navigational links."""

        attributeMap = dict(attributes)
        if "id" in attributeMap:
            self.ids.add(attributeMap["id"])
        if tag in {"a", "link"} and "href" in attributeMap:
            self.links.append(attributeMap["href"])
        if tag == "meta" and "name" in attributeMap:
            self.metaNames.add(attributeMap["name"])
        if tag == "title":
            self.hasTitle = True


def ParsePage(pagePath):
    """Parse one tracked UTF-8 HTML page for structural and link assertions."""

    parser = PageParser()
    parser.feed(pagePath.read_text(encoding="utf-8"))
    return parser


def test_PagesEntryPointHasRequiredMetadata():
    """Verify that pages entry point has required metadata."""

    pagePath = SITE_ROOT / "index.html"
    parser = ParsePage(pagePath)

    assert parser.hasTitle
    assert {"description", "viewport"} <= parser.metaNames


def test_PagesLocalLinksAndFragmentsResolve():
    """Verify that pages local links and fragments resolve."""

    pagePath = SITE_ROOT / "index.html"
    parser = ParsePage(pagePath)

    for link in parser.links:
        parsedLink = urlsplit(link)
        if parsedLink.scheme or parsedLink.netloc:
            assert parsedLink.scheme == "https"
            continue

        if parsedLink.path:
            assetPrefix = "api/latest/en/assets/"
            relativePath = parsedLink.path

            if relativePath.startswith(assetPrefix):
                relativePath = "site/content/en/assets/" + relativePath[len(assetPrefix):]

            targetPath = (pagePath.parent / relativePath).resolve()
            assert targetPath.is_relative_to(SITE_ROOT.resolve())
            assert targetPath.exists(), link

        if parsedLink.fragment:
            assert parsedLink.fragment in parser.ids, link


def test_PagesSiteKeepsInteractionsLocal():
    """Keep copy and image interactions available without remote scripts."""

    pageText = (SITE_ROOT / "index.html").read_text(encoding="utf-8")

    assert '<script defer src="assets/site.js"></script>' in pageText
    assert '<script defer src="api/latest/en/assets/javascripts/lightbox.js"></script>' in pageText
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


def test_PagesQuickstartProducesDisplayedOutput():
    """Execute the user-facing example and compare its advertised result."""

    from xml.etree import ElementTree
    import re

    pageText = (SITE_ROOT / "index.html").read_text(encoding="utf-8")
    blocks = {
        match.group(1): ElementTree.fromstring(match.group(0)).text
        for match in re.finditer(r'<code id="([^"]+)">.*?</code>', pageText, re.S)
    }
    output = StringIO()

    with contextlib.redirect_stdout(output):
        exec(compile(blocks["quickstart-code"], "homepage-quickstart", "exec"), {})

    assert output.getvalue().strip() == blocks["quickstart-output"]
    assert "git+" not in pageText
