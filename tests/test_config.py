"""Tests for config module."""

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


def test_placeholder() -> None:
    """Placeholder test until config is implemented."""
    assert True
