# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Exercise test-identity parity and complete branch-evidence rejection boundaries."""

import pytest

from tools.release_test_audit import CompareOutcomes, CoverageModules, ReadOutcomes


def Report(tmpPath, name, cases):
    """Write a minimal JUnit fixture with deliberately controlled identities."""

    path = tmpPath / name
    path.write_text("<testsuite>" + cases + "</testsuite>", encoding="utf-8")
    return path


def test_MatchingCountsCannotHideDifferentExecutedTests(tmpPath):
    """Equal totals are insufficient when a different test ran in one mode."""

    serial = Report(tmpPath, "serial.xml", '<testcase classname="suite" name="A"/>')
    parallel = Report(tmpPath, "parallel.xml", '<testcase classname="suite" name="B"/>')

    with pytest.raises(ValueError, match="serial/parallel mismatch"):
        CompareOutcomes([serial], [parallel])


def test_ExecutedTestsCannotBeCountedTwice(tmpPath):
    """A marker-isolation mistake must fail even if both outcomes passed."""

    report = Report(tmpPath, "report.xml", '<testcase classname="suite" name="A"/>')

    with pytest.raises(ValueError, match="duplicate executed test"):
        ReadOutcomes([report, report])


def test_CollectionSkipsDeduplicateButExecutedOutcomesRemainExact(tmpPath):
    """Repeated module collection skips are the only accepted duplicate identities."""

    skip = '<testcase name="optional.py"><skipped/></testcase>'
    passed = '<testcase classname="suite" name="A"/>'
    serial = Report(tmpPath, "serial.xml", skip + passed)
    parallel = Report(tmpPath, "parallel.xml", passed + skip)
    shared = Report(tmpPath, "shared.xml", skip)

    assert CompareOutcomes([serial], [parallel, shared]) == {"total": 2, "passed": 1, "skipped": 1}


def test_IdenticalFailuresDoNotEstablishReleaseAcceptance(tmpPath):
    """Parity cannot turn two equally failing runs into successful evidence."""

    report = Report(tmpPath, "report.xml", '<testcase classname="suite" name="A"><failure/></testcase>')

    with pytest.raises(ValueError, match="failures or process errors"):
        CompareOutcomes([report], [report])


def test_CoverageRequiresBranchesAndEveryLibraryModule(tmpPath):
    """Reject line-only reports and missing modules instead of hiding their gaps."""

    package = tmpPath / "fuzzyroutines"
    package.mkdir()
    (package / "model.py").write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="requires branch coverage"):
        CoverageModules({"meta": {}, "files": {}}, tmpPath)

    with pytest.raises(ValueError, match="lacks required library modules"):
        CoverageModules({"meta": {"branch_coverage": True}, "files": {}}, tmpPath)
