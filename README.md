# prompt-diff

A lightweight, dependency-free CLI for side-by-side diffs of LLM prompt outputs.

## Installation

```bash
uv pip install .
```

## Usage

```bash
prompt-diff [options] <file_a> <file_b>
```

Compare two files containing LLM prompt outputs:

```bash
prompt-diff response_a.txt response_b.txt
```

## Testing

Run the full test suite (unit and integration tests) with pytest:

```bash
python -m pytest -q
```

Or, if using `uv`:

```bash
uv run --no-project --with pytest python -m pytest -q
```

Both commands run the same suite of 36 tests covering:
- `compute_diff` — line-by-line diff computation
- `format_side_by_side` — side-by-side string rendering
- CLI integration via subprocess

## License

MIT
