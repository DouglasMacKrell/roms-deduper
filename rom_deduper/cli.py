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
from rom_deduper.config import load_config, load_config_from_file


def _add_verbosity(parser: argparse.ArgumentParser) -> None:
    """Add -q, -v, and --debug to a subparser."""
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", action="store_true", help="Summary only")
    group.add_argument("-v", "--verbose", action="store_true", help="Per-file details")
    group.add_argument("--debug", action="store_true", help="Parser and grouping details")


def main(args: list[str] | None = None) -> None:
    """Entry point for rom-deduper."""
    parser = argparse.ArgumentParser(description="Find and remove duplicate ROMs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_config_arg(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--config",
            type=Path,
            default=None,
            help="Path to config.json (default: roms_root/config.json)",
        )

    scan_parser = subparsers.add_parser("scan", help="Scan ROMs directory")
    scan_parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=None,
        help="Path to ROMs directory (default: from config roms_path)",
    )
    add_config_arg(scan_parser)
    scan_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Report only, do not remove (default)",
    )
    _add_verbosity(scan_parser)

    apply_parser = subparsers.add_parser("apply", help="Remove duplicates")
    apply_parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=None,
        help="Path to ROMs directory (default: from config roms_path)",
    )
    add_config_arg(apply_parser)
    apply_parser.add_argument(
        "--hard",
        action="store_true",
        help="Send to OS trash instead of _duplicates_removed",
    )
    apply_parser.add_argument(
        "--skip-uncertain",
        action="store_true",
        help="Skip groups with uncertain ranking (manual review recommended)",
    )
    _add_verbosity(apply_parser)

    restore_parser = subparsers.add_parser("restore", help="Restore from _duplicates_removed")
    restore_parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=None,
        help="Path to ROMs directory (default: from config roms_path)",
    )
    restore_parser.add_argument(
        "--on-conflict",
        choices=["skip", "overwrite", "remove"],
        default="skip",
        help="When original path exists: skip (default), overwrite, or remove from duplicates",
    )
    add_config_arg(restore_parser)
    _add_verbosity(restore_parser)

    parsed = parser.parse_args(args)

    quiet = getattr(parsed, "quiet", False)
    verbose = getattr(parsed, "verbose", False)
    debug = getattr(parsed, "debug", False)
    console = Console()
    config_path = getattr(parsed, "config", None)
    if parsed.path is not None:
        config = load_config(parsed.path, config_path=config_path)
        roms_path = parsed.path
    elif config_path and Path(config_path).exists():
        config = load_config_from_file(Path(config_path))
        roms_path = config.roms_path
        if roms_path is None:
            console.print("[red]Error: path required when config has no roms_path[/red]")
            raise SystemExit(1)
    else:
        console.print("[red]Error: path required (or use --config with roms_path)[/red]")
        raise SystemExit(1)

    if parsed.command == "scan":
        report = dry_run(roms_path, config=config)
        format_dry_run_report(report, quiet=quiet, debug=debug)
    elif parsed.command == "apply":
        report = dry_run(roms_path, config=config)
        count = apply_removal(
            roms_path,
            report,
            hard=parsed.hard,
            skip_uncertain=getattr(parsed, "skip_uncertain", False),
        )
        if verbose:
            for g in report.groups:
                for r in g.to_remove:
                    console.print(f"[dim]Removed:[/dim] {r.path.relative_to(roms_path)}")
        console.print(f"[green]Removed {count} duplicate(s)[/green]")
    elif parsed.command == "restore":
        count = restore(roms_path, on_conflict=parsed.on_conflict)
        console.print(f"[green]Restored {count} file(s)[/green]")
