# Configuration Files

This directory contains configuration files for the project.

## Quick Setup

```bash
# Copy the example to create your config
cp config/podcasts.yml.example config/podcasts.yml

# Edit your config
vim config/podcasts.yml
```

Your `config/podcasts.yml` is gitignored and won't be committed.

## Configuration Files

- **`podcasts.yml.example`** - Example configuration (version controlled)
- **`podcasts.yml`** - Your configuration (gitignored, you create this)

## Podcasts Configuration

Edit `config/podcasts.yml` to customize:

```yaml
# Number of days back to fetch podcasts
days_back: 7

# Podcast feeds (RSS URLs or Apple Podcasts URLs)
podcasts:
  my_podcast: "https://example.com/feed.xml"
  another_podcast: "https://podcasts.apple.com/us/podcast/..."
```

## Environment Variables

### Podcasts Task
- `PODCASTS_PATH` - Where to download podcasts (default: `/tmp/podcasts/content`)
- `PODCAST_TRANSCRIPT_PATH` - Where to save transcripts (default: `~/work/personal/drive/My Drive/podcasts/transcripts`)
- `PERSONAL_EMAIL` - Email address for sending wisdom summaries (required)
- `POSTMARK_API_KEY` - API key for Postmark email service (required)

### News Task
- `MALLORY_API_KEY` - API key for Mallory cybersecurity news service (required)

## File Structure

```
config/
├── README.md                 # This file
├── podcasts.yml.example      # Example config (in git)
└── podcasts.yml              # Your config (gitignored)
```
