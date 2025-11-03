# Emergent Mind Plugin

Search for academic papers using the Emergent Mind API.

## Features

- **Search academic papers** by query string
- **Filter papers** by publication date range
- **Configure result limits** to control output
- **Returns detailed metadata** including titles, authors, abstracts, and more
- **Automated notifications** via email and Slack (flow)
- **HTML email formatting** with rich paper details
- **Slack message formatting** optimized for readability

## Setup

1. Get an API key from [Emergent Mind](https://www.emergentmind.com)

2. Set the environment variable:
   ```bash
   export EMERGENT_MIND_API_KEY="your_api_key_here"
   ```

3. (Optional) Copy the example config and customize:
   ```bash
   cp src/plugins/emergent_mind/config.yml.example src/plugins/emergent_mind/config.yml
   ```

## Configuration

Edit `src/plugins/emergent_mind/config.yml` to set defaults:

```yaml
variables:
  num_results: 10
  start_published_date: "2024-01-01"
```

All configuration values can be overridden via CLI arguments.

## Usage

### Basic Paper Search

Search for papers with a query:

```bash
pdm run python3 ./korben.py --task paper_search --query "transformer attention mechanisms"
```

### Search with Custom Result Limit

```bash
pdm run python3 ./korben.py --task paper_search --query "large language models" --num_results 20
```

### Search with Date Range

Search for papers published within a specific date range:

```bash
pdm run python3 ./korben.py --task paper_search \
  --query "multimodal learning" \
  --start_published_date "2024-01-01" \
  --end_published_date "2024-12-31" \
  --num_results 15
```

## Task Reference

### paper_search

Search for academic papers using the Emergent Mind API.

**Parameters:**
- `query` (required): Search query string
- `num_results` (optional): Number of results to return (default: 10)
- `start_published_date` (optional): Start date in YYYY-MM-DD format
- `end_published_date` (optional): End date in YYYY-MM-DD format

**Returns:**
- JSON string containing paper search results with metadata

**Example:**
```bash
pdm run python3 ./korben.py --task paper_search \
  --query "neural architecture search" \
  --num_results 5
```

## Flow Reference

### paper_search_and_notify

Search for papers and automatically send the results via email and Slack.

**Dependencies:**
- `email` plugin
- `slack` plugin

**Parameters:**
- `query` (required): Search query string
- `num_results` (optional): Number of results to return (default: 10)
- `start_published_date` (optional): Start date in YYYY-MM-DD format
- `end_published_date` (optional): End date in YYYY-MM-DD format
- `recipient` (optional): Email recipient (falls back to email plugin config)
- `hook_name` (optional): Slack webhook name (falls back to slack plugin config)

**Returns:**
- Status message with summary of papers found and notification results

**Example:**
```bash
pdm run python3 ./korben.py --flow paper_search_and_notify \
  --query "large language models" \
  --num_results 5 \
  --start_published_date "2024-01-01"
```

**What it does:**
1. Searches for papers using the Emergent Mind API
2. Formats results into HTML email with paper details
3. Sends email to configured recipient
4. Formats results into Slack message
5. Posts to configured Slack webhook

## API Response Format

The task returns a JSON response containing:
- `papers`: Array of paper objects with metadata
  - Title
  - Authors
  - Abstract
  - Publication date
  - URLs
  - And more...

## Error Handling

The plugin handles common errors gracefully:
- Missing API key
- Invalid date formats
- Network errors
- API rate limits

## Environment Variables

- `EMERGENT_MIND_API_KEY`: Your Emergent Mind API key (required)


