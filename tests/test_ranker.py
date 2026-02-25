"""Tests for ranker module."""

from pathlib import Path

from rom_deduper.grouper import group_entries
from rom_deduper.ranker import rank_group
from rom_deduper.scanner import scan


def test_rank_single_entry_keeps_it(tmp_roms_dir: Path) -> None:
    """Single entry in group: keep it, nothing to remove."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    result = rank_group(groups[0])
    assert result.keeper is not None
    assert result.to_remove == []
    assert "Game (USA)" in str(result.keeper.path)


def test_rank_prefers_usa_over_japan(tmp_roms_dir: Path) -> None:
    """USA version preferred over Japan."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    result = rank_group(groups[0])
    assert result.keeper is not None
    assert "USA" in str(result.keeper.path)
    assert len(result.to_remove) == 1
    assert "Japan" in str(result.to_remove[0].path)


def test_rank_prefers_u_over_e(tmp_roms_dir: Path) -> None:
    """(U) preferred over (E) GoodROM style."""
    snes = tmp_roms_dir / "snes"
    snes.mkdir()
    (snes / "Game (U) [!].zip").write_bytes(b"x")
    (snes / "Game (E).zip").write_bytes(b"x")
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    result = rank_group(groups[0])
    assert result.keeper is not None
    assert "(U)" in str(result.keeper.path) or "U)" in str(result.keeper.path)


def test_rank_prefers_quality_tag(tmp_roms_dir: Path) -> None:
    """When region ties, prefer [!] over no tag or [b]."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (USA) [!].chd").write_bytes(b"x")
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    result = rank_group(groups[0])
    assert result.keeper is not None
    assert "[!]" in str(result.keeper.path)


def test_rank_prefers_larger_file_when_tied(tmp_roms_dir: Path) -> None:
    """When region/quality tie, prefer larger file."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    # Same region, same quality - file size breaks tie
    small = psx / "Game (USA) (Rev 1).chd"
    large = psx / "Game (USA) (Rev 2).chd"
    small.write_bytes(b"x" * 50)
    large.write_bytes(b"x" * 100)
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    result = rank_group(groups[0])
    assert result.keeper is not None
    assert result.keeper.path.stat().st_size == 100


def test_rank_prefers_chd_over_bin_cue(tmp_roms_dir: Path) -> None:
    """Prefer .chd over .bin/.cue for disc-based."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (USA).bin").write_bytes(b"x")
    (psx / "Game (USA).cue").write_bytes(b"x")
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    result = rank_group(groups[0])
    assert result.keeper is not None
    assert result.keeper.path.suffix.lower() == ".chd"


def test_rank_prefers_md_over_bin(tmp_roms_dir: Path) -> None:
    """Prefer .md over .bin for cartridge (Genesis)."""
    genesis = tmp_roms_dir / "genesis"
    genesis.mkdir()
    (genesis / "Game (USA).md").write_bytes(b"x")
    (genesis / "Game (USA).bin").write_bytes(b"x")
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    result = rank_group(groups[0])
    assert result.keeper is not None
    assert result.keeper.path.suffix.lower() == ".md"


def test_rank_japan_with_translation_over_japan_only(tmp_roms_dir: Path) -> None:
    """Japan + (En) translation preferred over Japan only."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (Japan).chd").write_bytes(b"x")
    (psx / "Game (J) (En).chd").write_bytes(b"x")
    entries = scan(tmp_roms_dir)
    groups = group_entries(entries)
    result = rank_group(groups[0])
    assert result.keeper is not None
    assert "En" in str(result.keeper.path) or "(En)" in str(result.keeper.path)
