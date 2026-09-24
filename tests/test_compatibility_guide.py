# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Executable contracts for the canonical compatibility guide."""

import re
import subprocess
import sys
from pathlib import Path

PROJECTROOT = Path(__file__).resolve().parents[1]
GUIDEPATH = PROJECTROOT / "docs" / "COMPATIBILITY.md"
PROTECTEDSYMBOLS = (
    "DiapasonParser",
    "IsNumber",
    "IsCorrectFuzzyNumberValue",
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


def test_GuideNamesEveryProtectedHistoricalSymbol():
    """Keep the canonical entry point complete when the facade evolves."""

    guideText = GUIDEPATH.read_text(encoding="utf-8")

    for symbol in PROTECTEDSYMBOLS:
        assert f"`{symbol}`" in guideText, (
            f"docs/COMPATIBILITY.md must identify protected symbol {symbol}."
        )


def test_GuidePythonExamplesExecuteAgainstCurrentPublicApi():
    """Prevent migration snippets from documenting unavailable call shapes."""

    guideText = GUIDEPATH.read_text(encoding="utf-8")
    examples = re.findall(r"```python\n(.*?)```", guideText, flags=re.DOTALL)

    assert len(examples) == 3, "The guide must retain one import and two migration examples."

    for example in examples:
        verification = "\nassert abs(centroid - 0.5) < 1e-12\n" if "centroid =" in example else ""
        result = subprocess.run(
            [sys.executable, "-c", example + verification],
            cwd=PROJECTROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        assert result.returncode == 0, (
            "A documented compatibility example no longer executes.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def test_GuideSeparatesGuaranteesFromCorrectedBehavior():
    """Keep defect corrections outside the protected-name guarantee."""

    guideText = GUIDEPATH.read_text(encoding="utf-8")

    assert "## Protected historical surface" in guideText
    assert "## Corrected behavior is not a compatibility promise" in guideText
    assert guideText.index("## Protected historical surface") < guideText.index(
        "## Corrected behavior is not a compatibility promise"
    )
