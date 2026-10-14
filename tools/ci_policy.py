# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Select reproducible full or explicitly reviewed focused PR validation.

PR opening, master promotion, manual dispatch and the head commit trailer
``CI-Full: true`` require the full gate. Routine updates declare complete-PR
feature coverage in ``CI-Tests: tests/test_one.py tests/test_two.py``. Selection
is never inferred from a commit subject. Changed tests and essential public
contracts are added automatically. Invalid or missing code scopes fail closed.
The command reads local Git/event data only and records both PR and tested SHAs.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = Path("_build/ci-policy.json")
TEST_PATTERN = re.compile(r"tests/(?:[A-Za-z0-9_]+/)*test_[A-Za-z0-9_]+\.py\Z")
DOCUMENTATION_TESTS = (
    "tests/test_markdown_source_style.py", "tests/test_locale_documentation.py",
    "tests/test_documentation_gates.py", "tests/test_pages_site.py",
)
PUBLIC_TESTS = (
    "tests/test_curated_exports.py", "tests/test_focused_modern_modules.py",
    "tests/test_public_typing_runtime.py", "tests/test_legacy_import_compatibility.py",
)
TOOL_TESTS = {
    "tools/ci_policy.py": "tests/test_ci_policy.py",
    "tools/pr_merge_links.py": "tests/test_pr_merge_links.py",
    "tools/verify_pypi_release.py": "tests/test_pypi_release_verification.py",
    "tools/check_license_headers.py": "tests/test_license_policy.py",
    "tools/reproducible_artifacts.py": "tests/test_reproducible_artifacts.py",
    "tools/typecheck.py": "tests/test_typecheck.py",
    "tools/test_runner.py": "tests/test_test_runner.py",
    "tools/release_test_audit.py": "tests/test_release_test_audit.py",
}


def Git(*arguments: str, projectRoot: Path = PROJECT_ROOT, inputText: str | None = None) -> str:
    """Run an argument-safe Git read and propagate missing-revision failures."""

    return subprocess.run(
        ["git", *arguments], cwd=projectRoot, input=inputText, text=True,
        capture_output=True, check=True,
    ).stdout


def Trailers(message: str, projectRoot: Path = PROJECT_ROOT) -> dict[str, str]:
    """Read unique CI footer fields using Git's trailer parser."""

    result = {}

    for line in Git("interpret-trailers", "--parse", projectRoot=projectRoot, inputText=message).splitlines():
        key, value = line.split(":", 1)
        key = key.lower()

        if key not in {"ci-full", "ci-tests"}:
            continue

        if key in result:
            raise ValueError(f"Duplicate {key} trailer; use one unambiguous value")

        result[key] = value.strip()

    if result.get("ci-full", "false") not in {"true", "false"}:
        raise ValueError("CI-Full must be exactly true or false")

    return result


def DocumentationPath(path: str) -> bool:
    """Recognize authored documentation and its executable rendering inputs."""

    return (
        path.startswith(("docs/", "examples/")) or path.endswith(".md")
        or path == "mkdocs.yml"
        or path.startswith("tools/") and any(
            token in path for token in ("documentation", "locale", "guide", "pages", "api_reference")
        )
    )


def SelectPolicy(
    eventName: str, event: dict, changes: list[str], trailers: dict[str, str], tracked: set[str],
) -> dict:
    """Return explicit applicability and safe test paths for a complete PR diff.

    Args:
        eventName: GitHub event name, restricted to supported workflow triggers.
        event: Parsed event payload; master promotion always requires full checks.
        changes: Complete merge-base-to-tested-revision path delta.
        trailers: Parsed footer fields from the actual PR head commit.
        tracked: Existing tracked files; deleted tests cannot be selected.

    Raises:
        ValueError: An event, path or focused code selection is unsafe or missing.
    """

    if eventName not in {"pull_request", "push", "workflow_dispatch"}:
        raise ValueError(f"Unsupported CI event: {eventName}")

    pullRequest = event.get("pull_request", {})
    full = (
        eventName == "workflow_dispatch"
        or eventName == "push" and event.get("ref") == "refs/heads/master"
        or eventName == "pull_request" and (
            event.get("action") == "opened" or pullRequest.get("base", {}).get("ref") == "master"
        )
        or trailers.get("ci-full") == "true"
    )

    if eventName == "push" and event.get("ref") != "refs/heads/master":
        raise ValueError("Development pushes must not duplicate PR gates")

    requested = trailers.get("ci-tests", "").split()

    for path in requested:
        if not TEST_PATTERN.fullmatch(path) or path not in tracked:
            raise ValueError(f"Unsafe or missing CI-Tests file: {path}")

    if not full and not changes:
        raise ValueError("Focused validation requires a nonempty complete PR diff")

    needsScope = any(
        (not DocumentationPath(path) or path.endswith((".py", ".cjs", ".yml", ".yaml")))
        and not TEST_PATTERN.fullmatch(path) and path not in {".gitignore", ".gitattributes", "LICENSE", "NOTICE"}
        for path in changes
    )

    if not full and needsScope and not requested:
        raise ValueError(
            "Code/tooling changes require a reviewed CI-Tests trailer covering the complete PR diff; "
            "after a bug fix use CI-Full: true"
        )

    selected = {"tests/test_ci_policy.py", *requested}
    selected.update(path for path in changes if TEST_PATTERN.fullmatch(path) and path in tracked)
    documentation = any(DocumentationPath(path) for path in changes)
    library = any(path.startswith("fuzzyroutines/") for path in changes)
    packaging = any(
        path in {"pyproject.toml", "setup.py", "setup.cfg", "MANIFEST.in", "LICENSE", "NOTICE", "requirements-build.txt"}
        or path == "tools/reproducible_artifacts.py" for path in changes
    )

    if documentation:
        selected.update(DOCUMENTATION_TESTS)

    if library:
        selected.update(PUBLIC_TESTS)

    if packaging:
        selected.update(("tests/test_reproducible_artifacts.py", "tests/test_license_policy.py"))

    for path in changes:
        if path in TOOL_TESTS:
            selected.add(TOOL_TESTS[path])

        if path.startswith(".github/"):
            selected.update(("tests/test_ci_policy.py", "tests/test_trusted_publishing_workflow.py", "tests/test_pr_merge_links.py"))

    missing = selected - tracked

    if missing:
        raise ValueError(f"Required policy tests are missing: {sorted(missing)}")

    return {
        "mode": "full" if full else "focused",
        "full": full, "documentation": full or documentation, "package": full or packaging,
        "tests": sorted(selected), "changed_files": sorted(changes),
    }


def ReadPolicy(projectRoot: Path = PROJECT_ROOT) -> dict:
    """Build policy from trusted workflow metadata and local checked-out history."""

    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    eventName = os.environ["GITHUB_EVENT_NAME"]
    testedSha = Git("rev-parse", "HEAD", projectRoot=projectRoot).strip()
    pullRequest = event.get("pull_request", {})
    headSha = pullRequest.get("head", {}).get("sha", testedSha)
    baseSha = pullRequest.get("base", {}).get("sha")

    for revision in (headSha, baseSha):
        if revision is not None and not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise ValueError("Event revisions must be full hexadecimal Git SHAs")

    message = Git("log", "-1", "--format=%B", headSha, projectRoot=projectRoot)
    changes = (
        Git("diff", "--name-only", "-z", f"{baseSha}...{testedSha}", "--", projectRoot=projectRoot).split("\0")
        if baseSha else []
    )
    tracked = {
        path for path in Git("ls-files", "-z", projectRoot=projectRoot).split("\0")
        if path and (projectRoot / path).is_file() and not (projectRoot / path).is_symlink()
    }
    policy = SelectPolicy(eventName, event, list(filter(None, changes)), Trailers(message, projectRoot), tracked)
    policy.update({"tested_sha": testedSha, "head_sha": headSha, "base_sha": baseSha})

    return policy


def Main(arguments: list[str] | None = None) -> int:
    """Write policy evidence or execute selected pytest files without a shell."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-tests", action="store_true")
    options = parser.parse_args(arguments)

    try:
        if options.run_tests:
            policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
            currentSha = Git("rev-parse", "HEAD").strip()

            if policy["tested_sha"] != currentSha:
                raise ValueError("Focused policy belongs to a different checked-out revision")

            command = [sys.executable, "-m", "pytest", "-q", *policy["tests"]]
            print("Focused checks (not full-suite evidence):", " ".join(command), flush=True)

            return subprocess.run(command, cwd=PROJECT_ROOT, check=False).returncode

        policy = ReadPolicy()
        POLICY_PATH.parent.mkdir(parents=True, exist_ok=True)
        POLICY_PATH.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(policy, indent=2))

        if outputPath := os.environ.get("GITHUB_OUTPUT"):
            with Path(outputPath).open("a", encoding="utf-8") as output:
                output.writelines(
                    f"{key}={str(policy[key]).lower()}\n" for key in ("full", "documentation", "package")
                )

        if summaryPath := os.environ.get("GITHUB_STEP_SUMMARY"):
            with Path(summaryPath).open("a", encoding="utf-8") as summary:
                summary.write("## Validation scope\n\n```json\n" + json.dumps(policy, indent=2) + "\n```\n")

        return 0

    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f"CI policy rejected: {error}", file=sys.stderr)

        return 1


if __name__ == "__main__":
    raise SystemExit(Main())
