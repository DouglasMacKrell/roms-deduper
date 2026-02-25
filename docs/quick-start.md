# Quick Start Guide

Get up and running with rom-deduper in a few minutes.

## 1. Install

```bash
cd rom-deduper
pip install -e ".[dev]"
```

This installs the package in editable mode with dev dependencies (pytest, ruff, pre-commit).

## 2. Scan Your ROMs

Run a dry run to see what would be removed without changing anything:

```bash
rom-deduper scan /path/to/your/ROMs
```

Example output:

```
Dry Run Report
Total files: 1247 | Duplicate groups: 42 | Files to remove: 89

┌─────────┬──────────────────┬─────────────────────┬─────────────────────┐
│ Console │ Title            │ Keeper              │ To Remove           │
├─────────┼──────────────────┼─────────────────────┼─────────────────────┤
│ psx     │ Game             │ Game (USA).chd      │ Game (Japan).chd    │
│ genesis │ Power Drive      │ Power Drive (E).md  │ Power Drive.bin     │
└─────────┴──────────────────┴─────────────────────┴─────────────────────┘
```

## 3. Review and Apply

If the report looks correct, apply the removal:

```bash
rom-deduper apply /path/to/your/ROMs
```

Duplicates are moved to `_duplicates_removed/` inside your ROMs directory, preserving the folder structure. A manifest (`.manifest.json`) tracks what was moved for restore.

## 4. Restore (Optional)

If you change your mind:

```bash
rom-deduper restore /path/to/your/ROMs
```

This moves files from `_duplicates_removed/` back to their original locations.

## Common Options

| Option | Use Case |
|--------|----------|
| `-q` | Quiet: summary only, no per-group table |
| `-v` | Verbose: list each file removed during apply |
| `--debug` | Debug: show parser/grouping details (scan) |
| `--hard` | Send to OS trash instead of `_duplicates_removed/` |
| `--skip-uncertain` | Skip groups where ranking is uncertain |
| `--config PATH` | Use a specific config file |

## Next Steps

- [Full Installation Guide](installation.md) — Virtual environments, pre-commit, CI
- [Testing Guide](testing.md) — Run and write tests
- [Config Reference](config.md) — All config options
