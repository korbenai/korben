"""Movies tasks - discover movies from TMDB."""

import logging
import json
import datetime
from src.plugins.movies.lib import TMDBService
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs

logger = logging.getLogger(__name__)


def discover_movies(**kwargs) -> str:
    """
    Discover movies from TMDB based on search criteria.
    
    Config file: src/plugins/movies/config.yml (optional)
    
    Args:
        genres: Comma-separated genre IDs (e.g., "28,878" for Action & Sci-Fi)
        min_rating: Minimum vote average (0-10, default: from config or 7.0)
        min_votes: Minimum vote count (default: from config or 100)
        min_runtime: Minimum runtime in minutes (default: 60)
        max_runtime: Maximum runtime in minutes
        start_year: Start year for filtering (default: current year)
        years_back: How many years back from current (alternative to start_year)
        sort_by: Sort order (default: "popularity.desc")
        limit: Maximum number of results to return (default: from config or 10)
    
    Returns:
        JSON string containing discovered movies
    """
    # Load plugin config and merge with kwargs
    config = get_plugin_config('movies')
    params_merged = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    # Calculate date range
    current_year = datetime.datetime.now().year
    start_year = params_merged.get('start_year')
    
    if start_year is None:
        years_back = params_merged.get('years_back')
        if years_back is not None:
            start_year = current_year - years_back
        else:
            # Default to current year
            start_year = current_year
    
    start_date = f"{start_year}-01-01"
    
    # Build parameters with config defaults
    params = {
        'with_genres': params_merged.get('genres'),
        'release_date_gte': start_date,
        'vote_average_gte': params_merged.get('min_rating') or config_vars.get('min_rating', 7.0),
        'vote_count_gte': params_merged.get('min_votes') or config_vars.get('min_votes', 100),
        'with_runtime_gte': params_merged.get('min_runtime', 60),
        'with_runtime_lte': params_merged.get('max_runtime'),
        'sort_by': params_merged.get('sort_by', 'popularity.desc'),
    }
    
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    
    logger.info(f"Discovering movies from {start_date} with criteria: {params}")
    
    try:
        tmdb_service = TMDBService()
        response_data = tmdb_service.discover_movies(**params)
        
        movies = response_data.get('results', [])
        
        # Apply limit from config or kwargs
        limit = params_merged.get('limit') or config_vars.get('limit', 10)
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

