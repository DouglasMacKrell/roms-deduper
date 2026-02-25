"""CLI entry point."""

import argparse
from pathlib import Path

from rich.console import Console

from rom_deduper.actions import (
    apply_removal,
    dry_run,
    format_dry_run_report,
    restore,
)


def _add_verbosity(parser: argparse.ArgumentParser) -> None:
    """Add -q and -v to a subparser."""
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", action="store_true", help="Summary only")
    group.add_argument("-v", "--verbose", action="store_true", help="Per-file details")


def main(args: list[str] | None = None) -> None:
    """Entry point for rom-deduper."""
    parser = argparse.ArgumentParser(description="Find and remove duplicate ROMs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan ROMs directory")
    scan_parser.add_argument("path", type=Path, help="Path to ROMs directory")
    scan_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Report only, do not remove (default)",
    )
    _add_verbosity(scan_parser)

    apply_parser = subparsers.add_parser("apply", help="Remove duplicates")
    apply_parser.add_argument("path", type=Path, help="Path to ROMs directory")
    apply_parser.add_argument(
        "--hard",
        action="store_true",
        help="Send to OS trash instead of _duplicates_removed",
    )
    _add_verbosity(apply_parser)

    restore_parser = subparsers.add_parser("restore", help="Restore from _duplicates_removed")
    restore_parser.add_argument("path", type=Path, help="Path to ROMs directory")
    _add_verbosity(restore_parser)

    parsed = parser.parse_args(args)

    quiet = getattr(parsed, "quiet", False)
    verbose = getattr(parsed, "verbose", False)
    console = Console()

    if parsed.command == "scan":
        report = dry_run(parsed.path)
        format_dry_run_report(report, quiet=quiet)
    elif parsed.command == "apply":
        report = dry_run(parsed.path)
        count = apply_removal(parsed.path, report, hard=parsed.hard)
        if verbose:
            for g in report.groups:
                for r in g.to_remove:
                    console.print(f"[dim]Removed:[/dim] {r.path.relative_to(parsed.path)}")
        console.print(f"[green]Removed {count} duplicate(s)[/green]")
    elif parsed.command == "restore":
        count = restore(parsed.path)
        console.print(f"[green]Restored {count} file(s)[/green]")
