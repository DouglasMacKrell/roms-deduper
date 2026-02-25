# Config Reference

Configuration for rom-deduper via `config.json`.

## Location

- **Default**: `{roms_root}/config.json`
- **Override**: `--config /path/to/config.json`

When using `--config` without a path argument, `roms_path` from the config is used as the ROMs root.

## Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `exclude_consoles` | `string[]` | `["daphne", "singe", "hypseus", "ports"]` | Console directories to skip (case-insensitive) |
| `translation_patterns` | `string[]` | `[]` | Regex patterns for translation tags beyond built-in |
| `region_priority` | `string[]` \| `null` | `null` | Override region ranking order |
| `roms_path` | `string` \| `null` | `null` | Default ROMs path when none given on CLI |

## exclude_consoles

Consoles listed here are not scanned. Default includes daphne (LaserDisc), singe, hypseus, and ports (PortMaster-managed).

```json
{
  "exclude_consoles": ["daphne", "singe", "hypseus", "mame"]
}
```

## translation_patterns

Additional regex patterns for "has English translation" when ranking. Built-in patterns: `(En)`, `(Translation)`, `(Translated)`, `(T-*)`.

```json
{
  "translation_patterns": ["\\(CustomTL\\)", "\\(Patch\\)"]
}
```

Use escaped parentheses in JSON: `\\(` and `\\)` for literal parens in the regex.

## region_priority

Override the default region ranking. First in list = highest priority.

Default order (when `null`): USA/U > World > Europe > Japan > ...

```json
{
  "region_priority": ["Japan", "USA", "Europe"]
}
```

With this config, Japan versions are preferred over USA.

## roms_path

Default path when no path is given on the CLI. Requires `--config` to be used.

```json
{
  "roms_path": "/media/retro/ROMs"
}
```

Then: `rom-deduper scan --config /path/to/config.json` uses `/media/retro/ROMs`.

## Example

See [config.example.json](../config.example.json) in the project root.
