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

    epoch_text = environment.get("SOURCE_DATE_EPOCH")

    if epoch_text is None:
        return None

    if not epoch_text.isascii() or not epoch_text.isdecimal():
        raise ValueError("SOURCE_DATE_EPOCH must be a nonnegative integer")

    epoch = int(epoch_text)

    if epoch > 0xFFFFFFFF:
        raise ValueError("SOURCE_DATE_EPOCH must fit the gzip 32-bit timestamp")

    return epoch


def WriteSourceArchive(source_directory: Path, archive_path: Path, epoch: int) -> str:
    """Archive the prepared sdist tree with stable metadata and intact payloads."""

    source_directory = source_directory.resolve()
    archive_path = archive_path.resolve()
    archive_path.parent.mkdir(parents=True, exist_ok=True)

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
        archive_path.open("wb") as raw_archive,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw_archive, mtime=epoch) as compressed,
        tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive,
    ):
        source_paths = (source_directory, *sorted(source_directory.rglob("*")))

        for source_path in source_paths:
            archive.dereference = not source_path.is_symlink()

            if source_path.is_symlink() and not source_path.resolve().is_relative_to(source_directory):
                raise ValueError(f"Source archive symlink escapes the prepared tree: {source_path}")

            archive_name = Path(source_directory.name) / source_path.relative_to(source_directory)
            member = NormalizeMember(archive.gettarinfo(source_path, arcname=archive_name.as_posix()))

            if member.isfile():
                with source_path.open("rb") as payload:
                    archive.addfile(member, payload)

            else:
                archive.addfile(member)

    return str(archive_path)


def ArtifactHashes(directory: Path) -> dict[str, str]:
    """Require one wheel and one sdist and hash their exact distribution bytes."""

    wheels = sorted(directory.glob("*.whl"))
    sdists = sorted(directory.glob("*.tar.gz"))

    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError(f"Expected one wheel and one sdist in {directory}")

    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (*wheels, *sdists)}


def CompareArtifacts(first_directory: Path, second_directory: Path) -> dict[str, str]:
    """Reject filename or byte changes between independent distribution builds."""

    first_hashes = ArtifactHashes(first_directory)
    second_hashes = ArtifactHashes(second_directory)

    if first_hashes != second_hashes:
        raise ValueError(
            "Independent distribution builds differ: "
            f"first={first_hashes}, second={second_hashes}"
        )

    return first_hashes


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

        archive_path = Path(str(base_name) + ".tar.gz")

        if self.dry_run:
            return str(archive_path)

        source_directory = Path(root_dir or ".") / (base_dir or ".")

        return WriteSourceArchive(source_directory, archive_path, epoch)


def BuildIndependentCandidate(
    source_root: Path,
    revision: str,
    workspace: Path,
    epoch: int,
    timestamp_offset: int,
) -> Path:
    """Build an isolated Git export with deliberately different source mtimes."""

    workspace.mkdir()
    export_path = workspace / "source.tar"
    source_directory = workspace / "source"
    source_directory.mkdir()
    subprocess.run(
        ["git", "archive", "--format=tar", f"--output={export_path}", revision],
        cwd=source_root,
        check=True,
    )

    with tarfile.open(export_path) as exported_source:
        exported_source.extractall(source_directory, filter="data")

    for source_path in source_directory.rglob("*"):
        os.utime(
            source_path,
            (epoch + timestamp_offset, epoch + timestamp_offset),
            follow_symlinks=False,
        )

    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = str(epoch)
    environment["PYTHONHASHSEED"] = "0"
    environment.pop("PYTHONPATH", None)
    environment.pop("MYPYPATH", None)
    artifact_directory = workspace / "dist"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--no-isolation",
            "--outdir",
            str(artifact_directory),
            str(source_directory),
        ],
        cwd=workspace,
        env=environment,
        check=True,
    )

    return artifact_directory


def BuildReproducibleArtifacts(source_root: Path, output_directory: Path) -> dict:
    """Build, compare, and preserve verified candidates and their source evidence."""

    source_root = source_root.resolve()
    output_directory = output_directory.resolve()

    if output_directory.exists():
        raise ValueError(f"Artifact output must be a new directory: {output_directory}")

    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source_root, text=True
    ).strip()
    epoch = int(
        subprocess.check_output(
            ["git", "show", "-s", "--format=%ct", revision], cwd=source_root, text=True
        ).strip()
    )
    SourceDateEpoch({"SOURCE_DATE_EPOCH": str(epoch)})

    with tempfile.TemporaryDirectory(prefix="fuzzyroutines-reproducibility-") as temporary:
        workspace = Path(temporary)
        first_directory = BuildIndependentCandidate(source_root, revision, workspace / "first", epoch, 1)
        second_directory = BuildIndependentCandidate(source_root, revision, workspace / "second", epoch, 86400)
        hashes = CompareArtifacts(first_directory, second_directory)
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
        output_directory.mkdir(parents=True)

        for name in hashes:
            shutil.copyfile(first_directory / name, output_directory / name)

    (output_directory / "source-revision.txt").write_text(revision + "\n", encoding="utf-8")
    (output_directory / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in hashes.items()), encoding="utf-8"
    )
    (output_directory / "reproducibility.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    return report


def Main(arguments: list[str] | None = None) -> int:
    """Build CI candidates and print a machine-readable reproducibility report."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-directory", type=Path, required=True)
    parsed_arguments = parser.parse_args(arguments)
    report = BuildReproducibleArtifacts(
        parsed_arguments.source_root, parsed_arguments.output_directory
    )
    print(json.dumps(report, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
