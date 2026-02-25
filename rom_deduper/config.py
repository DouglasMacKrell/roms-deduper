"""Load config and region priority."""

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_EXCLUDED_CONSOLES = {"daphne", "singe", "hypseus"}


@dataclass
class Config:
    """ROM deduper configuration."""

    exclude_consoles: set[str]
    translation_patterns: list[str]
    region_priority: list[str] | None
    roms_path: Path | None = None

    @classmethod
    def default(cls) -> "Config":
        """Return default configuration."""
        return cls(
            exclude_consoles=set(DEFAULT_EXCLUDED_CONSOLES),
            translation_patterns=[],
            region_priority=None,
        )


def load_config(roms_root: Path, config_path: Path | None = None) -> Config:
    """Load config from config.json or explicit path. Returns defaults if not found."""
    roms_root = Path(roms_root)
    to_load: Path | None = None
    if config_path is not None:
        to_load = Path(config_path) if config_path.exists() else None
    elif (roms_root / "config.json").exists():
        to_load = roms_root / "config.json"
    if to_load is None:
        return Config.default()
    data = json.loads(to_load.read_text())
    exclude = data.get("exclude_consoles")
    if exclude is not None:
        exclude_set = {str(c).lower() for c in exclude}
    else:
        exclude_set = set(DEFAULT_EXCLUDED_CONSOLES)
    return Config(
        exclude_consoles=exclude_set,
        translation_patterns=data.get("translation_patterns") or [],
        region_priority=data.get("region_priority"),
        roms_path=Path(data["roms_path"]) if data.get("roms_path") else None,
    )
