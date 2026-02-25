# rom-deduper

Find and remove duplicate ROM files across console subdirectories, with preference for USA and English language versions.

## Features

- Scans console subdirectories (psx, genesis, snes, etc.)
- Groups duplicates by normalized game title
- Ranks by region (USA > Europe > Japan) and language (English preferred)
- Soft delete to `_duplicates_removed/` by default; `--hard` sends to trash
- `--restore` to move files back from `_duplicates_removed/`
- Excludes Daphne (LaserDisc) and related folders
- Handles multi-disk games, .m3u playlists, .bin/.cue pairs

## Setup

```bash
pip install -e ".[dev]"
pre-commit install --install-hooks
```

## Usage

```bash
rom-deduper scan /path/to/ROMs --dry-run   # Report only (default)
rom-deduper apply /path/to/ROMs            # Remove duplicates
rom-deduper restore /path/to/ROMs         # Restore from _duplicates_removed
```

## Config

Optional `config.json` (next to ROMs root or via `--config`):

```json
{
  "exclude_consoles": ["daphne", "singe", "hypseus"],
  "translation_patterns": [],
  "region_priority": null,
  "roms_path": null
}
```

## Development

```bash
pytest
pytest --cov=rom_deduper --cov-fail-under=80
ruff check .
ruff format .
```
