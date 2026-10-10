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

    sourceDirectory = directory / "fuzzyroutines-2.0.0.dev0"
    sourceDirectory.mkdir(parents=True)

    for name in ("z-last.py", "a-first.py", "PKG-INFO"):
        sourceFile = sourceDirectory / name
        sourceFile.write_bytes(b"same source bytes\n")
        sourceFile.chmod(mode)
        os.utime(sourceFile, (timestamp, timestamp))

    executable = sourceDirectory / "runner"
    executable.write_bytes(b"#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)
    os.utime(executable, (timestamp, timestamp))
    os.utime(sourceDirectory, (timestamp, timestamp))

    return sourceDirectory


def CandidateFixture(directory: Path, wheel: bytes = b"wheel", sdistBytes: bytes = b"sdist") -> Path:
    """Create synthetic artifact bytes for comparison rather than package builds."""

    directory.mkdir(parents=True)
    (directory / "sample-2.0.0-py3-none-any.whl").write_bytes(wheel)
    (directory / "sample-2.0.0.tar.gz").write_bytes(sdistBytes)

    return directory


def test_SourceArchiveBytesIgnoreSourceMtimesModesAndOutputName(tmpPath):
    """A stable epoch removes host timestamps, non-executable modes, and gzip names."""

    firstSource = SourceFixture(tmpPath / "first", EPOCH + 1, 0o600)
    secondSource = SourceFixture(tmpPath / "second", EPOCH + 86400, 0o664)
    firstArchive = tmpPath / "first.tar.gz"
    secondArchive = tmpPath / "different-name.tar.gz"
    artifacts.WriteSourceArchive(firstSource, firstArchive, EPOCH)
    artifacts.WriteSourceArchive(secondSource, secondArchive, EPOCH)

    assert firstArchive.read_bytes() == secondArchive.read_bytes()
    gzipHeader = firstArchive.read_bytes()[:10]
    assert int.from_bytes(gzipHeader[4:8], "little") == EPOCH
    assert gzipHeader[3] == 0, "gzip filename and comment must be absent"

    with tarfile.open(firstArchive) as archive:
        members = archive.getmembers()
        assert [member.name for member in members] == sorted(member.name for member in members)

        for member in members:
            assert member.mtime == EPOCH
            assert (member.uid, member.gid, member.uname, member.gname) == (0, 0, "", "")
            expectedMode = 0o755 if member.isdir() or member.name.endswith("/runner") else 0o644
            assert member.mode == expectedMode

        payload = archive.extractfile("fuzzyroutines-2.0.0.dev0/PKG-INFO")
        assert payload is not None
        assert payload.read() == b"same source bytes\n"

    assert gzip.decompress(firstArchive.read_bytes()), "the archive must contain a valid tar payload"


def test_SourceArchiveDetectsActualContentChanges(tmpPath):
    """Metadata normalization must never conceal changed source payload bytes."""

    sourceDirectory = SourceFixture(tmpPath / "source", EPOCH, 0o644)
    firstArchive = tmpPath / "first.tar.gz"
    secondArchive = tmpPath / "second.tar.gz"
    artifacts.WriteSourceArchive(sourceDirectory, firstArchive, EPOCH)
    (sourceDirectory / "PKG-INFO").write_bytes(b"different metadata content\n")
    artifacts.WriteSourceArchive(sourceDirectory, secondArchive, EPOCH)

    assert firstArchive.read_bytes() != secondArchive.read_bytes()


def test_SourceArchivePreservesInternalSymlinksAndLongNames(tmpPath):
    """Safe symlink targets and extended tar filenames retain their source meaning."""

    sourceDirectory = SourceFixture(tmpPath / "source", EPOCH, 0o644)
    (sourceDirectory / "metadata-link").symlink_to("PKG-INFO")
    longName = "long-name-" + "x" * 110 + ".py"
    (sourceDirectory / longName).write_bytes(b"long filename payload\n")
    archivePath = tmpPath / "source.tar.gz"
    artifacts.WriteSourceArchive(sourceDirectory, archivePath, EPOCH)

    with tarfile.open(archivePath) as archive:
        link = archive.getmember(f"{sourceDirectory.name}/metadata-link")
        assert link.issym()
        assert link.linkname == "PKG-INFO"
        assert link.mtime == EPOCH
        payload = archive.extractfile(f"{sourceDirectory.name}/{longName}")
        assert payload is not None
        assert payload.read() == b"long filename payload\n"


def test_SourceArchiveRejectsSymlinksOutsidePreparedSource(tmpPath):
    """A source archive cannot pull untracked host files through escaping links."""

    sourceDirectory = SourceFixture(tmpPath / "source", EPOCH, 0o644)
    hostFile = tmpPath / "host-only.txt"
    hostFile.write_bytes(b"not committed source\n")
    (sourceDirectory / "host-link").symlink_to(hostFile)

    with pytest.raises(ValueError, match="symlink escapes the prepared tree"):
        artifacts.WriteSourceArchive(sourceDirectory, tmpPath / "source.tar.gz", EPOCH)


@pytest.mark.parametrize('epochText', ["", "-1", "1.5", " 12", "4294967296", "１２"])
def test_InvalidSourceEpochFailsClosed(epochText):
    """Invalid SOURCE_DATE_EPOCH values fail rather than silently use wall-clock time."""

    with pytest.raises(ValueError, match="SOURCE_DATE_EPOCH"):
        artifacts.SourceDateEpoch({"SOURCE_DATE_EPOCH": epochText})


def test_SourceEpochSupportsZeroAndUnset():
    """Unset epochs retain upstream behavior while zero remains an explicit value."""

    assert artifacts.SourceDateEpoch({}) is None
    assert artifacts.SourceDateEpoch({"SOURCE_DATE_EPOCH": "0"}) == 0
    assert artifacts.SourceDateEpoch({"SOURCE_DATE_EPOCH": str(EPOCH)}) == EPOCH


def test_SdistCommandWritesThePreparedTreeDirectly(tmpPath, monkeypatch):
    """The setuptools command uses the same deterministic archive writer."""

    sourceDirectory = SourceFixture(tmpPath, EPOCH + 86400, 0o600)
    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(EPOCH))
    command = artifacts.ReproducibleSdist(Distribution())
    archivePath = command.make_archive(
        tmpPath / "dist" / sourceDirectory.name,
        "gztar",
        root_dir=tmpPath,
        base_dir=sourceDirectory.name,
    )

    with tarfile.open(archivePath) as archive:
        assert all(member.mtime == EPOCH for member in archive.getmembers())
        assert archive.getmember(f"{sourceDirectory.name}/PKG-INFO").size == 18


def test_SdistCommandDryRunCreatesNoArchive(tmpPath, monkeypatch):
    """The setuptools dry-run contract performs no archive writes."""

    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(EPOCH))
    command = artifacts.ReproducibleSdist(Distribution())
    command.dry_run = True
    archivePath = command.make_archive(tmpPath / "sample", "gztar", base_dir="absent")

    assert archivePath == str(tmpPath / "sample.tar.gz")
    assert not Path(archivePath).exists()


@pytest.mark.parametrize('archiveFormat,epoch', [("gztar", None), ("zip", str(EPOCH))])
def test_SdistCommandPreservesUpstreamFallback(monkeypatch, archiveFormat, epoch):
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
    result = command.make_archive("sample", archiveFormat, "root", "base", "owner", "group")

    assert result == "upstream-archive"
    assert calls == [("sample", archiveFormat, "root", "base", "owner", "group")]


@pytest.mark.parametrize('changedArtifact', ["wheel", "sdist"])
def test_ComparisonRejectsChangedDistributionBytes(tmpPath, changedArtifact):
    """A change to either distribution blocks release candidate selection."""

    firstDirectory = CandidateFixture(tmpPath / "first")
    secondDirectory = CandidateFixture(
        tmpPath / "second",
        wheel=b"changed" if changedArtifact == "wheel" else b"wheel",
        sdistBytes=b"changed" if changedArtifact == "sdist" else b"sdist",
    )

    with pytest.raises(ValueError, match="Independent distribution builds differ"):
        artifacts.CompareArtifacts(firstDirectory, secondDirectory)


def test_ComparisonRejectsMissingDuplicateOrRenamedArtifacts(tmpPath):
    """Artifact completeness and filenames are part of the reproducibility contract."""

    firstDirectory = CandidateFixture(tmpPath / "first")
    secondDirectory = CandidateFixture(tmpPath / "second")
    wheelPath = secondDirectory / "sample-2.0.0-py3-none-any.whl"
    wheelPath.rename(secondDirectory / "other-2.0.0-py3-none-any.whl")

    with pytest.raises(ValueError, match="Independent distribution builds differ"):
        artifacts.CompareArtifacts(firstDirectory, secondDirectory)

    wheelPath.write_bytes(b"extra wheel")

    with pytest.raises(ValueError, match="Expected one wheel and one sdist"):
        artifacts.ArtifactHashes(secondDirectory)

    wheelPath.unlink()
    (secondDirectory / "other-2.0.0-py3-none-any.whl").unlink()

    with pytest.raises(ValueError, match="Expected one wheel and one sdist"):
        artifacts.ArtifactHashes(secondDirectory)


def test_CandidateSelectionPreservesComparedBytesAndSourceEvidence(tmpPath, monkeypatch):
    """CI selects exactly compared bytes and records two isolated candidate inputs."""

    calls = []

    def SourceEvidence(command, **options):
        """Supply fixed Git source evidence without a real repository operation."""

        return str(EPOCH) + "\n" if "show" in command else "abc123\n"

    def SyntheticCandidate(sourceRoot, revision, workspace, epoch, timestampOffset):
        """Stand in for build frontends while retaining candidate isolation evidence."""

        calls.append((revision, epoch, timestampOffset, workspace))

        return CandidateFixture(workspace / "dist")

    monkeypatch.setattr(artifacts.subprocess, "check_output", SourceEvidence)
    monkeypatch.setattr(artifacts, "BuildIndependentCandidate", SyntheticCandidate)
    monkeypatch.setattr(artifacts, "version", lambda name: "test-version")
    outputDirectory = tmpPath / "dist"
    report = artifacts.BuildReproducibleArtifacts(tmpPath, outputDirectory)

    assert [(revision, epoch, offset) for revision, epoch, offset, _ in calls] == [
        ("abc123", EPOCH, 1), ("abc123", EPOCH, 86400)
    ]
    assert calls[0][3] != calls[1][3], "builds must use separate export directories"
    assert (outputDirectory / "sample-2.0.0-py3-none-any.whl").read_bytes() == b"wheel"
    assert (outputDirectory / "sample-2.0.0.tar.gz").read_bytes() == b"sdist"
    assert (outputDirectory / "source-revision.txt").read_text() == "abc123\n"
    assert json.loads((outputDirectory / "reproducibility.json").read_text()) == report
    assert report["independent_builds"] == 2
    assert report["source_mtime_offsets"] == [1, 86400]
    assert len((outputDirectory / "SHA256SUMS").read_text().splitlines()) == 2


def test_CandidateSelectionRejectsExistingOutputBeforeRunningBuilds(tmpPath):
    """Existing candidates cannot be overwritten or mixed with a new build."""

    with pytest.raises(ValueError, match="Artifact output must be a new directory"):
        artifacts.BuildReproducibleArtifacts(tmpPath, tmpPath)


def test_IndependentExportUsesFixedEpochAndScrubsImportOverrides(tmpPath, monkeypatch):
    """Each candidate builds only its fresh export with a declared stable environment."""

    sourceFile = tmpPath / "pyproject.toml"
    sourceFile.write_bytes(b"synthetic committed source\n")
    calls = []

    def ExportOrBuild(command, **options):
        """Produce a synthetic Git export and inspect the subsequent build boundary."""

        calls.append((command, options))

        if command[0] == "git":
            exportPath = Path(command[3].removeprefix("--output="))

            with tarfile.open(exportPath, "w") as archive:
                archive.add(sourceFile, arcname="pyproject.toml")

        else:
            exportedFile = Path(command[-1]) / "pyproject.toml"
            assert exportedFile.read_bytes() == sourceFile.read_bytes()
            assert exportedFile.stat().st_mtime == EPOCH + 86400
            assert options["env"]["SOURCE_DATE_EPOCH"] == str(EPOCH)
            assert options["env"]["PYTHONHASHSEED"] == "0"
            assert "PYTHONPATH" not in options["env"]
            assert "MYPYPATH" not in options["env"]
            assert "--no-isolation" in command

    monkeypatch.setenv("PYTHONPATH", "/unexpected/source")
    monkeypatch.setenv("MYPYPATH", "/unexpected/types")
    monkeypatch.setattr(artifacts.subprocess, "run", ExportOrBuild)
    workspace = tmpPath / "isolated"
    result = artifacts.BuildIndependentCandidate(tmpPath, "abc123", workspace, EPOCH, 86400)

    assert result == workspace / "dist"
    assert calls[0][0][-1] == "abc123"
    assert calls[0][1]["cwd"] == tmpPath
    assert calls[1][1]["cwd"] == workspace


def test_CandidateMismatchLeavesNoSelectedArtifacts(tmpPath, monkeypatch):
    """A failed comparison creates no installable or publishable output candidates."""

    def SourceEvidence(command, **options):
        """Provide deterministic revision and epoch evidence."""

        return str(EPOCH) + "\n" if "show" in command else "abc123\n"

    def MismatchedCandidate(sourceRoot, revision, workspace, epoch, timestampOffset):
        """Produce different wheel bytes in the second isolated candidate."""

        return CandidateFixture(
            workspace / "dist", wheel=b"first" if timestampOffset == 1 else b"second"
        )

    monkeypatch.setattr(artifacts.subprocess, "check_output", SourceEvidence)
    monkeypatch.setattr(artifacts, "BuildIndependentCandidate", MismatchedCandidate)
    outputDirectory = tmpPath / "dist"

    with pytest.raises(ValueError, match="Independent distribution builds differ"):
        artifacts.BuildReproducibleArtifacts(tmpPath, outputDirectory)

    assert not outputDirectory.exists()
