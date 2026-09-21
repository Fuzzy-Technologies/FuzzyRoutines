# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Validate repository-wide Apache-2.0 licensing invariants."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tomllib
from pathlib import Path

PROJECTROOT = Path(__file__).resolve().parents[1]
LICENSEIDENTIFIER = "SPDX-License-Identifier: Apache-2.0"
COPYRIGHTIDENTIFIER = "SPDX-FileCopyrightText:"
SPDXPATTERN = re.compile(r"SPDX-License-Identifier:\s*([^\s*<>]+)")
LICENSEDIGEST = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
EXEMPTPATHS = frozenset({"LICENSE", "NOTICE"})
GOVERNEDSUFFIXES = frozenset(
    {
        ".css",
        ".html",
        ".js",
        ".md",
        ".py",
        ".rst",
        ".svg",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
)
GOVERNEDNAMES = frozenset({".gitignore"})


def _TrackedPaths(projectRoot: Path) -> tuple[Path, ...]:
    """Return project-owned tracked paths in deterministic order."""

    completedProcess = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=projectRoot,
        capture_output=True,
        check=True,
    )
    relativePaths = completedProcess.stdout.decode("utf-8").split("\0")
    return tuple(
        projectRoot / relativePath
        for relativePath in relativePaths
        if relativePath
    )


def _IsGoverned(path: Path, projectRoot: Path) -> bool:
    """Return whether a tracked text file requires an SPDX header."""

    relativePath = path.relative_to(projectRoot).as_posix()
    return (
        relativePath not in EXEMPTPATHS
        and (path.suffix in GOVERNEDSUFFIXES or path.name in GOVERNEDNAMES)
    )


def ValidateHeader(path: Path, projectRoot: Path = PROJECTROOT) -> tuple[str, ...]:
    """Return license-header violations for one governed file."""

    if not _IsGoverned(path, projectRoot):
        return ()

    headerText = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
    relativePath = path.relative_to(projectRoot).as_posix()
    errors = []

    if LICENSEIDENTIFIER not in headerText:
        errors.append(f"{relativePath}: missing {LICENSEIDENTIFIER}")

    for identifier in SPDXPATTERN.findall(headerText):
        if identifier != "Apache-2.0":
            errors.append(f"{relativePath}: conflicting SPDX license {identifier}")

    if COPYRIGHTIDENTIFIER not in headerText:
        errors.append(f"{relativePath}: missing {COPYRIGHTIDENTIFIER}")

    if path.suffix == ".py":
        for requiredField in (
            "Project: FuzzyRoutines by Fuzzy Technologies",
            "Maintainer: Fuzzy Technologies contributors",
        ):
            if requiredField not in headerText:
                errors.append(f"{relativePath}: missing {requiredField}")

    return tuple(errors)


def ValidateRepository(projectRoot: Path = PROJECTROOT) -> tuple[str, ...]:
    """Return all Apache-2.0 header and metadata violations."""

    errors = []
    for trackedPath in _TrackedPaths(projectRoot):
        errors.extend(ValidateHeader(trackedPath, projectRoot))

    licensePath = projectRoot / "LICENSE"
    licenseDigest = hashlib.sha256(licensePath.read_bytes()).hexdigest()
    if licenseDigest != LICENSEDIGEST:
        errors.append("LICENSE: content differs from the canonical Apache-2.0 text")

    noticeText = (projectRoot / "NOTICE").read_text(encoding="utf-8")
    for requiredNotice in ("FuzzyRoutines", "Fuzzy Technologies", "Timur Gilmullin"):
        if requiredNotice not in noticeText:
            errors.append(f"NOTICE: missing {requiredNotice}")

    metadata = tomllib.loads((projectRoot / "pyproject.toml").read_text(encoding="utf-8"))
    projectMetadata = metadata.get("project", {})
    if projectMetadata.get("license") != "Apache-2.0":
        errors.append('pyproject.toml: project.license must be "Apache-2.0"')
    if set(projectMetadata.get("license-files", ())) != {"LICENSE", "NOTICE"}:
        errors.append("pyproject.toml: project.license-files must include LICENSE and NOTICE")
    for classifier in projectMetadata.get("classifiers", ()):
        if classifier.startswith("License ::"):
            errors.append(
                "pyproject.toml: PEP 639 license expression must not be combined "
                f"with license classifier {classifier!r}"
            )

    return tuple(errors)


def Main() -> int:
    """Print actionable violations and return a failing exit code on drift."""

    errors = ValidateRepository()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Apache-2.0 license headers and metadata: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
