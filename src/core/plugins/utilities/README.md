# Utilities Plugin

Generic reusable utility tasks used by other plugins and workflows.

## Structure

```
utilities/
├── __init__.py
├── tasks.py       # All utility tasks
├── lib.py         # Email client and other utilities
└── README.md      # This file
```

## Tasks

- **send_email** - Send HTML/text emails via Postmark
- **read_file** - Read text from files
- **write_file** - Write text to files
- **markdown_to_html** - Convert markdown to HTML
- **extract_wisdom** - Extract insights from text using AI
- **entropy** - Example multi-agent AI collaboration
- **send_slack_hook** - Send Slack notifications

## Requirements

- `POSTMARK_API_KEY` - For send_email
- `PERSONAL_EMAIL` - Default email recipient
- `SLACK_WEBHOOK_URL` - For send_slack_hook

## Usage

These tasks are typically used as building blocks in workflows, but can be run standalone:

```bash
pdm run python3 ./korben.py --task send_email --recipient "you@example.com" --subject "Test" --content "Hello!"
pdm run python3 ./korben.py --task markdown_to_html --text "# Hello"
cat transcript.txt | pdm run python3 ./korben.py --task extract_wisdom
```

