# Utilities Plugin

Generic reusable utility tasks used by other plugins and workflows.

## Structure

```
utilities/
├── __init__.py
├── tasks.py       # All utility tasks
└── README.md      # This file
```

## Tasks

- **read_file** - Read text from files
- **write_file** - Write text to files
- **markdown_to_html** - Convert markdown to HTML
- **extract_wisdom** - Extract insights from text using AI
- **entropy** - Example multi-agent AI collaboration

## Requirements

- No special configuration needed
- Used by other plugins as building blocks

## Usage

These tasks are typically used as building blocks in workflows, but can be run standalone:

```bash
pdm run python3 ./korben.py --task send_email --recipient "you@example.com" --subject "Test" --content "Hello!"
pdm run python3 ./korben.py --task markdown_to_html --text "# Hello"
cat transcript.txt | pdm run python3 ./korben.py --task extract_wisdom
```

