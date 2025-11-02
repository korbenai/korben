# what is korben

<img alt="Korben" width="20%" style="border:none;box-shadow:none;" src="https://github.com/user-attachments/assets/cee1e900-f23b-47eb-83c5-6cae2e811008"  /> 

Hackable personal automation framework built on ControlFlow and Prefect - and pluggable for your personal enjoyment, bing badda boom.

## Features

* Intelligence built-in - easily spin up intelligent agents 
* Composable - build tasks and use them in more complex flows
* Extensible - Easy to add new tasks and flows in plugins
* Batteries includes - many built in plugins for hacker types

Out of the box capabilities: 

- **Generic Utilities** - Reusable building blocks:
  - `extract_wisdom` - Extract insights from text (returns markdown)
  - `markdown_to_html` - Convert markdown to HTML
  - `send_email` - Send email via Postmark
  - `read_file` / `write_file` - File I/O
- **Podcast Workflow** - ControlFlow flow demonstrating task composition:
  - `download_podcasts` - Download from RSS/Apple Podcasts feeds
  - `transcribe_podcasts` - Convert audio to text using Whisper
  - Flow orchestrates generic tasks: `read_file` → `extract_wisdom` → `write_file` → `markdown_to_html` → `send_email`
- **Mallory Stories Workflow** - Fetch and email cybersecurity stories:
  - `fetch_mallory_stories` - Fetch and summarize latest stories from Mallory API
  - Flow orchestrates: `fetch_mallory_stories` → `markdown_to_html` → `send_email`
- **Trending Movies Workflow** - Discover and email trending movies:
  - `discover_movies` - Query TMDB for movies matching criteria
  - `trending_movies` - Find trending movies by genre and send via email
  - `popular_movies` - Get popular movies from current/recent years
- **Books Discovery** - Find and recommend books:
  - `search_books` - Search ISBNdb for books by query, subject, or author
  - `trending_ai_books` - Get trending AI books and email recommendations

## Plugin Architecture

Korben uses an **auto-discovery plugin system** - plugins are automatically registered at startup.

```
src/plugins/
├── movies/       # TMDB movie discovery and recommendations
├── books/        # ISBNdb book search and recommendations
├── podcasts/     # Podcast download, transcribe, wisdom extraction
├── mallory/      # Cybersecurity news from Mallory API
├── email/        # Email delivery via Postmark
├── slack/        # Slack notifications via webhooks
└── utilities/    # Generic file I/O and text processing
```

### Plugin Structure

Each plugin is a self-contained directory:

```
my_plugin/
├── __init__.py              # Plugin marker
├── tasks.py                 # Task implementations (auto-registered)
├── flows.py                 # Workflow orchestrations (auto-registered)
├── lib.py                   # Plugin-specific libraries (optional)
├── config.yml.example       # Configuration template (optional)
└── README.md                # Documentation
```

Everything needed for the plugin lives in one folder!

### Auto-Registration

**Zero configuration needed!** The system automatically:
1. Scans `src/plugins/` for plugin directories
2. Imports `tasks.py` and `flows.py` from each plugin
3. Discovers all public functions via introspection
4. Registers them in global TASKS and FLOWS dictionaries

**Convention:**
- ✅ All public functions in `tasks.py` → registered as tasks
- ✅ All public functions in `flows.py` → registered as flows
- ✅ Flow names ending with `_workflow` → suffix auto-removed
- ❌ Functions starting with `_` → private (not registered)

**Dependencies:**
- Plugins can declare dependencies via `__dependencies__ = ['plugin1', 'plugin2']`
- System validates dependencies exist before registration
- Plugins with missing dependencies are disabled with clear warnings
- Prevents runtime errors from missing integrations

**Example:** Just create a plugin and it works immediately - no registry edits!


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
export TMDB_API_KEY="your-tmdb-api-key"        # Get from https://www.themoviedb.org/settings/api
export ISBNDB_API_KEY="your-isbndb-api-key"    # Get from https://isbndb.com/isbn-database
```

**Per-task config:**
```bash
# Copy and customize the podcast config
cp config/podcasts.yml.example config/podcasts.yml
vim config/podcasts.yml
```

Run: `pdm run python3 ./korben.py --flow podcasts`

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
pdm run python3 ./korben.py --list
```

Output:
```
Available tasks:
  - download_podcasts
  - entropy
  - extract_wisdom
  - fetch_mallory_stories
  - markdown_to_html
  - read_file
  - send_email
  - transcribe_podcasts
  - write_file

Available flows:
  - mallory_stories
  - podcast
  - popular_movies
  - trending_ai_books
  - trending_movies
```

### Run a Task or Flow

```bash
# Run complete podcasts workflow (ControlFlow flow)
pdm run python3 ./korben.py --flow podcast

# Run Mallory stories workflow (fetch and email security news)
pdm run python3 ./korben.py --flow mallory_stories
pdm run python3 ./korben.py --flow mallory_stories --recipient custom@email.com --subject "Today's Security News"

# Or run individual podcast tasks
pdm run python3 ./korben.py --task download_podcasts
pdm run python3 ./korben.py --task transcribe_podcasts

# Use generic tasks independently
pdm run python3 ./korben.py --task read_file --file_path transcript.txt
pdm run python3 ./korben.py --task extract_wisdom --text "Your text..."
pdm run python3 ./korben.py --task write_file --file_path output.txt --content "Content"
pdm run python3 ./korben.py --task send_email --recipient you@example.com --subject "Test" --content "Hello"
pdm run python3 ./korben.py --task markdown_to_html --text "# Markdown text"

# Fetch and summarize security stories from Mallory API
pdm run python3 ./korben.py --task fetch_mallory_stories

# Discover movies from TMDB
pdm run python3 ./korben.py --task discover_movies --genres "28,878" --min_rating 7.0

# Get trending movies and send via email
pdm run python3 ./korben.py --flow trending_movies
pdm run python3 ./korben.py --flow trending_movies --genres "sci-fi,action,thriller"

# Get popular recent movies (all genres)
pdm run python3 ./korben.py --flow popular_movies

# Get trending AI books and send via email
pdm run python3 ./korben.py --flow trending_ai_books
pdm run python3 ./korben.py --flow trending_ai_books --query "machine learning" --limit 10

# Extract wisdom from text
echo "Your text here" | pdm run python3 ./korben.py --task extract_wisdom

# Run the entropy example
pdm run python3 ./korben.py --task entropy
```

### Podcasts Flow

**Complete workflow** - `--flow podcast`:  
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
1. `fetch_mallory_stories` - Fetches top 20 stories sorted by reference count and generates AI summaries
2. `markdown_to_html` - Converts story summaries to formatted HTML
3. `send_email` - Sends formatted email

**Environment Variables:**
- `MALLORY_API_KEY` - Mallory API key (required)
- `PERSONAL_EMAIL` - Your email (default recipient)
- `POSTMARK_API_KEY` - Postmark API key (required)

**Usage:**
```bash
# Run complete flow with default recipient (PERSONAL_EMAIL)
pdm run python3 ./korben.py --flow mallory_stories

# Specify recipient and subject
pdm run python3 ./korben.py --flow mallory_stories \
  --recipient custom@email.com \
  --subject "Today's Security Stories"

# Or run just the task to get stories (no email)
pdm run python3 ./korben.py --task fetch_mallory_stories
```

**Output:** Each story includes title, description, reference count, and URL to Mallory's detailed analysis.

### Trending Movies Flow

**Complete workflow** - `--flow trending_movies`:  
Discovers popular movies from TMDB matching your preferred genres and emails them with ratings and descriptions.

**Note:** Uses TMDB's discover API with popularity sorting instead of the trending endpoint, because the trending endpoint doesn't support date filtering. This gives you popular recent movies filtered by your criteria.

**Flow steps:**
1. `discover_movies` - Queries TMDB API with genre, rating, vote, and date filters
2. Formats movies into beautiful HTML email with ratings, year, and descriptions
3. `send_email` - Sends formatted email

**Environment Variables:**
- `TMDB_API_KEY` - TMDB API key (required) - Get from https://www.themoviedb.org/settings/api
- `PERSONAL_EMAIL` - Your email (default recipient)
- `POSTMARK_API_KEY` - Postmark API key (required)

**Supported Genres:**
- `sci-fi`, `action`, `thriller`, `drama`, `fantasy`, `horror`, `comedy`, `romance`, `documentary`, `animation`, `adventure`, `crime`, `mystery`, `war`, `western`, `history`, `music`, `family`

**Usage:**
```bash
# Default: sci-fi, action, thriller, drama, fantasy (min rating 7.0)
pdm run python3 ./korben.py --flow trending_movies

# Custom genres
pdm run python3 ./korben.py --flow trending_movies --genres "horror,thriller,mystery"

# Custom filters
pdm run python3 ./korben.py --flow trending_movies \
  --genres "sci-fi,action" \
  --min_rating 8.0 \
  --min_votes 500 \
  --years_back 2 \
  --limit 5

# Popular movies from current/recent years (all genres)
pdm run python3 ./korben.py --flow popular_movies
pdm run python3 ./korben.py --flow popular_movies --min_rating 8.0 --limit 15 --years_back 2

# Just discover movies (no email)
pdm run python3 ./korben.py --task discover_movies \
  --genres "878,28" \
  --min_rating 7.0 \
  --min_votes 100
```

**Parameters:**
- `genres` - Comma-separated genre names or IDs (default: sci-fi, action, thriller, drama, fantasy)
- `min_rating` - Minimum TMDB rating 0-10 (default: 7.0)
- `min_votes` - Minimum vote count (default: 100)
- `years_back` - How many years back to search (default: 3)
- `limit` - Maximum movies to include (default: 10)
- `recipient` - Email recipient (default: PERSONAL_EMAIL)

**Output:** Formatted email with movie title, year, rating, vote count, popularity score, and description.

### Books Discovery Flow

**Complete workflow** - `--flow trending_ai_books`:  
Searches ISBNdb for books about AI and related topics, formats them beautifully, and emails the recommendations.

**Flow steps:**
1. `search_books` - Queries ISBNdb API with search criteria
2. Formats books into beautiful HTML email with title, author, publisher, ISBN, and synopsis
3. `send_email` - Sends formatted email

**Environment Variables:**
- `ISBNDB_API_KEY` - ISBNdb API key (required) - Get from https://isbndb.com/isbn-database
- `PERSONAL_EMAIL` - Your email (default recipient)
- `POSTMARK_API_KEY` - Postmark API key (required)

**Usage:**
```bash
# Default: search for "artificial intelligence" books
pdm run python3 ./korben.py --flow trending_ai_books

# Custom search query
pdm run python3 ./korben.py --flow trending_ai_books --query "machine learning"

# Search by subject
pdm run python3 ./korben.py --flow trending_ai_books --subject "Computer Science" --limit 10

# Search books directly (no email)
pdm run python3 ./korben.py --task search_books --query "deep learning" --limit 20

# Get book details by ISBN
pdm run python3 ./korben.py --task get_book_details --isbn "9780262046244"
```

**Parameters:**
- `query` - Search query (default: "artificial intelligence")
- `subject` - Search by subject category instead
- `author` - Search by author name
- `limit` - Maximum books to include (default: 15)
- `recipient` - Email recipient (default: PERSONAL_EMAIL)

**Output:** Formatted email with book title, author(s), publisher, publication date, ISBN, and synopsis.

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
pdm run python3 ./korben.py --task extract_wisdom --text "Your text here..."

# Extract wisdom from stdin (pipe)
cat transcript.txt | pdm run python3 ./korben.py --task extract_wisdom
```

**Output:** Structured markdown formatted for easy reading and HTML conversion.

**Composable:** Pure text → markdown function. Compose with `markdown_to_html` → `send_email` for formatted email delivery.

### Generic Tasks

**Read File:**
```bash
# Relative path (reads from tmp/ directory)
pdm run python3 ./korben.py --task read_file --file_path myfile.txt

# Absolute path
pdm run python3 ./korben.py --task read_file --file_path /absolute/path/to/file.txt
```

**Write File:**
```bash
# Relative path (writes to tmp/ directory)
pdm run python3 ./korben.py --task write_file --file_path output.txt --content "Content"

# Absolute path
pdm run python3 ./korben.py --task write_file --file_path /absolute/path/output.txt --content "Content"
```

**Send Email:**
```bash
pdm run python3 ./korben.py --task send_email \
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
export TMDB_API_KEY="your-tmdb-api-key"
export ISBNDB_API_KEY="your-isbndb-api-key"
```

### Plugin Configuration

Each plugin can have its own configuration file with a standard `variables` section.

**Location:** `src/plugins/{plugin_name}/config.yml` (copy from `.example` in plugin folder)

**Standard Format:**
```yaml
# All plugin configs follow this format
variables:
  # Plugin-specific variables
  query: "value"
  limit: 15
  # ... other variables

# Optional: presets, advanced options, etc.
```

**Examples:**

**Books Plugin:**
```bash
cp src/plugins/books/config.yml.example src/plugins/books/config.yml
vim src/plugins/books/config.yml
```

```yaml
variables:
  query: "artificial intelligence"
  limit: 15
  min_year: 2020
```

**Movies Plugin:**
```bash
cp src/plugins/movies/config.yml.example src/plugins/movies/config.yml
vim src/plugins/movies/config.yml
```

```yaml
variables:
  genres:
    - sci-fi
    - action
    - thriller
  min_rating: 7.0
  limit: 10
```

**Podcasts Plugin:**
```bash
cp src/plugins/podcasts/config.yml.example src/plugins/podcasts/config.yml
vim src/plugins/podcasts/config.yml
```

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

## Creating New Plugins

### Quick Start - Weather Plugin Example

**1. Create plugin directory:**
```bash
mkdir -p src/plugins/weather
```

**2. Create `tasks.py`:**
   ```python
"""Weather plugin tasks."""
   
def get_forecast(**kwargs):
    """Get weather forecast for a location."""
    location = kwargs.get('location', 'San Francisco')
    return f"Weather for {location}: Sunny, 75°F"

# Private helper (not registered)
def _api_call(location):
    return {"temp": 75}
```

**3. Create `flows.py` (optional):**
   ```python
"""Weather plugin flows."""
import controlflow as cf
from src.plugins.weather import tasks as weather_tasks
from src.plugins.utilities import tasks as utility_tasks

@cf.flow
def daily_weather_workflow(**kwargs):
    """Auto-registered as 'daily_weather' (removes _workflow suffix)."""
    forecast = weather_tasks.get_forecast(**kwargs)
    utility_tasks.send_email(
        subject="Daily Weather",
        content=forecast,
        **kwargs
    )
    return forecast
```

**4. Create `README.md`:**
```markdown
# Weather Plugin
Get weather forecasts and send via email.
```

**5. Done! Auto-registered instantly:**
   ```bash
pdm run python3 ./korben.py --list
# Shows: get_forecast, daily_weather

pdm run python3 ./korben.py --task get_forecast --location "Paris"
pdm run python3 ./korben.py --flow daily_weather
```

**No registry edits needed!** The system automatically discovers and registers your plugin.

## Project Structure

```
korben/
├── config/                    # Configuration files
│   ├── core.yml.example       # Example core config
│   ├── core.yml               # Core config (gitignored)
│   ├── podcasts.yml.example   # Example podcast config
│   ├── podcasts.yml           # Podcast config (gitignored)
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
│   │   └── plugins/           # 🆕 Self-contained plugin modules
│   │       ├── movies/        # TMDB movie discovery
│   │       │   ├── tasks.py   # discover_movies
│   │       │   ├── flows.py   # trending_movies, popular_movies
│   │       │   ├── lib.py     # TMDB API client
│   │       │   ├── config.yml.example  # Plugin configuration template
│   │       │   └── README.md
│   │       ├── books/         # ISBNdb book search
│   │       │   ├── tasks.py   # search_books, get_book_details
│   │       │   ├── flows.py   # trending_ai_books
│   │       │   ├── lib.py     # ISBNdb API client
│   │       │   ├── config.yml.example  # Plugin configuration template
│   │       │   └── README.md
│   │       ├── podcasts/      # Podcast processing
│   │       │   ├── tasks.py   # download_podcasts, transcribe_podcasts
│   │       │   ├── flows.py   # podcast_workflow
│   │       │   ├── lib.py     # podcast_utils, whisper
│   │       │   └── README.md
│   │       ├── mallory/       # Cybersecurity news
│   │       │   ├── tasks.py   # fetch_mallory_stories
│   │       │   ├── flows.py   # mallory_stories_workflow
│   │       │   ├── config.yml.example  # Plugin configuration template
│   │       │   └── README.md
│   │       └── utilities/     # Generic reusable tasks
│   │           ├── tasks.py   # send_email, read_file, write_file, etc.
│   │           ├── lib.py     # email client
│   │           └── README.md
│   └── lib/                   # Shared core utilities
│       └── core_utils.py      # Config access (used by all plugins)
├── examples/
│   └── tmdb_example.py        # TMDB API usage examples
├── tests/
├── korben.py                  # Main CLI entry point
├── pyproject.toml             # Dependencies
└── README.md                  # This file
```

## Architecture

### Plugin-Based Design

**Plugins** (`src/plugins/`) - Fully self-contained modules:
```
plugins/
├── movies/          # Movie discovery (TMDB)
├── books/           # Book search (ISBNdb)
├── podcasts/        # Podcast processing
├── mallory/         # Security news
├── email/           # Email delivery (Postmark)
├── slack/           # Slack notifications
└── utilities/       # Generic file & text processing
```

Each plugin is completely self-contained:
- **tasks.py** - Task implementations
- **flows.py** - Workflow orchestrations (if needed)
- **lib.py** - Plugin-specific libraries (if needed)
- **config.yml.example** - Configuration template (if needed)
- **README.md** - Documentation

**Tasks** - Independent units of work:
```python
def task_name(**kwargs):
    # Task implementation
    return result
```

**Flows** - Orchestrate tasks using `@cf.flow`:
```python
# From plugins/podcasts/flows.py
@cf.flow
def process_single_transcript(transcript_path, email):
    text = utility_tasks.read_file(file_path=transcript_path)
    wisdom_md = utility_tasks.extract_wisdom(text=text)
    utility_tasks.write_file(file_path=wisdom_file, content=wisdom_md)
    wisdom_html = utility_tasks.markdown_to_html(text=wisdom_md)
    utility_tasks.send_email(recipient=email, subject=subject, content=wisdom_html)

# From plugins/movies/flows.py
@cf.flow
def trending_movies_workflow(**kwargs):
    movies = movie_tasks.discover_movies(genres=genre_ids, ...)
    movies_html = format_movie_email(movies, genres)
    utility_tasks.send_email(recipient=email, subject=subject, content=movies_html)
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

**Registry** (`src/registry.py`) - Maps names to tasks and flows from plugins:
```python
# Import from plugins
from src.plugins.movies import tasks as movie_tasks, flows as movie_flows
from src.plugins.podcasts import tasks as podcast_tasks, flows as podcast_flows
from src.plugins.mallory import tasks as mallory_tasks, flows as mallory_flows
from src.plugins.utilities import tasks as utility_tasks

TASKS = {
    "discover_movies": movie_tasks.discover_movies,
    "download_podcasts": podcast_tasks.download_podcasts,
    "send_email": utility_tasks.send_email,
    # ... other tasks
}

FLOWS = {
    "trending_movies": movie_flows.trending_movies_workflow,
    "podcasts": podcast_flows.podcast_workflow,
    # ... other flows
}
```

### Creating New Plugins

**Auto-Registration** - Plugins are automatically discovered at startup! No manual registration needed.

To add a new plugin:

1. **Create plugin directory:**
   ```bash
   mkdir -p src/plugins/my_plugin
   ```

2. **Add tasks.py:**
   ```python
   """My plugin tasks."""
   
   def my_task(**kwargs):
       """Task implementation."""
       return "Task completed!"
   
   def another_task(**kwargs):
       """Another task."""
       return "Done!"
   
   # Helper functions: prefix with _ to hide from CLI
   def _internal_helper():
       return "Not registered"
   ```

3. **Add flows.py (optional):**
   ```python
   """My plugin flows."""
   import controlflow as cf
   
   @cf.flow
   def my_workflow(**kwargs):
       """Public workflow - auto-registered as 'my' (removes _workflow suffix)."""
       result = my_task(**kwargs)
       return result
   
   @cf.flow
   def _helper_flow(**kwargs):
       """Internal helper - not registered (starts with _)."""
       pass
   ```

4. **Add lib.py (optional):**
   ```python
   """Plugin-specific libraries."""
   # API clients, utilities, etc.
   ```

5. **Add README.md:**
   Document your plugin's tasks, flows, and usage.

6. **Done!** - Your plugin is automatically discovered and registered:
   ```bash
   pdm run python3 ./korben.py --list
   # Shows: my_task, another_task, my
   
   pdm run python3 ./korben.py --task my_task
   pdm run python3 ./korben.py --flow my
   ```

**Best Practices:**
- **Self-Contained** - Each plugin is independent
- **Clear Naming** - Function names become CLI commands
- **Private Helpers** - Prefix with `_` to hide from CLI
- **Document** - Include README.md for each plugin
- **Testable** - Plugins are isolated and easy to test

**Benefits:**
- **Fast Development** - Create folder, write code, done
- **True Pluggability** - No core modifications needed
- **Auto-Discovery** - `--list` shows everything automatically

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
pdm run python3 ./korben.py --flow podcasts
pdm run python3 ./korben.py --task download_podcasts
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
