# rom-deduper

Find and remove duplicate ROM files across console subdirectories, with preference for USA and English language versions.

## Features

- **Scan** console subdirectories (psx, genesis, snes, etc.) for ROM files
- **Group** duplicates by normalized game title within each console
- **Rank** by region (USA > Europe > Japan), format (.chd > .bin), quality [!], and language
- **Soft delete** to `_duplicates_removed/` by default; `--hard` sends to OS trash
- **Restore** from `_duplicates_removed/` back to originals
- **Config** via `config.json` or `--config` for exclude_consoles, region_priority, translation_patterns
- **Excludes** Daphne (LaserDisc), singe, hypseus, ports (PortMaster-managed), and dirs starting with `.` or `_`
- **Handles** multi-disk games (keeps all discs of same region; never removes sibling discs), .m3u playlists, .bin/.cue pairs, game folders as units
- **Keeps** .m3u playlists (never treats them as duplicates); removes orphan .m3u when they exclusively reference removed ROMs

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Scan (dry run, report only)
rom-deduper scan /path/to/ROMs

# Apply removal
rom-deduper apply /path/to/ROMs

# Restore if needed
rom-deduper restore /path/to/ROMs
```

See [docs/quick-start.md](docs/quick-start.md) for a guided walkthrough.

## Installation

```bash
pip install -e ".[dev]"
pre-commit install --install-hooks
```

Requires Python 3.10+. See [docs/installation.md](docs/installation.md) for full details.

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `scan [path]` | Report duplicates (dry run). Path optional if `roms_path` in config |
| `apply [path]` | Remove duplicates to `_duplicates_removed/` or trash |
| `restore [path]` | Restore files from `_duplicates_removed/` |

### Options

**Common**

- `--config PATH` — Path to config.json
- `-q, --quiet` — Summary only
- `-v, --verbose` — Per-file details
- `--debug` — Parser and grouping details (scan only)

**apply**

- `--hard` — Send to OS trash instead of `_duplicates_removed/`
- `--skip-uncertain` — Skip groups with uncertain ranking

**restore**

- `--on-conflict {skip,overwrite,remove}` — When original exists: skip (default), overwrite, or remove from duplicates

### Examples

```bash
# Scan with verbose output
rom-deduper scan /path/to/ROMs -v

# Apply with config, skip uncertain groups
rom-deduper apply /path/to/ROMs --config ./myconfig.json --skip-uncertain

# Restore, overwrite when original exists
rom-deduper restore /path/to/ROMs --on-conflict overwrite

# Use roms_path from config (no path)
rom-deduper scan --config /path/to/config.json
```

## Config

Optional `config.json` in ROMs root or via `--config`:

```json
{
  "exclude_consoles": ["daphne", "singe", "hypseus"],
  "translation_patterns": [],
  "region_priority": null,
  "roms_path": null
}
```

| Key | Description |
|-----|-------------|
| `exclude_consoles` | Console dirs to skip (case-insensitive) |
| `translation_patterns` | Regex list for translation tags beyond built-in `(En)`, `(Translation)`, `(T-*)` |
| `region_priority` | Override region order, e.g. `["Japan", "USA"]` |
| `roms_path` | Default ROMs path when none given on CLI |

Copy `config.example.json` as a starting point.

## Development

```bash
pytest
pytest --cov=rom_deduper --cov-fail-under=80
ruff check rom_deduper tests
ruff format rom_deduper tests
pyright rom_deduper tests
```

See [docs/testing.md](docs/testing.md) for full test documentation.

## Documentation

- [Quick Start](docs/quick-start.md) — Guided walkthrough
- [Installation](docs/installation.md) — Full install guide
- [Testing](docs/testing.md) — How to run tests
- [Config Reference](docs/config.md) — Config options
- [Technology Stack](docs/technology.md) — Tools and libraries used, and why

## License

MIT
