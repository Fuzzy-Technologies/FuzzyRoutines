# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Create a non-blocking JSON health report for documentation links."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import subprocess
import sys
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

PROJECTROOT = Path(__file__).resolve().parents[1]
DEFAULTTIMEOUTSECONDS = 10.0
DEFAULTMAXWORKERS = 8
URLPATTERN = re.compile(r"https?://[^\s<>\"'`]*", re.IGNORECASE)
TRAILINGPUNCTUATION = ".,;:!?"
MATCHINGDELIMITERS = {")": "(", "]": "[", "}": "{"}


@dataclass(frozen=True, order=True)
class LinkReference:
    """One external URL occurrence in a documentation source file."""

    path: str
    line: int
    url: str


@dataclass(frozen=True)
class ProbeResult:
    """The serializable outcome of probing one unique URL."""

    ok: bool
    status: int | None
    error: str | None


def _TrimUrl(candidate: str) -> str:
    """Remove prose punctuation and unmatched Markdown delimiters."""

    candidate = candidate.rstrip(TRAILINGPUNCTUATION)

    while candidate and candidate[-1] in MATCHINGDELIMITERS:
        closingDelimiter = candidate[-1]
        openingDelimiter = MATCHINGDELIMITERS[closingDelimiter]

        if candidate.count(closingDelimiter) < candidate.count(openingDelimiter):
            break

        candidate = candidate[:-1]

    return candidate


def _ValidateUrl(url: str) -> str | None:
    """Return a diagnostic for a malformed HTTP(S) URL, if any."""

    try:
        parsedUrl = urlsplit(url)
        port = parsedUrl.port

    except ValueError as error:
        return f"malformed URL: {error}"

    if parsedUrl.scheme.lower() not in {"http", "https"}:
        return "malformed URL: expected an HTTP(S) scheme"

    if not parsedUrl.hostname:
        return "malformed URL: missing host"

    if port is not None and not 1 <= port <= 65535:
        return "malformed URL: port is outside 1-65535"

    return None


def _IsExternalUrl(url: str) -> bool:
    """Return whether a URL targets a non-loopback network host."""

    try:
        hostName = urlsplit(url).hostname

        if hostName is None:
            return True

        if hostName.lower() == "localhost":
            return False

        return not ipaddress.ip_address(hostName).is_loopback

    except ValueError:
        return True


def TrackedDocumentationPaths(projectRoot: Path = PROJECTROOT) -> tuple[Path, ...]:
    """Return tracked Markdown and reStructuredText documentation sources."""

    completedProcess = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.md", "docs/*.rst", "docs/**/*.rst"],
        cwd=projectRoot,
        capture_output=True,
        check=True,
    )
    relativePaths = completedProcess.stdout.decode("utf-8").split("\0")

    return tuple(
        projectRoot / relativePath
        for relativePath in sorted(relativePaths)
        if relativePath
    )


def ScanDocuments(
    paths: Iterable[Path], projectRoot: Path = PROJECTROOT
) -> tuple[LinkReference, ...]:
    """Extract external links with deterministic source locations."""

    references = []

    for path in sorted(paths):
        relativePath = path.relative_to(projectRoot).as_posix()

        for lineNumber, lineText in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for match in URLPATTERN.finditer(lineText):
                url = _TrimUrl(match.group())

                if _IsExternalUrl(url):
                    references.append(LinkReference(relativePath, lineNumber, url))

    return tuple(sorted(references))


def ProbeUrl(url: str, timeoutSeconds: float) -> ProbeResult:
    """Probe one URL without downloading its response body."""

    malformedDiagnostic = _ValidateUrl(url)

    if malformedDiagnostic:
        return ProbeResult(False, None, malformedDiagnostic)

    requestHeaders = {"User-Agent": "FuzzyRoutines-link-report/1.0"}
    try:
        request = Request(url, headers=requestHeaders, method="HEAD")
        try:
            response = urlopen(request, timeout=timeoutSeconds)

        except HTTPError as error:
            if error.code not in {405, 501}:
                raise

            request = Request(url, headers=requestHeaders, method="GET")
            response = urlopen(request, timeout=timeoutSeconds)

        with response:
            status = response.getcode()

        if status is None or not 200 <= status < 400:
            return ProbeResult(False, status, f"unexpected HTTP status {status}")

        return ProbeResult(True, status, None)

    except HTTPError as error:
        return ProbeResult(False, error.code, f"HTTP {error.code}: {error.reason}")

    except (OSError, TimeoutError, URLError) as error:
        reason = getattr(error, "reason", error)

        return ProbeResult(False, None, f"unreachable: {reason}")

    except ValueError as error:
        return ProbeResult(False, None, f"malformed URL: {error}")


def BuildReport(
    references: Iterable[LinkReference],
    *,
    timeoutSeconds: float = DEFAULTTIMEOUTSECONDS,
    maxWorkers: int = DEFAULTMAXWORKERS,
    probe: Callable[[str, float], ProbeResult] | None = None,
) -> dict[str, object]:
    """Probe unique URLs concurrently and return a sorted JSON-ready report."""

    sortedReferences = tuple(sorted(references))
    uniqueUrls = tuple(sorted({reference.url for reference in sortedReferences}))
    malformedResults = {
        url: ProbeResult(False, None, diagnostic)
        for url in uniqueUrls
        if (diagnostic := _ValidateUrl(url)) is not None
    }
    validUrls = tuple(url for url in uniqueUrls if url not in malformedResults)
    activeProbe = probe or ProbeUrl

    with ThreadPoolExecutor(max_workers=maxWorkers) as executor:
        validResults = dict(
            zip(
                validUrls,
                executor.map(
                    lambda url: activeProbe(url, timeoutSeconds),
                    validUrls,
                ),
                strict=True,
            )
        )

    results = malformedResults | validResults
    links = [
        asdict(reference) | asdict(results[reference.url])
        for reference in sortedReferences
    ]
    failedCount = sum(not result.ok for result in results.values())

    return {
        "links": links,
        "summary": {
            "failed": failedCount,
            "references": len(sortedReferences),
            "uniqueUrls": len(uniqueUrls),
        },
    }


def _ArgumentParser() -> argparse.ArgumentParser:
    """Build the command-line parser for external-link reporting."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help="write the JSON report to this path instead of standard output",
    )
    parser.add_argument(
        "--timeout",
        dest="timeoutSeconds",
        type=float,
        default=DEFAULTTIMEOUTSECONDS,
        help=f"per-request timeout in seconds (default: {DEFAULTTIMEOUTSECONDS:g})",
    )
    parser.add_argument(
        "--workers",
        dest="maxWorkers",
        type=int,
        default=DEFAULTMAXWORKERS,
        help=f"maximum concurrent probes (default: {DEFAULTMAXWORKERS})",
    )
    return parser


def Main(arguments: list[str] | None = None) -> int:
    """Write the report and fail when any unique URL did not pass."""

    parser = _ArgumentParser()
    options = parser.parse_args(arguments)

    if options.timeoutSeconds <= 0:
        parser.error("--timeout must be greater than zero")

    if options.maxWorkers <= 0:
        parser.error("--workers must be greater than zero")

    try:
        references = ScanDocuments(TrackedDocumentationPaths(), PROJECTROOT)
        report = BuildReport(
            references,
            timeoutSeconds=options.timeoutSeconds,
            maxWorkers=options.maxWorkers,
        )

    except (OSError, subprocess.CalledProcessError, UnicodeError) as error:
        print(f"external-link report could not scan documentation: {error}", file=sys.stderr)
        return 2

    reportText = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if options.output is None:
        sys.stdout.write(reportText)

    else:
        try:
            options.output.parent.mkdir(parents=True, exist_ok=True)
            options.output.write_text(reportText, encoding="utf-8")

        except OSError as error:
            print(f"could not write external-link report: {error}", file=sys.stderr)
            return 2

    summary = report["summary"]

    assert isinstance(summary, dict)

    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(Main())
