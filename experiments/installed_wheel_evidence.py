# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Bind installed benchmark packages to wheel bytes and declared Git sources.

Artifact provenance JSON is supporting evidence, not a cryptographic attestation.
This module never imports the measured package, installs dependencies, changes
sys.path or starts a timed workload. Its guards fail before accepting evidence.
"""

import email.parser
import hashlib
import importlib.metadata
import importlib.util
import json
import re
import subprocess
import sys
import sysconfig
import tomllib
import zipfile
from pathlib import Path


def Digest(data):
    """Return a reproducible artifact identity."""

    return hashlib.sha256(data).hexdigest()


def Git(config, *arguments):
    """Read immutable repository objects without changing the checkout."""

    return subprocess.check_output(["git", "-C", config["repository"], *arguments])


def VerifyCandidateArtifact(config, artifact, provenance, wheelPath):
    """Bind a CI archive to its run and distinguish the built merge from PR head.

    GitHub's run head identifies the submitted branch commit; a pull-request
    checkout can instead build its synthetic merge. The archive records that
    actual source revision. Mutable PR head/base snapshots are never consulted.
    """

    if (provenance["conclusion"] != "success" or provenance["status"] != "completed"
            or provenance["html_url"] != artifact["source_evidence_url"]
            or provenance["path"] != ".github/workflows/package-build-install.yml"
            or provenance["name"] != "Package build and clean-install"
            or not re.fullmatch("[0-9a-f]{40}", provenance["head_sha"])):
        raise ValueError("candidate workflow evidence does not identify a successful package run")

    metadataPath = Path(artifact["artifact_metadata_json"])
    metadata = json.loads(metadataPath.read_text())
    archivePath = Path(artifact["artifact_archive"])
    archiveDigest = Digest(archivePath.read_bytes())

    if (metadata["workflow_run"]["id"] != provenance["id"]
            or metadata["workflow_run"]["head_sha"] != provenance["head_sha"]
            or metadata["name"] not in ("package-artifacts-python-3.13", "package-artifacts-python-3.14")):
        raise ValueError("candidate artifact belongs to a different workflow run or package job")

    if metadata["digest"] != "sha256:" + archiveDigest:
        raise ValueError("candidate artifact archive digest mismatch")

    with zipfile.ZipFile(archivePath) as archive:
        required = ("source-revision.txt", "reproducibility.json", "SHA256SUMS", wheelPath.name)

        if any(archive.namelist().count(name) != 1 for name in required):
            raise ValueError("candidate archive must contain each build record and wheel exactly once")

        sourceRecord = archive.read("source-revision.txt")
        reproducibilityBytes = archive.read("reproducibility.json")
        reproducibility = json.loads(reproducibilityBytes)
        checksumBytes = archive.read("SHA256SUMS")
        checksums = [line.split() for line in checksumBytes.decode().splitlines()]
        wheelChecksums = [parts[0] for parts in checksums if len(parts) == 2 and parts[1] == wheelPath.name]

        if sourceRecord.decode().strip() != artifact["source_commit"] or reproducibility["source_revision"] != artifact["source_commit"]:
            raise ValueError("candidate archive source records differ from the declared built source")

        buildHashes = reproducibility["artifacts"][wheelPath.name]

        if (reproducibility["independent_builds"] != 2
                or buildHashes["first_sha256"] != artifact["wheel_sha256"]
                or buildHashes["second_sha256"] != artifact["wheel_sha256"]
                or wheelChecksums != [artifact["wheel_sha256"]]):
            raise ValueError("candidate build checksums do not identify the measured wheel")

        if archive.read(wheelPath.name) != wheelPath.read_bytes():
            raise ValueError("supplied wheel differs from the candidate artifact archive")

    parents = Git(config, "show", "-s", "--format=%P", artifact["source_commit"]).decode().strip().split()
    sourceKind = "workflow_head"

    if artifact["source_commit"] != provenance["head_sha"]:
        if provenance["event"] != "pull_request" or len(parents) != 2 or parents[1] != provenance["head_sha"]:
            raise ValueError("built source is not the workflow head or its pull-request merge")

        sourceKind = "pull_request_merge"

    return {"workflow_run_id": provenance["id"], "workflow_head_sha": provenance["head_sha"],
            "built_source_commit": artifact["source_commit"], "built_source_kind": sourceKind,
            "built_source_parents": parents, "artifact_id": metadata["id"],
            "artifact_archive_sha256": archiveDigest, "artifact_metadata_json_sha256": Digest(metadataPath.read_bytes()),
            "source_revision_record_sha256": Digest(sourceRecord), "reproducibility_json_sha256": Digest(reproducibilityBytes),
            "checksums_record_sha256": Digest(checksumBytes)}


def VerifyWheel(config, label):
    """Bind downloaded artifact bytes, upstream provenance, version, and Git source."""

    artifact = config[label]
    path = Path(artifact["wheel"]).resolve()

    if not re.fullmatch("[0-9a-f]{64}", artifact["wheel_sha256"]) or not re.fullmatch("[0-9a-f]{40}", artifact["source_commit"]):
        raise ValueError("pin full wheel SHA256 and source commit identifiers")

    if Digest(path.read_bytes()) != artifact["wheel_sha256"]:
        raise ValueError(f"wheel digest mismatch: {label}")

    provenancePath = Path(artifact["provenance_json"])
    provenance = json.loads(provenancePath.read_text())
    candidateEvidence = {}

    if label == "baseline":
        if provenance["info"]["version"] != artifact["version"] or artifact["source_evidence_url"] != f"https://pypi.org/pypi/fuzzyroutines/{artifact['version']}/json":
            raise ValueError("PyPI release JSON version mismatch")

        matches = [item for item in provenance["urls"] if item["filename"] == path.name and item["digests"]["sha256"] == artifact["wheel_sha256"]]

        if len(matches) != 1:
            raise ValueError("the baseline wheel is not identified by its PyPI release JSON")

    else:
        candidateEvidence = {"candidate_build_evidence": VerifyCandidateArtifact(config, artifact, provenance, path)}

    project = tomllib.loads(Git(config, "show", artifact["source_commit"] + ":pyproject.toml").decode())["project"]

    with zipfile.ZipFile(path) as wheel:
        metadataName = next(name for name in wheel.namelist() if name.endswith(".dist-info/METADATA"))
        metadata = email.parser.Parser().parsestr(wheel.read(metadataName).decode())

        if metadata["Version"] != artifact["version"] or metadata["Name"].lower() != "fuzzyroutines":
            raise ValueError("wheel distribution identity mismatch")

        if metadata["Version"] != project["version"] or metadata["Name"].lower() != project["name"].lower():
            raise ValueError("wheel distribution identity differs from committed project metadata")

        requirements = metadata.get_all("Requires-Dist", [])

        if any("extra ==" not in requirement for requirement in requirements):
            raise ValueError("default scalar wheel unexpectedly declares a mandatory dependency")

        names = sorted(name for name in wheel.namelist() if name.startswith("fuzzyroutines/") and name.endswith((".py", "/py.typed")))
        tracked = Git(config, "ls-tree", "-r", "--name-only", artifact["source_commit"], "--", "fuzzyroutines").decode().splitlines()
        expected = sorted(name for name in tracked if name.endswith((".py", "/py.typed")))

        if names != expected:
            raise ValueError("wheel/source package file sets differ")

        fileHashes = {}

        for name in names:
            data = wheel.read(name)

            if data != Git(config, "show", artifact["source_commit"] + ":" + name):
                raise ValueError(f"wheel Python bytes differ from declared source: {name}")

            fileHashes[name] = Digest(data)

    return {**artifact, **candidateEvidence, "wheel": str(path), "wheel_python_source_matches_commit": True,
            "package_file_sha256": fileHashes, "declared_requires_dist": requirements,
            "provenance_json_sha256": Digest(provenancePath.read_bytes())}


def VerifyInstalledPackage(artifact, requireNoNumpy=True):
    """Check installed bytes and import origins without importing the measured package.

    The artifact must be the output of `VerifyWheel`. Scalar comparisons reject
    even an available NumPy installation; optional batch comparisons explicitly
    disable only that extra-dependency check. Source/editable imports fail.
    """

    distribution = importlib.metadata.distribution("fuzzyroutines")
    packageDirectory = Path(distribution.locate_file("fuzzyroutines")).resolve()
    expectedOrigin = packageDirectory / "__init__.py"
    installRoots = {Path(sysconfig.get_path(name)).resolve() for name in ("purelib", "platlib")}

    if not any(packageDirectory.is_relative_to(root) for root in installRoots) or distribution.version != artifact["version"]:
        raise ValueError("package origin/version is outside the isolated environment")

    specification = importlib.util.find_spec("fuzzyroutines")

    if specification is None or specification.origin is None or Path(specification.origin).resolve() != expectedOrigin:
        raise ValueError("resolved package is not the installed wheel")

    if requireNoNumpy and importlib.util.find_spec("numpy") is not None:
        raise ValueError("scalar comparison must not install optional NumPy")

    fileHashes = artifact["package_file_sha256"]
    installedNames = sorted(str(path.relative_to(packageDirectory.parent)) for path in packageDirectory.rglob("*") if path.is_file() and (path.suffix == ".py" or path.name == "py.typed"))

    if installedNames != sorted(fileHashes):
        raise ValueError("installed and wheel package file sets differ")

    for name, digest in fileHashes.items():
        if Digest(Path(distribution.locate_file(name)).read_bytes()) != digest:
            raise ValueError("installed package bytes differ from the verified wheel")

    loadedOrigins = {}

    for name, module in tuple(sys.modules.items()):
        if name == "fuzzyroutines" or name.startswith("fuzzyroutines."):
            origin = Path(module.__file__).resolve()

            if not origin.is_relative_to(packageDirectory):
                raise ValueError("loaded package module is outside the installed wheel")

            loadedOrigins[name] = str(origin)

    return {"package_origin": str(expectedOrigin), "package_version": distribution.version,
            "loaded_module_origins": loadedOrigins, "package_file_sha256": fileHashes}


def VerifyHarness(root, expectedCommit, paths=()):
    """Require a clean exact checkout and hash each declared execution source.

    Public availability of the pinned commit is established by the release
    coordinator's fetch. This local check proves the actual checkout and bytes,
    not that an arbitrary local Git object has been published remotely.
    """

    config = {"repository": str(root)}

    if not re.fullmatch("[0-9a-f]{40}", expectedCommit) or Git(config, "rev-parse", "HEAD").decode().strip() != expectedCommit:
        raise ValueError("harness checkout does not match the pinned commit")

    if Git(config, "status", "--porcelain").strip():
        raise ValueError("benchmark harness checkout must be clean")

    hashes = {}

    for relative in paths:
        actual = (Path(root) / relative).read_bytes()

        if actual != Git(config, "show", expectedCommit + ":" + relative):
            raise ValueError("harness file differs from its declared Git object")

        hashes[relative] = Digest(actual)

    return {"source_commit": expectedCommit, "dirty": False, "files_sha256": hashes}
