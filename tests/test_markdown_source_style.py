# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Source-layout and math-compatibility contracts for authored documentation."""

import ast
import re
import subprocess
from itertools import pairwise
from pathlib import Path

REPOSITORYROOT = Path(__file__).resolve().parents[1]


def _MarkdownFiles():
    """Return canonical prose files whose tables must remain source-aligned."""

    return (REPOSITORYROOT / "README.md", *sorted((REPOSITORYROOT / "docs").rglob("*.md")))


def _FenceOpening(line):
    """Return a CommonMark fence character and length, or `None`."""

    match = re.fullmatch(r" {0,3}(`{3,}|~{3,})(.*)", line)

    if match is None:
        return None

    marker, remainder = match.groups()

    if marker[0] == "`" and "`" in remainder:
        return None

    return marker[0], len(marker)


def _IsFenceClosing(line, fence):
    """Return whether a line closes the active CommonMark fence."""

    fenceCharacter, minimumLength = fence
    match = re.fullmatch(rf" {{0,3}}({re.escape(fenceCharacter)}+)[ \t]*", line)
    return match is not None and len(match.group(1)) >= minimumLength


def _DelimiterPositions(row):
    """Return source columns occupied by delimiters with even slash parity."""

    positions = []

    for characterIndex, character in enumerate(row):
        if character != "|":
            continue

        slashCount = 0
        precedingIndex = characterIndex - 1

        while precedingIndex >= 0 and row[precedingIndex] == "\\":
            slashCount += 1
            precedingIndex -= 1

        if slashCount % 2 == 0:
            positions.append(characterIndex)

    return tuple(positions)


def _IsDelimiterRow(row):
    """Return whether a pipe-wrapped row is a Markdown table delimiter."""

    positions = _DelimiterPositions(row)

    if len(positions) < 3 or positions[0] != 0 or positions[-1] != len(row) - 1:
        return False

    cells = (
        row[leftPosition + 1:rightPosition].strip()
        for leftPosition, rightPosition in pairwise(positions)
    )
    return all(re.fullmatch(r":?-{3,}:?", cell) is not None for cell in cells)


def _CompleteTableBlock(tableRows):
    """Return rows only when the second row is a Markdown delimiter row."""

    if len(tableRows) >= 2 and _IsDelimiterRow(tableRows[1][1]):
        return tuple(tableRows)

    return None


def _TableBlocks(markdownText):
    """Yield top-level pipe tables outside correctly matched fenced code."""

    activeFence = None
    tableRows = []

    for lineNumber, line in enumerate(markdownText.splitlines(), start=1):
        if activeFence is not None:
            if _IsFenceClosing(line, activeFence):
                activeFence = None

            continue

        fenceOpening = _FenceOpening(line)

        if fenceOpening is not None:
            completeTable = _CompleteTableBlock(tableRows)

            if completeTable is not None:
                yield completeTable

            tableRows = []
            activeFence = fenceOpening
            continue

        normalizedLine = line.rstrip()
        isTableRow = normalizedLine.startswith("|") and normalizedLine.endswith("|")

        if isTableRow:
            tableRows.append((lineNumber, normalizedLine))

        elif tableRows:
            completeTable = _CompleteTableBlock(tableRows)

            if completeTable is not None:
                yield completeTable

            tableRows = []

    completeTable = _CompleteTableBlock(tableRows)

    if completeTable is not None:
        yield completeTable


def test_TableBlocksIncludeRowsWithTrailingWhitespace():
    """Keep trailing whitespace from hiding a misaligned table row."""

    markdownText = "| A | B |\n|---|---|\n| longer | x |   "

    assert list(_TableBlocks(markdownText)) == [
        (
            (1, "| A | B |"),
            (2, "|---|---|"),
            (3, "| longer | x |"),
        )
    ]


def test_TableBlocksRequireMarkdownDelimiterRow():
    """Do not classify arbitrary pipe-wrapped prose as a table."""

    markdownText = "| phase one |\n| phase two      |"

    assert list(_TableBlocks(markdownText)) == []


def test_TableBlocksTrackFenceCharacterAndMinimumLength():
    """Ignore pipe rows until the matching fence is genuinely closed."""

    markdownText = """````python
| fake | row |
~~~
| still | fenced |
```
| also | fenced |
````
| Real | Table |
|------|-------|
| yes  | true  |
"""

    assert list(_TableBlocks(markdownText)) == [
        (
            (8, "| Real | Table |"),
            (9, "|------|-------|"),
            (10, "| yes  | true  |"),
        )
    ]


def test_DelimiterPositionsUseOddEvenBackslashEscaping():
    """Treat a pipe as escaped only after an odd backslash run."""

    oddSlashRow = r"| left \| literal | right |"
    evenSlashRow = r"| left \\| right |"
    oddInnerPipe = oddSlashRow.index("|", 1)
    evenInnerPipe = evenSlashRow.index("|", 1)

    assert oddInnerPipe not in _DelimiterPositions(oddSlashRow)
    assert evenInnerPipe in _DelimiterPositions(evenSlashRow)


def test_DelimiterRowRequiresCanonicalMarkdownCells():
    """Recognize only canonical alignment cells in the second table row."""

    assert _IsDelimiterRow("|:---|---:|:---:|")
    assert not _IsDelimiterRow("| text | not a delimiter |")
    assert not _IsDelimiterRow("|--|---|")


def test_MarkdownTableColumnsRemainAlignedInSource():
    """Require every row in a table block to use identical delimiter columns."""

    misalignedTables = []

    for markdownPath in _MarkdownFiles():
        for tableRows in _TableBlocks(markdownPath.read_text(encoding="utf-8")):
            expectedPositions = _DelimiterPositions(tableRows[0][1])

            for lineNumber, row in tableRows[1:]:
                actualPositions = _DelimiterPositions(row)

                if actualPositions != expectedPositions:
                    relativePath = markdownPath.relative_to(REPOSITORYROOT)
                    misalignedTables.append(
                        f"{relativePath}:{lineNumber}: expected delimiters "
                        f"{expectedPositions}, got {actualPositions}"
                    )

    assert not misalignedTables, "Markdown table columns are not source-aligned:\n" + "\n".join(
        misalignedTables
    )


def _MathFragments(markdownText):
    """Return dollar-delimited mathematics outside literal fenced/inline code."""

    activeFence = None
    proseLines = []

    for line in markdownText.splitlines():
        if activeFence is not None:
            if _IsFenceClosing(line, activeFence):
                activeFence = None

            continue

        fenceOpening = _FenceOpening(line)

        if fenceOpening is not None:
            activeFence = fenceOpening
            continue

        proseLines.append(line)

    prose = re.sub(r"(`+)(?!`)(.*?)\1(?!`)", "", "\n".join(proseLines), flags=re.DOTALL)

    return tuple(
        fragment
        for match in re.finditer(r"\$\$(.*?)\$\$|(?<!\\)\$(.*?)(?<!\\)\$", prose, flags=re.DOTALL)
        for fragment in match.groups()
        if fragment is not None
    )


def test_MathFragmentsKeepInlineAndMultilineDisplayExpressions():
    """Inspect every expression, including a complete piecewise formula."""

    prose = "Inline $x^2$ and $$\n\\begin{cases}x, & x>0\\end{cases}\n$$."

    assert _MathFragments(prose) == ("x^2", "\n\\begin{cases}x, & x>0\\end{cases}\n")


def test_MathFragmentsIgnoreLiteralCodeAndEscapedCurrency():
    """Permit explanations of blocked macros without treating code as math."""

    prose = r"""Literal `$\operatorname{example}$` and \$5.
````python
"$\operatorname{fenced}$"
```
"$\operatorname{still_fenced}$"
````
~~~text
$\operatorname{tilde}$
~~~
Real $\mathrm{height}(A)$.
"""

    assert _MathFragments(prose) == (r"\mathrm{height}(A)",)


def test_AuthoredMathAvoidsBlockedGitHubMacros():
    """Guard every authored Markdown page and production docstring in CI."""

    markdownPaths = subprocess.check_output(
        ["git", "ls-files", "--", "*.md"], cwd=REPOSITORYROOT, text=True,
    ).splitlines()
    sources = [
        (path, (REPOSITORYROOT / path).read_text(encoding="utf-8"))
        for path in markdownPaths
    ]

    for path in sorted((REPOSITORYROOT / "fuzzyroutines").rglob("*.py")):
        syntax = ast.parse(path.read_text(encoding="utf-8"))

        for node in ast.walk(syntax):
            if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            docstring = ast.get_docstring(node)

            if docstring:
                sources.append((f"{path.relative_to(REPOSITORYROOT)}:{getattr(node, 'lineno', 1)}", docstring))

    violations = [
        source
        for source, text in sources
        if any(re.search(r"\\operatorname\b", fragment) for fragment in _MathFragments(text))
    ]

    assert not violations, "GitHub blocks operatorname; use mathrm in rendered math: " + ", ".join(violations)
