from tools.pr_merge_links import extract_issue_numbers


def test_extracts_supported_keywords():
    body = """
    Closes #12
    Fixes #13
    Resolves #14
    Implements #15
    """
    assert extract_issue_numbers(body) == [12, 13, 14, 15]


def test_extracts_multiple_references_after_one_keyword():
    assert extract_issue_numbers("Closes #12, #13 and #14") == [12, 13, 14]


def test_is_case_insensitive_and_accepts_inflections():
    body = "closed #1\\nFIXED #2\\nresolved #3\\nimplemented #4"
    assert extract_issue_numbers(body) == [1, 2, 3, 4]


def test_deduplicates_while_preserving_order():
    body = "Closes #9 and #10\\nImplements #9\\nFixes #11"
    assert extract_issue_numbers(body) == [9, 10, 11]


def test_plain_references_do_not_close_anything():
    body = "Related: #12, #13\\nSee Feature #14 for context."
    assert extract_issue_numbers(body) == []


def test_keyword_without_issue_reference_is_ignored():
    assert extract_issue_numbers("This closes the implementation gap.") == []


def test_zero_and_non_numeric_references_are_ignored():
    assert extract_issue_numbers("Closes #0 and #abc") == []
