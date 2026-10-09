# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Extract standalone closing directives from PR Markdown.

The command reads `PR_BODY`, prints one deduplicated issue number per line,
creates no artifacts, and returns zero even when no closing reference exists.
Only standalone directive lines (optionally bulleted) count. Prose, quoted
text, code blocks, and references after a directive's issue list never close
additional tasks.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections.abc import Iterable

_CLOSING_CLAUSE = re.compile(
    r"^[ ]{0,3}(?:[-*+]\s+)?"
    r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|implement(?:s|ed)?)"
    r"\s*:?[ \t]+(?P<references>#[1-9][0-9]*"
    r"(?:[ \t]*(?:,|and|&)[ \t]*#[1-9][0-9]*)*)"
    r"(?=$|[ \t.;])",
    re.IGNORECASE,
)
_ISSUE_REF = re.compile(r"#(?P<number>[1-9][0-9]*)\b")
_CODE_FENCE = re.compile(r"^[ ]{0,3}(?P<fence>`{3,}|~{3,})")


def ExtractIssueNumbers(text: str) -> list[int]:
    """Return unique issue numbers from explicit non-code closing directives."""

    seen: set[int] = set()
    result: list[int] = []
    fenceMarker = ""
    fenceLength = 0

    for line in (text or "").splitlines():
        fenceMatch = _CODE_FENCE.match(line)
        if fenceMatch:
            marker = fenceMatch.group("fence")
            if not fenceMarker:
                fenceMarker, fenceLength = marker[0], len(marker)
            elif (
                marker[0] == fenceMarker
                and len(marker) >= fenceLength
                and not line[fenceMatch.end():].strip()
            ):
                fenceMarker = ""
            continue
        if fenceMarker:
            continue
        clause = _CLOSING_CLAUSE.match(line)
        if clause is None:
            continue
        for match in _ISSUE_REF.finditer(clause.group("references")):
            number = int(match.group("number"))
            if number not in seen:
                seen.add(number)
                result.append(number)

    return result


def _Lines(numbers: Iterable[int]) -> str:
    """Render issue numbers as deterministic newline-separated output."""

    return "\n".join(str(number) for number in numbers)


def ParseArguments(arguments=None):
    """Parse the no-option automation command and provide standard help."""

    parser = argparse.ArgumentParser(description=__doc__)
    return parser.parse_args(arguments)


def Main(arguments=None) -> int:
    """Emit explicitly closing issue numbers from the active PR body."""

    ParseArguments(arguments)
    body = os.environ.get("PR_BODY", "")
    numbers = ExtractIssueNumbers(body)
    sys.stdout.write(_Lines(numbers))
    if numbers:
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
