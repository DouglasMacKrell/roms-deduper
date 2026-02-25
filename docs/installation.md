# Installation Guide

Complete installation instructions for rom-deduper.

## Requirements

- **Python 3.10+**
- **pip** (or uv, pipx, etc.)

## Basic Install

From the project root:

```bash
pip install -e ".[dev]"
```

This installs:

- **Runtime**: `send2trash`, `rich`
- **Dev**: `pytest`, `pytest-cov`, `ruff`, `pre-commit`, `pyright`

The `-e` flag installs in editable mode so code changes take effect immediately.

## Virtual Environment (Recommended)

Using a venv keeps dependencies isolated:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Pre-commit Hooks

Install hooks to run ruff and pytest automatically:

```bash
pre-commit install --install-hooks
```

| Hook | When | What |
|------|------|------|
| ruff | On commit | Lint and format |
| ruff-format | On commit | Format code |
| pyright | On commit | Static type checking |
| pytest | On push | Full test suite + coverage (80% min) |

To bypass (not recommended): `git commit --no-verify` or `git push --no-verify`.

## Verify Installation

```bash
rom-deduper --help
rom-deduper scan --help
```

Run tests:

```bash
pytest -q
```

## Install from Source (Clone)

```bash
git clone https://github.com/DouglasMacKrell/roms-deduper.git
cd roms-deduper
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install --install-hooks
```

## CI

GitHub Actions runs on push/PR to `main` and `develop`:

- **lint**: `ruff check` and `ruff format --check`
- **type check**: `pyright rom_deduper tests`
- **test**: `pytest --cov --cov-fail-under=80`

See [.github/workflows/ci.yml](../.github/workflows/ci.yml).

## Troubleshooting

**`rom-deduper: command not found`**

- Ensure the venv is activated: `source .venv/bin/activate`
- Or run via module: `python -m rom_deduper.cli scan /path`

**Pre-commit pytest fails**

- Run `pytest` manually to see errors
- Ensure coverage is ≥80%: `pytest --cov=rom_deduper --cov-report=term-missing`

**Permission errors on apply**

- Ensure you have write access to the ROMs directory
- Try `--hard` to use OS trash instead of moving files
