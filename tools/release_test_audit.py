# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Compare real sequential/process test outcomes and inventory module branch coverage.

Consumes existing JUnit XML and coverage.py JSON, executes no tests, and writes
JSON only to --output. Coverage percentages are evidence, not mathematical proof.
Missing modules, non-branch reports, changed outcomes and duplicate test execution
fail with a nonzero exit. Repeated collection skips across runner phases are
deduplicated; executed tests must appear exactly once.
"""

import argparse
import json
from pathlib import Path
from xml.etree import ElementTree

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def ReadOutcomes(reportPaths):
    """Read stable test identities and reject duplicated execution or broken reports."""

    outcomes = {}

    if not reportPaths:
        raise ValueError("no JUnit evidence supplied")

    for reportPath in reportPaths:
        root = ElementTree.parse(reportPath).getroot()

        for case in root.iter("testcase"):
            identity = (case.get("classname", ""), case.get("name", ""))

            if not identity[1]:
                raise ValueError("JUnit test case lacks a stable name")

            outcome = next((kind for kind in ("error", "failure", "skipped") if case.find(kind) is not None), "passed")

            if identity in outcomes:
                if not identity[0] and outcome == outcomes[identity] == "skipped":
                    continue

                raise ValueError(f"duplicate executed test: {identity}")

            outcomes[identity] = outcome

    return outcomes


def CompareOutcomes(serialPaths, parallelPaths):
    """Require identical nonempty test sets and outcomes, not just matching totals."""

    serial = ReadOutcomes(serialPaths)
    parallel = ReadOutcomes(parallelPaths)

    if not serial or serial != parallel:
        missing = sorted(serial.keys() - parallel.keys())
        unexpected = sorted(parallel.keys() - serial.keys())
        changed = sorted(key for key in serial.keys() & parallel.keys() if serial[key] != parallel[key])
        raise ValueError(f"serial/parallel mismatch: missing={missing}, unexpected={unexpected}, changed={changed}")

    if any(outcome in {"error", "failure"} for outcome in serial.values()):
        raise ValueError("test outcomes contain failures or process errors")

    return {"total": len(serial), "passed": sum(outcome == "passed" for outcome in serial.values()), "skipped": sum(outcome == "skipped" for outcome in serial.values())}


def CoverageModules(coverageReport, projectRoot=PROJECT_ROOT):
    """Inventory every library source except the separately installed example CLI."""

    if not coverageReport.get("meta", {}).get("branch_coverage"):
        raise ValueError("release audit requires branch coverage")

    required = {
        path.relative_to(projectRoot).as_posix()
        for path in (projectRoot / "fuzzyroutines").rglob("*.py")
        if path.name != "Examples.py"
    }
    files = coverageReport["files"]
    missing = sorted(required - files.keys())

    if not required or missing:
        raise ValueError(f"coverage lacks required library modules: {missing}")

    modules = {}

    for name in sorted(required):
        data = files[name]
        summary = data["summary"]
        lines = summary["num_statements"]
        branches = summary["num_branches"]
        modules[name] = {
            "linePercent": round(100 * summary["covered_lines"] / lines, 2) if lines else 100.0,
            "branchPercent": round(100 * summary["covered_branches"] / branches, 2) if branches else None,
            "missingLines": data["missing_lines"],
            "missingBranches": data["missing_branches"],
        }

    return modules


def Main(arguments=None):
    """Validate supplied CI evidence and emit per-module audit inputs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--serial", type=Path, required=True)
    parser.add_argument("--parallel-directory", type=Path, dest="parallelDirectory", required=True)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args(arguments)
    report = {
        "schemaVersion": 1,
        "parity": CompareOutcomes([options.serial], sorted(options.parallelDirectory.glob("*.xml"))),
        "modules": CoverageModules(json.loads(options.coverage.read_text(encoding="utf-8"))),
    }
    options.output.parent.mkdir(parents=True, exist_ok=True)
    options.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("TEST_OUTCOME_PARITY " + json.dumps(report["parity"], sort_keys=True))

    for name, data in report["modules"].items():
        print("MODULE_COVERAGE " + json.dumps({"module": name, **data}, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
