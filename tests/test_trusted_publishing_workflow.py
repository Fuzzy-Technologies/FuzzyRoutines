# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Security invariants for the PyPI Trusted Publishing workflow."""

from pathlib import Path
import os
import subprocess
import textwrap

import pytest

PROJECTROOT = Path(__file__).parents[1]
WORKFLOWPATH = PROJECTROOT / ".github" / "workflows" / "release-pypi.yml"
RUNBOOKPATH = PROJECTROOT / "docs" / "trusted-publishing-runbook.md"


def WorkflowText():
    """Return the canonical workflow text for structural assertions."""

    return WORKFLOWPATH.read_text(encoding="utf-8")


def test_PublishIdentityIsJobScopedAndTokenless():
    """Publication permissions remain job-scoped and tokenless."""

    workflowText = WorkflowText()
    publishText = workflowText.split("  publish-pypi:", maxsplit=1)[1]

    assert "permissions:\n      id-token: write" in publishText
    assert "environment:\n      name: pypi" in publishText
    assert "pypa/gh-action-pypi-publish@release/v1" in publishText
    assert "password:" not in workflowText
    assert "PYPI_TOKEN" not in workflowText
    assert "secrets." not in workflowText


def test_PublishCannotRunForPullRequestOrManualDispatch():
    """Only protected tag pushes can reach the gated publication job."""

    workflowText = WorkflowText()
    publishText = workflowText.split("  publish-pypi:", maxsplit=1)[1]

    requiredCondition = (
        "github.event_name == 'push' &&\n"
        "      startsWith(github.ref, 'refs/tags/v') &&\n"
        "      vars.PYPI_TRUSTED_PUBLISHING_ENABLED == 'true'"
    )
    assert requiredCondition in publishText
    assert "pull_request:" in workflowText
    assert "workflow_dispatch:" in workflowText
    assert "needs:\n      - verify-distributions\n      - attest-provenance" in publishText


def test_ReleaseTagAndPackageVersionAreFailClosed():
    """Stable annotated tags must match the canonical package version."""

    workflowText = WorkflowText()

    assert "^refs/tags/v([0-9]+)" in workflowText
    assert 'git cat-file -t "$GITHUB_REF_NAME"' in workflowText
    assert 'metadata["project"]["version"]' in workflowText
    assert 'packageVersion" != "$tagVersion' in workflowText


@pytest.mark.parametrize("tagKind", ["annotated", "lightweight", "wrong-commit", "wrong-version"])
def test_ReleaseValidationRestoresCheckoutTagWithoutWeakeningChecks(tmpPath, tagKind):
    """Repair a peeled local ref while rejecting invalid protected remote tags."""

    remotePath = tmpPath / "remote"
    checkoutPath = tmpPath / "checkout"
    remotePath.mkdir()

    def Git(*arguments, cwd=remotePath):
        """Run Git against isolated repositories without external network access."""

        return subprocess.run(
            ["git", *arguments], cwd=cwd, check=True, capture_output=True, text=True,
        ).stdout.strip()

    Git("init")
    Git("config", "user.name", "Release test")
    Git("config", "user.email", "release-test@example.invalid")
    (remotePath / "pyproject.toml").write_text('[project]\nversion = "2.0.0"\n')
    Git("add", "pyproject.toml")
    Git("commit", "-m", "Release fixture")
    eventCommit = Git("rev-parse", "HEAD")

    if tagKind == "wrong-commit":
        Git("commit", "--allow-empty", "-m", "Different commit")

    tagName = "v2.0.1" if tagKind == "wrong-version" else "v2.0.0"
    tagRef = f"refs/tags/{tagName}"
    if tagKind == "lightweight":
        Git("tag", tagName)
    else:
        Git("tag", "-a", tagName, "-m", "Release fixture")
    remoteObject = Git("rev-parse", tagRef)
    Git("clone", "--no-local", str(remotePath), str(checkoutPath))
    Git("checkout", "--detach", eventCommit, cwd=checkoutPath)
    # Reproduce actions/checkout's second fetch, which peels the local tag.
    Git("fetch", "--no-tags", "origin", f"+{eventCommit}:{tagRef}", cwd=checkoutPath)
    assert Git("cat-file", "-t", tagRef, cwd=checkoutPath) == "commit"

    validationText = WorkflowText().split(
        "      - name: Validate protected release tag and version", maxsplit=1,
    )[1].split("      - name:", maxsplit=1)[0]
    script = textwrap.dedent(validationText.split("        run: |\n", maxsplit=1)[1])
    environment = {
        **os.environ, "GITHUB_REF": tagRef, "GITHUB_REF_NAME": tagName,
        "GITHUB_SHA": eventCommit,
    }
    result = subprocess.run(
        ["bash", "-c", script], cwd=checkoutPath, env=environment,
        capture_output=True, text=True,
    )
    assert (result.returncode == 0) == (tagKind == "annotated"), result.stderr
    assert Git("rev-parse", tagRef) == remoteObject
    assert Git("rev-parse", "HEAD", cwd=checkoutPath) == eventCommit


def test_BuildEvidencePrecedesPublishing():
    """Reproducible candidates and full CI evidence precede publication."""

    workflowText = WorkflowText()

    for evidence in (
        "python -m tools.reproducible_artifacts --output-directory dist",
        "-r requirements-build.txt",
        "python -m twine check --strict dist/*.whl dist/*.tar.gz",
        "sha256sum --check SHA256SUMS",
        "python -m tools.test_runner --jobs auto --timeout 60",
        "actions/attest-build-provenance@v3",
    ):
        assert evidence in workflowText

    assert 'python-version: ["3.13", "3.14"]' in workflowText


def test_RunbookDefinesExternalProtectionWithoutSecrets():
    """The runbook distinguishes platform protection from source mechanics."""

    runbookText = RUNBOOKPATH.read_text(encoding="utf-8")

    for requiredText in (
        "required reviewers",
        "tag ruleset",
        "release-pypi.yml",
        "Fuzzy-Technologies",
        "FuzzyRoutines",
        "Environment",
        "`pypi`",
        "annotated tag",
        "PYPI_TRUSTED_PUBLISHING_ENABLED",
    ):
        assert requiredText in runbookText

    assert "Do not create a `PYPI_TOKEN`" in runbookText


def test_PostPublicationVerificationHasNoPublishingIdentity():
    """Only a successful publish enables the read-only consumer verification matrix."""

    verification = WorkflowText().split("  verify-published:", maxsplit=1)[1]
    assert "if: needs.publish-pypi.result == 'success'" in verification
    assert "needs: publish-pypi" in verification
    assert "permissions:\n      contents: read" in verification
    assert "id-token:" not in verification
    assert "--require-hashes -r published-evidence/requirements-published.txt" in verification
    assert "--index-url https://pypi.org/simple" in verification
    assert "tools/verify_installed_executables.py" in verification
    assert 'python-version: ["3.13", "3.14"]' in verification
