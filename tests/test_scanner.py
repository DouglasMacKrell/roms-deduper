"""Tests for scanner module."""

from pathlib import Path

from rom_deduper.config import Config
from rom_deduper.scanner import scan


def test_scan_returns_empty_list_for_empty_dir(tmp_roms_dir: Path) -> None:
    """Scanning an empty ROMs dir returns no entries."""
    result = scan(tmp_roms_dir)
    assert result == []


def test_scan_finds_chd_in_console_subdir(tmp_roms_dir: Path) -> None:
    """Scanner finds .chd files in console subdirectories."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (USA).m3u").write_text("Game (USA).chd")

    result = scan(tmp_roms_dir)
    assert len(result) >= 1
    paths = [e.path for e in result]
    assert any("Game (USA).chd" in str(p) for p in paths)


def test_scan_finds_zip_in_console_subdir(tmp_roms_dir: Path) -> None:
    """Scanner finds .zip ROM files."""
    snes = tmp_roms_dir / "snes"
    snes.mkdir()
    (snes / "ActRaiser (U) [!].zip").write_bytes(b"x")

    result = scan(tmp_roms_dir)
    paths = [e.path for e in result]
    assert any("ActRaiser (U) [!].zip" in str(p) for p in paths)


def test_scan_excludes_daphne(tmp_roms_dir: Path) -> None:
    """Scanner does not scan daphne directory."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game.chd").write_bytes(b"x")

    daphne = tmp_roms_dir / "daphne"
    daphne.mkdir()
    (daphne / "lair.daphne").mkdir()
    (daphne / "lair.daphne" / "lair.zip").write_bytes(b"x")

    result = scan(tmp_roms_dir)
    assert any(e.console == "psx" for e in result), f"Expected psx entries, got: {result}"
    assert not any(e.console == "daphne" for e in result), "daphne should be excluded"


def test_scan_excludes_singe_and_hypseus(tmp_roms_dir: Path) -> None:
    """Scanner excludes singe and hypseus directories."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game.chd").write_bytes(b"x")

    for excluded in ["singe", "hypseus"]:
        subdir = tmp_roms_dir / excluded
        subdir.mkdir()
        (subdir / "game.zip").write_bytes(b"x")

    result = scan(tmp_roms_dir)
    assert not any(e.console in ("singe", "hypseus") for e in result)


def test_scan_includes_console_name_in_entries(tmp_roms_dir: Path) -> None:
    """Each entry includes the console subdir name."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")

    result = scan(tmp_roms_dir)
    assert len(result) >= 1
    assert all(hasattr(e, "console") for e in result)
    consoles = [e.console for e in result]
    assert "psx" in consoles


def test_scan_finds_md_and_bin_files(tmp_roms_dir: Path) -> None:
    """Scanner finds .md and .bin cartridge files."""
    genesis = tmp_roms_dir / "genesis"
    genesis.mkdir()
    (genesis / "Power Drive (Europe) (En,Fr,De,Es,Pt).md").write_bytes(b"x")
    (genesis / "Power Drive.bin").write_bytes(b"x")

    result = scan(tmp_roms_dir)
    paths = [str(e.path) for e in result]
    assert any(".md" in p for p in paths)
    assert any(".bin" in p for p in paths)


def test_scan_uses_config_exclude_consoles(tmp_roms_dir: Path) -> None:
    """Scanner uses config exclude_consoles when provided."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    genesis = tmp_roms_dir / "genesis"
    genesis.mkdir()
    (genesis / "Game.md").write_bytes(b"x")
    config = Config(exclude_consoles={"psx"}, translation_patterns=[], region_priority=None)
    result = scan(tmp_roms_dir, config=config)
    assert not any(e.console == "psx" for e in result)
    assert any(e.console == "genesis" for e in result)
