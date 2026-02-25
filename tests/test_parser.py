"""Tests for parser module."""

from rom_deduper.parser import parse_filename


def test_parse_extracts_usa_region() -> None:
    """Parser extracts (USA) region."""
    result = parse_filename("Game (USA).chd")
    assert result.region == "USA"


def test_parse_extracts_u_region() -> None:
    """Parser extracts (U) GoodROM-style region."""
    result = parse_filename("ActRaiser (U) [!].zip")
    assert result.region == "U"


def test_parse_extracts_japan_region() -> None:
    """Parser extracts (Japan) and (J) regions."""
    assert parse_filename("Game (Japan).chd").region == "Japan"
    assert parse_filename("Game (J).chd").region == "J"


def test_parse_extracts_base_title() -> None:
    """Parser extracts base title without region/language tags."""
    result = parse_filename("X-COM - UFO Defense (USA).chd")
    assert result.base_title == "X-COM - UFO Defense"


def test_parse_normalizes_article_reordering() -> None:
    """Parser handles 'The X' -> 'X, The' style."""
    result = parse_filename("Legend of Zelda, The (USA).nes")
    assert "Legend" in result.base_title and "Zelda" in result.base_title


def test_parse_extracts_disc_number() -> None:
    """Parser strips (Disc N) from base title."""
    result = parse_filename("X-Files, The (USA) (Disc 1).chd")
    assert "Disc" not in result.base_title
    assert result.disc_number == 1


def test_parse_extracts_language_tags() -> None:
    """Parser extracts (En), (En,Fr,De) style language tags."""
    result = parse_filename("Power Drive (Europe) (En,Fr,De,Es,Pt).md")
    assert "En" in (result.languages or [])
    assert result.region == "Europe"


def test_parse_extracts_translation_tag() -> None:
    """Parser recognizes (En), (Translation), (T-En) as translation."""
    r1 = parse_filename("Shin Megami Tensei (J) (En).chd")
    assert r1.has_translation is True

    r2 = parse_filename("Game (Japan) (Translation).chd")
    assert r2.has_translation is True


def test_parse_extracts_quality_tag() -> None:
    """Parser extracts [!] Good Dump and [b] Bad tags."""
    r1 = parse_filename("ActRaiser (U) [!].zip")
    assert r1.quality == "!"

    r2 = parse_filename("Game (USA) [b].chd")
    assert r2.quality == "b"


def test_parse_handles_no_region() -> None:
    """Parser handles filename with no region tag."""
    result = parse_filename("Power Drive.bin")
    assert result.region is None
    assert result.base_title == "Power Drive"


def test_parse_base_title_normalization_matches_same_game() -> None:
    """Different region variants normalize to same base title."""
    r1 = parse_filename("Game (USA).chd")
    r2 = parse_filename("Game (Japan).chd")
    assert r1.base_title_normalized == r2.base_title_normalized
