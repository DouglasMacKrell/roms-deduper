"""Pytest fixtures and configuration."""

from pathlib import Path

import pytest


@pytest.fixture
def tmp_roms_dir(tmp_path: Path) -> Path:
    """Create a temporary ROMs directory structure."""
    roms = tmp_path / "ROMs"
    roms.mkdir()
    return roms


@pytest.fixture
def tmp_psx_dir(tmp_roms_dir: Path) -> Path:
    """Create a psx subdirectory."""
    psx = tmp_roms_dir / "psx"
    psx.mkdir()
    return psx
