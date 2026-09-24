# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Executable contracts for the canonical compatibility guide."""

from pathlib import Path

from tools.verify_installed_executables import LoadCompatibilityGuideExamples

PROJECTROOT = Path(__file__).resolve().parents[1]
GUIDEPATH = PROJECTROOT / "docs" / "COMPATIBILITY.md"
ADRPROTECTEDSYMBOLS = (
    "FuzzyNOT",
    "FuzzyNOTParabolic",
    "FuzzyAND",
    "FuzzyOR",
    "TNorm",
    "TNormCompose",
    "SCoNorm",
    "SCoNormCompose",
    "MFunction",
    "FuzzySet",
    "FuzzyScale",
    "UniversalFuzzyScale",
)
OBSERVEDUTILITYSYMBOLS = (
    "DiapasonParser",
    "IsNumber",
    "IsCorrectFuzzyNumberValue",
)


def test_GuideNamesEveryAdrProtectedHistoricalSymbol():
    """Keep the canonical entry point aligned with ADR-0001."""

    guideText = GUIDEPATH.read_text(encoding="utf-8")

    for symbol in ADRPROTECTEDSYMBOLS:
        assert f"`{symbol}`" in guideText, (
            f"docs/COMPATIBILITY.md must identify ADR-protected symbol {symbol}."
        )


def test_GuideSeparatesObservedUtilitiesFromAdrProtection():
    """Do not silently broaden permanent compatibility guarantees."""

    guideText = GUIDEPATH.read_text(encoding="utf-8")
    protectedSection, observedSection = guideText.split(
        "## Currently supported observed surface",
        maxsplit=1,
    )

    for symbol in OBSERVEDUTILITYSYMBOLS:
        assert f"`{symbol}`" not in protectedSection
        assert f"`{symbol}`" in observedSection


def test_GuidePythonExamplesAreOwnedByCleanInstallVerifier():
    """Keep snippet discovery shared with the installed-artifact gate."""

    examples = LoadCompatibilityGuideExamples()

    assert len(examples) == 3, "The guide must retain one import and two migration examples."

    for example in examples:
        compile(example, str(GUIDEPATH), "exec")


def test_GuideSeparatesGuaranteesFromCorrectedBehavior():
    """Keep defect corrections outside the protected-name guarantee."""

    guideText = GUIDEPATH.read_text(encoding="utf-8")

    assert "## ADR-protected historical contract" in guideText
    assert "## Currently supported observed surface" in guideText
    assert "## Corrected behavior is not a compatibility promise" in guideText
    assert guideText.index("## ADR-protected historical contract") < guideText.index(
        "## Corrected behavior is not a compatibility promise"
    )
