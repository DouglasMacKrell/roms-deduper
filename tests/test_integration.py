"""End-to-end integration tests."""

import pathlib
import sys
from io import StringIO
from unittest.mock import patch

from rom_deduper.cli import main


def test_e2e_scan_apply_restore_flow(tmp_path: pathlib.Path) -> None:
    """Full flow: scan reports duplicates, apply moves them, restore brings them back."""
    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"usa")
    (psx / "Game (Japan).chd").write_bytes(b"japan")

    # Scan: dry run reports duplicates
    main(["scan", str(tmp_path)])
    assert (psx / "Game (USA).chd").exists()
    assert (psx / "Game (Japan).chd").exists()

    # Apply: moves Japan to staging
    main(["apply", str(tmp_path)])
    staging = tmp_path / "_duplicates_removed" / "psx"
    assert (staging / "Game (Japan).chd").exists()
    assert not (psx / "Game (Japan).chd").exists()
    assert (psx / "Game (USA).chd").exists()

    # Restore: brings Japan back
    main(["restore", str(tmp_path)])
    assert (psx / "Game (Japan).chd").exists()
    assert (psx / "Game (Japan).chd").read_bytes() == b"japan"
    assert not (staging / "Game (Japan).chd").exists()
    assert not (tmp_path / "_duplicates_removed" / ".manifest.json").exists()


def test_e2e_apply_hard_removes_files(tmp_path: pathlib.Path) -> None:
    """Apply with --hard sends to trash (mocked) and removes files."""
    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")

    def fake_trash(path: str) -> None:
        pathlib.Path(path).unlink()

    with patch("rom_deduper.actions.send2trash.send2trash", side_effect=fake_trash):
        main(["apply", str(tmp_path), "--hard"])

    assert not (psx / "Game (Japan).chd").exists()
    assert (psx / "Game (USA).chd").exists()
    assert not (tmp_path / "_duplicates_removed").exists()


def test_e2e_restore_empty_noop(tmp_path: pathlib.Path) -> None:
    """Restore with no manifest does nothing and does not error."""
    main(["restore", str(tmp_path)])
    assert True


def _capture_main(args: list[str]) -> str:
    """Run main with args and return stdout."""
    buf = StringIO()
    with patch.object(sys, "stdout", buf):
        main(args)
    return buf.getvalue()


def test_cli_scan_quiet_shows_summary_only(tmp_path: pathlib.Path) -> None:
    """Scan with -q shows summary, not per-group details."""
    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    out = _capture_main(["scan", str(tmp_path), "-q"])
    assert "Total files" in out or "Files to remove" in out
    assert "KEEP:" not in out
    assert "REMOVE:" not in out


def test_cli_scan_default_shows_full_report(tmp_path: pathlib.Path) -> None:
    """Scan without -q shows full report with keeper and to-remove files."""
    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    out = _capture_main(["scan", str(tmp_path)])
    assert "Game (USA)" in out
    assert "Game (Japan)" in out


def test_cli_apply_quiet_shows_count_only(tmp_path: pathlib.Path) -> None:
    """Apply with -q shows removal count and bytes saved."""
    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    out = _capture_main(["apply", str(tmp_path), "-q"])
    assert "Removed" in out
    assert "1" in out or "duplicate" in out
    assert "saved" in out


def test_cli_apply_verbose_lists_removed_files(tmp_path: pathlib.Path) -> None:
    """Apply with -v lists each file removed."""
    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    out = _capture_main(["apply", str(tmp_path), "-v"])
    assert "Game (Japan)" in out
    assert "Removed" in out or "removed" in out


def test_e2e_scan_with_config_excludes_consoles(tmp_path: pathlib.Path) -> None:
    """Scan with --config excludes consoles per config."""
    import json

    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"exclude_consoles": ["psx"]}))
    out = _capture_main(["scan", str(tmp_path), "--config", str(cfg)])
    assert "Game (Japan)" not in out
    assert "0" in out or "Files to remove" in out


def test_e2e_restore_on_conflict_overwrite(tmp_path: pathlib.Path) -> None:
    """Restore with --on-conflict overwrite replaces existing file."""
    import json

    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (Japan).chd").write_bytes(b"existing")
    staging = tmp_path / "_duplicates_removed" / "psx"
    staging.mkdir(parents=True)
    (staging / "Game (Japan).chd").write_bytes(b"staged")
    manifest = tmp_path / "_duplicates_removed" / ".manifest.json"
    manifest.write_text(
        json.dumps({"_duplicates_removed/psx/Game (Japan).chd": "psx/Game (Japan).chd"})
    )
    main(["restore", str(tmp_path), "--on-conflict", "overwrite"])
    assert (psx / "Game (Japan).chd").read_bytes() == b"staged"


def test_e2e_apply_skip_uncertain_preserves_files(tmp_path: pathlib.Path) -> None:
    """Apply with --skip-uncertain does not remove when group is uncertain."""
    from rom_deduper.actions import dry_run

    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")

    def dry_run_uncertain(roms_root, config=None):
        r = dry_run(roms_root, config)
        if r.groups:
            r.groups[0].uncertain = True
        return r

    with patch("rom_deduper.cli.dry_run", side_effect=dry_run_uncertain):
        main(["apply", str(tmp_path), "--skip-uncertain"])
    assert (psx / "Game (Japan).chd").exists()


def test_e2e_config_region_priority_affects_ranking(tmp_path: pathlib.Path) -> None:
    """Config region_priority overrides default (Japan > USA when configured)."""
    import json

    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps(
            {
                "exclude_consoles": [],
                "region_priority": ["Japan", "USA"],
            }
        )
    )
    main(["apply", str(tmp_path), "--config", str(cfg)])
    staging = tmp_path / "_duplicates_removed" / "psx"
    assert (staging / "Game (USA).chd").exists()
    assert (psx / "Game (Japan).chd").exists()


def test_cli_scan_debug_shows_extra_info(tmp_path: pathlib.Path) -> None:
    """Scan with --debug shows grouping/parser details."""
    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    out = _capture_main(["scan", str(tmp_path), "--debug"])
    assert "Game (USA)" in out or "game" in out.lower()
    assert "debug" in out.lower() or "group" in out.lower() or "console" in out.lower()
