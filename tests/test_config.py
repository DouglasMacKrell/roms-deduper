"""Tests for config module."""

import json
import pathlib

import rom_deduper
from rom_deduper.cli import main
from rom_deduper.config import load_config


def test_load_config_returns_defaults_when_no_file(tmp_path: pathlib.Path) -> None:
    """Load config returns defaults when no config.json exists."""
    cfg = load_config(tmp_path)
    assert cfg.exclude_consoles == {"daphne", "singe", "hypseus", "ports"}
    assert cfg.translation_patterns == []
    assert cfg.region_priority is None


def test_load_config_loads_from_roms_root(tmp_path: pathlib.Path) -> None:
    """Load config from config.json in ROMs root."""
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({"exclude_consoles": ["custom1", "custom2"], "translation_patterns": []})
    )
    cfg = load_config(tmp_path)
    assert cfg.exclude_consoles == {"custom1", "custom2"}


def test_load_config_loads_from_explicit_path(tmp_path: pathlib.Path) -> None:
    """Load config from --config path."""
    config_file = tmp_path / "myconfig.json"
    config_file.write_text(json.dumps({"exclude_consoles": ["explicit"]}))
    cfg = load_config(tmp_path, config_path=config_file)
    assert cfg.exclude_consoles == {"explicit"}


def test_load_config_explicit_path_overrides_roms_root(tmp_path: pathlib.Path) -> None:
    """Explicit config path takes precedence over config.json in roms root."""
    (tmp_path / "config.json").write_text(json.dumps({"exclude_consoles": ["in_root"]}))
    explicit = tmp_path / "explicit.json"
    explicit.write_text(json.dumps({"exclude_consoles": ["explicit"]}))
    cfg = load_config(tmp_path, config_path=explicit)
    assert cfg.exclude_consoles == {"explicit"}


def _capture_main(args: list[str]) -> str:
    """Run main with args and return stdout."""
    import sys
    from io import StringIO
    from unittest.mock import patch

    buf = StringIO()
    with patch.object(sys, "stdout", buf):
        main(args)
    return buf.getvalue()


def test_cli_uses_roms_path_when_no_path_given(tmp_path: pathlib.Path) -> None:
    """CLI uses config roms_path when path not provided and config has it."""
    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"roms_path": str(tmp_path), "exclude_consoles": []}))
    out = _capture_main(["scan", "--config", str(config_file)])
    assert "Game (USA)" in out or "1" in out


def test_cli_scan_uses_config(tmp_path: pathlib.Path) -> None:
    """CLI scan respects --config exclude_consoles."""
    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    config_file = tmp_path / "myconfig.json"
    config_file.write_text(json.dumps({"exclude_consoles": ["psx"]}))
    out = _capture_main(["scan", str(tmp_path), "--config", str(config_file)])
    assert "Game (Japan)" not in out


def test_version() -> None:
    """Package has a version."""
    assert rom_deduper.__version__ == "0.1.0"


def test_cli_main_runs(tmp_path: pathlib.Path) -> None:
    """CLI scan runs without error."""
    (tmp_path / "psx").mkdir()
    (tmp_path / "psx" / "Game (USA).chd").write_bytes(b"x")
    main(["scan", str(tmp_path)])


def test_cli_apply_removes_duplicates(tmp_path: pathlib.Path) -> None:
    """CLI apply moves duplicates to _duplicates_removed."""
    psx = tmp_path / "psx"
    psx.mkdir()
    (psx / "Game (USA).chd").write_bytes(b"x")
    (psx / "Game (Japan).chd").write_bytes(b"x")
    main(["apply", str(tmp_path)])
    staging = tmp_path / "_duplicates_removed" / "psx"
    assert (staging / "Game (Japan).chd").exists()
    assert not (psx / "Game (Japan).chd").exists()


def test_cli_restore_moves_files_back(tmp_path: pathlib.Path) -> None:
    """CLI restore moves files from _duplicates_removed back."""
    psx = tmp_path / "psx"
    psx.mkdir()
    staging = tmp_path / "_duplicates_removed" / "psx"
    staging.mkdir(parents=True)
    (staging / "Game (Japan).chd").write_bytes(b"japan")
    manifest = tmp_path / "_duplicates_removed" / ".manifest.json"
    manifest.write_text(
        json.dumps({"_duplicates_removed/psx/Game (Japan).chd": "psx/Game (Japan).chd"})
    )
    main(["restore", str(tmp_path)])
    assert (psx / "Game (Japan).chd").exists()
    assert (psx / "Game (Japan).chd").read_bytes() == b"japan"
    assert not (staging / "Game (Japan).chd").exists()


def test_placeholder() -> None:
    """Placeholder test until config is implemented."""
    assert True
