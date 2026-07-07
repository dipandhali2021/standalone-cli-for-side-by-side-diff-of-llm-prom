import difflib


def compute_diff(old: str, new: str) -> list[tuple[str, str]]:
    """Compare two strings and return a line-by-line diff.

    Args:
        old: The original string.
        new: The new/modified string.

    Returns:
        A list of (tag, line) tuples where tag is '+', '-', or ' '.
    """
    result: list[tuple[str, str]] = []
    for line in difflib.Differ().compare(old.splitlines(), new.splitlines()):
        if len(line) >= 2:
            tag = line[0]
            if tag in ('+', '-', ' '):
                result.append((tag, line[2:]))
    return result
