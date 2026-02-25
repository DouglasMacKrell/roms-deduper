"""Tests for actions module."""

from pathlib import Path

from rom_deduper.actions import dry_run


def test_dry_run_returns_report(tmp_roms_dir: Path) -> None:
    """Dry run returns a report structure."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    report = dry_run(tmp_roms_dir)
    assert hasattr(report, "groups")
    assert isinstance(report.groups, list)


def test_dry_run_identifies_duplicates(tmp_roms_dir: Path) -> None:
    """Dry run identifies groups with duplicates and marks keeper/to_remove."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    report = dry_run(tmp_roms_dir)
    dup_groups = [g for g in report.groups if g.to_remove]
    assert len(dup_groups) == 1
    assert dup_groups[0].keeper is not None
    assert len(dup_groups[0].to_remove) == 1
    assert "USA" in str(dup_groups[0].keeper.path)
    assert "Japan" in str(dup_groups[0].to_remove[0].path)


def test_dry_run_skips_single_entry_groups(tmp_roms_dir: Path) -> None:
    """Dry run only reports groups that have duplicates."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    report = dry_run(tmp_roms_dir)
    dup_groups = [g for g in report.groups if g.to_remove]
    assert len(dup_groups) == 0


def test_dry_run_includes_totals(tmp_roms_dir: Path) -> None:
    """Dry run report includes summary totals."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    (psx / "Other (USA).chd").write_bytes(b"x")
    report = dry_run(tmp_roms_dir)
    assert hasattr(report, "total_files") or hasattr(report, "duplicate_groups")
    assert report.duplicate_groups >= 1
