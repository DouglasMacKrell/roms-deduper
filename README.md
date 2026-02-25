# rom-deduper

Find and remove duplicate ROM files across console subdirectories, with preference for USA and English language versions.

## Setup

```bash
pip install -e .
pre-commit install --install-hooks
```

## Usage

```bash
rom-deduper scan /path/to/ROMs --dry-run   # Report only
rom-deduper apply /path/to/ROMs            # Remove duplicates
rom-deduper restore /path/to/ROMs          # Restore from _duplicates_removed
```
