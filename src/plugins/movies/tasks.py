"""Movies tasks - discover movies from TMDB."""

import logging
import json
import datetime
from src.plugins.movies.lib import TMDBService

logger = logging.getLogger(__name__)


def discover_movies(**kwargs) -> str:
    """
    Discover movies from TMDB based on search criteria.
    
    Args:
        genres: Comma-separated genre IDs (e.g., "28,878" for Action & Sci-Fi)
        min_rating: Minimum vote average (0-10)
        min_votes: Minimum vote count (default: 100)
        min_runtime: Minimum runtime in minutes (default: 60)
        max_runtime: Maximum runtime in minutes
        start_year: Start year for filtering (default: current year)
        years_back: How many years back from current (alternative to start_year)
        sort_by: Sort order (default: "popularity.desc")
        limit: Maximum number of results to return
    
    Returns:
        JSON string containing discovered movies
    """
    # Calculate date range
    current_year = datetime.datetime.now().year
    start_year = kwargs.get('start_year')
    
    if start_year is None:
        years_back = kwargs.get('years_back')
        if years_back is not None:
            start_year = current_year - years_back
        else:
            # Default to current year
            start_year = current_year
    
    start_date = f"{start_year}-01-01"
    
    # Build parameters (using snake_case with _gte/_lte - auto-converted by client)
    params = {
        'with_genres': kwargs.get('genres'),
        'release_date_gte': start_date,
        'vote_average_gte': kwargs.get('min_rating'),
        'vote_count_gte': kwargs.get('min_votes', 100),
        'with_runtime_gte': kwargs.get('min_runtime', 60),
        'with_runtime_lte': kwargs.get('max_runtime'),
        'sort_by': kwargs.get('sort_by', 'popularity.desc'),
    }
    
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    
    logger.info(f"Discovering movies from {start_date} with criteria: {params}")
    
    try:
        tmdb_service = TMDBService()
        response_data = tmdb_service.discover_movies(**params)
        
        movies = response_data.get('results', [])
        
        # Apply limit if specified
        limit = kwargs.get('limit')
        if limit:
            movies = movies[:int(limit)]
        
        logger.info(f"Found {len(movies)} movies matching criteria")
        
        # Return formatted results
        return json.dumps({
            'movies': movies,
            'total_results': len(movies),
            'criteria': {
                'genres': params.get('with_genres'),
                'min_rating': params.get('vote_average_gte'),
                'min_votes': params.get('vote_count_gte'),
                'start_year': start_year
            }
        })
        
    except Exception as e:
        error_msg = f"Failed to discover movies: {e}"
        logger.error(error_msg)
        return json.dumps({'error': error_msg})

