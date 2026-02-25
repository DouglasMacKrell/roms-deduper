"""Apply region/language priority rules to select keepers."""

from dataclasses import dataclass

from rom_deduper.grouper import GameGroup
from rom_deduper.parser import parse_filename
from rom_deduper.scanner import ROMEntry

# Region priority: higher = better. USA/U highest.
REGION_SCORE = {
    "USA": 100,
    "U": 100,
    "World": 90,
    "USA, Europe": 85,
    "Japan, USA": 85,
    "Europe": 70,
    "E": 70,
    "Australia": 65,
    "Brazil": 60,
    "Asia": 50,
    "Japan": 40,
    "J": 40,
    "China": 30,
    "Korea": 30,
    "Hong Kong": 25,
}

# Format preference: .chd > .bin/.cue, .md > .bin
PREFERRED_EXTENSIONS = {".chd", ".md", ".zip", ".sfc", ".nes", ".gb", ".gba"}
SECONDARY_EXTENSIONS = {".cue"}  # .cue preferred over .bin when paired


@dataclass
class RankResult:
    """Result of ranking a game group."""

    keeper: ROMEntry | None
    to_remove: list[ROMEntry]
    uncertain: bool = False


def _score_entry(entry: ROMEntry) -> tuple[int, int, int, int, int]:
    """Score entry for ranking. Higher is better.
    Returns (region, format, quality, version, size)."""
    parsed = parse_filename(entry.path.name)
    region_score = REGION_SCORE.get(parsed.region or "", 0)

    # Translation bonus for Japan
    if parsed.region in ("J", "Japan") and parsed.has_translation:
        region_score += 30

    # Europe with En
    if parsed.region in ("Europe", "E") and parsed.languages and "En" in parsed.languages:
        region_score += 10

    # Format score
    ext = (entry.extension or "").lower()
    if ext in PREFERRED_EXTENSIONS:
        format_score = 100
    elif ext in SECONDARY_EXTENSIONS:
        format_score = 80
    elif ext == ".bin":
        format_score = 50
    else:
        format_score = 70

    # Quality: ! = 100, b = 0, else 50
    quality_score = 50
    if parsed.quality == "!":
        quality_score = 100
    elif parsed.quality == "b":
        quality_score = 0

    # Version: prefer newer
    version_score = 0
    if parsed.version:
        try:
            version_score = int(parsed.version.split(".")[0])
        except (ValueError, AttributeError):
            version_score = 0

    # File size (use 0 as placeholder, we'll use actual size)
    try:
        size = entry.path.stat().st_size
    except OSError:
        size = 0

    return (region_score, format_score, quality_score, version_score, size)


def rank_group(group: GameGroup) -> RankResult:
    """Rank entries in a group and select keeper. Returns keeper and to_remove list."""
    if len(group.entries) == 1:
        return RankResult(keeper=group.entries[0], to_remove=[])

    scored = [(entry, _score_entry(entry)) for entry in group.entries]
    scored.sort(key=lambda x: x[1], reverse=True)

    keeper = scored[0][0]
    to_remove = [e for e, _ in scored[1:]]

    # Check for tie (same score)
    uncertain = len(scored) > 1 and scored[0][1] == scored[1][1]

    return RankResult(keeper=keeper, to_remove=to_remove, uncertain=uncertain)
