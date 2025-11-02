# Mallory Plugin

Fetch and email curated cybersecurity stories from the Mallory API.

## Structure

```
mallory/
├── __init__.py
├── tasks.py       # fetch_mallory_stories
├── flows.py       # mallory_stories_workflow
└── README.md      # This file
```

## Tasks

- **fetch_mallory_stories** - Fetch and summarize top cybersecurity stories

## Flows

- **mallory_stories_workflow** - Fetch stories, convert to HTML, and email

## Requirements

- `MALLORY_API_KEY` - Mallory API key
- `POSTMARK_API_KEY` - For email delivery
- `PERSONAL_EMAIL` - Default recipient

## Usage

```bash
# Complete workflow
pdm run python3 ./korben.py --flow mallory_stories

# Just fetch stories (no email)
pdm run python3 ./korben.py --task fetch_mallory_stories
```

