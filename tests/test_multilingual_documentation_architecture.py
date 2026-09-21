# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Contract tests for the multilingual documentation-pipeline design."""

import re
from pathlib import Path

PROJECTROOT = Path(__file__).parents[1]
ADRPATH = PROJECTROOT / "docs" / "adr" / "0011-multilingual-documentation-pipeline.md"
CONTRACTPATH = (
    PROJECTROOT / "docs" / "architecture" / "multilingual-documentation-pipeline.md"
)


def _LocalMarkdownTargets(documentPath):
    """Yield local Markdown link targets without fragments or external URLs."""

    documentText = documentPath.read_text(encoding="utf-8")

    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", documentText):
        targetPath = target.split("#", 1)[0]

        if targetPath and "://" not in targetPath:
            yield targetPath


def test_MultilingualDecisionDefinesEveryRequiredInvariant():
    """Keep the accepted design complete enough for downstream implementation."""

    decisionText = ADRPATH.read_text(encoding="utf-8")
    contractText = CONTRACTPATH.read_text(encoding="utf-8")
    combinedText = " ".join((decisionText + contractText).split())

    requiredFragments = (
        "`en`",
        "`ru`",
        "`zh-CN`",
        "page:mathematics.fuzzy-set.operations",
        "symbol:fuzzyroutines.fuzzysets.ScalarFuzzySet",
        "concept:fuzzy-set.positive-support",
        "sourceHash",
        "reviewedSourceHash",
        "SHA-256",
        "`stale`",
        "Each locale has its own navigation and search index.",
        "human mathematical/technical",
        "Generic validation must not contain a hard-coded FuzzyRoutines import",
    )

    for requiredFragment in requiredFragments:
        assert requiredFragment in combinedText, (
            f"missing multilingual architecture invariant: {requiredFragment}"
        )


def test_MultilingualDecisionLinksResolveLocally():
    """Prevent the ADR and detailed contract from linking to missing local files."""

    for documentPath in (ADRPATH, CONTRACTPATH):
        for target in _LocalMarkdownTargets(documentPath):
            targetPath = (documentPath.parent / target).resolve()
            assert targetPath.is_relative_to(PROJECTROOT.resolve()), target
            assert targetPath.exists(), f"broken local documentation link: {target}"


def test_MultilingualContractTablesHaveConsistentColumns():
    """Keep design tables structurally readable before rendered validation exists."""

    contractLines = CONTRACTPATH.read_text(encoding="utf-8").splitlines()
    tableColumnCount = None

    for line in contractLines + [""]:
        if line.startswith("|") and line.endswith("|"):
            columnCount = line.count("|") - 1

            if tableColumnCount is None:
                tableColumnCount = columnCount

            assert columnCount == tableColumnCount, (
                f"inconsistent Markdown table width: {line}"
            )

        else:
            tableColumnCount = None
