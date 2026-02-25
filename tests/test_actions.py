"""Tests for actions module."""

import json
from pathlib import Path
from unittest.mock import patch

from rom_deduper.actions import apply_removal, dry_run, restore


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


def test_apply_removal_moves_to_staging(tmp_roms_dir: Path) -> None:
    """Apply removal moves duplicates to _duplicates_removed preserving structure."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"usa")
    (psx / "Game (Japan).chd").write_bytes(b"japan")
    report = dry_run(tmp_roms_dir)
    apply_removal(tmp_roms_dir, report, hard=False)
    staging = tmp_roms_dir / "_duplicates_removed" / "psx"
    assert (staging / "Game (Japan).chd").exists()
    assert (staging / "Game (Japan).chd").read_bytes() == b"japan"
    assert not (psx / "Game (Japan).chd").exists()
    assert (psx / "Game (USA).chd").exists()


def test_apply_removal_creates_manifest(tmp_roms_dir: Path) -> None:
    """Apply removal creates manifest mapping moved files to originals."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    report = dry_run(tmp_roms_dir)
    apply_removal(tmp_roms_dir, report, hard=False)
    manifest_path = tmp_roms_dir / "_duplicates_removed" / ".manifest.json"
    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text())
    assert "psx/Game (Japan).chd" in data.values() or any(
        "Game (Japan)" in v for v in data.values()
    )


def test_apply_removal_merge_manifest(tmp_roms_dir: Path) -> None:
    """Subsequent apply merges new entries into existing manifest."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    report1 = dry_run(tmp_roms_dir)
    apply_removal(tmp_roms_dir, report1, hard=False)
    (psx / "Other (USA).chd").write_bytes(b"x")
    (psx / "Other (Japan).chd").write_bytes(b"x")
    report2 = dry_run(tmp_roms_dir)
    apply_removal(tmp_roms_dir, report2, hard=False)
    manifest_path = tmp_roms_dir / "_duplicates_removed" / ".manifest.json"
    data = json.loads(manifest_path.read_text())
    assert len(data) >= 2


def test_apply_removal_hard_uses_send2trash(tmp_roms_dir: Path) -> None:
    """Apply removal with hard=True sends files to trash via send2trash."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    report = dry_run(tmp_roms_dir)

    def fake_trash(path: str) -> None:
        Path(path).unlink()

    with patch("rom_deduper.actions.send2trash.send2trash", side_effect=fake_trash) as mock_send:
        apply_removal(tmp_roms_dir, report, hard=True)
        assert mock_send.call_count >= 1
        assert not (psx / "Game (Japan).chd").exists()


def test_restore_moves_files_back(tmp_roms_dir: Path) -> None:
    """Restore moves files from _duplicates_removed back to originals."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    staging = tmp_roms_dir / "_duplicates_removed" / "psx"
    staging.mkdir(parents=True)
    (staging / "Game (Japan).chd").write_bytes(b"japan")
    manifest = tmp_roms_dir / "_duplicates_removed" / ".manifest.json"
    manifest.write_text(
        json.dumps({"_duplicates_removed/psx/Game (Japan).chd": "psx/Game (Japan).chd"})
    )
    restore(tmp_roms_dir)
    assert (psx / "Game (Japan).chd").exists()
    assert (psx / "Game (Japan).chd").read_bytes() == b"japan"
    assert not (staging / "Game (Japan).chd").exists()
    assert not manifest.exists()


def test_restore_skips_missing_files(tmp_roms_dir: Path) -> None:
    """Restore skips manifest entries when file is missing in _duplicates_removed."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    staging_dir = tmp_roms_dir / "_duplicates_removed"
    staging_dir.mkdir()
    manifest = staging_dir / ".manifest.json"
    manifest.write_text(json.dumps({"_duplicates_removed/psx/Missing.chd": "psx/Missing.chd"}))
    restore(tmp_roms_dir)
    assert not (psx / "Missing.chd").exists()
    assert not manifest.exists()
