"""Scan ROM directories for files and folders."""

from dataclasses import dataclass
from pathlib import Path

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

EXCLUDED_CONSOLES = {"daphne", "singe", "hypseus"}
EXCLUDED_PREFIXES = (".", "_")  # Skip .venv, .git, _duplicates_removed, etc.


@dataclass
class ROMEntry:
    """A ROM file or folder entry."""

    path: Path
    console: str
    extension: str | None = None  # None for folders


def scan(roms_root: Path) -> list[ROMEntry]:
    """Scan ROMs directory for ROM files, excluding daphne/singe/hypseus."""
    entries: list[ROMEntry] = []
    roms_root = Path(roms_root)

    if not roms_root.is_dir():
        return entries

    for console_dir in sorted(roms_root.iterdir()):
        if not console_dir.is_dir():
            continue
        if console_dir.name.lower() in EXCLUDED_CONSOLES:
            continue
        if console_dir.name.startswith(EXCLUDED_PREFIXES):
            continue

        console = console_dir.name
        for path in console_dir.rglob("*"):
            if path.is_dir():
                continue
            suffix = path.suffix.lower()
            if suffix in ROM_EXTENSIONS:
                entries.append(ROMEntry(path=path, console=console, extension=suffix or None))

    return entries
