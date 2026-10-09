# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Parser contracts for explicit Task-closing PR references."""

from tools.pr_merge_links import ExtractIssueNumbers


def test_ExtractsSupportedKeywords():
    body = """
    Closes #12
    Fixes #13
    Resolves #14
    Implements #15
    """
    assert ExtractIssueNumbers(body) == [12, 13, 14, 15]


def test_ExtractsMultipleReferencesAfterOneKeyword():
    assert ExtractIssueNumbers("Closes #12, #13 and #14") == [12, 13, 14]


def test_IsCaseInsensitiveAndAcceptsInflections():
    body = "closed #1\\nFIXED #2\\nresolved #3\\nimplemented #4"
    assert ExtractIssueNumbers(body) == [1, 2, 3, 4]


def test_DeduplicatesWhilePreservingOrder():
    body = "Closes #9 and #10\\nImplements #9\\nFixes #11"
    assert ExtractIssueNumbers(body) == [9, 10, 11]


def test_PlainReferencesDoNotCloseAnything():
    body = "Related: #12, #13\\nSee Feature #14 for context."
    assert ExtractIssueNumbers(body) == []


def test_KeywordWithoutIssueReferenceIsIgnored():
    assert ExtractIssueNumbers("This closes the implementation gap.") == []


def test_ZeroAndNonNumericReferencesAreIgnored():
    assert ExtractIssueNumbers("Closes #0 and #abc") == []
