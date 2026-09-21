# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Contract and end-to-end tests for the unified process test runner."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tools.test_runner import (
    AggregateResults,
    BuildPhases,
    ExecutionPhase,
    ParseJunitReport,
    PhaseResult,
    ResolveJobs,
)

PROJECTROOT = Path(__file__).resolve().parents[1]


def RunSyntheticSuite(tmpPath: Path, testFiles: dict[str, str], *arguments: str) -> subprocess.CompletedProcess[str]:
    for relativePath, content in testFiles.items():
        testPath = tmpPath / relativePath
        testPath.parent.mkdir(parents=True, exist_ok=True)
        testPath.write_text(content, encoding="utf-8")

    command = [sys.executable, "-m", "tools.test_runner", *arguments, str(tmpPath)]
    return subprocess.run(
        command,
        cwd=PROJECTROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def ParseSummary(completedProcess: subprocess.CompletedProcess[str]) -> dict[str, int | float]:
    summaryLines = [line for line in completedProcess.stdout.splitlines() if line.startswith("TEST_SUMMARY ")]
    assert len(summaryLines) == 1, (
        "The runner must emit exactly one machine-readable TEST_SUMMARY line.\n"
        + completedProcess.stdout
        + completedProcess.stderr
    )
    return json.loads(summaryLines[0].removeprefix("TEST_SUMMARY "))


@pytest.mark.parametrize(
    ("cpuCount", "expectedWorkers"),
    ((None, 1), (1, 1), (4, 4), (64, 12)),
)
def test_AutoWorkersRespectCpuAvailabilityAndConfiguredCap(cpuCount, expectedWorkers, monkeypatch):
    monkeypatch.setattr(os, "cpu_count", lambda: cpuCount)
    assert ResolveJobs("auto", maxWorkers=12) == expectedWorkers


@pytest.mark.parametrize("requestedJobs", ("0", "-1", "thirteen", "13"))
def test_InvalidWorkerRequestsFailClosed(requestedJobs):
    with pytest.raises(ValueError, match="positive integer|configured maximum"):
        ResolveJobs(requestedJobs, maxWorkers=12, cpuCount=64)


def test_DefaultPhasesSeparateParallelSafeAndSerialTests():
    assert BuildPhases(serialOnly=False, workers=4) == (
        ExecutionPhase("parallel", "not serial", 4),
        ExecutionPhase("serial", "serial", 0),
    )


def test_SerialModeUsesOneSequentialPhase():
    phases = BuildPhases(serialOnly=True, workers=4)
    assert len(phases) == 1
    assert phases[0].name == "serial-all"
    assert phases[0].workers == 0
    assert phases[0].markerExpression is None


def test_JunitAggregationSeparatesFailuresTimeoutsAndSkips(tmp_path):
    reportPath = tmp_path / "report.xml"
    reportPath.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite>
  <testcase name="pass" />
  <testcase name="skip"><skipped message="not applicable" /></testcase>
  <testcase name="fail"><failure message="assertion failed" /></testcase>
  <testcase name="slow"><failure message="Timeout (&gt;0.1s) from pytest-timeout." /></testcase>
</testsuite></testsuites>
""",
        encoding="utf-8",
    )
    assert ParseJunitReport(reportPath) == {
        "total": 4,
        "passed": 1,
        "failed": 1,
        "skipped": 1,
        "timeout": 1,
        "process_errors": 0,
    }


def test_AggregateSchemaIsIndependentOfPhaseCompletionOrder():
    first = PhaseResult("parallel", 0, 3, 2, 0, 1, 0, 0.2, 0)
    second = PhaseResult("serial", 1, 2, 0, 1, 0, 1, 0.1, 0)
    expected = {
        "duration": 0.5,
        "failed": 1,
        "passed": 2,
        "process_errors": 0,
        "skipped": 1,
        "timeout": 1,
        "total": 5,
    }
    assert AggregateResults((first, second), 0.5) == expected
    assert AggregateResults((second, first), 0.5) == expected


def test_ParallelAndSerialPhasesRunInDifferentProcesses(tmp_path):
    evidenceRoot = tmp_path / "evidence"
    evidenceRoot.mkdir()
    moduleTemplate = """
import os
from pathlib import Path
import time

def test_RecordWorker():
    time.sleep(0.2)
    evidenceRoot = Path({evidenceRoot!r})
    (evidenceRoot / ("parallel-" + str(os.getpid()))).write_text("worker", encoding="utf-8")
"""
    serialModule = """
import os
from pathlib import Path
import pytest

@pytest.mark.serial
def test_RecordSerialProcess():
    evidenceRoot = Path({evidenceRoot!r})
    (evidenceRoot / ("serial-" + str(os.getpid()))).write_text("serial", encoding="utf-8")
"""
    completedProcess = RunSyntheticSuite(
        tmp_path,
        {
            "test_worker_a.py": moduleTemplate.format(evidenceRoot=str(evidenceRoot)),
            "test_worker_b.py": moduleTemplate.format(evidenceRoot=str(evidenceRoot)),
            "test_serial.py": serialModule.format(evidenceRoot=str(evidenceRoot)),
        },
        "--jobs",
        "2",
        "--timeout",
        "5",
    )
    summary = ParseSummary(completedProcess)
    parallelEvidence = tuple(evidenceRoot.glob("parallel-*"))
    serialEvidence = tuple(evidenceRoot.glob("serial-*"))

    assert completedProcess.returncode == 0, completedProcess.stdout + completedProcess.stderr
    assert summary["total"] == 3
    assert summary["passed"] == 3
    assert len(parallelEvidence) == 2, "Two loadscope modules must execute in distinct worker processes."
    assert len(serialEvidence) == 1
    assert serialEvidence[0].name.removeprefix("serial-") not in {
        path.name.removeprefix("parallel-") for path in parallelEvidence
    }


def test_TimeoutIsReportedSeparatelyAndFailsTheRun(tmp_path):
    completedProcess = RunSyntheticSuite(
        tmp_path,
        {"test_timeout.py": "import time\n\ndef test_Slow():\n    time.sleep(1)\n"},
        "--jobs",
        "1",
        "--timeout",
        "0.05",
    )
    summary = ParseSummary(completedProcess)

    assert completedProcess.returncode != 0
    assert summary["timeout"] == 1
    assert summary["failed"] == 0


def test_FailFastDoesNotRunTheLaterSerialPhase(tmp_path):
    serialEvidence = tmp_path / "serial-ran"
    completedProcess = RunSyntheticSuite(
        tmp_path,
        {
            "test_failure.py": "def test_Failure():\n    assert False, 'expected synthetic failure'\n",
            "test_serial.py": (
                "from pathlib import Path\nimport pytest\n\n"
                "@pytest.mark.serial\n"
                "def test_Serial():\n"
                f"    Path({str(serialEvidence)!r}).write_text('ran', encoding='utf-8')\n"
            ),
        },
        "--jobs",
        "1",
        "--timeout",
        "5",
        "--fail-fast",
    )
    summary = ParseSummary(completedProcess)

    assert completedProcess.returncode != 0
    assert summary["failed"] == 1
    assert not serialEvidence.exists(), "Fail-fast must not hide the failure by starting a later phase."


def test_CollectionErrorReturnsNonZeroProcessError(tmp_path):
    completedProcess = RunSyntheticSuite(
        tmp_path,
        {"test_broken.py": "def test_Broken(:\n    pass\n"},
        "--jobs",
        "1",
        "--timeout",
        "5",
    )
    summary = ParseSummary(completedProcess)

    assert completedProcess.returncode != 0
    assert summary["process_errors"] >= 1
