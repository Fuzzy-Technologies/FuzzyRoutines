# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Create deterministic sdists and compare independent CI distribution builds.

The archive writer runs within setuptools before an sdist exists. The CLI
exports the exact Git revision twice, varies source filesystem timestamps,
builds with the active locked environment, and copies unchanged candidates only
after both wheel and sdist hashes match. It never publishes distributions.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from importlib.metadata import version
from pathlib import Path

from setuptools.command.sdist import sdist

BUILD_TOOLS = ("build", "packaging", "pyproject_hooks", "setuptools")


def SourceDateEpoch(environment: dict[str, str]) -> int | None:
    """Return a valid gzip-compatible source epoch or reject malformed input."""

    epochText = environment.get("SOURCE_DATE_EPOCH")

    if epochText is None:
        return None

    if not epochText.isascii() or not epochText.isdecimal():
        raise ValueError("SOURCE_DATE_EPOCH must be a nonnegative integer")

    epoch = int(epochText)

    if epoch > 0xFFFFFFFF:
        raise ValueError("SOURCE_DATE_EPOCH must fit the gzip 32-bit timestamp")

    return epoch


def WriteSourceArchive(sourceDirectory: Path, archivePath: Path, epoch: int) -> str:
    """Archive the prepared sdist tree with stable metadata and intact payloads."""

    sourceDirectory = sourceDirectory.resolve()
    archivePath = archivePath.resolve()
    archivePath.parent.mkdir(parents=True, exist_ok=True)

    def NormalizeMember(member: tarfile.TarInfo) -> tarfile.TarInfo:
        """Remove host ownership and filesystem timestamp variation."""

        member.uid = member.gid = 0
        member.uname = member.gname = ""
        member.mtime = epoch
        member.pax_headers = {}

        if member.isdir():
            member.mode = 0o755

        elif member.isfile():
            member.mode = 0o755 if member.mode & 0o111 else 0o644

        elif member.issym():
            member.mode = 0o777

        else:
            raise ValueError(f"Unsupported source archive member: {member.name}")

        return member

    with (
        archivePath.open("wb") as rawArchive,
        gzip.GzipFile(filename="", mode="wb", fileobj=rawArchive, mtime=epoch) as compressed,
        tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive,
    ):
        sourcePaths = (sourceDirectory, *sorted(sourceDirectory.rglob("*")))

        for sourcePath in sourcePaths:
            archive.dereference = not sourcePath.is_symlink()

            if sourcePath.is_symlink() and not sourcePath.resolve().is_relative_to(sourceDirectory):
                raise ValueError(f"Source archive symlink escapes the prepared tree: {sourcePath}")

            archiveName = Path(sourceDirectory.name) / sourcePath.relative_to(sourceDirectory)
            member = NormalizeMember(archive.gettarinfo(sourcePath, arcname=archiveName.as_posix()))

            if member.isfile():
                with sourcePath.open("rb") as payload:
                    archive.addfile(member, payload)

            else:
                archive.addfile(member)

    return str(archivePath)


def ArtifactHashes(directory: Path) -> dict[str, str]:
    """Require one wheel and one sdist and hash their exact distribution bytes."""

    wheels = sorted(directory.glob("*.whl"))
    sdists = sorted(directory.glob("*.tar.gz"))

    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError(f"Expected one wheel and one sdist in {directory}")

    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (*wheels, *sdists)}


def CompareArtifacts(firstDirectory: Path, secondDirectory: Path) -> dict[str, str]:
    """Reject filename or byte changes between independent distribution builds."""

    firstHashes = ArtifactHashes(firstDirectory)
    secondHashes = ArtifactHashes(secondDirectory)

    if firstHashes != secondHashes:
        raise ValueError(
            "Independent distribution builds differ: "
            f"first={firstHashes}, second={secondHashes}"
        )

    return firstHashes


class ReproducibleSdist(sdist):
    """Preserve setuptools preparation and normalize archive metadata at creation."""

    def make_archive(
        self, base_name, format, root_dir=None, base_dir=None, owner=None, group=None
    ):
        """Honor SOURCE_DATE_EPOCH while preserving the setuptools command API."""

        epoch = SourceDateEpoch(os.environ)

        if epoch is None or format != "gztar":
            return super().make_archive(
                base_name, format, root_dir, base_dir, owner, group
            )

        archivePath = Path(str(base_name) + ".tar.gz")

        if self.dry_run:
            return str(archivePath)

        sourceDirectory = Path(root_dir or ".") / (base_dir or ".")

        return WriteSourceArchive(sourceDirectory, archivePath, epoch)


def BuildIndependentCandidate(
    sourceRoot: Path,
    revision: str,
    workspace: Path,
    epoch: int,
    timestampOffset: int,
) -> Path:
    """Build an isolated Git export with deliberately different source mtimes."""

    workspace.mkdir()
    exportPath = workspace / "source.tar"
    sourceDirectory = workspace / "source"
    sourceDirectory.mkdir()
    subprocess.run(
        ["git", "archive", "--format=tar", f"--output={exportPath}", revision],
        cwd=sourceRoot,
        check=True,
    )

    with tarfile.open(exportPath) as exportedSource:
        exportedSource.extractall(sourceDirectory, filter="data")

    for sourcePath in sourceDirectory.rglob("*"):
        os.utime(
            sourcePath,
            (epoch + timestampOffset, epoch + timestampOffset),
            follow_symlinks=False,
        )

    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = str(epoch)
    environment["PYTHONHASHSEED"] = "0"
    environment.pop("PYTHONPATH", None)
    environment.pop("MYPYPATH", None)
    artifactDirectory = workspace / "dist"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--no-isolation",
            "--outdir",
            str(artifactDirectory),
            str(sourceDirectory),
        ],
        cwd=workspace,
        env=environment,
        check=True,
    )

    return artifactDirectory


def BuildReproducibleArtifacts(sourceRoot: Path, outputDirectory: Path) -> dict:
    """Build, compare, and preserve verified candidates and their source evidence."""

    sourceRoot = sourceRoot.resolve()
    outputDirectory = outputDirectory.resolve()

    if outputDirectory.exists():
        raise ValueError(f"Artifact output must be a new directory: {outputDirectory}")

    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=sourceRoot, text=True
    ).strip()
    epoch = int(
        subprocess.check_output(
            ["git", "show", "-s", "--format=%ct", revision], cwd=sourceRoot, text=True
        ).strip()
    )
    SourceDateEpoch({"SOURCE_DATE_EPOCH": str(epoch)})

    with tempfile.TemporaryDirectory(prefix="fuzzyroutines-reproducibility-") as temporary:
        workspace = Path(temporary)
        firstDirectory = BuildIndependentCandidate(sourceRoot, revision, workspace / "first", epoch, 1)
        secondDirectory = BuildIndependentCandidate(sourceRoot, revision, workspace / "second", epoch, 86400)
        hashes = CompareArtifacts(firstDirectory, secondDirectory)
        report = {
            "source_revision": revision,
            "source_date_epoch": epoch,
            "python": sys.version,
            "platform": sys.platform,
            "build_tools": {name: version(name) for name in BUILD_TOOLS},
            "source_mtime_offsets": [1, 86400],
            "independent_builds": 2,
            "artifacts": {
                name: {"first_sha256": digest, "second_sha256": digest}
                for name, digest in hashes.items()
            },
        }
        outputDirectory.mkdir(parents=True)

        for name in hashes:
            shutil.copyfile(firstDirectory / name, outputDirectory / name)

    (outputDirectory / "source-revision.txt").write_text(revision + "\n", encoding="utf-8")
    (outputDirectory / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in hashes.items()), encoding="utf-8"
    )
    (outputDirectory / "reproducibility.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    return report


def Main(arguments: list[str] | None = None) -> int:
    """Build CI candidates and print a machine-readable reproducibility report."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path.cwd(), dest = 'sourceRoot')
    parser.add_argument("--output-directory", type=Path, required=True, dest = 'outputDirectory')
    parsedArguments = parser.parse_args(arguments)
    report = BuildReproducibleArtifacts(
        parsedArguments.sourceRoot, parsedArguments.outputDirectory
    )
    print(json.dumps(report, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
