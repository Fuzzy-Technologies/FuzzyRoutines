# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Build and inspect the API-documentation architecture candidates."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECTROOT = Path(__file__).parents[1]
EVALUATIONROOT = PROJECTROOT / "docs" / "api-evaluation"
DEFAULTOUTPUTROOT = PROJECTROOT / "_build" / "api-evaluation"
DEFAULTENVIRONMENTROOT = DEFAULTOUTPUTROOT / "environments"
TOOLS = ("pdoc", "mkdocstrings", "sphinx")
PACKAGES = {
    "pdoc": ("pdoc",),
    "mkdocstrings": (
        "mkdocs",
        "mkdocs-material",
        "mkdocstrings",
        "mkdocstrings-python",
        "griffelib",
        "pymdown-extensions",
    ),
    "sphinx": ("sphinx",),
}


def ParseArguments():
    """Parse the deterministic evaluation command-line contract."""

    parser = argparse.ArgumentParser(
        description="Build pdoc, mkdocstrings-python, and Sphinx autodoc spikes.",
    )
    parser.add_argument(
        "tools",
        nargs="*",
        choices=TOOLS,
        default=list(TOOLS),
        help="Candidate tools to evaluate; defaults to all three.",
    )
    parser.add_argument(
        "--environment-root",
        dest="environmentRoot",
        type=Path,
        default=DEFAULTENVIRONMENTROOT,
        help="Directory containing one isolated virtual environment per tool.",
    )
    parser.add_argument(
        "--output-root",
        dest="outputRoot",
        type=Path,
        default=DEFAULTOUTPUTROOT / "sites",
        help="New directory that receives disposable sites, logs, and evidence.",
    )
    parser.add_argument(
        "--python",
        dest="pythonVersion",
        default="3.14",
        help="CPython version used by uv when environments are created.",
    )
    parser.add_argument(
        "--skip-install",
        dest="skipInstall",
        action="store_true",
        help="Reuse already-created environments without changing packages.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Require uv to resolve packages from its local cache only.",
    )
    return parser.parse_args()


def RunCommand(command, environment=None, logPath=None):
    """Run one command and preserve combined output for auditable evidence."""

    startedAt = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=PROJECTROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    elapsedSeconds = time.perf_counter() - startedAt
    combinedOutput = result.stdout + result.stderr

    if logPath is not None:
        logPath.write_text(combinedOutput, encoding="utf-8")

    if result.returncode != 0:
        raise RuntimeError(
            f"command failed with exit code {result.returncode}: {' '.join(command)}\n"
            f"{combinedOutput}"
        )

    return elapsedSeconds, combinedOutput


def PrepareEnvironment(toolName, environmentRoot, pythonVersion, offline, skipInstall):
    """Create or validate one candidate's isolated documentation environment."""

    environmentPath = environmentRoot / toolName
    pythonPath = environmentPath / "bin" / "python"

    if skipInstall:
        if not pythonPath.is_file():
            raise FileNotFoundError(f"missing reusable environment interpreter: {pythonPath}")

        return pythonPath

    if environmentPath.exists():
        raise FileExistsError(
            f"refusing to replace existing environment: {environmentPath}; "
            "use a new --environment-root or --skip-install"
        )

    environmentRoot.mkdir(parents=True, exist_ok=True)
    uvPath = shutil.which("uv")

    if uvPath is None:
        raise RuntimeError("uv is required to create isolated evaluation environments")

    RunCommand([uvPath, "venv", "--python", pythonVersion, str(environmentPath)])

    requirementsPath = GetRequirementsPath(toolName)
    syncCommand = [uvPath, "pip", "sync", "--python", str(pythonPath)]

    if offline:
        syncCommand.append("--offline")

    syncCommand.append(str(requirementsPath))
    RunCommand(syncCommand)
    return pythonPath


def GetRequirementsPath(toolName):
    """Return the pinned docs-only dependency manifest for one candidate."""

    if toolName == "mkdocstrings":
        return PROJECTROOT / "docs" / "requirements-api.txt"

    return EVALUATIONROOT / "requirements" / f"{toolName}.txt"


def GetBuildCommand(toolName, pythonPath, sitePath):
    """Return the strict HTML build command for one candidate."""

    if toolName == "pdoc":
        return [
            str(pythonPath),
            "-m",
            "pdoc",
            "fuzzyroutines.domain",
            "fuzzyroutines.fuzzysets",
            "--docformat",
            "google",
            "--math",
            "--search",
            "--show-source",
            "--output-directory",
            str(sitePath),
        ]

    if toolName == "mkdocstrings":
        return [
            str(pythonPath),
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            str(EVALUATIONROOT / "mkdocs.yml"),
            "--site-dir",
            str(sitePath),
        ]

    return [
        str(pythonPath),
        "-m",
        "sphinx",
        "-W",
        "--keep-going",
        "-b",
        "html",
        str(EVALUATIONROOT / "sphinx"),
        str(sitePath),
    ]


def GetPackageVersions(pythonPath, toolName):
    """Read evaluated package versions from the candidate environment."""

    packageNames = PACKAGES[toolName]
    versionCode = (
        "import importlib.metadata as metadata, json; "
        f"print(json.dumps({{name: metadata.version(name) for name in {packageNames!r}}}, "
        "sort_keys=True))"
    )
    _, versionOutput = RunCommand([str(pythonPath), "-c", versionCode])
    return json.loads(versionOutput)


def ReadHtml(sitePath):
    """Return every generated HTML document as one inspection corpus."""

    htmlPaths = sorted(sitePath.rglob("*.html"))

    if not htmlPaths:
        raise AssertionError(f"no HTML files were generated in {sitePath}")

    return "\n".join(path.read_text(encoding="utf-8") for path in htmlPaths)


def VerifyOutput(toolName, sitePath, buildOutput):
    """Verify observable criteria shared by the three generated sites."""

    htmlText = ReadHtml(sitePath)
    checks = {
        "apiRendered": "ScalarFuzzySet" in htmlText,
        "runtimeImportDetected": "fuzzyroutines.fuzzysets" in buildOutput,
    }

    if toolName == "pdoc":
        checks.update(
            {
                "stableAnchor": 'id="ScalarFuzzySet"' in htmlText,
                "sourceView": "View Source" in htmlText,
                "search": (sitePath / "search.js").is_file(),
                "mathRenderer": "MathJax-script" in htmlText,
                "typeCrossReferences": "domain.html#ContinuousUniverse" in htmlText,
            }
        )

    elif toolName == "mkdocstrings":
        checks.update(
            {
                "stableAnchor": 'id="fuzzyroutines.fuzzysets.ScalarFuzzySet"' in htmlText,
                "sourceView": "Source code in" in htmlText,
                "search": (sitePath / "search" / "search_index.json").is_file(),
                "mathRenderer": "arithmatex" in htmlText and "mathjax@3.2.2" in htmlText,
                "objectInventory": (sitePath / "objects.inv").is_file(),
                "typeCrossReferences": (
                    'href="api/domain/#fuzzyroutines.domain.ContinuousUniverse"' in htmlText
                ),
            }
        )

    else:
        checks.update(
            {
                "stableAnchor": 'id="fuzzyroutines.fuzzysets.ScalarFuzzySet"' in htmlText,
                "sourceView": "_modules/fuzzyroutines/fuzzysets.html" in htmlText,
                "search": (sitePath / "searchindex.js").is_file(),
                "mathRenderer": "mathjax@4" in htmlText,
                "objectInventory": (sitePath / "objects.inv").is_file(),
                "typeCrossReferences": (
                    'href="#fuzzyroutines.domain.ContinuousUniverse"' in htmlText
                ),
            }
        )

    requiredChecks = {
        checkName: passed
        for checkName, passed in checks.items()
        if checkName != "runtimeImportDetected"
    }
    failedChecks = sorted(checkName for checkName, passed in requiredChecks.items() if not passed)

    if failedChecks:
        raise AssertionError(f"{toolName} generated output failed checks: {failedChecks}")

    filePaths = [path for path in sitePath.rglob("*") if path.is_file()]
    byteCount = sum(path.stat().st_size for path in filePaths)
    return checks, len(filePaths), byteCount


def EvaluateTool(toolName, environmentRoot, outputRoot, pythonVersion, offline, skipInstall):
    """Build and inspect one candidate in its isolated environment."""

    pythonPath = PrepareEnvironment(
        toolName,
        environmentRoot,
        pythonVersion,
        offline,
        skipInstall,
    )
    toolOutputPath = outputRoot / toolName

    if toolOutputPath.exists():
        raise FileExistsError(
            f"refusing to replace existing evaluation output: {toolOutputPath}; "
            "use a new --output-root"
        )

    sitePath = toolOutputPath / "site"
    toolOutputPath.mkdir(parents=True)
    buildEnvironment = os.environ.copy()
    buildEnvironment["PYTHONPATH"] = str(PROJECTROOT)
    buildEnvironment["PYTHONPROFILEIMPORTTIME"] = "1"
    buildCommand = GetBuildCommand(toolName, pythonPath, sitePath)
    elapsedSeconds, buildOutput = RunCommand(
        buildCommand,
        environment=buildEnvironment,
        logPath=toolOutputPath / "build.log",
    )
    checks, fileCount, byteCount = VerifyOutput(toolName, sitePath, buildOutput)
    return {
        "tool": toolName,
        "python": subprocess.check_output(
            [str(pythonPath), "--version"],
            text=True,
        ).strip(),
        "packages": GetPackageVersions(pythonPath, toolName),
        "command": buildCommand,
        "elapsedSeconds": round(elapsedSeconds, 6),
        "generatedFiles": fileCount,
        "generatedBytes": byteCount,
        "checks": checks,
    }


def Main():
    """Run requested candidate builds and emit machine-readable evidence."""

    arguments = ParseArguments()
    outputRoot = arguments.outputRoot.resolve()

    if outputRoot.exists():
        raise FileExistsError(
            f"refusing to replace existing output root: {outputRoot}; use a new --output-root"
        )

    outputRoot.mkdir(parents=True)
    evidence = {
        "schemaVersion": 1,
        "module": "fuzzyroutines.fuzzysets",
        "sourceRevision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECTROOT,
            text=True,
        ).strip(),
        "tools": [],
    }

    for toolName in arguments.tools:
        evidence["tools"].append(
            EvaluateTool(
                toolName,
                arguments.environmentRoot.resolve(),
                outputRoot,
                arguments.pythonVersion,
                arguments.offline,
                arguments.skipInstall,
            )
        )

    evidencePath = outputRoot / "evaluation.json"
    evidenceText = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    evidencePath.write_text(evidenceText, encoding="utf-8")
    sys.stdout.write(evidenceText)


if __name__ == "__main__":
    Main()
