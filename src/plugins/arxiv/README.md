# arXiv Plugin

Search for academic papers using the free arXiv API.

## Features

- **Search academic papers** on arXiv.org by query
- **No API key required** - completely free to use
- **Rich search syntax** - search by title, author, category, abstract, etc.
- **Detailed metadata** including titles, authors, abstracts, categories, and links
- **PDF links** direct to downloadable PDFs
- **Automated notifications** via email and Slack (flow)
- **HTML email formatting** with styled paper cards
- **Slack message formatting** optimized for readability
- **Pagination support** for large result sets
- **Flexible sorting** by relevance, date, or submission date

## Setup

No API key needed! Just start using it.

Optionally copy the example config and customize:
```bash
cp src/plugins/arxiv/config.yml.example src/plugins/arxiv/config.yml
```

## Configuration

Edit `src/plugins/arxiv/config.yml` to set defaults:

```yaml
variables:
  max_results: 10
  sort_by: "relevance"
  sort_order: "descending"
```

All configuration values can be overridden via CLI arguments.

## Usage

### Basic Paper Search

Search for papers with a query:

```bash
pdm run python3 ./korben.py --task arxiv_search --query "all:transformer"
```

### Search by Title

```bash
pdm run python3 ./korben.py --task arxiv_search --query "ti:attention mechanisms"
```

### Search by Author

```bash
pdm run python3 ./korben.py --task arxiv_search --query "au:lecun"
```

### Search by Category

```bash
pdm run python3 ./korben.py --task arxiv_search --query "cat:cs.AI"
```

### Combined Queries

```bash
pdm run python3 ./korben.py --task arxiv_search --query "ti:transformer AND au:vaswani"
```

### Search with Custom Result Limit

```bash
pdm run python3 ./korben.py --task arxiv_search --query "all:neural networks" --max_results 20
```

### Search and Notify (Flow)

Search for papers and automatically send results via email and Slack:

```bash
pdm run python3 ./korben.py --flow arxiv_search \
  --query "all:large language models" \
  --max_results 5
```

## Query Syntax

The arXiv API supports powerful search syntax:

| Prefix | Description | Example |
|--------|-------------|---------|
| `all:` | Search all fields | `all:quantum` |
| `ti:` | Search titles | `ti:neural networks` |
| `au:` | Search authors | `au:hinton` |
| `abs:` | Search abstracts | `abs:deep learning` |
| `cat:` | Search by category | `cat:cs.AI` |
| `AND` | Combine queries | `ti:attention AND au:vaswani` |
| `OR` | Alternative queries | `ti:GAN OR ti:generative` |
| `ANDNOT` | Exclude terms | `all:neural ANDNOT ti:networks` |

### Popular Categories

- `cs.AI` - Artificial Intelligence
- `cs.CL` - Computation and Language
- `cs.CV` - Computer Vision
- `cs.LG` - Machine Learning
- `cs.NE` - Neural and Evolutionary Computing
- `stat.ML` - Machine Learning (Statistics)

## Task Reference

### arxiv_search

Search for academic papers using the arXiv API.

**Parameters:**
- `query` (required): Search query string
- `max_results` (optional): Maximum number of results (default: 10)
- `start` (optional): Starting index for pagination (default: 0)
- `sort_by` (optional): Sort by 'relevance', 'lastUpdatedDate', or 'submittedDate' (default: 'relevance')
- `sort_order` (optional): 'ascending' or 'descending' (default: 'descending')

**Returns:**
- JSON string containing paper search results with metadata

**Example:**
```bash
pdm run python3 ./korben.py --task arxiv_search \
  --query "ti:transformer" \
  --max_results 5 \
  --sort_by "submittedDate"
```

## Flow Reference

### arxiv_search

Search for papers and automatically send the results via email and Slack.

**Dependencies:**
- `email` plugin
- `slack` plugin

**Parameters:**
- `query` (required): Search query string
- `max_results` (optional): Maximum number of results (default: 10)
- `start` (optional): Starting index for pagination (default: 0)
- `sort_by` (optional): Sort by 'relevance', 'lastUpdatedDate', or 'submittedDate' (default: 'relevance')
- `sort_order` (optional): 'ascending' or 'descending' (default: 'descending')
- `recipient` (optional): Email recipient (falls back to email plugin config)
- `hook_name` (optional): Slack webhook name (falls back to slack plugin config)

**Returns:**
- Status message with summary of papers found and notification results

**Example:**
```bash
pdm run python3 ./korben.py --flow arxiv_search \
  --query "all:attention mechanisms" \
  --max_results 5 \
  --sort_by "lastUpdatedDate"
```

**What it does:**
1. Searches for papers using the arXiv API
2. Formats results into HTML email with paper details, categories, and links
3. Sends email to configured recipient
4. Formats results into Slack message with clickable links
5. Posts to configured Slack webhook

## API Response Format

The task returns a JSON response containing:
- `papers`: Array of paper objects with metadata
  - `title`: Paper title
  - `authors`: List of author names
  - `abstract`: Paper abstract/summary
  - `published`: Publication date
  - `updated`: Last update date
  - `url`: Link to paper on arXiv
  - `pdf_url`: Direct link to PDF
  - `primary_category`: Main arXiv category
  - `categories`: All applicable categories
  - `comment`: Author comments (page count, etc.)
  - `journal_ref`: Journal reference if published
  - `doi`: DOI if available

## Error Handling

The plugin handles common errors gracefully:
- Invalid query syntax
- Network errors
- XML parsing errors
- Empty results

## Resources

- [arXiv API Documentation](https://arxiv.org/help/api/index)
- [arXiv Category Taxonomy](https://arxiv.org/category_taxonomy)
- [arXiv Search Help](https://arxiv.org/help/search)


