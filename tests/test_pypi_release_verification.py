# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Offline contracts for post-publication identity and actual-byte verification."""

import copy
import io
import json
import subprocess
import textwrap
import urllib.error
from pathlib import Path

import pytest

from tools.verify_pypi_release import (
    CandidateFiles,
    FetchMetadata,
    ValidateMetadata,
    VerifyPublishedRelease,
)


def ReleaseFixture(tmpPath):
    """Create two distinct candidate payloads and their independent remote fixture."""

    artifacts = tmpPath / "dist"
    artifacts.mkdir()
    (artifacts / "fuzzyroutines-2.0.0-py3-none-any.whl").write_bytes(b"wheel fixture")
    (artifacts / "fuzzyroutines-2.0.0.tar.gz").write_bytes(b"source fixture")
    candidates = CandidateFiles(artifacts, "2.0.0")
    metadata = {"info": {"version": "2.0.0"}, "urls": [
        {"filename": name, "size": item["size"], "digests": {"sha256": item["sha256"]}, "yanked": False, "url": f"https://files.pythonhosted.org/packages/{name}"}
        for name, item in candidates.items()
    ]}
    return artifacts, candidates, metadata


def test_PublishedBytesAndPipRequirementMatchApprovedCandidates(tmpPath):
    """Hash both downloads and constrain the later index-based pip installation."""

    artifacts, candidates, metadata = ReleaseFixture(tmpPath)

    def OpenUrl(url, timeout):
        """Serve public-API and artifact responses entirely from offline fixtures."""

        return io.BytesIO(json.dumps(metadata).encode() if url.endswith("/json") else (artifacts / url.rsplit("/", 1)[1]).read_bytes())

    output = tmpPath / "verified"
    report = VerifyPublishedRelease(artifacts, output, "2.0.0", openUrl=OpenUrl)
    assert report["artifacts"] == candidates
    assert (output / "fuzzyroutines-2.0.0.tar.gz").read_bytes() == b"source fixture"
    assert (output / "requirements-published.txt").read_text() == "fuzzyroutines==2.0.0 --hash=sha256:" + candidates["fuzzyroutines-2.0.0-py3-none-any.whl"]["sha256"] + "\n"


@pytest.mark.parametrize("defect", ("version", "hash", "size", "yanked", "host", "duplicate", "extra"))
def test_ContradictoryPublishedMetadataFailsClosed(tmpPath, defect):
    """Reject wrong identity and distribution metadata before downloading bytes."""

    _, candidates, metadata = ReleaseFixture(tmpPath)
    entry = metadata["urls"][0]
    if defect == "version":
        metadata["info"]["version"] = "1.0.3"

    elif defect == "hash":
        entry["digests"]["sha256"] = "0" * 64

    elif defect == "size":
        entry["size"] += 1

    elif defect == "yanked":
        entry["yanked"] = True

    elif defect == "host":
        entry["url"] = "https://example.org/package.whl"

    elif defect == "duplicate":
        metadata["urls"].append(copy.deepcopy(entry))

    else:
        extra = copy.deepcopy(entry)
        extra["filename"] = "unexpected.whl"
        metadata["urls"].append(extra)

    with pytest.raises(ValueError):
        ValidateMetadata(metadata, candidates, "2.0.0")


def test_CorrectMetadataCannotHideTamperedDownloadedBytes(tmpPath):
    """Remote listing hashes alone cannot establish artifact-byte equality."""

    artifacts, _, metadata = ReleaseFixture(tmpPath)

    def OpenUrl(url, timeout):
        """Return truthful metadata followed by different same-length bytes."""

        return io.BytesIO(json.dumps(metadata).encode() if url.endswith("/json") else b"x" * (artifacts / url.rsplit("/", 1)[1]).stat().st_size)

    output = tmpPath / "verified"
    with pytest.raises(ValueError, match="downloaded bytes"):
        VerifyPublishedRelease(artifacts, output, "2.0.0", openUrl=OpenUrl)
    assert not (output / "requirements-published.txt").exists()


def test_OnlyVisibilityDelayIsRetriedAndBounded(tmpPath):
    """Allow initial propagation but do not turn a mismatch into a later success."""

    _, candidates, metadata = ReleaseFixture(tmpPath)
    incomplete = copy.deepcopy(metadata)
    incomplete["urls"].pop()
    responses = [None, incomplete, metadata]
    pauses = []

    def OpenUrl(url, timeout):
        """Simulate a missing release, partial file list and complete publication."""

        response = responses.pop(0)
        if response is None:
            raise urllib.error.HTTPError(url, 404, "pending", {}, None)
        return io.BytesIO(json.dumps(response).encode())

    result, _ = FetchMetadata("2.0.0", candidates, 3, openUrl=OpenUrl, pause=pauses.append)
    assert result == metadata and pauses == [5, 5]
    with pytest.raises(ValueError, match="positive"):
        FetchMetadata("2.0.0", candidates, 0, openUrl=OpenUrl)


def test_CandidateIdentityAndExistingEvidenceAreProtected(tmpPath):
    """Refuse prereleases, unexpected candidate files and evidence replacement."""

    artifacts, _, _ = ReleaseFixture(tmpPath)
    with pytest.raises(ValueError, match="stable"):
        CandidateFiles(artifacts, "2.0.0.dev0")
    with pytest.raises(FileExistsError):
        VerifyPublishedRelease(artifacts, artifacts, "2.0.0")
    (artifacts / "extra.whl").write_bytes(b"extra")
    with pytest.raises(ValueError, match="exactly"):
        CandidateFiles(artifacts, "2.0.0")


def test_MetadataMismatchAndExhaustedVisibilityNeverReportSuccess(tmpPath):
    """Bound the retry path and never retry contradictory release identities."""

    _, candidates, metadata = ReleaseFixture(tmpPath)
    metadata["urls"] = []
    calls = []

    def OpenUrl(url, timeout):
        """Count offline requests for incomplete or contradictory responses."""

        calls.append(url)
        return io.BytesIO(json.dumps(metadata).encode())

    with pytest.raises(LookupError):
        FetchMetadata("2.0.0", candidates, 2, openUrl=OpenUrl, pause=lambda delay: None)
    assert len(calls) == 2
    calls.clear()
    metadata["info"]["version"] = "1.0.3"
    with pytest.raises(ValueError):
        FetchMetadata("2.0.0", candidates, 12, openUrl=OpenUrl, pause=lambda delay: None)
    assert len(calls) == 1


@pytest.mark.parametrize("defect", (None, "extra-wheel", "missing-sdist", "tampered", "existing-upload"))
def test_PublishingStagesOnlyVerifiedDistributions(tmpPath, defect):
    """Execute the production staging script without credentials or network access."""

    artifacts, candidates, _ = ReleaseFixture(tmpPath)
    manifest = "".join(f"{item['sha256']}  {name}\n" for name, item in candidates.items())
    (artifacts / "SHA256SUMS").write_text(manifest)
    (artifacts / "reproducibility.json").write_text('{"independent_builds": 2}\n')
    (artifacts / "source-revision.txt").write_text("approved revision\n")
    upload = tmpPath / "pypi-upload"

    if defect == "extra-wheel":
        (artifacts / "unexpected.whl").write_bytes(b"unapproved wheel")

    elif defect == "missing-sdist":
        (artifacts / "fuzzyroutines-2.0.0.tar.gz").unlink()

    elif defect == "tampered":
        (artifacts / "fuzzyroutines-2.0.0-py3-none-any.whl").write_bytes(b"tampered")

    elif defect == "existing-upload":
        upload.mkdir()
        (upload / "unapproved.whl").write_bytes(b"stale artifact")

    before = {path.name: path.read_bytes() for path in artifacts.iterdir()}
    workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/release-pypi.yml").read_text()
    preparation = workflow.split("- name: Prepare distribution-only upload directory\n", 1)[1]
    script = textwrap.dedent(preparation.split("run: |\n", 1)[1].split("      - name:", 1)[0])
    publication = workflow.split("- name: Publish with PyPI Trusted Publishing\n", 1)[1].split("\n  verify-published:", 1)[0]
    assert "packages-dir: pypi-upload" in publication, "Publisher must consume the isolated distribution directory"
    result = subprocess.run(["bash", "-c", script], cwd=tmpPath, capture_output=True, text=True, check=False)
    assert {path.name: path.read_bytes() for path in artifacts.iterdir()} == before, "Staging must preserve all original evidence"

    if defect is not None:
        assert result.returncode != 0, f"Unsafe release staging must fail: {defect}"
        assert not upload.exists() or {path.name for path in upload.iterdir()} == {"unapproved.whl"}, "Failed staging must not prepare an upload"

    else:
        assert result.returncode == 0, result.stderr
        assert {path.name for path in upload.iterdir()} == set(candidates), "PyPI must receive only the wheel and sdist"
        assert all((upload / name).read_bytes() == before[name] for name in candidates), "Staging must retain the approved bytes"
