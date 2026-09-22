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


def test_CoverageReportsMissingSymbolWithFileAndSymbol(tmp_path):
    """Make a newly undocumented public symbol actionable."""

    _Write(tmp_path / "fuzzyroutines" / "__init__.py", '__all__ = ["Visible"]\n')
    _Write(
        tmp_path / "fuzzyroutines" / "surface.py",
        'def Visible():\n    """Return a visible value."""\n    return 1\n\n'
        'def Missing():\n    """Return a missing value."""\n    return 2\n',
    )
    _Write(
        tmp_path / "docs" / "site" / "api-coverage.toml",
        'schemaVersion = 1\n\n[[surfaces]]\nmodule = "fuzzyroutines.surface"\n'
        'source = "fuzzyroutines/surface.py"\nmode = "authored"\n',
    )
    _Write(
        tmp_path / "docs" / "site" / "content" / "en" / "api.md",
        '# API\n\n::: fuzzyroutines.surface\n    options:\n'
        '      members:\n        - Visible\n',
    )

    violations = ValidateCoverage(projectRoot=tmp_path)

    assert any("fuzzyroutines/surface.py:5" in value for value in violations)
    assert any("fuzzyroutines.surface.Missing" in value for value in violations)


def test_CoverageRejectsUnexplainedAndStaleExclusions(tmp_path):
    """Prevent exclusion records from becoming an unreviewed escape hatch."""

    _Write(tmp_path / "fuzzyroutines" / "__init__.py", '__all__ = []\n')
    _Write(
        tmp_path / "docs" / "site" / "api-coverage.toml",
        'schemaVersion = 1\n\n[[surfaces]]\nmodule = "fuzzyroutines"\n'
        'source = "fuzzyroutines/__init__.py"\nmode = "exports"\n\n'
        '[[exclusions]]\nsymbol = "fuzzyroutines.Gone"\nreason = "short"\n',
    )
    _Write(tmp_path / "docs" / "site" / "content" / "en" / "index.md", "# API\n")

    violations = ValidateCoverage(projectRoot=tmp_path)

    assert any("requires an actionable reason" in value for value in violations)


def test_SourceLinksReportExactMissingFileAndAnchor(tmp_path):
    """Report the authoring file and line for broken local links."""

    sourcePath = tmp_path / "guide.md"
    targetPath = tmp_path / "target.md"
    _Write(
        sourcePath,
        "# Guide\n\n[missing](absent.md)\n[anchor](target.md#absent)\n",
    )
    _Write(targetPath, "# Present\n")

    violations = ValidateSourceLinks(
        projectRoot=tmp_path,
        markdownPaths=(sourcePath, targetPath),
    )

    assert violations == (
        "guide.md:3: missing local link target: absent.md",
        "guide.md:4: missing Markdown anchor 'absent' in target.md",
    )


def test_RenderedLinksValidateExactGeneratedFragments(tmp_path):
    """Validate links against renderer-produced IDs rather than assumptions."""

    siteRoot = tmp_path / "site"
    referenceRoot = tmp_path / "source"
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
        projectRoot=tmp_path,
    )

    assert violations == (
        "source/index.md: missing rendered anchor 'missing': api/#missing",
    )
