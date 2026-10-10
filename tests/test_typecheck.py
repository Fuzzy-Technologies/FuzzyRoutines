# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Typing scope completeness and isolated-consumer failure boundaries."""

import configparser
import subprocess
from pathlib import Path

import pytest

from tools import typecheck


def test_ModernTypingScopeCoversEveryFocusedModule():
    """Require strict source and consumer coverage as modern modules grow."""

    configuration = configparser.ConfigParser()
    configuration.read(typecheck.PROJECT_ROOT / "mypy.ini")
    targets = {
        target.strip()
        for target in configuration["mypy"]["files"].split(",")
    }
    modernSources = {
        path.relative_to(typecheck.PROJECT_ROOT).as_posix()
        for path in (typecheck.PROJECT_ROOT / "fuzzyroutines").glob("*.py")
        if path.name not in {"Examples.py", "FuzzyRoutines.py"}
    }
    assert modernSources <= targets, "Every focused modern module must remain a strict checker target"
    assert configuration.getboolean("mypy", "strict"), "Consumer negative probes require strict unused-ignore checking"
    assert not configuration.has_option("mypy", "ignore_errors"), "Global suppression would invalidate typing evidence"
    assert not any("_legacy" in target for target in targets), "Historical adapters are outside the modern typing promise"
    assert {
        path.relative_to(typecheck.PROJECT_ROOT).as_posix()
        for path in typecheck.ConsumerPaths()
    } <= targets, "Every static consumer must participate in the source gate"


@pytest.mark.parametrize("boundary", ["checkout", "missing-marker", "missing-consumers"])
def test_InstalledGateRejectsInvalidPackageBoundary(tmpPath, monkeypatch, capsys, boundary):
    """Reject checkout imports, absent markers, and absent consumer probes."""

    projectRoot = tmpPath / "checkout"
    packageRoot = projectRoot / "fuzzyroutines" if boundary == "checkout" else tmpPath / "installed"
    packageRoot.mkdir(parents=True)
    packagePath = packageRoot / "__init__.py"
    packagePath.write_text("", encoding="utf-8")

    if boundary != "missing-marker":
        packageRoot.joinpath("py.typed").write_text("", encoding="utf-8")

    def ProbeInstalled(command, **options):
        """Report the candidate package without starting a checker."""

        assert "-c" in command, "An invalid installed boundary must fail before invoking mypy"

        return subprocess.CompletedProcess(command, 0, stdout=str(packagePath), stderr="")

    monkeypatch.setattr(typecheck.subprocess, "run", ProbeInstalled)
    assert typecheck.CheckInstalled(projectRoot) == 1, "Invalid installation evidence must fail closed"
    expected = {
        "checkout": "resolved the source checkout",
        "missing-marker": "missing py.typed",
        "missing-consumers": "No typing consumer probes",
    }
    assert expected[boundary] in capsys.readouterr().err, "The failed boundary must have an actionable diagnostic"


def test_InstalledGatePreservesImportFailure(tmpPath, monkeypatch, capsys):
    """Keep the installed import failure status and diagnostic visible."""

    def FailedImport(command, **options):
        """Model an unavailable installed package."""

        return subprocess.CompletedProcess(command, 7, stdout="", stderr="package import failed\n")

    monkeypatch.setattr(typecheck.subprocess, "run", FailedImport)
    assert typecheck.CheckInstalled(tmpPath) == 7, "Installed import failure must retain its process status"
    assert "package import failed" in capsys.readouterr().err, "The original import failure must remain visible"


@pytest.mark.parametrize('checkerStatus', [0, 2])
def test_InstalledConsumersAreCopiedAndFailureStatusIsPreserved(tmpPath, monkeypatch, checkerStatus):
    """Isolate complete consumers and clean their temporary files on failure."""

    projectRoot = tmpPath / "checkout"
    fixtureRoot = projectRoot / "tests" / "typing"
    fixtureRoot.mkdir(parents=True)
    fixtureRoot.joinpath("probe.py").write_text(
        '"""Modern installed package typing probe."""\nfrom fuzzyroutines import Triangle\n',
        encoding="utf-8",
    )
    packageRoot = tmpPath / "installed"
    packageRoot.mkdir()
    packageRoot.joinpath("py.typed").write_text("", encoding="utf-8")
    isolatedRoots = []
    monkeypatch.setenv("MYPYPATH", str(projectRoot))
    monkeypatch.setenv("PYTHONPATH", str(projectRoot))

    def RunIsolated(command, **options):
        """Observe the package probe and checker process boundaries."""

        assert "MYPYPATH" not in options["env"], "Mypy environment paths must not expose checkout annotations"
        assert "PYTHONPATH" not in options["env"], "Python environment paths must not expose the checkout package"

        if "-c" in command:
            return subprocess.CompletedProcess(command, 0, stdout=str(packageRoot / "__init__.py"), stderr="")

        isolatedRoot = Path(options["cwd"])
        isolatedRoots.append(isolatedRoot)
        assert not isolatedRoot.is_relative_to(projectRoot), "Consumer discovery must happen outside the checkout"
        assert isolatedRoot.joinpath("probe.py").read_text(encoding="utf-8") == fixtureRoot.joinpath("probe.py").read_text(encoding="utf-8"), (
            "The installed checker must see the complete source consumer probe"
        )
        assert "-I" in command, "Python path environment injection must not expose the source package"
        assert "--no-incremental" in command, "Installed evidence must not reuse source checker cache results"

        return subprocess.CompletedProcess(command, checkerStatus)

    monkeypatch.setattr(typecheck.subprocess, "run", RunIsolated)
    assert typecheck.CheckInstalled(projectRoot) == checkerStatus, "A failed consumer checker must fail the gate"
    assert isolatedRoots and not isolatedRoots[0].exists(), "Temporary probes must be removed after either checker result"


def test_SourceGatePreservesCheckerFailure(monkeypatch):
    """Return source checker failures from the public command entry point."""

    def FailedChecker(command, **options):
        """Model checker failure at the command-line boundary."""

        return subprocess.CompletedProcess(command, 2)

    monkeypatch.setattr(typecheck.subprocess, "run", FailedChecker)
    assert typecheck.Main([]) == 2, "Source checker errors must propagate to the command exit status"
