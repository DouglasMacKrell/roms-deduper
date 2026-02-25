"""Scan ROM directories for files and folders."""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rom_deduper.config import Config

ROM_EXTENSIONS = {
    ".chd",
    ".bin",
    ".cue",
    ".m3u",
    ".zip",
    ".md",
    ".sfc",
    ".nes",
    ".gb",
    ".gba",
}

EXCLUDED_CONSOLES = {"daphne", "singe", "hypseus", "ports"}
EXCLUDED_PREFIXES = (".", "_")  # Skip .venv, .git, _duplicates_removed, etc.


@dataclass
class ROMEntry:
    """A ROM file or folder entry."""

    path: Path
    console: str
    extension: str | None = None  # None for folders


def scan(roms_root: Path, config: "Config | None" = None) -> list[ROMEntry]:
    """Scan ROMs directory for ROM files, excluding daphne/singe/hypseus or config."""
    entries: list[ROMEntry] = []
    roms_root = Path(roms_root)
    excluded = config.exclude_consoles if config else EXCLUDED_CONSOLES

    if not roms_root.is_dir():
        return entries

    for console_dir in sorted(roms_root.iterdir()):
        if not console_dir.is_dir():
            continue
        if console_dir.name.lower() in excluded:
            continue
        if console_dir.name.startswith(EXCLUDED_PREFIXES):
            continue

        console = console_dir.name
        game_folders: set[Path] = set()
        for path in console_dir.rglob("*"):
            if path.is_dir():
                continue
            suffix = path.suffix.lower()
            if suffix not in ROM_EXTENSIONS:
                continue
            parent = path.parent
            if parent != console_dir and parent.name not in (".", ".."):
                has_roms = any(
                    p.suffix.lower() in ROM_EXTENSIONS for p in parent.iterdir() if p.is_file()
                )
                if has_roms:
                    game_folders.add(parent)
        added_from_folders: set[Path] = set()
        for path in console_dir.rglob("*"):
            if path.is_dir():
                continue
            if path.parent in game_folders:
                if path.parent not in added_from_folders:
                    entries.append(ROMEntry(path=path.parent, console=console, extension=None))
                    added_from_folders.add(path.parent)
                continue
            suffix = path.suffix.lower()
            if suffix in ROM_EXTENSIONS:
                entries.append(ROMEntry(path=path, console=console, extension=suffix or None))

    return entries
