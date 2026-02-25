"""Tests for config module."""

import json
import pathlib

import rom_deduper
from rom_deduper.cli import main


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
