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
    "guide_example_coverage",
    "pr_merge_links",
    "report_universal_scale_coverage",
    "test_runner",
    "verify_installed_executables",
)


def test_NonLibraryModulesDeclareTheirEvidenceFamily():
    """Verify that non library modules declare their evidence family."""

    modulePaths = tuple(
        path
        for sourceRoot in ("tests", "tools", "examples")
        for path in (PROJECTROOT / sourceRoot).rglob("*.py")
    )

    for modulePath in modulePaths:
        module = ast.parse(modulePath.read_text(encoding="utf-8"))
        assert ast.get_docstring(module), f"{modulePath.relative_to(PROJECTROOT)} needs a module docstring"


def test_ExecutableToolCallablesDocumentTheirBoundary():
    """Verify that executable tool callables document their boundary."""

    for modulePath in (PROJECTROOT / "tools").glob("*.py"):
        module = ast.parse(modulePath.read_text(encoding="utf-8"))

        for node in ast.walk(module):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                assert ast.get_docstring(node), (
                    f"{modulePath.relative_to(PROJECTROOT)}:{node.lineno} "
                    f"needs a callable contract for {node.name}"
                )


def test_ExecutableToolsExposeUsefulHelp(tmpPath):
    """Verify that executable tools expose useful help."""

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECTROOT)
    initialEntries = tuple(tmpPath.iterdir())

    for toolName in EXECUTABLETOOLS:
        result = subprocess.run(
            [sys.executable, "-m", f"tools.{toolName}", "--help"],
            cwd=tmpPath,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, f"{toolName} --help failed:\n{result.stderr}"
        assert "usage:" in result.stdout.lower(), f"{toolName} has no argparse usage output"
        assert tuple(tmpPath.iterdir()) == initialEntries, f"{toolName} --help created an artifact"


def test_LegacyBenchmarkSupportsModuleAndDirectCheckoutHelp(tmpPath):
    """Verify that legacy benchmark supports module and direct checkout help."""

    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    scriptPath = PROJECTROOT / "tools" / "benchmark_legacy_baseline.py"
    commands = (
        [sys.executable, "-m", "tools.benchmark_legacy_baseline", "--help"],
        [sys.executable, "-I", "-S", str(scriptPath), "--help"],
    )

    for command in commands:
        result = subprocess.run(
            command,
            cwd=PROJECTROOT if "-m" in command else tmpPath,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert "usage:" in result.stdout.lower()


def test_ExecutableGuideDocumentsShellAndArtifactContracts():
    """Verify that executable guide documents shell and artifact contracts."""

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
