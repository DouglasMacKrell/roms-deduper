"""Tests for grouper module."""

from pathlib import Path

from rom_deduper.grouper import group_entries
from rom_deduper.scanner import scan


def test_group_empty_returns_empty() -> None:
    """Grouping no entries returns no groups."""
    assert group_entries([]) == []


def test_group_single_entry_single_group(tmp_roms_dir: Path) -> None:
    """Single ROM becomes one group."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    assert len(groups) == 1
    assert len(groups[0].entries) == 1


def test_group_same_game_different_regions(tmp_roms_dir: Path) -> None:
    """USA and Japan versions of same game group together."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    assert len(groups) == 1
    assert len(groups[0].entries) == 2


def test_group_different_consoles_separate(tmp_roms_dir: Path) -> None:
    """Same game name in different consoles are separate groups."""
    psx = tmp_roms_dir / "psx"
    snes = tmp_roms_dir / "snes"
    psx.mkdir()
    snes.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (snes / "Game (USA).zip").write_bytes(b"x")
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    assert len(groups) == 2


def test_group_multidisk_same_group(tmp_roms_dir: Path) -> None:
    """Multi-disk game (Disc 1, Disc 2) groups together."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "X-Files, The (USA) (Disc 1).chd").write_bytes(b"x")
    (psx / "X-Files, The (USA) (Disc 2).chd").write_bytes(b"x")
    (psx / "X-Files, The (USA) (Disc 3).chd").write_bytes(b"x")
    m3u_content = "X-Files, The (USA) (Disc 1).chd\nX-Files, The (USA) (Disc 2).chd"
    (psx / "X-Files, The (USA).m3u").write_text(m3u_content)
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    assert len(groups) == 1
    assert len(groups[0].entries) >= 3  # 3 discs + m3u


def test_group_associates_bin_cue(tmp_roms_dir: Path) -> None:
    """bin and cue with same stem are associated."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).bin").write_bytes(b"x")
    (psx / "Game (USA).cue").write_bytes(b"x")
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    assert len(groups) == 1
    # Both bin and cue in same group
    paths = [e.path.name for e in groups[0].entries]
    assert "Game (USA).bin" in paths
    assert "Game (USA).cue" in paths
