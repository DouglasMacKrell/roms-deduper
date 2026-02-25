"""Dry-run, move to _duplicates_removed, trash, restore."""

import json
from dataclasses import dataclass, field
from pathlib import Path

import send2trash
from rich.console import Console
from rich.table import Table

from rom_deduper.config import Config, load_config
from rom_deduper.grouper import group_entries
from rom_deduper.ranker import rank_group
from rom_deduper.scanner import ROMEntry, scan


@dataclass
class DryRunGroup:
    """One group in a dry-run report."""

    console: str
    base_title: str
    keeper: ROMEntry | None
    to_remove: list[ROMEntry] = field(default_factory=list)
    uncertain: bool = False


@dataclass
class DryRunReport:
    """Result of a dry-run scan."""

    groups: list[DryRunGroup] = field(default_factory=list)
    total_files: int = 0
    duplicate_groups: int = 0
    total_to_remove: int = 0


def dry_run(roms_root: Path, config: Config | None = None) -> DryRunReport:
    """Scan, group, rank; return report of what would be kept/removed."""
    roms_root = Path(roms_root)
    if config is None:
        config = load_config(roms_root)
    entries = scan(roms_root, config=config)
    groups = group_entries(entries)

    report_groups: list[DryRunGroup] = []
    total_to_remove = 0

    for group in groups:
        result = rank_group(group, config=config)
        if result.to_remove:
            report_groups.append(
                DryRunGroup(
                    console=group.console,
                    base_title=group.base_title,
                    keeper=result.keeper,
                    to_remove=result.to_remove,
                    uncertain=result.uncertain,
                )
            )
            total_to_remove += len(result.to_remove)

    return DryRunReport(
        groups=report_groups,
        total_files=len(entries),
        duplicate_groups=len(report_groups),
        total_to_remove=total_to_remove,
    )


STAGING_DIR = "_duplicates_removed"
MANIFEST_FILENAME = ".manifest.json"


def _staging_path(roms_root: Path, entry: ROMEntry) -> Path:
    """Path for entry in _duplicates_removed, preserving console subdir."""
    rel = entry.path.relative_to(roms_root)
    return roms_root / STAGING_DIR / rel


def _load_manifest(roms_root: Path) -> dict[str, str]:
    """Load manifest: dest_rel -> orig_rel (both relative to roms_root)."""
    path = roms_root / STAGING_DIR / MANIFEST_FILENAME
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_manifest(roms_root: Path, manifest: dict[str, str]) -> None:
    """Save manifest."""
    staging = roms_root / STAGING_DIR
    staging.mkdir(parents=True, exist_ok=True)
    (staging / MANIFEST_FILENAME).write_text(json.dumps(manifest, indent=2))


def _expand_to_remove_with_m3u(entries: list[ROMEntry]) -> list[ROMEntry]:
    """Add .m3u files to remove when they exclusively reference entries being removed."""
    to_remove_paths = {e.path.resolve() for e in entries}
    expanded = list(entries)
    for entry in entries:
        if entry.path.suffix.lower() not in (".chd", ".bin", ".cue"):
            continue
        m3u_path = entry.path.with_suffix(".m3u")
        if not m3u_path.exists():
            continue
        if any(e.path == m3u_path for e in expanded):
            continue
        try:
            refs = [
                (m3u_path.parent / line.strip()).resolve()
                for line in m3u_path.read_text().splitlines()
                if line.strip()
            ]
        except OSError:
            continue
        if refs and all(r in to_remove_paths for r in refs):
            expanded.append(ROMEntry(path=m3u_path, console=entry.console, extension=".m3u"))
            to_remove_paths.add(m3u_path.resolve())
    return expanded


def apply_removal(
    roms_root: Path,
    report: DryRunReport,
    *,
    hard: bool = False,
    skip_uncertain: bool = False,
) -> int:
    """Apply removal: move to _duplicates_removed (or trash if hard). Returns count removed."""
    roms_root = Path(roms_root)
    count = 0
    if hard:
        for g in report.groups:
            if skip_uncertain and g.uncertain:
                continue
            to_remove = _expand_to_remove_with_m3u(g.to_remove)
            for entry in to_remove:
                send2trash.send2trash(str(entry.path))
                count += 1
        return count

    manifest = _load_manifest(roms_root)
    for g in report.groups:
        if skip_uncertain and g.uncertain:
            continue
        to_remove = _expand_to_remove_with_m3u(g.to_remove)
        for entry in to_remove:
            src = entry.path
            if not src.exists():
                continue
            dest = _staging_path(roms_root, entry)
            dest.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dest)
            dest_rel = str(dest.relative_to(roms_root)).replace("\\", "/")
            orig_rel = str(src.relative_to(roms_root)).replace("\\", "/")
            manifest[dest_rel] = orig_rel
            count += 1
    if manifest:
        _save_manifest(roms_root, manifest)
    return count


def restore(
    roms_root: Path,
    *,
    on_conflict: str = "skip",
) -> int:
    """Restore files from _duplicates_removed to originals.
    on_conflict: 'skip' (default), 'overwrite', or 'remove'.
    Returns count restored."""
    roms_root = Path(roms_root)
    manifest = _load_manifest(roms_root)
    if not manifest:
        return 0
    count = 0
    had_skip = False
    for dest_rel, orig_rel in list(manifest.items()):
        dest = roms_root / dest_rel.replace("\\", "/")
        orig = roms_root / orig_rel.replace("\\", "/")
        if not dest.exists():
            continue
        if orig.exists():
            if on_conflict == "skip":
                had_skip = True
                continue
            if on_conflict == "overwrite":
                orig.unlink()
            elif on_conflict == "remove":
                dest.unlink()
                manifest.pop(dest_rel, None)
                _save_manifest(roms_root, manifest)
                continue
        orig.parent.mkdir(parents=True, exist_ok=True)
        dest.rename(orig)
        count += 1
    manifest_path = roms_root / STAGING_DIR / MANIFEST_FILENAME
    if manifest_path.exists() and not had_skip:
        manifest_path.unlink()
    for p in sorted((roms_root / STAGING_DIR).rglob("*"), reverse=True):
        if p.is_dir() and not any(p.iterdir()):
            p.rmdir()
    if (roms_root / STAGING_DIR).exists() and not any((roms_root / STAGING_DIR).iterdir()):
        (roms_root / STAGING_DIR).rmdir()
    return count


def format_dry_run_report(
    report: DryRunReport, *, quiet: bool = False, debug: bool = False
) -> None:
    """Format and print dry-run report. Uses Rich table when not quiet."""
    from rom_deduper.parser import parse_filename

    console = Console()
    summary = (
        f"[bold]Dry Run Report[/bold]\n"
        f"Total files: {report.total_files} | "
        f"Duplicate groups: {report.duplicate_groups} | "
        f"Files to remove: {report.total_to_remove}"
    )
    console.print(summary)
    if debug and report.groups:
        console.print("\n[bold]Debug — grouping details:[/bold]")
        for g in report.groups:
            console.print(f"  [cyan]{g.console}[/cyan] [green]{g.base_title}[/green]")
            if g.keeper:
                p = parse_filename(g.keeper.path.name)
                console.print(f"    keeper: {g.keeper.path.name} (region={p.region})")
            for r in g.to_remove:
                p = parse_filename(r.path.name)
                console.print(f"    remove: {r.path.name} (region={p.region})")
    if quiet:
        return
    if not report.groups:
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("Console", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Keeper", style="green")
    table.add_column("To Remove", style="red")
    for g in report.groups:
        keeper_name = g.keeper.path.name if g.keeper else "?"
        to_remove_names = ", ".join(r.path.name for r in g.to_remove)
        uncertain = " (uncertain)" if g.uncertain else ""
        table.add_row(g.console, g.base_title + uncertain, keeper_name, to_remove_names)
    console.print(table)
