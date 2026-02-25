"""Dry-run, move to _duplicates_removed, trash, restore."""

from dataclasses import dataclass, field
from pathlib import Path

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


def dry_run(roms_root: Path) -> DryRunReport:
    """Scan, group, rank; return report of what would be kept/removed."""
    entries = scan(Path(roms_root))
    groups = group_entries(entries)

    report_groups: list[DryRunGroup] = []
    total_to_remove = 0

    for group in groups:
        result = rank_group(group)
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


def format_dry_run_report(report: DryRunReport) -> str:
    """Format dry-run report as human-readable text."""
    lines = [
        "=== Dry Run Report ===",
        f"Total files: {report.total_files}",
        f"Duplicate groups: {report.duplicate_groups}",
        f"Files to remove: {report.total_to_remove}",
        "",
    ]
    for g in report.groups:
        lines.append(f"[{g.console}] {g.base_title}")
        lines.append(f"  KEEP: {g.keeper.path.name if g.keeper else '?'}")
        for r in g.to_remove:
            lines.append(f"  REMOVE: {r.path.name}")
        if g.uncertain:
            lines.append("  (uncertain - manual review recommended)")
        lines.append("")
    return "\n".join(lines)
