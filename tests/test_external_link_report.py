# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Tests for deterministic, network-independent external-link reporting."""

from __future__ import annotations

import json
import threading

from tools import report_external_links as reportExternalLinks
from tools.report_external_links import LinkReference, ProbeResult


def test_ScanDocumentsReportsActionableSortedLocations(tmpPath):
    """Return source locations and URLs in deterministic document order."""

    secondPath = tmpPath / "z.md"
    secondPath.write_text("See <https://example.com/z>.\n", encoding="utf-8")
    firstPath = tmpPath / "a.md"
    firstPath.write_text(
        "heading\n[documentation](https://example.com/a).\n"
        "Malformed: https://\n",
        encoding="utf-8",
    )

    references = reportExternalLinks.ScanDocuments(
        (secondPath, firstPath), projectRoot=tmpPath
    )

    assert references == (
        LinkReference("a.md", 2, "https://example.com/a"),
        LinkReference("a.md", 3, "https://"),
        LinkReference("z.md", 1, "https://example.com/z"),
    )


def test_ScanDocumentsIgnoresIntentionalLoopbackExamples(tmpPath):
    """Exclude intentional localhost and loopback URLs from external health checks."""

    documentPath = tmpPath / "offline.md"
    documentPath.write_text(
        "http://127.0.0.1:9\nhttp://localhost:8000\nhttps://example.com\n",
        encoding="utf-8",
    )

    references = reportExternalLinks.ScanDocuments(
        (documentPath,), projectRoot=tmpPath
    )

    assert references == (
        LinkReference("offline.md", 3, "https://example.com"),
    )


def test_BuildReportIsDeterministicAndProbesEachUrlOnce():
    """Probe each distinct URL once and preserve deterministic report ordering."""

    references = (
        LinkReference("z.md", 8, "https://example.com/shared"),
        LinkReference("a.md", 2, "https://example.com/failure"),
        LinkReference("a.md", 1, "https://example.com/shared"),
    )
    calls = []

    def FakeProbe(url, timeoutSeconds):
        """Return deterministic link-probe evidence without making network requests."""

        calls.append((url, timeoutSeconds))
        if url.endswith("failure"):
            return ProbeResult(False, 503, "HTTP 503: unavailable")
        return ProbeResult(True, 204, None)

    report = reportExternalLinks.BuildReport(
        references, timeoutSeconds=0.25, maxWorkers=2, probe=FakeProbe
    )

    assert sorted(calls) == [
        ("https://example.com/failure", 0.25),
        ("https://example.com/shared", 0.25),
    ]
    assert report == {
        "links": [
            {
                "path": "a.md",
                "line": 1,
                "url": "https://example.com/shared",
                "ok": True,
                "status": 204,
                "error": None,
            },
            {
                "path": "a.md",
                "line": 2,
                "url": "https://example.com/failure",
                "ok": False,
                "status": 503,
                "error": "HTTP 503: unavailable",
            },
            {
                "path": "z.md",
                "line": 8,
                "url": "https://example.com/shared",
                "ok": True,
                "status": 204,
                "error": None,
            },
        ],
        "summary": {"failed": 1, "references": 3, "uniqueUrls": 2},
    }
    assert json.dumps(report, sort_keys=True) == json.dumps(report, sort_keys=True)


def test_BuildReportRecordsMalformedUrlWithoutProbingIt():
    """Report malformed URLs without passing them to the network probe."""

    def UnexpectedProbe(url, timeoutSeconds):
        """Fail if a malformed URL incorrectly reaches the network probe."""

        raise AssertionError(f"unexpected network probe: {url}, {timeoutSeconds}")

    report = reportExternalLinks.BuildReport(
        (LinkReference("README.md", 7, "https://"),), probe=UnexpectedProbe
    )

    assert report["links"] == [
        {
            "path": "README.md",
            "line": 7,
            "url": "https://",
            "ok": False,
            "status": None,
            "error": "malformed URL: missing host",
        }
    ]
    assert report["summary"]["failed"] == 1


def test_BuildReportRunsProbesConcurrently():
    """Demonstrate overlapping independent probes with a synchronization barrier."""

    barrier = threading.Barrier(2, timeout=1)

    def SynchronizedProbe(url, timeoutSeconds):
        """Coordinate concurrent fixture probes and expose serialized execution."""

        barrier.wait()
        return ProbeResult(True, 200, None)

    report = reportExternalLinks.BuildReport(
        (
            LinkReference("README.md", 1, "https://example.com/one"),
            LinkReference("README.md", 2, "https://example.com/two"),
        ),
        maxWorkers=2,
        probe=SynchronizedProbe,
    )

    assert report["summary"]["failed"] == 0


def test_MainWritesReportAndReturnsNonzeroForFailedProbe(
    tmpPath, monkeypatch
):
    """Verify that main writes report and returns nonzero for failed probe."""

    outputPath = tmpPath / "report.json"
    monkeypatch.setattr(
        reportExternalLinks,
        "TrackedDocumentationPaths",
        lambda: (tmpPath / "README.md",),
    )
    (tmpPath / "README.md").write_text(
        "https://example.invalid\n", encoding="utf-8"
    )
    monkeypatch.setattr(reportExternalLinks, "PROJECTROOT", tmpPath)
    monkeypatch.setattr(
        reportExternalLinks,
        "ProbeUrl",
        lambda url, timeoutSeconds: ProbeResult(False, None, "unreachable: timeout"),
    )

    exitCode = reportExternalLinks.Main(["--output", str(outputPath)])

    assert exitCode == 1
    report = json.loads(outputPath.read_text(encoding="utf-8"))
    assert report["links"][0]["path"] == "README.md"
    assert report["links"][0]["line"] == 1
    assert report["links"][0]["error"] == "unreachable: timeout"


def test_MainRejectsInvalidProbeLimits(capsys):
    """Verify that main rejects invalid probe limits."""

    try:
        reportExternalLinks.Main(["--timeout", "0"])

    except SystemExit as error:
        assert error.code == 2

    else:
        raise AssertionError("invalid timeout should terminate argument parsing")

    assert "--timeout must be greater than zero" in capsys.readouterr().err


def test_ProbeUrlRecordsUnreachableError(monkeypatch):
    """Verify that probe url records unreachable error."""

    def FailingUrlopen(request, timeout):
        """Raise a deterministic connection error in place of real URL access."""

        raise TimeoutError("timed out")

    monkeypatch.setattr(reportExternalLinks, "urlopen", FailingUrlopen)

    result = reportExternalLinks.ProbeUrl("https://example.com", 0.01)

    assert result == ProbeResult(False, None, "unreachable: timed out")
