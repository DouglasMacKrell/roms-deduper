"""Group ROMs by game and associate m3u/bin/cue."""

from collections import defaultdict
from dataclasses import dataclass

from rom_deduper.parser import parse_filename
from rom_deduper.scanner import ROMEntry


@dataclass
class GameGroup:
    """A group of ROM entries representing the same game within a console."""

    console: str
    base_title: str
    entries: list[ROMEntry]


def group_entries(entries: list[ROMEntry]) -> list[GameGroup]:
    """Group ROM entries by (console, normalized base title)."""
    if not entries:
        return []

    # Group by (console, base_title_normalized)
    groups_map: dict[tuple[str, str], list[ROMEntry]] = defaultdict(list)

    for entry in entries:
        parsed = parse_filename(entry.path.name)
        # For multi-disk, use base_title without Disc N for grouping
        key = (entry.console, parsed.base_title_normalized)
        groups_map[key].append(entry)

    return [
        GameGroup(
            console=console,
            base_title=base_title,
            entries=group_entries_list,
        )
        for (console, base_title), group_entries_list in sorted(groups_map.items())
    ]
