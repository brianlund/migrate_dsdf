# Dreaming Spanish/French Progress Migration Tool

A Python script to migrate language learning progress between Dreaming.com accounts and languages.

## Features

- Migrate progress between any combination of Spanish (es) and French (fr)
- Supports migration between different accounts
- Supports migration between languages within the same account
- Dry-run mode to preview changes before executing
- Preserves all video metadata (duration, description, URL, type, date)

## Requirements

- Python 3.7+
- `requests` library

## Installation

```bash
pip install requests
```

## Usage

### Basic Usage (Spanish to French)

```bash
python migrate_progress.py \
  --source-token YOUR_SOURCE_TOKEN \
  --target-token YOUR_TARGET_TOKEN
```

### Specify Languages

```bash
# French to Spanish
python migrate_progress.py \
  --source-token SOURCE_TOKEN \
  --target-token TARGET_TOKEN \
  --source-language fr \
  --target-language es

# Spanish to Spanish (different accounts)
python migrate_progress.py \
  --source-token SOURCE_TOKEN \
  --target-token TARGET_TOKEN \
  --source-language es \
  --target-language es
```

### Execute Migration

By default, the script runs in dry-run mode (shows what would be migrated without making changes). To actually perform the migration, add the `--execute` flag:

```bash
python migrate_progress.py \
  --source-token SOURCE_TOKEN \
  --target-token TARGET_TOKEN \
  --source-language es \
  --target-language fr \
  --execute
```

## Getting Your Bearer Token

1. Go to https://app.dreaming.com and log in
2. Open browser DevTools (F12)
3. Go to Console tab
4. Run: `localStorage.getItem('token')`
5. Copy the token (without quotes)

## Options

- `--source-token` (required): Bearer token for the source account
- `--target-token` (required): Bearer token for the target account  
- `--source-language`: Source language code (`es` or `fr`). Default: `es`
- `--target-language`: Target language code (`es` or `fr`). Default: `fr`
- `--execute`: Actually perform the migration (omit for dry-run)

## Example Output

```
Running in DRY RUN mode (no changes will be made)

Fetching Spanish progress from source account...
Found 42 time entries
Total time: 15.25 hours (54900 seconds)

DRY RUN - showing first 5 entries that would be migrated:

1. YouTube - Dreaming Spanish: Superbeginner Video #1
   Date: 2024-01-15
   Duration: 600 seconds
   Type: watching
   URL: https://www.youtube.com/watch?v=abc123
...
```

## Notes

- The script creates new idempotency keys for each entry to avoid conflicts
- Original entry IDs are removed to let the target account generate new ones
- Progress is made every 10 entries during execution
- If you're migrating to the same account but different language, use the same token for both source and target

## License

MIT
