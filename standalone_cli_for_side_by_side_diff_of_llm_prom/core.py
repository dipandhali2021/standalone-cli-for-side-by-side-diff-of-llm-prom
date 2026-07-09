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

def format_side_by_side(diff: list[tuple[str, str]]) -> str:
    """Render a diff as a side-by-side string with change markers.

    Args:
        diff: A list of (tag, line) tuples from compute_diff().

    Returns:
        A formatted side-by-side string where old and new lines are
        aligned with '-', '+', and ' ' markers on each side.
    """
    left_lines: list[str] = []
    right_lines: list[str] = []

    for tag, line in diff:
        if tag == ' ':
            left_lines.append(f' {line}')
            right_lines.append(f' {line}')
        elif tag == '-':
            left_lines.append(f'-{line}')
            right_lines.append('')
        elif tag == '+':
            left_lines.append('')
            right_lines.append(f'+{line}')

    if not left_lines:
        return ''

    left_width = max(len(l) for l in left_lines)

    parts: list[str] = []
    for left, right in zip(left_lines, right_lines):
        parts.append(f'{left:<{left_width}} | {right}')

    return '\n'.join(parts)
