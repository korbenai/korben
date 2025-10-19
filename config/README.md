# Configuration Files

This directory contains default and example configuration files for the project.

## Setup

### 1. Set your profiles path (optional)
```bash
export PROFILES_PATH=~/profiles  # Default location
```

### 2. Copy example configs to your profiles directory
```bash
mkdir -p $PROFILES_PATH/scripts/config
cp config/podcasts.yml.example $PROFILES_PATH/scripts/config/podcasts.yml
```

### 3. Customize your config
Edit `$PROFILES_PATH/scripts/config/podcasts.yml` with your preferred podcast feeds.

## Configuration Priority

The application will look for configs in this order:
1. `$PROFILES_PATH/scripts/config/podcasts.yml` (user-specific)
2. `config/podcasts.yml` (fallback, if exists in repo)
3. `config/podcasts.yml.example` (example only, not loaded)

## Environment Variables

### Podcasts Task
- `PROFILES_PATH` - Base path for user configs (default: `~/profiles`)
- `PODCASTS_PATH` - Where to download podcasts (default: `/tmp/podcasts/content`)
- `PODCAST_TRANSCRIPT_PATH` - Where to save transcripts (default: `~/work/personal/drive/My Drive/podcasts/transcripts`)
- `PERSONAL_EMAIL` - Email address for sending wisdom summaries
- `POSTMARK_API_KEY` - API key for Postmark email service

### News Task
- `MALLORY_API_KEY` - API key for Mallory cybersecurity news service

## File Locations

```
Repository (version controlled):
├── config/
│   ├── README.md
│   └── podcasts.yml.example    # Example config

User directory (not in git):
└── $PROFILES_PATH/
    └── scripts/
        └── config/
            └── podcasts.yml     # Your customized config
```

