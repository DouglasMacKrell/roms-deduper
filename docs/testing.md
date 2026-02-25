# Testing Guide

How to run tests for rom-deduper.

## Quick Run

```bash
pytest
```

Runs all tests in `tests/` with verbose output.

## Coverage

```bash
pytest --cov=rom_deduper --cov-fail-under=80 --cov-report=term-missing
```

- `--cov=rom_deduper` — Measure coverage for the package
- `--cov-fail-under=80` — Fail if coverage drops below 80%
- `--cov-report=term-missing` — Show which lines are not covered

Coverage config is in `pyproject.toml` under `[tool.coverage.run]` and `[tool.coverage.report]`.

## Run Specific Tests

**By file:**

```bash
pytest tests/test_parser.py
pytest tests/test_actions.py
```

**By test name (pattern):**

```bash
pytest -k "restore"
pytest -k "test_rank_prefers"
```

**Single test:**

```bash
pytest tests/test_parser.py::test_parse_extracts_usa_region
```

## Quiet Mode

```bash
pytest -q
```

Minimal output, useful for quick checks.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Fixtures: tmp_roms_dir, tmp_psx_dir
├── test_actions.py      # dry_run, apply_removal, restore
├── test_config.py       # load_config, CLI with config
├── test_grouper.py      # group_entries
├── test_integration.py  # E2E: scan→apply→restore, config, verbosity
├── test_parser.py       # parse_filename
├── test_ranker.py       # rank_group
├── test_scanner.py      # scan
└── test_config.py       # Config loading, CLI
```

## Fixtures

Defined in `conftest.py`:

| Fixture | Description |
|---------|-------------|
| `tmp_roms_dir` | `tmp_path/ROMs` — ROMs root for tests |
| `tmp_psx_dir` | `tmp_roms_dir/psx` — PSX subdir |

Use `tmp_roms_dir` or `tmp_path` for tests that need a temp directory.

## Pre-commit and Pre-push

- **pre-commit** (on `git commit`): ruff, ruff-format
- **pre-push** (on `git push`): pytest with coverage

To run pre-commit manually:

```bash
pre-commit run --all-files
pre-commit run --hook-stage push
```

## Writing Tests

1. Place tests in `tests/` mirroring `rom_deduper/` structure
2. Use `tmp_path` or `tmp_roms_dir` for file operations
3. Follow TDD: write failing test first, then implement

Example:

```python
def test_my_feature(tmp_roms_dir: Path) -> None:
    """Description of what is tested."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    result = some_function(tmp_roms_dir)
    assert result == expected
```

## CI

GitHub Actions runs the same commands on push/PR:

```yaml
ruff check rom_deduper tests
ruff format --check rom_deduper tests
pytest --cov=rom_deduper --cov-fail-under=80 --cov-report=term-missing
```

Ensure tests pass locally before pushing.
