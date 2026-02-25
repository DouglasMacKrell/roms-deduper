"""CLI entry point."""

import argparse
from pathlib import Path

from rom_deduper.actions import (
    apply_removal,
    dry_run,
    format_dry_run_report,
    restore,
)


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

    apply_parser = subparsers.add_parser("apply", help="Remove duplicates")
    apply_parser.add_argument("path", type=Path, help="Path to ROMs directory")
    apply_parser.add_argument(
        "--hard",
        action="store_true",
        help="Send to OS trash instead of _duplicates_removed",
    )

    restore_parser = subparsers.add_parser("restore", help="Restore from _duplicates_removed")
    restore_parser.add_argument("path", type=Path, help="Path to ROMs directory")

    parsed = parser.parse_args(args)

    if parsed.command == "scan":
        report = dry_run(parsed.path)
        print(format_dry_run_report(report))
    elif parsed.command == "apply":
        report = dry_run(parsed.path)
        count = apply_removal(parsed.path, report, hard=parsed.hard)
        print(f"Removed {count} duplicate(s)")
    elif parsed.command == "restore":
        count = restore(parsed.path)
        print(f"Restored {count} file(s)")
