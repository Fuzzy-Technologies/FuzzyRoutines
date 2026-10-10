# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Parser contracts for explicit Task-closing PR references."""

from tools.pr_merge_links import ExtractIssueNumbers


def test_ExtractsSupportedKeywords():
    """Extract completion references after each supported GitHub closing keyword."""

    body = "Closes #12\nFixes #13\nResolves #14\nImplements #15"
    assert ExtractIssueNumbers(body) == [12, 13, 14, 15]


def test_ExtractsMultipleReferencesAfterOneKeyword():
    """Extract every issue in a completion-keyword list."""

    assert ExtractIssueNumbers("Closes #12, #13 and #14") == [12, 13, 14]


def test_IsCaseInsensitiveAndAcceptsInflections():
    """Accept case variations and supported inflections of completion keywords."""

    body = "closed #1\nFIXED #2\nresolved #3\nimplemented #4"
    assert ExtractIssueNumbers(body) == [1, 2, 3, 4]


def test_DeduplicatesWhilePreservingOrder():
    """Deduplicate completion references while retaining first-appearance order."""

    body = "Closes #9 and #10\nImplements #9\nFixes #11"
    assert ExtractIssueNumbers(body) == [9, 10, 11]


def test_PlainReferencesDoNotCloseAnything():
    """Verify that plain references do not close anything."""

    body = "Related: #12, #13\nSee Feature #14 for context."
    assert ExtractIssueNumbers(body) == []


def test_KeywordWithoutIssueReferenceIsIgnored():
    """Verify that keyword without issue reference is ignored."""

    assert ExtractIssueNumbers("This closes the implementation gap.") == []


def test_ZeroAndNonNumericReferencesAreIgnored():
    """Verify that zero and nonnumeric references are ignored."""

    assert ExtractIssueNumbers("Closes #0 and #abc") == []


def test_ReferencesAfterSentenceAreNotCompletion():
    """Keep contextual references after a closing directive open."""

    assert ExtractIssueNumbers("Closes #294. Refs #280, #295, #296, #297.") == [294]


def test_NegatedAndNarrativeClosingWordsDoNotCloseTasks():
    """Prevent the release-note prose that prematurely closed M6 tasks."""

    body = (
        "This does not close the acceptance in #280 or publication in #299.\n"
        "The fix implements a gate for #297.\n"
        "Do not close #298.\n"
        "Not yet: Closes #299"
    )
    assert ExtractIssueNumbers(body) == []


def test_MarkdownExamplesAndQuotesAreNotDirectives():
    """Ignore fenced, indented, inline-code and quoted completion examples."""

    body = (
        "```text\nCloses #1\n````\n"
        "~~~markdown\nFixes #2\n~~~\n"
        "> Closes #3\n    Closes #4\n`Closes #5`\n"
        "- Resolves #6 and #7; references #8"
    )
    assert ExtractIssueNumbers(body) == [6, 7]


def test_UnclosedFenceAndInvalidReferenceSuffixAreIgnored():
    """Fail closed on incomplete Markdown examples and non-issue identifiers."""

    assert ExtractIssueNumbers("Closes #12abc\n```\nCloses #13") == []


def test_CompletionListCannotConsumeLaterProse():
    """Limit completion to adjacent issue numbers separated by list punctuation."""

    assert ExtractIssueNumbers("Fixes: #12, #13 and #14 with context #15") == [12, 13, 14]
