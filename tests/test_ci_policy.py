# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Fail-closed CI scope selection and exact-revision evidence contracts."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tools.ci_policy import (
    DOCUMENTATION_TESTS,
    PUBLIC_TESTS,
    TOOL_TESTS,
    Git,
    SelectPolicy,
    Trailers,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRACKED = {
    "tests/test_ci_policy.py", "tests/test_membership_function_contracts.py",
    "tests/test_trusted_publishing_workflow.py", "tests/test_pr_merge_links.py",
    *DOCUMENTATION_TESTS, *PUBLIC_TESTS, *TOOL_TESTS.values(),
}


def Event(action="synchronize", base="develop"):
    """Return minimal PR metadata without pretending to supply Git evidence."""

    return {"action": action, "pull_request": {"base": {"ref": base}}}


@pytest.mark.parametrize("eventName,event,trailers", [
    ("pull_request", Event("opened"), {}),
    ("pull_request", Event(base="master"), {}),
    ("pull_request", Event(), {"ci-full": "true"}),
    ("workflow_dispatch", {}, {}),
    ("push", {"ref": "refs/heads/master"}, {}),
])
def test_ExplicitFullTriggersCannotBecomeFocused(eventName, event, trailers):
    """Preserve opening, correction and release full-gate requirements."""

    policy = SelectPolicy(eventName, event, ["fuzzyroutines/membership.py"], trailers, TRACKED)

    assert policy["full"] is True
    assert policy["documentation"] is True
    assert policy["package"] is True


@pytest.mark.parametrize("action", ["synchronize", "reopened"])
def test_OrdinaryUpdatesRequireReviewedCodeScope(action):
    """Reject missing coverage declarations instead of silently skipping tests."""

    with pytest.raises(ValueError, match="reviewed CI-Tests"):
        SelectPolicy("pull_request", Event(action), ["fuzzyroutines/membership.py"], {}, TRACKED)


@pytest.mark.parametrize("path", [
    "--collect-only", "/tmp/test_fake.py", "tests/../test_fake.py", "tests/test_missing.py",
    "tests/test_ci_policy.py::test_Fake", "tests/test_ci_policy.py;exit",
])
def test_InvalidPathsCannotBecomePytestOptions(path):
    """Allow only existing repository test files, never options or shell syntax."""

    with pytest.raises(ValueError, match="Unsafe or missing"):
        SelectPolicy("pull_request", Event(), ["tools/ci_policy.py"], {"ci-tests": path}, TRACKED)


def test_LibraryScopeIncludesPublicContractsAndChangedTests():
    """Supplement a reviewed selection with changed tests and public imports."""

    policy = SelectPolicy(
        "pull_request", Event(),
        ["fuzzyroutines/membership.py", "tests/test_membership_function_contracts.py"],
        {"ci-tests": "tests/test_ci_policy.py"}, TRACKED,
    )

    assert policy["mode"] == "focused"
    assert set(PUBLIC_TESTS) <= set(policy["tests"])
    assert "tests/test_membership_function_contracts.py" in policy["tests"]
    assert policy["documentation"] is False
    assert policy["package"] is False


def test_DocumentationScopeBuildsWithoutRunningWholeMathSuite():
    """Use documentation contracts automatically for authored prose changes."""

    policy = SelectPolicy("pull_request", Event(), ["docs/guide.md"], {}, TRACKED)

    assert policy["full"] is False
    assert policy["documentation"] is True
    assert set(DOCUMENTATION_TESTS) <= set(policy["tests"])


def test_ToolingAndWorkflowScopesRetainSafetyTests():
    """Always add tested workflow and task-closing policy invariants."""

    policy = SelectPolicy(
        "pull_request", Event(), ["tools/pr_merge_links.py", ".github/workflows/release-pypi.yml"],
        {"ci-tests": "tests/test_ci_policy.py"}, TRACKED,
    )

    assert {"tests/test_pr_merge_links.py", "tests/test_trusted_publishing_workflow.py"} <= set(policy["tests"])


def test_EmptyDiffUnsupportedEventAndMissingContractsFailClosed():
    """Treat incomplete metadata and missing mandatory tests as failures."""

    cases = [
        ("pull_request", Event(), [], TRACKED),
        ("schedule", {}, ["README.md"], TRACKED),
        ("push", {"ref": "refs/heads/develop"}, [], TRACKED),
        ("pull_request", Event(), ["README.md"], set()),
    ]

    for eventName, event, changes, tracked in cases:
        with pytest.raises(ValueError):
            SelectPolicy(eventName, event, changes, {}, tracked)


def test_TrailersUseGitFooterParsingAndRejectAmbiguity():
    """Ignore incidental prose and reject repeated or malformed control values."""

    assert Trailers("Describe CI-Full: true inside a sentence\n") == {}
    assert Trailers("Update tests\n\nCI-Tests: tests/test_ci_policy.py\nCI-Full: true\n") == {
        "ci-tests": "tests/test_ci_policy.py", "ci-full": "true",
    }

    for footer in ("CI-Full: yes", "CI-Full: true\nCI-Full: false", "CI-Tests: one\nCI-Tests: two"):
        with pytest.raises(ValueError):
            Trailers("Update tests\n\n" + footer + "\n")


def EventEnvironment(eventPath):
    """Keep synthetic CI fixtures out of the real runner's output and summary files."""

    environment = {
        key: value for key, value in os.environ.items()
        if key not in {"GITHUB_OUTPUT", "GITHUB_STEP_SUMMARY"}
    }
    environment.update({"GITHUB_EVENT_PATH": str(eventPath), "GITHUB_EVENT_NAME": "pull_request"})

    return environment


def MakeRepository(directory):
    """Create an isolated real Git checkout for event-to-evidence integration."""

    directory.mkdir()
    Git("init", "-q", projectRoot=directory)
    Git("config", "user.email", "ci-policy@example.invalid", projectRoot=directory)
    Git("config", "user.name", "CI Policy Test", projectRoot=directory)

    for path in TRACKED:
        destination = directory / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text('"""Synthetic policy test fixture."""\n', encoding="utf-8")

    tool = directory / "tools" / "ci_policy.py"
    tool.parent.mkdir()
    tool.write_bytes((PROJECT_ROOT / "tools" / "ci_policy.py").read_bytes())
    Git("add", ".", projectRoot=directory)
    Git("commit", "-qm", "Create policy fixture", projectRoot=directory)

    return Git("rev-parse", "HEAD", projectRoot=directory).strip()


def test_CliRecordsHeadAndCheckedRevisionAndRejectsUntrackedScope(tmpPath):
    """Exercise the actual CLI on Git history, including its nonzero failure path."""

    checkout = tmpPath / "repository"
    baseSha = MakeRepository(checkout)
    (checkout / "README.md").write_text("Example\n", encoding="utf-8")
    Git("add", "README.md", projectRoot=checkout)
    Git("commit", "-qm", "Document example", projectRoot=checkout)
    headSha = Git("rev-parse", "HEAD", projectRoot=checkout).strip()
    event = Event()
    event["pull_request"]["base"]["sha"] = baseSha
    event["pull_request"]["head"] = {"sha": headSha}
    eventPath = tmpPath / "event.json"
    eventPath.write_text(json.dumps(event), encoding="utf-8")
    outputPath = tmpPath / "output.txt"
    summaryPath = tmpPath / "summary.md"
    environment = {
        **os.environ, "GITHUB_EVENT_PATH": str(eventPath), "GITHUB_EVENT_NAME": "pull_request",
        "GITHUB_OUTPUT": str(outputPath), "GITHUB_STEP_SUMMARY": str(summaryPath),
    }
    result = subprocess.run(
        [sys.executable, "tools/ci_policy.py"], cwd=checkout, env=environment,
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 0, result.stderr
    policy = json.loads((checkout / "_build" / "ci-policy.json").read_text(encoding="utf-8"))

    assert policy["head_sha"] == policy["tested_sha"] == headSha
    assert policy["base_sha"] == baseSha
    assert policy["changed_files"] == ["README.md"]
    assert "full=false" in outputPath.read_text(encoding="utf-8")
    assert headSha in summaryPath.read_text(encoding="utf-8")

    Git("commit", "--allow-empty", "-qm", "Declare bad scope\n\nCI-Tests: tests/test_absent.py", projectRoot=checkout)
    event["pull_request"]["head"]["sha"] = Git("rev-parse", "HEAD", projectRoot=checkout).strip()
    eventPath.write_text(json.dumps(event), encoding="utf-8")
    rejected = subprocess.run(
        [sys.executable, "tools/ci_policy.py"], cwd=checkout, env=environment,
        capture_output=True, text=True, check=False,
    )

    assert rejected.returncode != 0
    assert "Unsafe or missing CI-Tests" in rejected.stderr
    stale = subprocess.run(
        [sys.executable, "tools/ci_policy.py", "--run-tests"], cwd=checkout,
        capture_output=True, text=True, check=False,
    )

    assert stale.returncode != 0
    assert "different checked-out revision" in stale.stderr


def test_WorkflowsKeepScopedChecksAndDoNotRepeatDevelopmentPushes():
    """Retain real current-head work and full release protection without duplicate push runs."""

    workflowRoot = PROJECT_ROOT / ".github" / "workflows"
    names = (
        "quick-gate.yml", "math-coverage.yml", "package-build-install.yml",
        "public-typing.yml", "documentation-gates.yml", "api-reference.yml",
    )

    for name in names:
        text = (workflowRoot / name).read_text(encoding="utf-8")

        assert "uses: ./.github/actions/ci-policy" in text, name
        assert "fetch-depth: 0" in text, name
        assert "cancel-in-progress: true" in text, name
        assert "  push:" not in text or name == "api-reference.yml", name

    math = (workflowRoot / "math-coverage.yml").read_text(encoding="utf-8")
    package = (workflowRoot / "package-build-install.yml").read_text(encoding="utf-8")
    pages = (workflowRoot / "api-reference.yml").read_text(encoding="utf-8")

    assert "python tools/ci_policy.py --run-tests" in math
    assert "if: steps.scope.outputs.full == 'true'" in math
    assert '== "2.0.0"' not in package
    assert 'os.environ["EXPECTED_PACKAGE_VERSION"]' in package
    assert "github.ref == 'refs/heads/master'" in pages
    assert "  push:\n    branches:\n      - master\n" in pages


def test_MergeCheckoutUsesHeadTrailersAndRecordsBothRevisions(tmpPath):
    """Read feature trailers even when Actions checks out a synthetic merge commit."""

    checkout = tmpPath / "merge-repository"
    originalBase = MakeRepository(checkout)
    Git("checkout", "-qb", "feature", projectRoot=checkout)
    (checkout / "README.md").write_text("Feature docs\n", encoding="utf-8")
    Git("add", "README.md", projectRoot=checkout)
    Git("commit", "-qm", "Correct behavior\n\nCI-Full: true", projectRoot=checkout)
    headSha = Git("rev-parse", "HEAD", projectRoot=checkout).strip()
    Git("checkout", "-qb", "base-update", originalBase, projectRoot=checkout)
    (checkout / "base.txt").write_text("Independent base change\n", encoding="utf-8")
    Git("add", "base.txt", projectRoot=checkout)
    Git("commit", "-qm", "Update base", projectRoot=checkout)
    baseSha = Git("rev-parse", "HEAD", projectRoot=checkout).strip()
    Git("merge", "--no-ff", "-m", "Merge feature without CI trailers", "feature", projectRoot=checkout)
    testedSha = Git("rev-parse", "HEAD", projectRoot=checkout).strip()
    event = Event()
    event["pull_request"]["base"]["sha"] = baseSha
    event["pull_request"]["head"] = {"sha": headSha}
    eventPath = tmpPath / "merge-event.json"
    eventPath.write_text(json.dumps(event), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "tools/ci_policy.py"], cwd=checkout,
        env=EventEnvironment(eventPath),
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 0, result.stderr
    policy = json.loads((checkout / "_build" / "ci-policy.json").read_text(encoding="utf-8"))

    assert policy["full"] is True, "The merge message must not hide the head's full-gate request."
    assert policy["head_sha"] == headSha != testedSha
    assert policy["tested_sha"] == testedSha
    assert policy["base_sha"] == baseSha
    assert policy["changed_files"] == ["README.md"]


@pytest.mark.parametrize("kind", ["deleted", "symlink"])
def test_TrackedButUnavailableScopeFailsAtTheCliBoundary(tmpPath, kind):
    """Reject removed tests and symlinks even when Git history contains their names."""

    checkout = tmpPath / "invalid-scope"
    baseSha = MakeRepository(checkout)
    relativePath = "tests/test_membership_function_contracts.py"
    selected = checkout / relativePath
    selected.unlink()

    if kind == "symlink":
        selected.symlink_to("test_ci_policy.py")

    Git("add", relativePath, projectRoot=checkout)
    Git("commit", "-qm", f"Change test\n\nCI-Tests: {relativePath}", projectRoot=checkout)
    headSha = Git("rev-parse", "HEAD", projectRoot=checkout).strip()
    event = Event()
    event["pull_request"]["base"]["sha"] = baseSha
    event["pull_request"]["head"] = {"sha": headSha}
    eventPath = tmpPath / "invalid-event.json"
    eventPath.write_text(json.dumps(event), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "tools/ci_policy.py"], cwd=checkout,
        env=EventEnvironment(eventPath),
        capture_output=True, text=True, check=False,
    )

    assert result.returncode != 0
    assert "Unsafe or missing CI-Tests" in result.stderr


def test_ExecutableDocumentationStillRequiresReviewedFeatureScope():
    """Prose convenience must not authorize arbitrary executable changes without a scope."""

    for path in ("tools/generate_guide_figures.py", "examples/agent_recipe.py", "docs/mkdocs.yml"):
        with pytest.raises(ValueError, match="reviewed CI-Tests"):
            SelectPolicy("pull_request", Event(), [path], {}, TRACKED)


def test_ReleaseWorkflowPreservesFullTagChecksWithFocusedPrUpdates():
    """Scoped PR checks cannot bypass full protected-tag verification or publish authorization."""

    text = (PROJECT_ROOT / ".github" / "workflows" / "release-pypi.yml").read_text(encoding="utf-8")

    assert "if: github.event_name != 'pull_request' || needs.build-distributions.outputs.full == 'true'" in text
    assert "if: github.event_name != 'pull_request' || needs.build-distributions.outputs.package == 'true'" in text
    assert "python -m pytest -q tests/test_trusted_publishing_workflow.py tests/test_pypi_release_verification.py" in text
    assert "cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in text
    assert "vars.PYPI_TRUSTED_PUBLISHING_ENABLED == 'true'" in text
