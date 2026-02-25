"""Tests for config module."""

import rom_deduper
from rom_deduper.cli import main


def test_version() -> None:
    """Package has a version."""
    assert rom_deduper.__version__ == "0.1.0"


def test_cli_main_runs() -> None:
    """CLI main runs without error."""
    main()


def test_placeholder() -> None:
    """Placeholder test until config is implemented."""
    assert True
