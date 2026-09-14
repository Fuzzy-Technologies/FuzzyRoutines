#!/usr/bin/env python3
"""Extract explicitly closing same-repository issue references from PR text."""

from __future__ import annotations

import os
import re
import sys
from typing import Iterable


_CLOSING_CLAUSE = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|implement(?:s|ed)?)\b(?P<tail>[^\n]*)",
    re.IGNORECASE,
)
_ISSUE_REF = re.compile(r"#(?P<number>[1-9][0-9]*)\b")


def extract_issue_numbers(text: str) -> list[int]:
    """Return unique issue numbers explicitly attached to a closing keyword."""

    seen: set[int] = set()
    result: list[int] = []

    for clause in _CLOSING_CLAUSE.finditer(text or ""):
        for match in _ISSUE_REF.finditer(clause.group("tail")):
            number = int(match.group("number"))
            if number not in seen:
                seen.add(number)
                result.append(number)

    return result


def _lines(numbers: Iterable[int]) -> str:
    return "\n".join(str(number) for number in numbers)


def main() -> int:
    body = os.environ.get("PR_BODY", "")
    numbers = extract_issue_numbers(body)
    sys.stdout.write(_lines(numbers))
    if numbers:
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
