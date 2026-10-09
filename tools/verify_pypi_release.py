# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Compare published PyPI bytes with the exact approved CI distributions.

Run after protected publication with --version, --artifact-directory and a new
--output-directory. The command reads public PyPI release metadata and downloads
its wheel/sdist, verifies names, sizes and SHA-256 against local CI candidates,
and writes a JSON report plus a hash-pinned pip requirement. It never publishes,
changes candidates or installs packages. Any mismatch exits nonzero; only a
not-yet-visible release/file listing is retried for bounded CDN propagation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


class PublicationNotVisible(LookupError):
    """Indicate that a valid published file listing is still incomplete."""


def CandidateFiles(artifactDirectory, releaseVersion):
    """Require exactly the approved stable wheel and sdist and hash their bytes."""

    if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", releaseVersion) is None:
        raise ValueError("expected a stable X.Y.Z version")

    paths = sorted((*artifactDirectory.glob("*.whl"), *artifactDirectory.glob("*.tar.gz")))
    expectedNames = {
        f"fuzzyroutines-{releaseVersion}-py3-none-any.whl",
        f"fuzzyroutines-{releaseVersion}.tar.gz",
    }
    if {path.name for path in paths} != expectedNames:
        raise ValueError("candidate directory must contain exactly the versioned wheel and sdist")

    return {
        path.name: {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "size": path.stat().st_size}
        for path in paths
    }


def ValidateMetadata(metadata, candidates, releaseVersion):
    """Bind PyPI's release listing to the candidate identity before any download."""

    if metadata.get("info", {}).get("version") != releaseVersion:
        raise ValueError("PyPI release version does not match the approved candidate")

    entries = metadata.get("urls", [])
    names = [entry["filename"] for entry in entries]
    if len(names) != len(set(names)) or set(names) - candidates.keys():
        raise ValueError("unexpected or duplicate published distribution")

    for entry in entries:
        expected = candidates[entry["filename"]]
        if entry.get("yanked") or entry.get("digests", {}).get("sha256") != expected["sha256"] or entry.get("size") != expected["size"]:
            raise ValueError("published metadata does not match the approved artifact")

        url = urllib.parse.urlsplit(entry["url"])
        if url.scheme != "https" or url.netloc != "files.pythonhosted.org":
            raise ValueError("unexpected PyPI distribution host")

    if set(names) != candidates.keys():
        raise PublicationNotVisible("published distribution listing is not complete yet")

    return {entry["filename"]: entry["url"] for entry in entries}


def FetchMetadata(releaseVersion, candidates, attempts, *, openUrl=urllib.request.urlopen, pause=time.sleep):
    """Retry only initial release visibility; reject contradictory metadata immediately."""

    metadataUrl = f"https://pypi.org/pypi/fuzzyroutines/{releaseVersion}/json"
    for attempt in range(attempts):
        try:
            with openUrl(metadataUrl, timeout=30) as response:
                metadata = json.load(response)
            return metadata, ValidateMetadata(metadata, candidates, releaseVersion)

        except urllib.error.HTTPError as error:
            if error.code != 404 or attempt + 1 == attempts:
                raise

        except PublicationNotVisible:
            if attempt + 1 == attempts:
                raise

        pause(5)

    raise ValueError("attempts must be positive")


def VerifyPublishedRelease(artifactDirectory, outputDirectory, releaseVersion, attempts=12, *, openUrl=urllib.request.urlopen, pause=time.sleep):
    """Verify actual downloaded bytes and emit evidence for a clean pip installation."""

    if outputDirectory.exists():
        raise FileExistsError("verification output directory must be new")

    candidates = CandidateFiles(artifactDirectory, releaseVersion)
    metadata, urls = FetchMetadata(releaseVersion, candidates, attempts, openUrl=openUrl, pause=pause)
    outputDirectory.mkdir(parents=True)

    for name, url in urls.items():
        expected = candidates[name]
        with openUrl(url, timeout=30) as response:
            payload = response.read(expected["size"] + 1)

        if len(payload) != expected["size"] or hashlib.sha256(payload).hexdigest() != expected["sha256"]:
            raise ValueError(f"downloaded bytes differ from the approved candidate: {name}")

        (outputDirectory / name).write_bytes(payload)

    wheelName = next(name for name in candidates if name.endswith(".whl"))
    requirement = f"fuzzyroutines=={releaseVersion} --hash=sha256:{candidates[wheelName]['sha256']}\n"
    (outputDirectory / "requirements-published.txt").write_text(requirement, encoding="utf-8")
    (outputDirectory / "pypi-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    report = {"version": releaseVersion, "releaseUrl": f"https://pypi.org/project/fuzzyroutines/{releaseVersion}/", "artifacts": candidates}
    (outputDirectory / "published-artifacts.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def Main(arguments=None):
    """Parse the read-only post-publication verifier and print its hash evidence."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, dest="releaseVersion")
    parser.add_argument("--artifact-directory", required=True, type=Path, dest="artifactDirectory")
    parser.add_argument("--output-directory", required=True, type=Path, dest="outputDirectory")
    options = parser.parse_args(arguments)
    print(json.dumps(VerifyPublishedRelease(options.artifactDirectory, options.outputDirectory, options.releaseVersion), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
