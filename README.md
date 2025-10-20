# core

Agentic automation built on  for hackers

## Features

- **Generic Tasks** - Reusable building blocks:
  - `extract_wisdom` - Extract insights from text (returns markdown)
  - `markdown_to_html` - Convert markdown to HTML
  - `send_email` - Send email via Postmark
  - `read_file` / `write_file` - File I/O
- **Podcast Workflow** - ControlFlow flow demonstrating task composition:
  - `download_podcasts` - Download from RSS/Apple Podcasts feeds
  - `transcribe_podcasts` - Convert audio to text using Whisper
  - Flow orchestrates generic tasks: `read_file` → `extract_wisdom` → `write_file` → `markdown_to_html` → `send_email`
- **Mallory Stories Workflow** - Fetch and email cybersecurity stories:
  - `get_mallory_stories` - Fetch and summarize latest stories from Mallory API
  - Flow orchestrates: `get_mallory_stories` → `markdown_to_html` → `send_email`
- **Entropy** - Example task demonstrating multi-agent AI collaboration
- **CSV State Tracking** - Resume interrupted workflows without re-processing
- **Composable Architecture** - Generic tasks composed via ControlFlow flows
- **Extensible** - Easy to add new tasks and flows using the registry pattern

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
# 1. Core configuration
cp config/core.yml.example config/core.yml

# 2. Environment variables (add to ~/.zshrc or ~/.bashrc)
export PERSONAL_EMAIL="your@email.com"
export POSTMARK_API_KEY="your-postmark-api-key"
export MALLORY_API_KEY="your-mallory-api-key"
```

**Per-task config:**
```bash
# Copy and customize the podcast config
cp config/podcasts.yml.example config/podcasts.yml
vim config/podcasts.yml
```

Run: `pdm run python3 ./run.py --flow podcasts`

### Prefect Cloud (Optional)

**For production:** Schedule workflows, monitor runs, view logs in a web UI.

**How it works:** Code runs on YOUR machine (worker), Prefect Cloud handles scheduling/orchestration. Free tier includes unlimited runs.

```bash
# 1. Login to Prefect Cloud (free tier)
prefect cloud login

# 2. Deploy workflow (daily at 6 AM PST)
pdm run python3 deployments/prefect_cloud.py

# 3. Start worker on your machine
prefect worker start --pool default-pool
```

**Requirements:** Worker needs access to your configs, env vars (`PERSONAL_EMAIL`, `POSTMARK_API_KEY`), and dependencies.

**Monitor:** https://app.prefect.cloud - View runs, logs, manually trigger, edit schedules

## How to Use

### List Available Tasks

```bash
pdm run python3 ./run.py --list
```

Output:
```
Available tasks:
  - download_podcasts
  - entropy
  - extract_wisdom
  - get_mallory_stories
  - markdown_to_html
  - read_file
  - send_email
  - transcribe_podcasts
  - write_file

Available flows:
  - mallory_stories
  - podcasts
```

### Run a Task or Flow

```bash
# Run complete podcasts workflow (ControlFlow flow)
pdm run python3 ./run.py --flow podcasts

# Run Mallory stories workflow (fetch and email security news)
pdm run python3 ./run.py --flow mallory_stories
pdm run python3 ./run.py --flow mallory_stories --recipient custom@email.com --subject "Today's Security News"

# Or run individual podcast tasks
pdm run python3 ./run.py --task download_podcasts
pdm run python3 ./run.py --task transcribe_podcasts

# Use generic tasks independently
pdm run python3 ./run.py --task read_file --file_path transcript.txt
pdm run python3 ./run.py --task extract_wisdom --text "Your text..."
pdm run python3 ./run.py --task write_file --file_path output.txt --content "Content"
pdm run python3 ./run.py --task send_email --recipient you@example.com --subject "Test" --content "Hello"
pdm run python3 ./run.py --task markdown_to_html --text "# Markdown text"

# Fetch and summarize security stories from Mallory API
pdm run python3 ./run.py --task get_mallory_stories

# Extract wisdom from text
echo "Your text here" | pdm run python3 ./run.py --task extract_wisdom

# Run the entropy example
pdm run python3 ./run.py --task entropy
```

### Podcasts Flow

**Complete workflow** - `--flow podcasts`:  
ControlFlow flow demonstrating task composition. Orchestrates podcast tasks and generic tasks.

**Flow steps:**
1. `download_podcasts` - Downloads from configured feeds
2. `transcribe_podcasts` - Transcribes MP3s to text  
3. For each transcript: `read_file` → `extract_wisdom` → `write_file` → `markdown_to_html` → `send_email`

This demonstrates **composability**: generic tasks are composed to build a complete workflow with proper HTML email formatting.

**Config:** `config/podcasts.yml` (copy from `config/podcasts.yml.example`)

**Environment Variables:**
- `PERSONAL_EMAIL` - Your email (required)
- `POSTMARK_API_KEY` - Postmark API key (required)

**Data Storage:** `data/podcasts/` with CSV tracking to prevent re-processing

### Mallory Stories Flow

**Complete workflow** - `--flow mallory_stories`:  
Fetches cybersecurity stories from Mallory API, converts to HTML, and emails them.

**Flow steps:**
1. `get_mallory_stories` - Fetches top 20 stories sorted by reference count and generates AI summaries
2. `markdown_to_html` - Converts story summaries to formatted HTML
3. `send_email` - Sends formatted email

**Environment Variables:**
- `MALLORY_API_KEY` - Mallory API key (required)
- `PERSONAL_EMAIL` - Your email (default recipient)
- `POSTMARK_API_KEY` - Postmark API key (required)

**Usage:**
```bash
# Run complete flow with default recipient (PERSONAL_EMAIL)
pdm run python3 ./run.py --flow mallory_stories

# Specify recipient and subject
pdm run python3 ./run.py --flow mallory_stories \
  --recipient custom@email.com \
  --subject "Today's Security Stories"

# Or run just the task to get stories (no email)
pdm run python3 ./run.py --task get_mallory_stories
```

**Output:** Each story includes title, description, reference count, and URL to Mallory's detailed analysis.

### Extract Wisdom Task

Pure text processing task that extracts comprehensive insights from text. Uses a detailed extraction framework to pull out:
- Summary (25 words)
- Ideas (20-50 items, exactly 16 words each)
- Insights (10-20 refined takeaways, 16 words each)
- Quotes (15-30 with speaker attribution)
- Habits (15-30 practical habits, 16 words each)
- Facts (15-30 surprising facts, 16 words each)
- References (books, tools, projects mentioned)
- One-sentence takeaway (15 words)
- Recommendations (15-30 items, 16 words each)

**Usage:**
```bash
# Extract wisdom from text argument
pdm run python3 ./run.py --task extract_wisdom --text "Your text here..."

# Extract wisdom from stdin (pipe)
cat transcript.txt | pdm run python3 ./run.py --task extract_wisdom
```

**Output:** Structured markdown formatted for easy reading and HTML conversion.

**Composable:** Pure text → markdown function. Compose with `markdown_to_html` → `send_email` for formatted email delivery.

### Generic Tasks

**Read File:**
```bash
# Relative path (reads from tmp/ directory)
pdm run python3 ./run.py --task read_file --file_path myfile.txt

# Absolute path
pdm run python3 ./run.py --task read_file --file_path /absolute/path/to/file.txt
```

**Write File:**
```bash
# Relative path (writes to tmp/ directory)
pdm run python3 ./run.py --task write_file --file_path output.txt --content "Content"

# Absolute path
pdm run python3 ./run.py --task write_file --file_path /absolute/path/output.txt --content "Content"
```

**Send Email:**
```bash
pdm run python3 ./run.py --task send_email \
  --recipient you@example.com \
  --subject "Subject" \
  --content "Body"
```

Environment: `PERSONAL_EMAIL` (default recipient), `POSTMARK_API_KEY` (required)

These generic tasks are composable building blocks used by flows.

## Configuration

### Base Configuration

**Core Config** - `config/core.yml`:
```bash
cp config/core.yml.example config/core.yml
```

Example:
```yaml
data_dir: "data"  # Where all task data is stored
tmp_dir: "tmp"    # Where temporary files are stored
```

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

### Data Storage

Task data and temporary files are stored in configurable directories (`config/core.yml`):

**Data directory** (`data/` by default):
```
data/
└── podcasts/
    ├── downloads/        # Downloaded MP3 files
    ├── transcripts/      # Transcribed text files
    ├── wisdom/           # Extracted wisdom summaries
    └── podcasts.csv      # Processing state tracker
```

**Temporary directory** (`tmp/` by default):
- Used by `read_file` and `write_file` tasks for relative paths
- Gitignored for ephemeral files
- Configurable via `tmp_dir` in `config/core.yml`

CSV tracker prevents re-processing and allows resuming interrupted workflows.

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
│   ├── core.yml.example       # Example core config
│   ├── core.yml               # Core config (gitignored)
│   ├── podcasts.yml.example   # Example podcast config
│   ├── podcasts.yml           # Podcast config (gitignored)
│   ├── workers.py             # Worker/task mapping config
│   └── README.md
├── deployments/               # Prefect Cloud deployments
│   ├── prefect_cloud.py       # Deploy to Prefect Cloud
│   ├── run_local.py           # Run locally without Prefect
│   └── README.md
├── data/                      # Task data (gitignored)
│   └── podcasts/
│       ├── downloads/         # Downloaded MP3s
│       ├── transcripts/       # Transcribed texts
│       ├── wisdom/            # Wisdom summaries
│       └── podcasts.csv       # State tracker
├── src/
│   ├── core/
│   │   ├── registry.py        # Task & flow registry
│   │   ├── flows/             # ControlFlow orchestrations
│   │   │   └── podcasts.py    # Podcast workflow flow
│   │   └── tasks/             # Task implementations
│   │       ├── download_podcasts.py    # Downloads podcasts
│   │       ├── transcribe_podcasts.py  # Transcribes to text
│   │       ├── extract_wisdom.py       # Extracts wisdom from text (generic)
│   │       ├── send_email.py           # Sends email (generic)
│   │       ├── read_file.py            # Reads file (generic)
│   │       ├── write_file.py           # Writes file (generic)
│   │       ├── cybernews.py
│   │       └── entropy.py
│   └── lib/                   # Shared utilities
│       ├── email.py           # Email sending via Postmark
│       ├── llm.py             # LLM utilities (Whisper)
│       ├── podcast_utils.py   # Podcast tracking & config
│       └── core_utils.py      # Core config utilities
├── tests/
├── run.py                     # Main CLI entry point
├── pyproject.toml             # Dependencies
└── README.md                  # This file
```

## Architecture

### Tasks & Flows

**Tasks** (`src/core/tasks/`) - Independent units of work:
```python
def run(**kwargs):
    # Task implementation
    return result
```

**Flows** (`src/core/flows/`) - Orchestrate tasks using `@cf.flow`:
```python
@cf.flow
def process_single_transcript(transcript_path, email):
    text = read_file.run(file_path=transcript_path)
    wisdom_md = extract_wisdom.run(text=text)           # AI extraction → markdown
    write_file.run(file_path=wisdom_file, content=wisdom_md)
    wisdom_html = markdown_to_html.run(text=wisdom_md)  # markdown → HTML
    send_email.run(recipient=email, subject=subject, content=wisdom_html)

@cf.flow
def podcast_workflow(**kwargs):
    download_podcasts.run(**kwargs)
    transcribe_podcasts.run(**kwargs)
    # Process each transcript using generic tasks
    for transcript in transcripts:
        process_single_transcript(transcript, email)
```

**AI Operations** use `cf.run()` for agent-based processing:
```python
def extract_wisdom(text):
    wisdom_agent = cf.Agent(
        name="Wisdom Extractor",
        instructions="..."  # Detailed extraction framework
    )
    return cf.run(
        "Extract wisdom and insights...", 
        agents=[wisdom_agent],
        result_type=str
    )
```

**Registry** (`src/core/registry.py`) - Maps names to tasks and flows:
```python
TASKS = {"download_podcasts": download_podcasts.run, ...}
FLOWS = {"podcasts": podcast_workflow}
```

This follows ControlFlow best practices: tasks are independent, flows orchestrate, `cf.run()` for AI.

## Dependencies

- **Python 3.13+**
- **controlflow** - AI agent framework
- **prefect** - Workflow orchestration (optional, for cloud deployment)
- **openai-whisper** - Audio transcription
- **getpodcast** - Podcast downloading
- **pyyaml** - Configuration parsing
- **requests** - HTTP client
- **lxml** - XML parsing for podcast feeds

See `pyproject.toml` for complete list.

## Deployment

### Local Execution

```bash
# Run workflows locally
pdm run python3 ./run.py --flow podcasts
pdm run python3 ./run.py --task download_podcasts
```

### Prefect Cloud (Production)

For scheduled execution and monitoring:

```bash
# Deploy to Prefect Cloud
python deployments/prefect_cloud.py

# Start worker
prefect worker start --pool default-pool
```

See:
- `deployments/README.md` - Deployment setup guide

## Documentation

- **[README.md](README.md)** - This file (overview and quick start)
- **[deployments/README.md](deployments/README.md)** - Deployment scripts documentation
- **[config/README.md](config/README.md)** - Configuration reference

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
