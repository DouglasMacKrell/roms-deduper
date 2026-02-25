# Technology Stack

A breakdown of every tool and library used in rom-deduper, and why it was selected.

---

## Language & Runtime

### Python 3.10+

**What:** The project targets Python 3.10 or newer.

**Why:** 3.10 adds structural pattern matching, improved error messages, and `ParamSpec` for better typing. It's widely available (Ubuntu 22.04+, macOS, Windows) and avoids the end-of-life cutoff of 3.9. The `requires-python = ">=3.10"` in pyproject.toml enforces this.

---

## Build & Packaging

### setuptools

**What:** Build backend and package manager. Declares dependencies, scripts, and package layout in `pyproject.toml`.

**Why:** Standard for Python packaging, well-supported, and works with `pip install -e ".[dev]"` for editable installs. PEP 517/518 compliant. No need for Poetry or PDM for a focused CLI tool.

### pyproject.toml (PEP 517/621)

**What:** Single config file for build, project metadata, and tool settings (pytest, ruff, pyright, coverage).

**Why:** Replaces setup.py, setup.cfg, and scattered config files. One place for project definition and tool configuration.

---

## Runtime Dependencies

### send2trash

**What:** Cross-platform library that moves files to the OS trash/recycle bin instead of permanently deleting.

**Why:** When users pass `--hard`, we send duplicates to trash rather than `_duplicates_removed/`. Permanent delete would be risky. send2trash works on Windows, macOS, and Linux with a simple API. No need to handle platform-specific trash paths.

### rich

**What:** Terminal formatting library: tables, colors, panels, progress bars.

**Why:** The dry-run report uses Rich tables for readable output. Apply/restore use styled success messages. Rich handles TTY detection, fallback for pipes, and consistent cross-platform rendering. Avoids manual ANSI codes or heavy frameworks like Click's formatting.

---

## Standard Library (No Extra Deps)

| Module | Use |
|--------|-----|
| `argparse` | CLI argument parsing. Built-in, sufficient for subcommands and flags. |
| `dataclasses` | Data structures (Config, ROMEntry, DryRunReport). Reduces boilerplate. |
| `json` | Config loading and manifest storage. No need for YAML/TOML. |
| `pathlib` | Path handling. Cross-platform, object-oriented, replaces os.path. |
| `re` | Regex for parsing ROM filenames (region, language, quality tags). |
| `collections.defaultdict` | Grouping entries by (console, title). |
| `typing` | Type hints and TYPE_CHECKING for forward references. |

**Why stdlib-first:** Fewer dependencies, smaller install, fewer supply-chain risks. We only add deps when stdlib is insufficient (trash, terminal UI).

---

## Development Dependencies

### pytest

**What:** Test framework. Runs tests in `tests/`, supports fixtures, parametrization, and plugins.

**Why:** De facto standard for Python testing. Clear assertion messages, good discovery, integrates with coverage. No need for unittest or nose.

### pytest-cov

**What:** Coverage plugin for pytest. Measures line and branch coverage.

**Why:** Enforces 80% minimum coverage. Integrates with pytest via `--cov`. Reports which lines are uncovered. Coverage config lives in pyproject.toml.

### ruff

**What:** Fast linter and formatter written in Rust. Replaces flake8, isort, Black, and more.

**Why:** One tool for lint and format. Much faster than flake8+Black. Ruff format is Black-compatible. Catches import errors, style issues, and common bugs (E, F, I, W). We use `pass_filenames: false` so it checks the full codebase on every commit.

### pyright

**What:** Static type checker from Microsoft. Powers Pylance in VS Code.

**Why:** Chosen over mypy for speed and modern design. Catches type errors before runtime. `typeCheckingMode = "standard"` balances strictness with practicality. Integrates with existing type hints.

### pre-commit

**What:** Framework for running hooks before commits (and optionally before push).

**Why:** Runs ruff and pyright on commit, pytest+coverage on push. Catches issues before they reach CI. `pre-commit install --install-hooks` sets it up. Hooks run on full codebase for consistency.

---

## CI/CD

### GitHub Actions

**What:** Workflow runs on push/PR to `main` and `develop`. Two jobs: lint and test.

**Why:** Free for public repos, integrated with GitHub. Same checks as local (ruff, pyright, pytest). Ensures pushed code passes even if someone bypasses pre-push.

### actions/checkout@v4, actions/setup-python@v5

**What:** Official actions for cloning the repo and installing Python.

**Why:** Maintained by GitHub. setup-python handles caching and version selection. We pin Python 3.10 to match pyproject.toml.

---

## Config & Data Formats

### JSON

**What:** Config file (`config.json`) and manifest (`.manifest.json` in `_duplicates_removed/`).

**Why:** Stdlib support, human-readable, widely understood. No need for YAML or TOML. Config keys: `exclude_consoles`, `translation_patterns`, `region_priority`, `roms_path`.

---

## Project Structure

```
rom-deduper/
├── rom_deduper/          # Package
│   ├── scanner.py        # File discovery
│   ├── parser.py         # Filename parsing
│   ├── grouper.py        # Duplicate grouping
│   ├── ranker.py         # Keeper selection
│   ├── actions.py        # Apply, restore, manifest
│   ├── config.py         # Config loading
│   └── cli.py            # Entry point
├── tests/                # Mirrors package structure
├── docs/                 # Documentation
├── .github/workflows/    # CI
├── pyproject.toml        # Single config
├── config.example.json   # Config template
└── .pre-commit-config.yaml
```

---

## What We Explicitly Avoided

| Tool | Why Not |
|------|---------|
| **Black** | Ruff format is Black-compatible and faster. One tool (ruff) for lint+format. |
| **mypy** | Pyright is faster and more modern. Same role, better performance. |
| **Poetry/PDM** | setuptools + pyproject.toml is enough. No need for lockfiles or extra tooling. |
| **Click/Typer** | argparse handles our CLI. No need for a framework. |
| **YAML/TOML config** | JSON is sufficient and stdlib-supported. |
| **Database** | Manifest is a single JSON file. No persistence layer needed. |

---

## Version Pinning

We use minimum versions (`>=`) rather than exact pins in pyproject.toml. CI and pre-commit provide reproducibility. For production deploys, consider `pip freeze` or a lockfile if strict reproducibility is required.
