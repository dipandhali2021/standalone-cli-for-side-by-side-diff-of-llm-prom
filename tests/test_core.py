import pytest
from standalone_cli_for_side_by_side_diff_of_llm_prom.core import compute_diff, format_side_by_side


# --- compute_diff ---


class TestComputeDiff:
    """Tests for compute_diff(old, new)."""

    def test_identical_strings(self):
        diff = compute_diff("hello", "hello")
        assert diff == [(" ", "hello")]

    def test_identical_multiline(self):
        diff = compute_diff("a\nb\nc", "a\nb\nc")
        assert diff == [(" ", "a"), (" ", "b"), (" ", "c")]

    def test_insertion(self):
        diff = compute_diff("hello", "hello\nworld")
        assert diff == [(" ", "hello"), ("+", "world")]

    def test_deletion(self):
        diff = compute_diff("hello\nworld", "hello")
        assert diff == [(" ", "hello"), ("-", "world")]

    def test_modification(self):
        diff = compute_diff("hello\nworld", "hello\nthere")
        assert diff == [(" ", "hello"), ("-", "world"), ("+", "there")]

    def test_both_empty(self):
        diff = compute_diff("", "")
        assert diff == []

    def test_old_empty(self):
        diff = compute_diff("", "hello\nworld")
        assert diff == [("+", "hello"), ("+", "world")]

    def test_new_empty(self):
        diff = compute_diff("hello\nworld", "")
        assert diff == [("-", "hello"), ("-", "world")]

    def test_leading_whitespace(self):
        diff = compute_diff("  hello", "  hello\n  world")
        assert diff == [(" ", "  hello"), ("+", "  world")]

    def test_trailing_whitespace(self):
        diff = compute_diff("hello ", "hello \nworld")
        assert diff == [(" ", "hello "), ("+", "world")]

    def test_multiple_changes(self):
        old = "one\ntwo\nthree\nfour"
        new = "one\ntwo_b\nthree\nfour_extra"
        diff = compute_diff(old, new)
        assert diff == [
            (" ", "one"),
            ("-", "two"),
            ("+", "two_b"),
            (" ", "three"),
            ("-", "four"),
            ("+", "four_extra"),
        ]


# --- format_side_by_side ---


class TestFormatSideBySide:
    """Tests for format_side_by_side(diff)."""

    def test_empty_diff(self):
        assert format_side_by_side([]) == ""

    def test_identical(self):
        diff = [(" ", "hello"), (" ", "world")]
        expected = " hello |  hello\n world |  world"
        assert format_side_by_side(diff) == expected

    def test_insertion(self):
        diff = [(" ", "hello"), ("+", "world")]
        expected = " hello |  hello\n       | +world"
        assert format_side_by_side(diff) == expected

    def test_deletion(self):
        diff = [(" ", "hello"), ("-", "world")]
        expected = " hello |  hello\n-world | "
        assert format_side_by_side(diff) == expected

    def test_mixed_change(self):
        diff = [(" ", "hello"), ("-", "world"), ("+", "there")]
        expected = " hello |  hello\n-world | \n       | +there"
        assert format_side_by_side(diff) == expected

    def test_only_additions(self):
        diff = [("+", "hello"), ("+", "world")]
        expected = " | +hello\n | +world"
        assert format_side_by_side(diff) == expected

    def test_only_deletions(self):
        diff = [("-", "hello"), ("-", "world")]
        expected = "-hello | \n-world | "
        assert format_side_by_side(diff) == expected

    def test_single_insertion(self):
        diff = [("+", "hello")]
        expected = " | +hello"
        assert format_side_by_side(diff) == expected

    def test_single_deletion(self):
        diff = [("-", "hello")]
        expected = "-hello | "
        assert format_side_by_side(diff) == expected

    def test_longer_lines_align_properly(self):
        diff = [(" ", "short"), ("-", "a bit longer"), ("+", "tiny")]
        expected = " short        |  short\n-a bit longer | \n              | +tiny"
        assert format_side_by_side(diff) == expected
