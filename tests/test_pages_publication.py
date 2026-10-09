# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic contracts for GitHub Pages composition and publication."""

import json
from pathlib import Path

from tools import compose_pages_site as composePagesSite

PROJECTROOT = Path(__file__).parents[1]
WORKFLOWPATH = PROJECTROOT / ".github" / "workflows" / "api-reference.yml"


def CreateApiFixture(apiRoot):
    """Create the smallest generated API tree accepted by the composer."""

    (apiRoot / "api").mkdir(parents=True)
    (apiRoot / "search").mkdir()
    (apiRoot / "index.html").write_text("<html>English API</html>", encoding="utf-8")
    (apiRoot / "api" / "index.html").write_text(
        "<html>API index</html>",
        encoding="utf-8",
    )
    (apiRoot / "objects.inv").write_bytes(b"inventory")
    (apiRoot / "search" / "search_index.json").write_text("{}", encoding="utf-8")


def test_PagesCompositionPublishesEnglishAndHonestLocaleFallbacks(tmpPath):
    """Keep every advertised language route real and semantically honest."""

    apiRoot = tmpPath / "generated-api"
    outputRoot = tmpPath / "pages"
    CreateApiFixture(apiRoot)

    composePagesSite.ComposeSite(apiRoot, outputRoot)

    englishPage = outputRoot / "api" / "latest" / "en" / "index.html"
    russianPage = outputRoot / "api" / "latest" / "ru" / "index.html"
    chinesePage = outputRoot / "api" / "latest" / "zh-CN" / "index.html"

    assert englishPage.read_text(encoding="utf-8") == "<html>English API</html>"
    for fallbackPage in (russianPage, chinesePage):
        fallbackText = fallbackPage.read_text(encoding="utf-8")

        assert "Reviewed documentation is not available" in fallbackText
        assert "/api/latest/en/" in fallbackText
        assert 'rel="canonical"' in fallbackText
        assert fallbackPage.is_file()


def test_PagesCompositionRejectsIncompleteApiInputBeforeWriting(tmpPath):
    """Fail closed rather than publishing a partial API reference."""

    apiRoot = tmpPath / "incomplete-api"
    outputRoot = tmpPath / "pages"
    apiRoot.mkdir()

    try:
        composePagesSite.ComposeSite(apiRoot, outputRoot)

    except FileNotFoundError as error:
        assert "generated API reference is incomplete" in str(error)

    else:
        raise AssertionError("incomplete API input must fail Pages composition")

    assert not outputRoot.exists()


def test_DraftLocalesAreAvailableOnlyInAnExplicitReviewArtifact(tmpPath):
    """Production composition must not replace honest fallbacks with unapproved prose."""

    apiRoot = tmpPath / "english"
    CreateApiFixture(apiRoot)
    localeRoot = tmpPath / "locales"
    CreateApiFixture(localeRoot / "ru/site")
    (localeRoot / "ru/evidence.json").write_text(json.dumps({"approved": False}), encoding="utf-8")
    publicRoot = tmpPath / "public"
    reviewRoot = tmpPath / "review"
    composePagesSite.ComposeSite(apiRoot, publicRoot, localeRoot)
    composePagesSite.ComposeSite(apiRoot, reviewRoot, localeRoot, includeDrafts=True)
    assert "Reviewed documentation is not available" in (publicRoot / "api/latest/ru/index.html").read_text(encoding="utf-8")
    assert (reviewRoot / "api/latest/ru/index.html").read_text(encoding="utf-8") == "<html>English API</html>"
    deepFallback = (publicRoot / "api/latest/ru/api/index.html").read_text(encoding="utf-8")
    assert "/api/latest/en/api/" in deepFallback
    assert 'href="../../../../assets/site.css"' in deepFallback


def test_PagesVersionIndexDoesNotInventAnUnreleasedVersion(tmpPath):
    """Distinguish the moving latest route from immutable stable releases."""

    apiRoot = tmpPath / "generated-api"
    outputRoot = tmpPath / "pages"
    CreateApiFixture(apiRoot)

    composePagesSite.ComposeSite(apiRoot, outputRoot)
    versionText = (
        outputRoot / "api" / "versions" / "index.html"
    ).read_text(encoding="utf-8")

    assert "2.0.0.dev0" in versionText
    assert "No stable 2.x release documentation has been published yet" in versionText
    assert "/api/versions/&lt;version&gt;/" in versionText


def test_PagesWorkflowBuildsEveryReviewButDeploysOnlyMaster():
    """Keep documentation builds independent from production publication."""

    workflowText = WORKFLOWPATH.read_text(encoding="utf-8")

    assert "actions/upload-pages-artifact@v3" in workflowText
    assert "actions/deploy-pages@v4" in workflowText
    assert "github.event_name == 'push'" in workflowText
    assert "github.ref == 'refs/heads/master'" in workflowText
    assert "pages: write" in workflowText
    assert "id-token: write" in workflowText
    assert "python tools/compose_pages_site.py" in workflowText
