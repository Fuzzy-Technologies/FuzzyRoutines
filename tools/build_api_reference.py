# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Build the canonical API reference from an isolated wheel installation.

The command owns only `_build/api-reference`, installs documentation tooling
outside runtime package metadata, and blocks project-package imports while
Griffe discovers the installed sources.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECTROOT = Path(__file__).parents[1]
DEFAULTBUILDROOT = PROJECTROOT / "_build" / "api-reference"
CONFIGPATH = PROJECTROOT / "docs" / "site" / "mkdocs.yml"
REQUIREMENTSPATH = PROJECTROOT / "docs" / "requirements-api.txt"
DOCUMENTATIONPACKAGES = (
    "griffelib",
    "mkdocs",
    "mkdocs-material",
    "mkdocstrings",
    "mkdocstrings-python",
)


def ParseArguments(arguments=None):
    """Parse the clean-build and local-preview command contract."""

    parser = argparse.ArgumentParser(
        description="Build the canonical API reference from an installed wheel.",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve the verified site after the clean strict build.",
    )
    parser.add_argument(
        "--dev-addr",
        dest="devAddress",
        default="127.0.0.1:8000",
        help="Local address used with --serve; defaults to 127.0.0.1:8000.",
    )
    return parser.parse_args(arguments)


def RunCommand(command, *, environment=None, cwd=PROJECTROOT, captureOutput=False):
    """Run a command and fail with its complete diagnostic output."""

    result = subprocess.run(
        [str(part) for part in command],
        cwd=cwd,
        env=environment,
        capture_output=captureOutput,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        diagnostic = ""
        if captureOutput:
            diagnostic = f"\n{result.stdout}{result.stderr}"
        raise RuntimeError(
            f"command failed with exit code {result.returncode}: "
            f"{' '.join(str(part) for part in command)}{diagnostic}"
        )

    return result.stdout.strip() if captureOutput else ""


def RecreateBuildRoot(buildRoot):
    """Replace only the canonical disposable API-reference build directory."""

    resolvedRoot = buildRoot.resolve()
    expectedRoot = DEFAULTBUILDROOT.resolve()
    if resolvedRoot != expectedRoot:
        raise ValueError(f"refusing to replace non-canonical build root: {resolvedRoot}")

    if resolvedRoot.exists():
        shutil.rmtree(resolvedRoot)

    resolvedRoot.mkdir(parents=True)


def WriteImportGuard(guardRoot):
    """Install a generated Python startup guard against project imports."""

    guardRoot.mkdir()
    guardPath = guardRoot / "sitecustomize.py"
    guardPath.write_text(
        """\
import sys


class FuzzyRoutinesImportGuard:
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "fuzzyroutines" or fullname.startswith("fuzzyroutines."):
            raise RuntimeError(
                "API discovery attempted to import the fuzzyroutines package"
            )
        return None


sys.meta_path.insert(0, FuzzyRoutinesImportGuard())
""",
        encoding="utf-8",
    )


def GetEnvironmentPython(environmentRoot):
    """Return the platform-specific interpreter inside a virtual environment."""

    scriptsDirectory = "Scripts" if os.name == "nt" else "bin"
    executableName = "python.exe" if os.name == "nt" else "python"
    return environmentRoot / scriptsDirectory / executableName


def GetInstalledPackagesPath(environmentPython):
    """Return the installed environment path that contains `fuzzyroutines`."""

    code = "import sysconfig; print(sysconfig.get_paths()['purelib'])"
    return Path(
        RunCommand(
            [environmentPython, "-c", code],
            cwd=PROJECTROOT.parent,
            captureOutput=True,
        )
    ).resolve()


def GetPackageVersions(environmentPython):
    """Return exact installed documentation-tool versions."""

    packageLiteral = repr(DOCUMENTATIONPACKAGES)
    code = (
        "import importlib.metadata as m, json; "
        f"print(json.dumps({{p: m.version(p) for p in {packageLiteral}}}, sort_keys=True))"
    )
    output = RunCommand(
        [environmentPython, "-c", code],
        cwd=PROJECTROOT.parent,
        captureOutput=True,
    )
    return json.loads(output)


def VerifySite(siteRoot):
    """Verify navigation, search, inventory, formulas, and representative API."""

    requiredPaths = (
        siteRoot / "index.html",
        siteRoot / "api" / "modern" / "fuzzysets" / "index.html",
        siteRoot / "api" / "legacy" / "index.html",
        siteRoot / "objects.inv",
        siteRoot / "search" / "search_index.json",
    )
    for requiredPath in requiredPaths:
        if not requiredPath.is_file():
            raise FileNotFoundError(f"missing generated reference artifact: {requiredPath}")

    htmlText = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(siteRoot.rglob("*.html"))
    )
    expectedFragments = (
        'id="fuzzyroutines.fuzzysets.ScalarFuzzySet"',
        'id="fuzzyroutines.FuzzyRoutines.MFunction"',
        "mathjax@3.2.2",
        "arithmatex",
        '<span class="doc-section-title">Examples:</span>',
        "Source code in",
    )
    for fragment in expectedFragments:
        if fragment not in htmlText:
            raise AssertionError(f"generated reference is missing required content: {fragment}")


def WriteEvidence(buildRoot, wheelPath, packageVersions):
    """Write machine-readable local evidence beside disposable output."""

    wheelDigest = hashlib.sha256(wheelPath.read_bytes()).hexdigest()
    sourceRevision = RunCommand(
        ["git", "rev-parse", "HEAD"],
        captureOutput=True,
    )
    evidence = {
        "buildCommand": "python tools/build_api_reference.py",
        "discovery": "static-installed-wheel",
        "documentationPackages": packageVersions,
        "generatedHtmlTracked": False,
        "sourceRevision": sourceRevision,
        "wheel": {
            "name": wheelPath.name,
            "sha256": wheelDigest,
        },
    }
    evidencePath = buildRoot / "build-evidence.json"
    evidencePath.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def BuildReference():
    """Create an isolated environment and build the strict installed API site."""

    buildRoot = DEFAULTBUILDROOT
    environmentRoot = buildRoot / "environment"
    artifactRoot = buildRoot / "artifacts"
    siteRoot = buildRoot / "site"
    guardRoot = buildRoot / "import-guard"

    RecreateBuildRoot(buildRoot)
    artifactRoot.mkdir()
    WriteImportGuard(guardRoot)

    RunCommand([sys.executable, "-m", "venv", environmentRoot])
    environmentPython = GetEnvironmentPython(environmentRoot)
    RunCommand(
        [
            environmentPython,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--requirement",
            REQUIREMENTSPATH,
        ]
    )
    RunCommand(
        [
            environmentPython,
            "-m",
            "build",
            "--no-isolation",
            "--wheel",
            "--outdir",
            artifactRoot,
            PROJECTROOT,
        ]
    )

    wheelPaths = list(artifactRoot.glob("*.whl"))
    if len(wheelPaths) != 1:
        raise AssertionError(f"expected one wheel, found {len(wheelPaths)}")
    wheelPath = wheelPaths[0]
    RunCommand(
        [
            environmentPython,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-deps",
            "--force-reinstall",
            wheelPath,
        ],
        cwd=PROJECTROOT.parent,
    )

    installedPackagesPath = GetInstalledPackagesPath(environmentPython)
    installedPackagePath = installedPackagesPath / "fuzzyroutines"
    if not installedPackagePath.is_dir():
        raise FileNotFoundError(f"installed package is missing: {installedPackagePath}")

    environment = os.environ.copy()
    environment["FUZZYROUTINES_INSTALLED_PACKAGES"] = str(installedPackagesPath)
    environment["PYTHONPATH"] = str(guardRoot)
    RunCommand(
        [
            environmentPython,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            CONFIGPATH,
            "--site-dir",
            siteRoot,
        ],
        environment=environment,
        cwd=buildRoot,
    )

    VerifySite(siteRoot)
    packageVersions = GetPackageVersions(environmentPython)
    WriteEvidence(buildRoot, wheelPath, packageVersions)
    return environmentPython, environment, siteRoot


def Main(arguments=None):
    """Build the reference and optionally start its installed-package preview."""

    options = ParseArguments(arguments)
    environmentPython, environment, siteRoot = BuildReference()
    print(f"API reference build: PASS ({siteRoot})")

    if options.serve:
        RunCommand(
            [
                environmentPython,
                "-m",
                "mkdocs",
                "serve",
                "--strict",
                "--config-file",
                CONFIGPATH,
                "--dev-addr",
                options.devAddress,
            ],
            environment=environment,
            cwd=DEFAULTBUILDROOT,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
