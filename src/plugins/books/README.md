# Books Plugin

Search and discover books using the ISBNdb API. Get trending AI books and send recommendations via email.

## Structure

```
books/
├── __init__.py
├── tasks.py       # search_books, get_book_details
├── flows.py       # trending_ai_books
├── lib.py         # ISBNdb API client
└── README.md      # This file
```

## Tasks

- **search_books** - Search ISBNdb for books by query, subject, or author
- **get_book_details** - Get detailed information about a book by ISBN

## Flows

- **trending_ai_books** - Search for AI books and email recommendations

## Requirements

### Environment Variables

- **`ISBNDB_API_KEY`** (required) - Your ISBNdb API key
  - Get one from: https://isbndb.com/isbn-database
- **`POSTMARK_API_KEY`** (required) - For email delivery
- **`PERSONAL_EMAIL`** (optional) - Default recipient

### Configuration File (Optional)

**Location:** `src/plugins/books/config.yml`

```bash
# Copy example to create your config
cp src/plugins/books/config.yml.example src/plugins/books/config.yml
vim src/plugins/books/config.yml
```

```yaml
variables:
  query: "artificial intelligence"       # Default search query
  limit: 15                              # Maximum books to return
  min_year: 2020                         # Filter by publication year
```

**Priority:** CLI arguments > config file > hardcoded defaults

This allows you to set your preferences once in the config, then override as needed via CLI.

## Usage

### Search for Books

```bash
# Search for AI books
pdm run python3 ./korben.py --task search_books \
  --query "artificial intelligence" \
  --limit 20

# Search by subject
pdm run python3 ./korben.py --task search_books \
  --subject "Machine Learning" \
  --limit 15

# Search by author
pdm run python3 ./korben.py --task search_books \
  --author "Stuart Russell" \
  --limit 10
```

### Get Book Details

```bash
# Get details by ISBN
pdm run python3 ./korben.py --task get_book_details \
  --isbn "9780262046244"
```

### Trending AI Books Flow

```bash
# Get trending AI books and email them (default query: 'artificial intelligence')
pdm run python3 ./korben.py --flow trending_ai_books

# Custom search query
pdm run python3 ./korben.py --flow trending_ai_books \
  --query "machine learning" \
  --limit 10

# Search by subject
pdm run python3 ./korben.py --flow trending_ai_books \
  --subject "Artificial Intelligence" \
  --limit 15 \
  --recipient "you@example.com"
```

## Parameters

### search_books Task

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | - | General search query |
| `subject` | string | - | Search by subject category |
| `author` | string | - | Search by author name |
| `limit` | int | 20 | Maximum results to return |
| `page` | int | 1 | Page number for pagination |

### trending_ai_books Flow

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | "artificial intelligence" | Search query |
| `subject` | string | - | Search by subject instead |
| `limit` | int | 15 | Maximum books to include |
| `recipient` | string | PERSONAL_EMAIL | Email recipient |

## Output

Books include:
- Title
- Author(s)
- Publisher
- Publication date
- ISBN-13
- Synopsis/description

## Examples

### Discover Latest Deep Learning Books

```bash
pdm run python3 ./korben.py --flow trending_ai_books \
  --query "deep learning" \
  --limit 10
```

### Get Books by Specific Author

```bash
pdm run python3 ./korben.py --task search_books \
  --author "Yann LeCun" \
  --limit 5
```

### Search Computer Vision Books

```bash
pdm run python3 ./korben.py --flow trending_ai_books \
  --subject "Computer Vision" \
  --limit 12
```

## API Reference

- ISBNdb API Documentation: https://isbndb.com/isbndb-api-documentation-v2
- Search endpoint: `/books/{query}`
- Subject endpoint: `/subject/{subject}`
- Author endpoint: `/author/{author}`
- ISBN endpoint: `/book/{isbn}`

## Notes

- ISBNdb has rate limits on free tier
- Results sorted by relevance
- Some books may not have full synopsis
- ISBN-13 preferred over ISBN-10
- Auto-registered via plugin system - no registry edits needed!

