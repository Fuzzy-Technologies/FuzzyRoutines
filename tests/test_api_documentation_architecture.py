import subprocess
from pathlib import Path

PROJECTROOT = Path(__file__).parents[1]
EVALUATIONROOT = PROJECTROOT / "docs" / "api-evaluation"


def test_ApiDocumentationDecisionIsBackedByReproducibleInputs():
    requiredPaths = [
        PROJECTROOT / "docs" / "adr" / "0010-api-documentation-architecture.md",
        PROJECTROOT / "docs" / "requirements-api.txt",
        EVALUATIONROOT / "README.md",
        EVALUATIONROOT / "comparison-evidence.md",
        EVALUATIONROOT / "mkdocs.yml",
        EVALUATIONROOT / "requirements" / "pdoc.txt",
        EVALUATIONROOT / "requirements" / "sphinx.txt",
        EVALUATIONROOT / "sphinx" / "conf.py",
        PROJECTROOT / "tools" / "evaluate_api_documentation.py",
    ]

    for requiredPath in requiredPaths:
        assert requiredPath.is_file(), f"missing API-documentation evidence input: {requiredPath}"


def test_ApiDocumentationDependenciesRemainDocsOnly():
    projectText = (PROJECTROOT / "pyproject.toml").read_text(encoding="utf-8")
    documentationDependencies = (PROJECTROOT / "docs" / "requirements-api.txt").read_text(
        encoding="utf-8"
    )

    for packageName in ("mkdocs", "mkdocstrings", "griffelib"):
        assert packageName in documentationDependencies
        assert packageName not in projectText, f"{packageName} leaked into runtime package metadata"


def test_ApiDocumentationGeneratedHtmlIsNotTracked():
    trackedPaths = subprocess.check_output(
        ["git", "ls-files"],
        cwd=PROJECTROOT,
        text=True,
    ).splitlines()

    assert not any(path.startswith("_build/") for path in trackedPaths)


def test_MkdocstringsSpikeUsesStableQualifiedAnchorsAndSafeDiscovery():
    configurationText = (EVALUATIONROOT / "mkdocs.yml").read_text(encoding="utf-8")
    apiPageText = (EVALUATIONROOT / "source" / "api" / "fuzzysets.md").read_text(
        encoding="utf-8"
    )

    assert "mkdocstrings:" in configurationText
    assert "show_root_full_path: true" in configurationText
    assert "signature_crossrefs: true" in configurationText
    assert "::: fuzzyroutines.fuzzysets" in apiPageText
