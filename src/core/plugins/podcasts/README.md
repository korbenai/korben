# Podcasts Plugin

Automated podcast processing: download, transcribe, extract wisdom, and email summaries.

## Structure

```
podcasts/
├── __init__.py
├── tasks.py       # download_podcasts, transcribe_podcasts  
├── flows.py       # podcast_workflow
├── lib.py         # podcast_utils, whisper transcription
└── README.md      # This file
```

## Tasks

- **download_podcasts** - Download episodes from RSS feeds
- **transcribe_podcasts** - Transcribe audio to text using Whisper

## Flows

- **podcast_workflow** - Complete pipeline: download → transcribe → extract wisdom → email

## Requirements

- `config/podcasts.yml` - Podcast feeds configuration
- `PERSONAL_EMAIL` - Email recipient
- `POSTMARK_API_KEY` - For email delivery
- OpenAI Whisper - For transcription

## Usage

```bash
# Complete workflow
pdm run python3 ./korben.py --flow podcasts

# Individual tasks
pdm run python3 ./korben.py --task download_podcasts
pdm run python3 ./korben.py --task transcribe_podcasts
```

