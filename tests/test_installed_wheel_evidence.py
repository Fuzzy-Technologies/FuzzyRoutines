# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Reject mislabeled artifacts and source imports without building distributions."""

import json
import subprocess
import sys
import types
import zipfile
from pathlib import Path

import pytest

from experiments import installed_wheel_evidence as evidence


def WriteBuildEvidence(config, records=None):
    """Create an API-digest-bound synthetic archive without building a package."""

    artifact = config["candidate"]
    wheelPath = Path(artifact["wheel"])
    run = json.loads(Path(artifact["provenance_json"]).read_text())

    if records is None:
        reproducibility = {"source_revision": artifact["source_commit"], "independent_builds": 2,
                           "artifacts": {wheelPath.name: {"first_sha256": artifact["wheel_sha256"], "second_sha256": artifact["wheel_sha256"]}}}
        records = {"source-revision.txt": (artifact["source_commit"] + "\n").encode(),
                   "reproducibility.json": json.dumps(reproducibility).encode(),
                   "SHA256SUMS": f"{artifact['wheel_sha256']}  {wheelPath.name}\n".encode(),
                   wheelPath.name: wheelPath.read_bytes()}

    archivePath = Path(artifact["artifact_archive"])

    with zipfile.ZipFile(archivePath, "w") as archive:
        for name, data in records.items():
            archive.writestr(name, data)

    metadata = {"id": 456, "name": "package-artifacts-python-3.14",
                "digest": "sha256:" + evidence.Digest(archivePath.read_bytes()),
                "workflow_run": {"id": run["id"], "head_sha": run["head_sha"]}}
    Path(artifact["artifact_metadata_json"]).write_text(json.dumps(metadata))


def SetBuildRevision(config, commit, head=None, event="push"):
    """Update all legitimate source records before testing independent payload checks."""

    artifact = config["candidate"]
    artifact["source_commit"] = commit
    runPath = Path(artifact["provenance_json"])
    run = json.loads(runPath.read_text())
    run.update({"head_sha": head or commit, "event": event})
    runPath.write_text(json.dumps(run))
    WriteBuildEvidence(config)


def PullRequestMerge(config):
    """Construct actual Git branch/merge objects with unchanged package payloads."""

    base = config["candidate"]["source_commit"]
    tree = evidence.Git(config, "rev-parse", base + "^{tree}").decode().strip()
    identity = ("-c", "user.name=Evidence Test", "-c", "user.email=evidence@example.invalid")
    head = evidence.Git(config, *identity, "commit-tree", tree, "-p", base, "-m", "PR head").decode().strip()
    merge = evidence.Git(config, *identity, "commit-tree", tree, "-p", base, "-p", head, "-m", "Synthetic PR merge").decode().strip()
    SetBuildRevision(config, merge, head, "pull_request")

    return base, head, merge


@pytest.fixture(name="artifactCase")
def ArtifactCase(tmpPath):
    """Create a tiny synthetic archive and real Git object for byte-identity tests."""

    repository = tmpPath / "repository"
    package = repository / "fuzzyroutines"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("raise RuntimeError('must never import the fixture package')\n")
    (package / "py.typed").write_bytes(b"")
    (repository / "pyproject.toml").write_text('[project]\nname = "fuzzyroutines"\nversion = "2.1.0.dev0"\n')
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(["git", "-C", str(repository), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repository), "-c", "user.name=Evidence Test", "-c", "user.email=evidence@example.invalid", "commit", "-qm", "Synthetic fixture"], check=True)
    commit = evidence.Git({"repository": str(repository)}, "rev-parse", "HEAD").decode().strip()
    wheelPath = tmpPath / "fuzzyroutines-2.1.0.dev0-py3-none-any.whl"

    with zipfile.ZipFile(wheelPath, "w") as archive:
        for path in package.iterdir():
            archive.writestr("fuzzyroutines/" + path.name, path.read_bytes())

        archive.writestr("fuzzyroutines-2.1.0.dev0.dist-info/METADATA", "Name: fuzzyroutines\nVersion: 2.1.0.dev0\nRequires-Dist: numpy>=2.3.5; extra == 'numpy'\n")

    provenance = tmpPath / "workflow.json"
    url = "https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/123"
    provenance.write_text(json.dumps({"id": 123, "head_sha": commit, "conclusion": "success", "status": "completed", "html_url": url,
                                     "event": "push", "path": ".github/workflows/package-build-install.yml", "name": "Package build and clean-install"}))
    artifact = {"wheel": str(wheelPath), "wheel_sha256": evidence.Digest(wheelPath.read_bytes()),
                "version": "2.1.0.dev0", "source_commit": commit, "provenance_json": str(provenance), "source_evidence_url": url,
                "artifact_archive": str(tmpPath / "package-artifacts.zip"), "artifact_metadata_json": str(tmpPath / "artifact-api.json")}
    config = {"repository": str(repository), "candidate": artifact}
    WriteBuildEvidence(config)

    return config


def test_WheelBindsActualBytesToWorkflowAndGitWithoutPackageImport(artifactCase):
    """Import-hostile source can be verified without execution or installation."""

    verified = evidence.VerifyWheel(artifactCase, "candidate")
    assert verified["wheel_python_source_matches_commit"] is True
    assert set(verified["package_file_sha256"]) == {"fuzzyroutines/__init__.py", "fuzzyroutines/py.typed"}
    assert verified["candidate_build_evidence"]["built_source_kind"] == "workflow_head"
    assert verified["candidate_build_evidence"]["workflow_head_sha"] == verified["source_commit"]


def test_PullRequestArchiveRetainsBuiltMergeAndImmutableRunHead(artifactCase):
    """Accept the actual PR checkout model without consulting mutable PR snapshots."""

    base, head, merge = PullRequestMerge(artifactCase)
    runPath = Path(artifactCase["candidate"]["provenance_json"])
    run = json.loads(runPath.read_text())
    run["pull_requests"] = [{"head": {"sha": "f" * 40}, "base": {"sha": "e" * 40}}]
    runPath.write_text(json.dumps(run))
    result = evidence.VerifyWheel(artifactCase, "candidate")["candidate_build_evidence"]
    assert result["built_source_kind"] == "pull_request_merge"
    assert result["built_source_commit"] == merge and result["workflow_head_sha"] == head
    assert result["built_source_parents"] == [base, head]
    assert result["artifact_archive_sha256"] == evidence.Digest(Path(artifactCase["candidate"]["artifact_archive"]).read_bytes())


def test_IdenticalPayloadCannotRelabelTheBuiltMergeAsItsHead(artifactCase):
    """Keep the recorded built revision even when head and merge have identical code."""

    _, head, merge = PullRequestMerge(artifactCase)
    assert evidence.Git(artifactCase, "rev-parse", head + "^{tree}") == evidence.Git(artifactCase, "rev-parse", merge + "^{tree}")
    artifactCase["candidate"]["source_commit"] = head

    with pytest.raises(ValueError, match="source records"):
        evidence.VerifyWheel(artifactCase, "candidate")


@pytest.mark.parametrize("mutation", ("head_parent", "single_parent", "non_pr_event"))
def test_ArchiveCannotRelabelUnrelatedSourceAsTheRunMerge(artifactCase, mutation):
    """Reject unrelated heads, ordinary descendants, and unsupported event relationships."""

    base, head, merge = PullRequestMerge(artifactCase)

    if mutation == "head_parent":
        SetBuildRevision(artifactCase, merge, base, "pull_request")

    elif mutation == "single_parent":
        SetBuildRevision(artifactCase, head, base, "pull_request")

    else:
        SetBuildRevision(artifactCase, merge, head, "push")

    with pytest.raises(ValueError, match="pull-request merge"):
        evidence.VerifyWheel(artifactCase, "candidate")


@pytest.mark.parametrize("key,value", [("head_sha", "0" * 40), ("conclusion", "failure"), ("status", "in_progress"),
                                      ("html_url", "https://example.invalid/other-run"), ("path", ".github/workflows/another.yml"), ("name", "Other workflow")])
def test_WheelRejectsDifferentOrFailedWorkflow(artifactCase, key, value):
    """An unrelated successful-looking source record cannot identify the candidate."""

    path = Path(artifactCase["candidate"]["provenance_json"])
    data = json.loads(path.read_text())
    data[key] = value
    path.write_text(json.dumps(data))

    with pytest.raises(ValueError, match="workflow"):
        evidence.VerifyWheel(artifactCase, "candidate")


@pytest.mark.parametrize("mutation", ("run_id", "run_head", "job", "archive_digest"))
def test_ArtifactApiMustIdentifyTheRunAndDownloadedArchive(artifactCase, mutation):
    """Independently bind API artifact metadata to its run, job, and ZIP bytes."""

    path = Path(artifactCase["candidate"]["artifact_metadata_json"])
    metadata = json.loads(path.read_text())

    if mutation == "run_id":
        metadata["workflow_run"]["id"] += 1

    elif mutation == "run_head":
        metadata["workflow_run"]["head_sha"] = "0" * 40

    elif mutation == "job":
        metadata["name"] = "some-other-artifact"

    else:
        metadata["digest"] = "sha256:" + "0" * 64

    path.write_text(json.dumps(metadata))

    with pytest.raises(ValueError, match="artifact"):
        evidence.VerifyWheel(artifactCase, "candidate")


def test_ArchiveRejectsDuplicateBuildRecords(artifactCase):
    """Reject ambiguous archive entries even when the API archive digest matches."""

    artifact = artifactCase["candidate"]

    with zipfile.ZipFile(artifact["artifact_archive"], "a") as archive, pytest.warns(UserWarning, match="Duplicate name"):
        archive.writestr("source-revision.txt", artifact["source_commit"] + "\n")

    metadataPath = Path(artifact["artifact_metadata_json"])
    metadata = json.loads(metadataPath.read_text())
    metadata["digest"] = "sha256:" + evidence.Digest(Path(artifact["artifact_archive"]).read_bytes())
    metadataPath.write_text(json.dumps(metadata))

    with pytest.raises(ValueError, match="exactly once"):
        evidence.VerifyWheel(artifactCase, "candidate")


@pytest.mark.parametrize("mutation", ("source_record", "repro_source", "first_hash", "second_hash", "build_count", "sums_hash", "duplicate_sums", "embedded_wheel", "missing_record"))
def test_ArchiveRecordsCannotContradictBuiltSourceOrMeasuredWheel(artifactCase, mutation):
    """A valid archive digest cannot conceal contradictory source or wheel evidence."""

    artifact = artifactCase["candidate"]

    with zipfile.ZipFile(artifact["artifact_archive"]) as archive:
        records = {name: archive.read(name) for name in archive.namelist()}

    reproducibility = json.loads(records["reproducibility.json"])
    wheelName = Path(artifact["wheel"]).name

    if mutation == "source_record":
        records["source-revision.txt"] = ("0" * 40).encode()

    elif mutation == "repro_source":
        reproducibility["source_revision"] = "0" * 40

    elif mutation in ("first_hash", "second_hash"):
        key = "first_sha256" if mutation == "first_hash" else "second_sha256"
        reproducibility["artifacts"][wheelName][key] = "0" * 64

    elif mutation == "build_count":
        reproducibility["independent_builds"] = 1

    elif mutation == "sums_hash":
        records["SHA256SUMS"] = f"{'0' * 64}  {wheelName}\n".encode()

    elif mutation == "duplicate_sums":
        records["SHA256SUMS"] *= 2

    elif mutation == "embedded_wheel":
        records[wheelName] = b"different wheel bytes"

    else:
        del records["source-revision.txt"]

    records["reproducibility.json"] = json.dumps(reproducibility).encode()
    WriteBuildEvidence(artifactCase, records)

    with pytest.raises(ValueError, match="archive|source|checksums"):
        evidence.VerifyWheel(artifactCase, "candidate")


def test_WheelRejectsDigestAndSourceMismatchIndependently(artifactCase):
    """A valid checksum alone does not establish correspondence to source bytes."""

    original = artifactCase["candidate"]["wheel_sha256"]
    artifactCase["candidate"]["wheel_sha256"] = "0" * 64

    with pytest.raises(ValueError, match="digest"):
        evidence.VerifyWheel(artifactCase, "candidate")

    artifactCase["candidate"]["wheel_sha256"] = original
    repository = Path(artifactCase["repository"])
    (repository / "fuzzyroutines/__init__.py").write_text("changed = True\n")
    subprocess.run(["git", "-C", str(repository), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repository), "-c", "user.name=Evidence Test", "-c", "user.email=evidence@example.invalid", "commit", "-qm", "Changed fixture"], check=True)
    commit = evidence.Git(artifactCase, "rev-parse", "HEAD").decode().strip()
    SetBuildRevision(artifactCase, commit)

    with pytest.raises(ValueError, match="Python bytes"):
        evidence.VerifyWheel(artifactCase, "candidate")


@pytest.mark.parametrize("name,version", [("fuzzyroutines", "2.0.0"), ("another-project", "2.1.0.dev0")])
def test_WheelMustMatchCommittedProjectMetadataNotOnlyConfig(artifactCase, name, version):
    """Identical Python payload and matching config cannot override source identity."""

    repository = Path(artifactCase["repository"])
    (repository / "pyproject.toml").write_text(f'[project]\nname = "{name}"\nversion = "{version}"\n')
    subprocess.run(["git", "-C", str(repository), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repository), "-c", "user.name=Evidence Test", "-c", "user.email=evidence@example.invalid", "commit", "-qm", "Changed identity"], check=True)
    commit = evidence.Git(artifactCase, "rev-parse", "HEAD").decode().strip()
    SetBuildRevision(artifactCase, commit)

    with pytest.raises(ValueError, match="committed project metadata"):
        evidence.VerifyWheel(artifactCase, "candidate")


def test_BaselineRequiresItsExactPypiFileAndDigest(artifactCase):
    """PyPI release metadata must identify the exact retained baseline wheel."""

    artifact = dict(artifactCase["candidate"])
    artifact["source_evidence_url"] = "https://pypi.org/pypi/fuzzyroutines/2.1.0.dev0/json"
    release = {"info": {"version": artifact["version"]}, "urls": [{"filename": Path(artifact["wheel"]).name, "digests": {"sha256": artifact["wheel_sha256"]}}]}
    path = Path(artifact["provenance_json"])
    path.write_text(json.dumps(release))
    artifactCase["baseline"] = artifact
    assert evidence.VerifyWheel(artifactCase, "baseline")["wheel_python_source_matches_commit"]
    release["urls"][0]["filename"] = "different.whl"
    path.write_text(json.dumps(release))

    with pytest.raises(ValueError, match="PyPI release"):
        evidence.VerifyWheel(artifactCase, "baseline")


@pytest.fixture(name="installedCase")
def InstalledCase(artifactCase, tmpPath, monkeypatch):
    """Model an installed distribution location without invoking pip or imports."""

    artifact = evidence.VerifyWheel(artifactCase, "candidate")
    site = tmpPath / "site-packages"
    package = site / "fuzzyroutines"
    package.mkdir(parents=True)

    with zipfile.ZipFile(artifact["wheel"]) as archive:
        for relative in artifact["package_file_sha256"]:
            (site / relative).write_bytes(archive.read(relative))

    distribution = types.SimpleNamespace(version=artifact["version"], locate_file=lambda name: site / name)
    monkeypatch.setattr(evidence.importlib.metadata, "distribution", lambda name: distribution)
    monkeypatch.setattr(evidence.sysconfig, "get_path", lambda name: str(site))
    monkeypatch.setattr(evidence.importlib.util, "find_spec", lambda name: types.SimpleNamespace(origin=str(package / "__init__.py")) if name == "fuzzyroutines" else None)

    for name in tuple(sys.modules):
        if name == "fuzzyroutines" or name.startswith("fuzzyroutines."):
            monkeypatch.delitem(sys.modules, name)

    return artifact, package


def test_InstalledGuardDoesNotImportPackageAndChecksAllFiles(installedCase):
    """Exact fixture bytes pass and subsequent package tampering is rejected."""

    artifact, package = installedCase
    actual = evidence.VerifyInstalledPackage(artifact)
    assert actual["package_origin"] == str(package / "__init__.py")
    assert "fuzzyroutines" not in sys.modules
    (package / "__init__.py").write_text("tampered = True\n")

    with pytest.raises(ValueError, match="bytes"):
        evidence.VerifyInstalledPackage(artifact)


def test_InstalledGuardRejectsExtraSourceAndForeignImport(installedCase, monkeypatch):
    """Untracked installed code and neighboring checkout resolution both fail."""

    artifact, package = installedCase
    extra = package / "extra.py"
    extra.write_bytes(b"")

    with pytest.raises(ValueError, match="file sets"):
        evidence.VerifyInstalledPackage(artifact)

    extra.unlink()
    monkeypatch.setattr(evidence.importlib.util, "find_spec", lambda name: types.SimpleNamespace(origin=str(package.parent / "source/__init__.py")))

    with pytest.raises(ValueError, match="resolved package"):
        evidence.VerifyInstalledPackage(artifact)


def test_InstalledGuardRejectsLoadedForeignSubmoduleAndOptionalDependency(installedCase, monkeypatch):
    """Loaded core origins and optional-dependency policy remain independently guarded."""

    artifact, package = installedCase
    monkeypatch.setitem(sys.modules, "fuzzyroutines.foreign", types.SimpleNamespace(__file__=str(package.parent / "foreign.py")))

    with pytest.raises(ValueError, match="loaded package"):
        evidence.VerifyInstalledPackage(artifact)

    monkeypatch.delitem(sys.modules, "fuzzyroutines.foreign")
    monkeypatch.setattr(evidence.importlib.util, "find_spec", lambda name: types.SimpleNamespace(origin=str(package / "__init__.py")))

    with pytest.raises(ValueError, match="optional NumPy"):
        evidence.VerifyInstalledPackage(artifact)

    assert evidence.VerifyInstalledPackage(artifact, requireNoNumpy=False)["package_version"] == artifact["version"]


def test_HarnessRequiresExactCleanCommitAndExecutionBytes(artifactCase):
    """Unpublished status is not inferred; exact local revision and clean state are verified."""

    root = Path(artifactCase["repository"])
    commit = artifactCase["candidate"]["source_commit"]
    result = evidence.VerifyHarness(root, commit, ("fuzzyroutines/__init__.py",))
    assert result["dirty"] is False and result["source_commit"] == commit

    with pytest.raises(ValueError, match="pinned commit"):
        evidence.VerifyHarness(root, "0" * 40)

    (root / "untracked.txt").write_text("not part of the benchmark commit")

    with pytest.raises(ValueError, match="must be clean"):
        evidence.VerifyHarness(root, commit)
