# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Source-layout contracts for human-readable Markdown tables."""

from pathlib import Path

REPOSITORYROOT = Path(__file__).resolve().parents[1]


def _MarkdownFiles():
    """Return canonical prose files whose tables must remain source-aligned."""

    return (REPOSITORYROOT / "README.md", *sorted((REPOSITORYROOT / "docs").rglob("*.md")))


def _TableBlocks(markdownText):
    """Yield consecutive top-level pipe-table rows outside fenced code."""

    inFence = False
    tableRows = []

    for lineNumber, line in enumerate(markdownText.splitlines(), start=1):
        strippedLine = line.lstrip()

        if strippedLine.startswith(("```", "~~~")):
            inFence = not inFence

        isTableRow = not inFence and line.startswith("|") and line.endswith("|")

        if isTableRow:
            tableRows.append((lineNumber, line))

        elif tableRows:
            if len(tableRows) >= 2:
                yield tableRows

            tableRows = []

    if len(tableRows) >= 2:
        yield tableRows


def _DelimiterPositions(row):
    """Return source columns occupied by unescaped table delimiters."""

    return tuple(
        characterIndex
        for characterIndex, character in enumerate(row)
        if character == "|" and (characterIndex == 0 or row[characterIndex - 1] != "\\")
    )


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
