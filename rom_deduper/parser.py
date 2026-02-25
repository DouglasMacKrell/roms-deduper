"""Parse ROM filenames for title, region, and language."""

import re
from dataclasses import dataclass


@dataclass
class ParseResult:
    """Result of parsing a ROM filename."""

    base_title: str
    base_title_normalized: str
    region: str | None
    languages: list[str] | None
    disc_number: int | None
    has_translation: bool
    quality: str | None


REGION_PATTERNS = [
    (r"\(USA\)", "USA"),
    (r"\(U\)", "U"),
    (r"\(Japan\)", "Japan"),
    (r"\(J\)", "J"),
    (r"\(Europe\)", "Europe"),
    (r"\(E\)", "E"),
    (r"\(World\)", "World"),
    (r"\(Australia\)", "Australia"),
    (r"\(Brazil\)", "Brazil"),
    (r"\(Asia\)", "Asia"),
]

TRANSLATION_PATTERNS = [
    r"\(En\)",
    r"\(Translation\)",
    r"\(Translated\)",
    r"\(T-[^)]+\)",
]

DISC_PATTERN = re.compile(r"\(Disc\s+(\d+)\)", re.I)
QUALITY_PATTERN = re.compile(r"\[([!bafho])\]")
LANGUAGE_PATTERN = re.compile(r"\(([A-Za-z]{2}(?:,[A-Za-z]{2})*)\)")


def _normalize_title(title: str) -> str:
    """Normalize title for comparison: lowercase, strip extra spaces."""
    t = title.strip().lower()
    return " ".join(t.split())


def parse_filename(filename: str) -> ParseResult:
    """Parse a ROM filename and extract metadata."""
    # Remove extension
    stem = filename
    if "." in filename:
        stem = filename.rsplit(".", 1)[0]

    # Extract disc number and remove from stem
    disc_number = None
    disc_match = DISC_PATTERN.search(stem)
    if disc_match:
        disc_number = int(disc_match.group(1))
        stem = DISC_PATTERN.sub("", stem).strip()

    # Extract quality tag
    quality = None
    quality_match = QUALITY_PATTERN.search(stem)
    if quality_match:
        quality = quality_match.group(1)
        stem = QUALITY_PATTERN.sub("", stem).strip()

    # Extract region (before language - region is single, language can be multi)
    region = None
    for pattern, code in REGION_PATTERNS:
        m = re.search(pattern, stem, re.I)
        if m:
            region = code
            stem = re.sub(re.escape(m.group(0)), "", stem, flags=re.I).strip()
            stem = stem.strip(" -")
            break

    # Extract languages (En,Fr,De style) - only if looks like language list, not region
    languages = None
    lang_match = LANGUAGE_PATTERN.search(stem)
    if lang_match:
        lang_str = lang_match.group(1)
        # Region codes are single (USA) or (Europe) - language lists have comma or 2-char codes
        if "," in lang_str or (len(lang_str) == 2 and lang_str.isalpha()):
            languages = [c.strip() for c in lang_str.split(",")]
            stem = LANGUAGE_PATTERN.sub("", stem, count=1).strip()
            stem = stem.strip(" -")

    # Check for translation: (En) with Japan, or explicit (Translation)/(T-*)
    has_translation = False
    for pattern in TRANSLATION_PATTERNS:
        if re.search(pattern, stem):
            has_translation = True
            break
    # (En) captured as language + Japan region = translation
    if not has_translation and region in ("J", "Japan") and languages and "En" in languages:
        has_translation = True

    # Clean up remaining parentheticals and get base title
    stem = re.sub(r"\s+", " ", stem).strip()
    stem = stem.strip(" -,")
    base_title = stem

    return ParseResult(
        base_title=base_title,
        base_title_normalized=_normalize_title(base_title),
        region=region,
        languages=languages,
        disc_number=disc_number,
        has_translation=has_translation,
        quality=quality,
    )
