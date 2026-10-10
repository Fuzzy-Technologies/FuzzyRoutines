# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Tests for deterministic documentation coverage and link gates."""

from pathlib import Path

from tools.documentation_gates import (
    ValidateCoverage,
    ValidateGeneratedPolicy,
    ValidateRenderedLinks,
    ValidateSourceLinks,
    ValidateTestDocumentation,
)

PROJECTROOT = Path(__file__).parents[1]


def _Write(path, text):
    """Write a UTF-8 fixture below its prepared temporary root."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_CurrentPublicApiHasCompleteReviewedCoverage():
    """Keep all public modules and symbols documented or reason-excluded."""

    assert ValidateCoverage() == ()


def test_CurrentMarkdownHasNoBrokenRepositoryLocalLinks():
    """Keep tracked narrative links and same-page fragments resolvable."""

    assert ValidateSourceLinks() == ()


def test_CurrentGeneratedOutputPolicyMatchesAcceptedAdr():
    """Keep generated-reference drift inapplicable by not committing output."""

    assert ValidateGeneratedPolicy() == ()


def test_AllTestDeclarationsHaveNonemptySourceDocstrings():
    """Cover every tracked test class, method, fixture and nested helper."""

    assert ValidateTestDocumentation() == ()


def test_TestDocumentationReportsNestedAndAsyncDeclarationsWithoutImport(tmpPath):
    """Inspect all scopes statically even when module import would fail."""

    _Write(
        tmpPath / "tests" / "test_static.py",
        'raise RuntimeError("This module must never be imported")\n'
        'class Fixture:\n'
        '    async def Evaluate(self):\n'
        '        def Nested():\n'
        '            return 1\n'
        '        return Nested()\n',
    )

    violations = ValidateTestDocumentation(tmpPath)

    assert len(violations) == 4
    assert any("test module has no source docstring" in value for value in violations)
    assert any("Fixture has no source docstring" in value for value in violations)
    assert any("Evaluate has no source docstring" in value for value in violations)
    assert any("Nested has no source docstring" in value for value in violations)


def test_TestDocumentationAcceptsDeclaredContractsAndIgnoresFixtureStrings(tmpPath):
    """Accept documented declarations without interpreting generated fixture code."""

    _Write(
        tmpPath / "tests" / "test_static.py",
        '\"\"\"Describe the static fixture.\"\"\"\n'
        'source = "def Generated(): return 1"\n'
        'class Fixture:\n'
        '    \"\"\"Own the fixture contract.\"\"\"\n'
        '    async def Evaluate(self):\n'
        '        \"\"\"Evaluate the fixture.\"\"\"\n'
        '        def Nested():\n'
        '            \"\"\"Return the fixture value.\"\"\"\n'
        '            return 1\n'
        '        return Nested()\n',
    )

    assert ValidateTestDocumentation(tmpPath) == ()


def test_TestDocumentationRejectsWhitespaceAndInvalidSyntax(tmpPath):
    """Report unusable docstrings and unreadable source with their file paths."""

    _Write(tmpPath / "tests" / "blank.py", '\"\"\"   \"\"\"\ndef Empty():\n    \"\"\"   \"\"\"\n    pass\n')
    _Write(tmpPath / "tests" / "invalid.py", 'def Broken(:\n')

    violations = ValidateTestDocumentation(tmpPath)

    assert any("blank.py:1: test module" in value for value in violations)
    assert any("Empty has no source docstring" in value for value in violations)
    assert any("invalid.py: cannot inspect test documentation" in value for value in violations)


def test_CurrentReleaseNotesDoNotDescribeTravisAsActive():
    """Keep retired Travis deployment out of current release instructions."""

    releaseNotes = (PROJECTROOT / "docs" / "release-packaging-notes.md").read_text(
        encoding="utf-8"
    )

    assert "Travis deployment configuration is retained" not in releaseNotes
    assert not (PROJECTROOT / ".travis.yml").exists()


def test_CoverageReportsMissingSymbolWithFileAndSymbol(tmpPath):
    """Make a newly undocumented public symbol actionable."""

    _Write(tmpPath / "fuzzyroutines" / "__init__.py", '__all__ = ["Visible"]\n')
    _Write(
        tmpPath / "fuzzyroutines" / "surface.py",
        'def Visible():\n    """Return a visible value."""\n    return 1\n\n'
        'def Missing():\n    """Return a missing value."""\n    return 2\n',
    )
    _Write(
        tmpPath / "docs" / "site" / "api-coverage.toml",
        'schemaVersion = 1\n\n[[surfaces]]\nmodule = "fuzzyroutines.surface"\n'
        'source = "fuzzyroutines/surface.py"\nmode = "authored"\n',
    )
    _Write(
        tmpPath / "docs" / "site" / "content" / "en" / "api.md",
        '# API\n\n::: fuzzyroutines.surface\n    options:\n'
        '      members:\n        - Visible\n',
    )

    violations = ValidateCoverage(projectRoot=tmpPath)

    assert any("fuzzyroutines/surface.py:5" in value for value in violations)
    assert any("fuzzyroutines.surface.Missing" in value for value in violations)


def test_CoverageRejectsUnexplainedAndStaleExclusions(tmpPath):
    """Prevent exclusion records from becoming an unreviewed escape hatch."""

    _Write(tmpPath / "fuzzyroutines" / "__init__.py", '__all__ = []\n')
    _Write(
        tmpPath / "docs" / "site" / "api-coverage.toml",
        'schemaVersion = 1\n\n[[surfaces]]\nmodule = "fuzzyroutines"\n'
        'source = "fuzzyroutines/__init__.py"\nmode = "exports"\n\n'
        '[[exclusions]]\nsymbol = "fuzzyroutines.Gone"\nreason = "short"\n',
    )
    _Write(tmpPath / "docs" / "site" / "content" / "en" / "index.md", "# API\n")

    violations = ValidateCoverage(projectRoot=tmpPath)

    assert any("requires an actionable reason" in value for value in violations)


def test_SourceLinksReportExactMissingFileAndAnchor(tmpPath):
    """Report the authoring file and line for broken local links."""

    sourcePath = tmpPath / "guide.md"
    targetPath = tmpPath / "target.md"
    _Write(
        sourcePath,
        "# Guide\n\n[missing](absent.md)\n[anchor](target.md#absent)\n",
    )
    _Write(targetPath, "# Present\n")

    violations = ValidateSourceLinks(
        projectRoot=tmpPath,
        markdownPaths=(sourcePath, targetPath),
    )

    assert violations == (
        "guide.md:3: missing local link target: absent.md",
        "guide.md:4: missing Markdown anchor 'absent' in target.md",
    )


def test_ComposedLocaleLinksAreCheckedWithinTheWholeDeployment(tmpPath):
    """Validate cross-language routes without silently treating them as external URLs."""

    english = tmpPath / "site/api/latest/en"
    russian = tmpPath / "site/api/latest/ru"
    english.mkdir(parents=True)
    russian.mkdir(parents=True)
    (english / "index.html").write_text('<a href="/FuzzyRoutines/api/latest/ru/#same">Russian</a>', encoding="utf-8")
    target = russian / "index.html"
    target.write_text('<h1 id="same">Русский</h1>', encoding="utf-8")
    assert not ValidateRenderedLinks(tmpPath / "site", projectRoot=tmpPath, deploymentPath="/FuzzyRoutines")
    target.unlink()
    assert any("missing rendered target" in value for value in ValidateRenderedLinks(tmpPath / "site", projectRoot=tmpPath, deploymentPath="/FuzzyRoutines"))


def test_RenderedLinksValidateExactGeneratedFragments(tmpPath):
    """Validate links against renderer-produced IDs rather than assumptions."""

    siteRoot = tmpPath / "site"
    referenceRoot = tmpPath / "source"
    _Write(
        siteRoot / "index.html",
        '<a href="api/#present">ok</a><a href="api/#missing">bad</a>',
    )
    _Write(siteRoot / "api" / "index.html", '<h2 id="present">Present</h2>')
    _Write(referenceRoot / "index.md", "# Home\n")
    _Write(referenceRoot / "api.md", "# API\n")

    violations = ValidateRenderedLinks(
        siteRoot=siteRoot,
        referenceRoot=referenceRoot,
        projectRoot=tmpPath,
    )

    assert violations == (
        "source/index.md: missing rendered anchor 'missing': api/#missing",
    )
