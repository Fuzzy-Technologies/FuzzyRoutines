import subprocess
from pathlib import Path
from xml.etree import ElementTree

PROJECTROOT = Path(__file__).parents[1]
EVALUATIONROOT = PROJECTROOT / "docs" / "api-evaluation"


def test_ApiDocumentationDecisionIsBackedByReproducibleInputs():
    requiredPaths = [
        PROJECTROOT / "docs" / "adr" / "0010-api-documentation-architecture.md",
        PROJECTROOT / "docs" / "requirements-api.txt",
        EVALUATIONROOT / "README.md",
        EVALUATIONROOT / "brand-identity.md",
        EVALUATIONROOT / "comparison-evidence.md",
        EVALUATIONROOT / "mkdocs.yml",
        EVALUATIONROOT / "requirements" / "pdoc.txt",
        EVALUATIONROOT / "requirements" / "sphinx.txt",
        EVALUATIONROOT / "source" / "assets" / "brand" / "fuzzyroutines-sign.svg",
        EVALUATIONROOT / "source" / "assets" / "brand" / "fuzzyroutines-horizontal.svg",
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


def test_FuzzyRoutinesIdentityAssetsAreSelfContainedVectors():
    assetsRoot = EVALUATIONROOT / "source" / "assets"
    faviconPath = assetsRoot / "favicon.svg"
    signPath = assetsRoot / "brand" / "fuzzyroutines-sign.svg"
    horizontalPath = assetsRoot / "brand" / "fuzzyroutines-horizontal.svg"

    assert faviconPath.read_text(encoding="utf-8") == signPath.read_text(encoding="utf-8")

    for assetPath, expectedViewBox in (
        (faviconPath, "0 0 64 64"),
        (signPath, "0 0 64 64"),
        (horizontalPath, "0 0 520 96"),
    ):
        assetRoot = ElementTree.parse(assetPath).getroot()
        assetText = assetPath.read_text(encoding="utf-8")

        assert assetRoot.attrib["viewBox"] == expectedViewBox
        assert "<title" in assetText
        assert "<script" not in assetText
        assert "<image" not in assetText
        for element in assetRoot.iter():
            for attributeName, attributeValue in element.attrib.items():
                if attributeName.endswith("href"):
                    assert not attributeValue.startswith(("http://", "https://"))


def test_FuzzyRoutinesIdentityIsIntegratedIntoTheDocsTheme():
    configurationText = (EVALUATIONROOT / "mkdocs.yml").read_text(encoding="utf-8")
    landingPageText = (EVALUATIONROOT / "source" / "index.md").read_text(encoding="utf-8")

    assert "logo: assets/brand/fuzzyroutines-sign.svg" in configurationText
    assert "favicon: assets/favicon.svg" in configurationText
    assert "assets/stylesheets/fuzzyroutines.css" in configurationText
    assert "assets/brand/fuzzyroutines-horizontal.svg" in landingPageText
