# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Documentation and shell-boundary contracts for non-library Python code."""

import ast
import os
import subprocess
import sys
from pathlib import Path

PROJECTROOT = Path(__file__).resolve().parents[1]
DOCUMENTATIONPATH = PROJECTROOT / "docs" / "executable-tests-tools-and-examples.md"
EXECUTABLETOOLS = (
    "benchmark_fuzzyset_centroid",
    "benchmark_legacy_baseline",
    "benchmark_membership_operators",
    "benchmark_scale_lookup",
    "check_license_headers",
    "evaluate_api_documentation",
    "pr_merge_links",
    "report_universal_scale_coverage",
    "test_runner",
    "verify_installed_executables",
)


def test_NonLibraryModulesDeclareTheirEvidenceFamily():
    modulePaths = tuple(
        path
        for sourceRoot in ("tests", "tools", "examples")
        for path in (PROJECTROOT / sourceRoot).rglob("*.py")
    )

    for modulePath in modulePaths:
        module = ast.parse(modulePath.read_text(encoding="utf-8"))
        assert ast.get_docstring(module), f"{modulePath.relative_to(PROJECTROOT)} needs a module docstring"


def test_ExecutableToolCallablesDocumentTheirBoundary():
    for modulePath in (PROJECTROOT / "tools").glob("*.py"):
        module = ast.parse(modulePath.read_text(encoding="utf-8"))

        for node in ast.walk(module):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                assert ast.get_docstring(node), (
                    f"{modulePath.relative_to(PROJECTROOT)}:{node.lineno} "
                    f"needs a callable contract for {node.name}"
                )


def test_ExecutableToolsExposeUsefulHelp(tmp_path):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECTROOT)
    initialEntries = tuple(tmp_path.iterdir())

    for toolName in EXECUTABLETOOLS:
        result = subprocess.run(
            [sys.executable, "-m", f"tools.{toolName}", "--help"],
            cwd=tmp_path,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, f"{toolName} --help failed:\n{result.stderr}"
        assert "usage:" in result.stdout.lower(), f"{toolName} has no argparse usage output"
        assert tuple(tmp_path.iterdir()) == initialEntries, f"{toolName} --help created an artifact"


def test_ExecutableDocumentationTablesAreSourceAligned():
    lines = DOCUMENTATIONPATH.read_text(encoding="utf-8").splitlines()
    table = []

    def AssertAligned(rows):
        widths = [[len(cell) for cell in row.strip("|").split("|")] for row in rows]
        columnCount = len(widths[0])
        assert all(len(row) == columnCount for row in widths)

        for columnIndex in range(columnCount):
            assert len({row[columnIndex] for row in widths}) == 1, (
                f"Markdown table column {columnIndex + 1} is not padded to one source width"
            )

    for line in [*lines, ""]:
        if line.startswith("|") and line.endswith("|"):
            table.append(line)

        elif table:
            AssertAligned(table)
            table = []


def test_ExecutableGuideDocumentsShellAndArtifactContracts():
    documentation = DOCUMENTATIONPATH.read_text(encoding="utf-8")

    for requiredConcept in (
        "--help",
        "--output",
        "exit",
        "stdout",
        "stderr",
        "artifact",
        "cleanup",
        "clean-install",
        "PYTHONPATH",
    ):
        assert requiredConcept in documentation
