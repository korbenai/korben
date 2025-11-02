# Movies Plugin

Discover movies from TMDB and get personalized recommendations via email.

## Structure

```
movies/
├── __init__.py
├── tasks.py       # discover_movies task
├── flows.py       # trending_movies, weekly_trending_movies flows
├── lib.py         # TMDB API client
└── README.md      # This file
```

## Tasks

- **discover_movies** - Query TMDB for movies matching criteria (genre, rating, year, etc.)

## Flows

- **trending_movies** - Get popular movies by genre and email them
- **popular_movies** - Get popular movies across all genres

## Requirements

### Environment Variables

- `TMDB_API_KEY` - Get from https://www.themoviedb.org/settings/api
- `POSTMARK_API_KEY` - For email delivery
- `PERSONAL_EMAIL` - Default recipient

### Configuration File (Optional)

**Location:** `src/plugins/movies/config.yml`

```bash
# Copy example to create your config
cp src/plugins/movies/config.yml.example src/plugins/movies/config.yml
vim src/plugins/movies/config.yml
```

```yaml
variables:
  genres:                                # Default genres
    - sci-fi
    - action
    - thriller
  min_rating: 7.0                        # Minimum rating
  limit: 10                              # Maximum movies
```

**Priority:** CLI arguments > config file > hardcoded defaults

## Usage

```bash
# Discover movies
pdm run python3 ./korben.py --task discover_movies --genres "878,28" --min_rating 7.0

# Get trending movies by genre
pdm run python3 ./korben.py --flow trending_movies --genres "sci-fi,action"

# Get popular recent movies (all genres)
pdm run python3 ./korben.py --flow weekly_trending_movies
```

