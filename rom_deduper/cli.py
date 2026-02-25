"""CLI entry point."""

import argparse
from pathlib import Path

from rom_deduper.actions import dry_run, format_dry_run_report


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

    parsed = parser.parse_args(args)

    if parsed.command == "scan":
        report = dry_run(parsed.path)
        print(format_dry_run_report(report))
