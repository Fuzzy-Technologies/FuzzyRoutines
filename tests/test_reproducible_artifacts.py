# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Focused archive and comparison contracts without real distribution builds."""

import gzip
import json
import os
import tarfile
from pathlib import Path

import pytest
from setuptools import Distribution
from setuptools.command.sdist import sdist

from tools import reproducible_artifacts as artifacts

EPOCH = 1700000000


def SourceFixture(directory: Path, timestamp: int, mode: int) -> Path:
    """Prepare identical content with different creation order and host metadata."""

    source_directory = directory / "fuzzyroutines-2.0.0.dev0"
    source_directory.mkdir(parents=True)

    for name in ("z-last.py", "a-first.py", "PKG-INFO"):
        source_file = source_directory / name
        source_file.write_bytes(b"same source bytes\n")
        source_file.chmod(mode)
        os.utime(source_file, (timestamp, timestamp))

    executable = source_directory / "runner"
    executable.write_bytes(b"#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)
    os.utime(executable, (timestamp, timestamp))
    os.utime(source_directory, (timestamp, timestamp))

    return source_directory


def CandidateFixture(directory: Path, wheel: bytes = b"wheel", sdist_bytes: bytes = b"sdist") -> Path:
    """Create synthetic artifact bytes for comparison rather than package builds."""

    directory.mkdir(parents=True)
    (directory / "sample-2.0.0-py3-none-any.whl").write_bytes(wheel)
    (directory / "sample-2.0.0.tar.gz").write_bytes(sdist_bytes)

    return directory


def test_SourceArchiveBytesIgnoreSourceMtimesModesAndOutputName(tmp_path):
    """A stable epoch removes host timestamps, non-executable modes, and gzip names."""

    first_source = SourceFixture(tmp_path / "first", EPOCH + 1, 0o600)
    second_source = SourceFixture(tmp_path / "second", EPOCH + 86400, 0o664)
    first_archive = tmp_path / "first.tar.gz"
    second_archive = tmp_path / "different-name.tar.gz"
    artifacts.WriteSourceArchive(first_source, first_archive, EPOCH)
    artifacts.WriteSourceArchive(second_source, second_archive, EPOCH)

    assert first_archive.read_bytes() == second_archive.read_bytes()
    gzip_header = first_archive.read_bytes()[:10]
    assert int.from_bytes(gzip_header[4:8], "little") == EPOCH
    assert gzip_header[3] == 0, "gzip filename and comment must be absent"

    with tarfile.open(first_archive) as archive:
        members = archive.getmembers()
        assert [member.name for member in members] == sorted(member.name for member in members)

        for member in members:
            assert member.mtime == EPOCH
            assert (member.uid, member.gid, member.uname, member.gname) == (0, 0, "", "")
            expected_mode = 0o755 if member.isdir() or member.name.endswith("/runner") else 0o644
            assert member.mode == expected_mode

        payload = archive.extractfile("fuzzyroutines-2.0.0.dev0/PKG-INFO")
        assert payload is not None
        assert payload.read() == b"same source bytes\n"

    assert gzip.decompress(first_archive.read_bytes()), "the archive must contain a valid tar payload"


def test_SourceArchiveDetectsActualContentChanges(tmp_path):
    """Metadata normalization must never conceal changed source payload bytes."""

    source_directory = SourceFixture(tmp_path / "source", EPOCH, 0o644)
    first_archive = tmp_path / "first.tar.gz"
    second_archive = tmp_path / "second.tar.gz"
    artifacts.WriteSourceArchive(source_directory, first_archive, EPOCH)
    (source_directory / "PKG-INFO").write_bytes(b"different metadata content\n")
    artifacts.WriteSourceArchive(source_directory, second_archive, EPOCH)

    assert first_archive.read_bytes() != second_archive.read_bytes()


def test_SourceArchivePreservesInternalSymlinksAndLongNames(tmp_path):
    """Safe symlink targets and extended tar filenames retain their source meaning."""

    source_directory = SourceFixture(tmp_path / "source", EPOCH, 0o644)
    (source_directory / "metadata-link").symlink_to("PKG-INFO")
    long_name = "long-name-" + "x" * 110 + ".py"
    (source_directory / long_name).write_bytes(b"long filename payload\n")
    archive_path = tmp_path / "source.tar.gz"
    artifacts.WriteSourceArchive(source_directory, archive_path, EPOCH)

    with tarfile.open(archive_path) as archive:
        link = archive.getmember(f"{source_directory.name}/metadata-link")
        assert link.issym()
        assert link.linkname == "PKG-INFO"
        assert link.mtime == EPOCH
        payload = archive.extractfile(f"{source_directory.name}/{long_name}")
        assert payload is not None
        assert payload.read() == b"long filename payload\n"


def test_SourceArchiveRejectsSymlinksOutsidePreparedSource(tmp_path):
    """A source archive cannot pull untracked host files through escaping links."""

    source_directory = SourceFixture(tmp_path / "source", EPOCH, 0o644)
    host_file = tmp_path / "host-only.txt"
    host_file.write_bytes(b"not committed source\n")
    (source_directory / "host-link").symlink_to(host_file)

    with pytest.raises(ValueError, match="symlink escapes the prepared tree"):
        artifacts.WriteSourceArchive(source_directory, tmp_path / "source.tar.gz", EPOCH)


@pytest.mark.parametrize("epoch_text", ["", "-1", "1.5", " 12", "4294967296", "１２"])
def test_InvalidSourceEpochFailsClosed(epoch_text):
    """Invalid SOURCE_DATE_EPOCH values fail rather than silently use wall-clock time."""

    with pytest.raises(ValueError, match="SOURCE_DATE_EPOCH"):
        artifacts.SourceDateEpoch({"SOURCE_DATE_EPOCH": epoch_text})


def test_SourceEpochSupportsZeroAndUnset():
    """Unset epochs retain upstream behavior while zero remains an explicit value."""

    assert artifacts.SourceDateEpoch({}) is None
    assert artifacts.SourceDateEpoch({"SOURCE_DATE_EPOCH": "0"}) == 0
    assert artifacts.SourceDateEpoch({"SOURCE_DATE_EPOCH": str(EPOCH)}) == EPOCH


def test_SdistCommandWritesThePreparedTreeDirectly(tmp_path, monkeypatch):
    """The setuptools command uses the same deterministic archive writer."""

    source_directory = SourceFixture(tmp_path, EPOCH + 86400, 0o600)
    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(EPOCH))
    command = artifacts.ReproducibleSdist(Distribution())
    archive_path = command.make_archive(
        tmp_path / "dist" / source_directory.name,
        "gztar",
        root_dir=tmp_path,
        base_dir=source_directory.name,
    )

    with tarfile.open(archive_path) as archive:
        assert all(member.mtime == EPOCH for member in archive.getmembers())
        assert archive.getmember(f"{source_directory.name}/PKG-INFO").size == 18


def test_SdistCommandDryRunCreatesNoArchive(tmp_path, monkeypatch):
    """The setuptools dry-run contract performs no archive writes."""

    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(EPOCH))
    command = artifacts.ReproducibleSdist(Distribution())
    command.dry_run = True
    archive_path = command.make_archive(tmp_path / "sample", "gztar", base_dir="absent")

    assert archive_path == str(tmp_path / "sample.tar.gz")
    assert not Path(archive_path).exists()


@pytest.mark.parametrize("archive_format, epoch", [("gztar", None), ("zip", str(EPOCH))])
def test_SdistCommandPreservesUpstreamFallback(monkeypatch, archive_format, epoch):
    """Normal local builds and unsupported archive formats keep setuptools behavior."""

    if epoch is None:
        monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)

    else:
        monkeypatch.setenv("SOURCE_DATE_EPOCH", epoch)

    calls = []

    def UpstreamArchive(self, *arguments):
        """Record the preserved upstream command arguments."""

        calls.append(arguments)

        return "upstream-archive"

    monkeypatch.setattr(sdist, "make_archive", UpstreamArchive)
    command = artifacts.ReproducibleSdist(Distribution())
    result = command.make_archive("sample", archive_format, "root", "base", "owner", "group")

    assert result == "upstream-archive"
    assert calls == [("sample", archive_format, "root", "base", "owner", "group")]


@pytest.mark.parametrize("changed_artifact", ["wheel", "sdist"])
def test_ComparisonRejectsChangedDistributionBytes(tmp_path, changed_artifact):
    """A change to either distribution blocks release candidate selection."""

    first_directory = CandidateFixture(tmp_path / "first")
    second_directory = CandidateFixture(
        tmp_path / "second",
        wheel=b"changed" if changed_artifact == "wheel" else b"wheel",
        sdist_bytes=b"changed" if changed_artifact == "sdist" else b"sdist",
    )

    with pytest.raises(ValueError, match="Independent distribution builds differ"):
        artifacts.CompareArtifacts(first_directory, second_directory)


def test_ComparisonRejectsMissingDuplicateOrRenamedArtifacts(tmp_path):
    """Artifact completeness and filenames are part of the reproducibility contract."""

    first_directory = CandidateFixture(tmp_path / "first")
    second_directory = CandidateFixture(tmp_path / "second")
    wheel_path = second_directory / "sample-2.0.0-py3-none-any.whl"
    wheel_path.rename(second_directory / "other-2.0.0-py3-none-any.whl")

    with pytest.raises(ValueError, match="Independent distribution builds differ"):
        artifacts.CompareArtifacts(first_directory, second_directory)

    wheel_path.write_bytes(b"extra wheel")

    with pytest.raises(ValueError, match="Expected one wheel and one sdist"):
        artifacts.ArtifactHashes(second_directory)

    wheel_path.unlink()
    (second_directory / "other-2.0.0-py3-none-any.whl").unlink()

    with pytest.raises(ValueError, match="Expected one wheel and one sdist"):
        artifacts.ArtifactHashes(second_directory)


def test_CandidateSelectionPreservesComparedBytesAndSourceEvidence(tmp_path, monkeypatch):
    """CI selects exactly compared bytes and records two isolated candidate inputs."""

    calls = []

    def SourceEvidence(command, **options):
        """Supply fixed Git source evidence without a real repository operation."""

        return str(EPOCH) + "\n" if "show" in command else "abc123\n"

    def SyntheticCandidate(source_root, revision, workspace, epoch, timestamp_offset):
        """Stand in for build frontends while retaining candidate isolation evidence."""

        calls.append((revision, epoch, timestamp_offset, workspace))

        return CandidateFixture(workspace / "dist")

    monkeypatch.setattr(artifacts.subprocess, "check_output", SourceEvidence)
    monkeypatch.setattr(artifacts, "BuildIndependentCandidate", SyntheticCandidate)
    monkeypatch.setattr(artifacts, "version", lambda name: "test-version")
    output_directory = tmp_path / "dist"
    report = artifacts.BuildReproducibleArtifacts(tmp_path, output_directory)

    assert [(revision, epoch, offset) for revision, epoch, offset, _ in calls] == [
        ("abc123", EPOCH, 1), ("abc123", EPOCH, 86400)
    ]
    assert calls[0][3] != calls[1][3], "builds must use separate export directories"
    assert (output_directory / "sample-2.0.0-py3-none-any.whl").read_bytes() == b"wheel"
    assert (output_directory / "sample-2.0.0.tar.gz").read_bytes() == b"sdist"
    assert (output_directory / "source-revision.txt").read_text() == "abc123\n"
    assert json.loads((output_directory / "reproducibility.json").read_text()) == report
    assert report["independent_builds"] == 2
    assert report["source_mtime_offsets"] == [1, 86400]
    assert len((output_directory / "SHA256SUMS").read_text().splitlines()) == 2


def test_CandidateSelectionRejectsExistingOutputBeforeRunningBuilds(tmp_path):
    """Existing candidates cannot be overwritten or mixed with a new build."""

    with pytest.raises(ValueError, match="Artifact output must be a new directory"):
        artifacts.BuildReproducibleArtifacts(tmp_path, tmp_path)


def test_IndependentExportUsesFixedEpochAndScrubsImportOverrides(tmp_path, monkeypatch):
    """Each candidate builds only its fresh export with a declared stable environment."""

    source_file = tmp_path / "pyproject.toml"
    source_file.write_bytes(b"synthetic committed source\n")
    calls = []

    def ExportOrBuild(command, **options):
        """Produce a synthetic Git export and inspect the subsequent build boundary."""

        calls.append((command, options))

        if command[0] == "git":
            export_path = Path(command[3].removeprefix("--output="))

            with tarfile.open(export_path, "w") as archive:
                archive.add(source_file, arcname="pyproject.toml")

        else:
            exported_file = Path(command[-1]) / "pyproject.toml"
            assert exported_file.read_bytes() == source_file.read_bytes()
            assert exported_file.stat().st_mtime == EPOCH + 86400
            assert options["env"]["SOURCE_DATE_EPOCH"] == str(EPOCH)
            assert options["env"]["PYTHONHASHSEED"] == "0"
            assert "PYTHONPATH" not in options["env"]
            assert "MYPYPATH" not in options["env"]
            assert "--no-isolation" in command

    monkeypatch.setenv("PYTHONPATH", "/unexpected/source")
    monkeypatch.setenv("MYPYPATH", "/unexpected/types")
    monkeypatch.setattr(artifacts.subprocess, "run", ExportOrBuild)
    workspace = tmp_path / "isolated"
    result = artifacts.BuildIndependentCandidate(tmp_path, "abc123", workspace, EPOCH, 86400)

    assert result == workspace / "dist"
    assert calls[0][0][-1] == "abc123"
    assert calls[0][1]["cwd"] == tmp_path
    assert calls[1][1]["cwd"] == workspace


def test_CandidateMismatchLeavesNoSelectedArtifacts(tmp_path, monkeypatch):
    """A failed comparison creates no installable or publishable output candidates."""

    def SourceEvidence(command, **options):
        """Provide deterministic revision and epoch evidence."""

        return str(EPOCH) + "\n" if "show" in command else "abc123\n"

    def MismatchedCandidate(source_root, revision, workspace, epoch, timestamp_offset):
        """Produce different wheel bytes in the second isolated candidate."""

        return CandidateFixture(
            workspace / "dist", wheel=b"first" if timestamp_offset == 1 else b"second"
        )

    monkeypatch.setattr(artifacts.subprocess, "check_output", SourceEvidence)
    monkeypatch.setattr(artifacts, "BuildIndependentCandidate", MismatchedCandidate)
    output_directory = tmp_path / "dist"

    with pytest.raises(ValueError, match="Independent distribution builds differ"):
        artifacts.BuildReproducibleArtifacts(tmp_path, output_directory)

    assert not output_directory.exists()
