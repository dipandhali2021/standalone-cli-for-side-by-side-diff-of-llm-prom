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

    def test_unicode_characters(self):
        diff = compute_diff("caf\u00e9", "caf\u00e9\u2615")
        assert diff == [("-", "caf\u00e9"), ("+", "caf\u00e9\u2615")]

    def test_lines_with_tabs(self):
        diff = compute_diff("\tindented", "\tindented\n\ttabbed")
        assert diff == [(" ", "\tindented"), ("+", "\ttabbed")]

    def test_empty_lines_in_middle(self):
        diff = compute_diff("a\n\nb", "a\n\nb\nc")
        assert diff == [(" ", "a"), (" ", ""), (" ", "b"), ("+", "c")]

    def test_whitespace_only_lines(self):
        diff = compute_diff("  \n\t", "  \n\t\n   ")
        assert diff == [(" ", "  "), (" ", "\t"), ("+", "   ")]

    def test_trailing_newline_no_diff(self):
        assert compute_diff("hello\n", "hello") == [(" ", "hello")]

    def test_context_lines_filtered(self):
        """Verify that '?' context lines from difflib are filtered out."""
        old = "a\nb\nc"
        new = "a\nB\nc"
        diff = compute_diff(old, new)
        for tag, _ in diff:
            assert tag in (" ", "+", "-")
        assert len(diff) > 0

    def test_repeated_lines_with_changes(self):
        old = "x\nx\ny\nx"
        new = "x\nz\ny\nx"
        diff = compute_diff(old, new)
        assert (" ", "x") in diff
        assert (" ", "y") in diff
        assert ("-", "x") in diff or ("+", "z") in diff

    def test_differing_only_by_blank_lines(self):
        diff = compute_diff("a\nb", "a\n\nb")
        assert diff == [(" ", "a"), ("+", ""), (" ", "b")]

    def test_both_identical_with_trailing_newline(self):
        assert compute_diff("line\n", "line\n") == [(" ", "line")]

    def test_emoji_sequences(self):
        diff = compute_diff("\U0001f525\U0001f525", "\U0001f525\U0001f525\U0001f4a7")
        assert diff == [("-", "\U0001f525\U0001f525"), ("+", "\U0001f525\U0001f525\U0001f4a7")]


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

    def test_unicode_characters(self):
        diff = [(" ", "caf\u00e9"), ("+", "caf\u00e9\u2615")]
        result = format_side_by_side(diff)
        assert "caf\u00e9" in result
        assert "\u2615" in result
        assert " | " in result

    def test_lines_with_tabs(self):
        diff = [(" ", "\tindented")]
        result = format_side_by_side(diff)
        assert "\tindented" in result

    def test_empty_line_in_diff_content(self):
        diff = [(" ", "a"), (" ", ""), (" ", "b")]
        result = format_side_by_side(diff)
        assert " a" in result
        assert " b" in result
        assert result.count(" | ") == 3

    def test_format_repeated_identical(self):
        diff = [(" ", "x"), (" ", "x"), (" ", "y")]
        result = format_side_by_side(diff)
        assert result.count(" x |  x") == 2
        assert result.count(" y |  y") == 1


class TestCliIntegration:
    """Integration tests that invoke the CLI via subprocess."""

    def test_side_by_side_diff_via_subprocess(self):
        """Invoke llm-diff on two temporary files and verify expected diff lines."""
        import os
        import shutil
        import subprocess
        import tempfile

        llm_diff = shutil.which("llm-diff")
        if llm_diff is None:
            pytest.skip("llm-diff not found in PATH")

        old_content = "hello\nworld\n"
        new_content = "hello\nthere\n"

        f1 = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        f1.write(old_content)
        f1.close()
        f2 = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        f2.write(new_content)
        f2.close()

        try:
            result = subprocess.run(
                [llm_diff, f1.name, f2.name],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert "-world" in result.stdout
            assert "+there" in result.stdout
            assert "hello" in result.stdout
            assert " | " in result.stdout
        finally:
            os.unlink(f1.name)
            os.unlink(f2.name)
