# Obsidian Plugin

Interact with Obsidian/wiki notes and generate AI-powered daily summaries.

## Features

- **Daily Summary Generation**: Analyze daily notes and backlog to produce work summaries and tomorrow's priorities
- **Daily Note Cleanup**: Clean up and organize daily notes with AI assistance
- **Smart Date Deduction**: Automatically determines target date based on time of day

## Configuration

Copy `config.yml.example` to `config.yml` and customize:

```yaml
variables:
  # Path to your Obsidian wiki/vault
  wiki_path: ~/work/personal/local/jcran.wiki
  
  # Subdirectory containing daily notes
  daily_notes_subdir: daily
  
  # Backlog file name (relative to wiki_path)
  backlog_file: "!backlog.md"
  
  # Email recipient for daily summary (optional)
  recipient: null
```

## Tasks

### `generate_daily_summary`

Generate a daily summary from wiki notes and backlog.

**Parameters:**
- `date` (optional): Date in YYYY-MM-DD format. Auto-deduced if not provided:
  - After 5pm: Uses today's date (end-of-day summary)
  - Before 5pm: Uses yesterday's date (morning planning)

**Returns:** Markdown-formatted daily summary with:
- Work accomplished (3-5 key items)
- Suggested priorities for tomorrow (5-7 items)
- Brief observations

**Usage:**
```bash
# Auto-detect date
pdm run python korben.py --task generate_daily_summary

# Specific date
pdm run python korben.py --task generate_daily_summary --date 2026-01-13
```

### `cleanup_daily_note`

Clean up and organize a daily note.

**Parameters:**
- `date` (optional): Date in YYYY-MM-DD format

**Returns:** Cleaned and organized daily note content

**Usage:**
```bash
pdm run python korben.py --task cleanup_daily_note --date 2026-01-14
```

## Flows

### `daily_summary`

Complete workflow that generates a summary and emails it.

**Parameters:**
- `date` (optional): Target date
- `recipient` (optional): Email recipient (falls back to config)
- `send_email` (optional): Whether to send email (default: True)

**Usage:**
```bash
# Generate and email summary
pdm run python korben.py --flow daily_summary

# Just generate, no email
pdm run python korben.py --flow daily_summary --send_email false

# Specific date
pdm run python korben.py --flow daily_summary --date 2026-01-13
```

### `cleanup_daily_note`

Workflow to clean up a daily note with optional save.

**Parameters:**
- `date` (optional): Target date
- `save` (optional): Whether to save changes (default: False)

**Usage:**
```bash
# Preview cleanup
pdm run python korben.py --flow cleanup_daily_note

# Clean and save
pdm run python korben.py --flow cleanup_daily_note --save true
```

## Dependencies

This plugin depends on:
- `email` - For sending summary emails
- `utilities` - For markdown to HTML conversion

## Expected Wiki Structure

The plugin expects an Obsidian vault with:

```
wiki/
├── daily/
│   ├── 2026-01-14.md
│   ├── 2026-01-13.md
│   └── ...
├── !backlog.md
└── ...
```

### Daily Note Format

Daily notes should include task lists:
```markdown
## Plan
- [ ] Incomplete task
- [x] Completed task ✅ 2026-01-14

## Completed
- [x] Another completed task ✅ 2026-01-14
```

### Backlog Format

The backlog should be a markdown file with task lists. Items near the top are considered higher priority:
```markdown
## Backlog
- [ ] High priority item
- [ ] Medium priority item
- [ ] Lower priority item
```

## Technical Details

This plugin uses LangChain with Claude (via `langchain-anthropic`) to generate summaries and clean up notes. The centralized `DailySummaryAgent` in `src/agents/` provides:
- Consistent prompt engineering
- Configurable temperature and model settings
- Reusable agent patterns

The plugin reads wiki files directly using Python file I/O and passes the content to Claude for analysis. This allows for:
- Fast local file access
- Offline file reading (only Claude API call requires network)
- Flexible date handling and content extraction
