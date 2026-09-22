# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Executable contracts for the repository-specific sparse Python layout."""

import io
import re
import subprocess
import tokenize
from pathlib import Path

PROJECTROOT = Path(__file__).parents[1]
SPACEDHEADERPATTERN = re.compile(
    r'^\s*(?:elif\b|else:|except\b|finally:|if __name__ == ["\']__main__["\']:)'
)
COMPACTHEADERPATTERN = re.compile(
    r"^\s*(?:class\s|def\s|try:|if\s.+:|elif\s.+:|else:|except.*:|finally:|"
    r"for\s.+:|while\s.+:|with\s.+:|match\s.+:|case\s.+:)\s*$"
)


def _TrackedPythonPaths():
    """Return tracked Python sources in deterministic repository order."""

    output = subprocess.check_output(
        ["git", "ls-files", "-z", "*.py"],
        cwd=PROJECTROOT,
    ).decode("utf-8")

    return tuple(
        PROJECTROOT / relativePath
        for relativePath in output.split("\0")
        if relativePath
    )


def _StatementHeaderLines(sourceText):
    """Return physical lines that begin with an executable name token."""

    headerLines = set()
    tokens = tokenize.generate_tokens(io.StringIO(sourceText).readline)

    for token in tokens:
        if token.type != tokenize.NAME:
            continue

        linePrefix = token.line[: token.start[1]]

        if not linePrefix.strip():
            headerLines.add(token.start[0])

    return frozenset(headerLines)


def test_ClauseTransitionsHaveRequiredLeadingBlankLine():
    violations = []

    for path in _TrackedPythonPaths():
        sourceText = path.read_text(encoding="utf-8")
        lines = sourceText.splitlines()
        headerLines = _StatementHeaderLines(sourceText)

        for lineIndex, line in enumerate(lines):
            if lineIndex + 1 not in headerLines:
                continue

            if not SPACEDHEADERPATTERN.match(line):
                continue

            if lineIndex == 0 or lines[lineIndex - 1].strip():
                relativePath = path.relative_to(PROJECTROOT).as_posix()
                violations.append(f"{relativePath}:{lineIndex + 1}")

    assert not violations, (
        "One blank line is required before elif, else, except, finally, and "
        f"the main guard: {', '.join(violations)}"
    )


def test_BlockHeadersHaveNoImmediateBlankLine():
    violations = []

    for path in _TrackedPythonPaths():
        sourceText = path.read_text(encoding="utf-8")
        lines = sourceText.splitlines()
        headerLines = _StatementHeaderLines(sourceText)

        for lineIndex, line in enumerate(lines[:-1]):
            if lineIndex + 1 not in headerLines:
                continue

            if not COMPACTHEADERPATTERN.match(line):
                continue

            if not lines[lineIndex + 1].strip():
                relativePath = path.relative_to(PROJECTROOT).as_posix()
                violations.append(f"{relativePath}:{lineIndex + 1}")

    assert not violations, (
        "A block header must be followed immediately by its first statement: "
        f"{', '.join(violations)}"
    )
