# core

Agentic automation built on  for hackers

## Features

- **Podcasts** - Download, transcribe, extract wisdom, and email podcast insights
- **News** - Fetch and summarize latest cybersecurity headlines from Mallory API
- **Entropy** - Example task demonstrating multi-agent AI collaboration
- ... 
- **Extensible** - Easy to add new tasks using the task registry pattern

## Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd core

# Install dependencies
pdm install
```

### Configuration

**Base setup:**
```bash
# Set environment variables (add to ~/.zshrc or ~/.bashrc)
export PERSONAL_EMAIL="your@email.com"
export POSTMARK_API_KEY="your-postmark-api-key"
export MALLORY_API_KEY="your-mallory-api-key" # cybernews task 
```

**Per-task config:**
```bash
# Copy and customize the podcast config
cp config/podcasts.yml.example config/podcasts.yml
vim config/podcasts.yml
```

Run: `pdm run python3 ./run.py --task podcasts`

## How to Use

### List Available Tasks

```bash
pdm run python3 ./run.py --list
```

Output:
```
Available tasks:
  - cybernews
  - entropy
  - podcasts
```

### Run a Task

```bash
# Run the podcasts workflow (download → transcribe → extract wisdom → email)
pdm run python3 ./run.py --task podcasts

# Run the cybersecurity news summarizer
pdm run python3 ./run.py --task cybernews

# Run the entropy example
pdm run python3 ./run.py --task entropy
```

### Podcasts Task

Downloads, transcribes, extracts wisdom, and emails podcast insights.

**Config:** `config/podcasts.yml` (copy from `config/podcasts.yml.example`)

**Environment Variables:**
- `PERSONAL_EMAIL` - Your email (required)
- `POSTMARK_API_KEY` - Postmark API key (required)
- `PODCASTS_PATH` - Download location (default: `/tmp/podcasts/content`)
- `PODCAST_TRANSCRIPT_PATH` - Transcript location (default: `~/work/personal/drive/My Drive/podcasts/transcripts`)

### News Task

Fetches and summarizes cybersecurity stories from Mallory API.

**Environment Variables:**
- `MALLORY_API_KEY` - Mallory API key (required)

## Configuration

### Base Configuration

**Environment Variables** (add to `~/.zshrc` or `~/.bashrc`):
```bash
export PERSONAL_EMAIL="your@email.com"
export POSTMARK_API_KEY="your-postmark-api-key"  
export MALLORY_API_KEY="your-mallory-api-key"
```

### Task Configuration

**Podcasts** - `config/podcasts.yml`:
```bash
cp config/podcasts.yml.example config/podcasts.yml
vim config/podcasts.yml
```

Example:
```yaml
days_back: 7
podcasts:
  my_podcast: "https://example.com/feed.xml"
```

**Optional environment variables:**
- `PODCASTS_PATH` - Download location (default: `/tmp/podcasts/content`)
- `PODCAST_TRANSCRIPT_PATH` - Transcript location (default: `~/work/personal/drive/My Drive/podcasts/transcripts`)

## Creating New Tasks

1. **Create a new task file** in `src/core/tasks/`:
   ```python
   """Your task description."""
   import controlflow as cf
   
   def run(**kwargs):
       """Your task implementation."""
       # Your code here
       return "Task completed!"
   ```

2. **Register the task** in `src/core/registry.py`:
   ```python
   from src.core.tasks import your_task
   
   TASKS = {
       "your_task": your_task.run,
       # ... other tasks
   }
   ```

3. **Run it:**
   ```bash
   pdm run python3 ./run.py --task your_task
   ```

## Project Structure

```
core/
├── config/                    # Configuration files
│   ├── podcasts.yml.example   # Example podcast config
│   ├── podcasts.yml           # Your config (gitignored)
│   └── README.md
├── src/
│   ├── core/
│   │   ├── registry.py        # Task registry
│   │   └── tasks/             # Task implementations
│   │       ├── podcasts.py
│   │       ├── cybernews.py
│   │       └── entropy.py
│   └── lib/                   # Shared utilities
│       ├── email.py           # Email sending via Postmark
│       └── llm.py             # LLM utilities (Whisper)
├── tests/
├── run.py                     # Main CLI entry point
├── pyproject.toml             # Dependencies
└── README.md                  # This file
```

## Dependencies

- **Python 3.13+**
- **controlflow** - AI agent framework
- **openai-whisper** - Audio transcription
- **getpodcast** - Podcast downloading
- **pyyaml** - Configuration parsing
- **requests** - HTTP client
- **lxml** - XML parsing for podcast feeds

See `pyproject.toml` for complete list.

## Development


## Troubleshooting

### "No config file found"
```bash
cp config/podcasts.yml.example config/podcasts.yml
```

### "Config not found" after git pull
- Check if `config/podcasts.yml.example` has new fields
- Update your `config/podcasts.yml` accordingly

### Which config is being used?
The app prints the config file it's loading:
```
Using local config: /path/to/core/config/podcasts.yml
```

## License

MIT
