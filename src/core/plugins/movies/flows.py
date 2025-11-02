"""Movies flows - discover and email movie recommendations."""

import os
import json
import logging
import controlflow as cf
from src.core.plugins.movies import tasks as movie_tasks
from src.core.plugins.utilities import tasks as utility_tasks
from src.core.plugins.movies.lib import TMDBService
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs

logger = logging.getLogger(__name__)

# Genre mappings for TMDB
GENRE_MAP = {
    'action': '28',
    'adventure': '12',
    'animation': '16',
    'comedy': '35',
    'crime': '80',
    'documentary': '99',
    'drama': '18',
    'family': '10751',
    'fantasy': '14',
    'history': '36',
    'horror': '27',
    'music': '10402',
    'mystery': '9648',
    'romance': '10749',
    'science fiction': '878',
    'sci-fi': '878',
    'thriller': '53',
    'tv movie': '10770',
    'war': '10752',
    'western': '37'
}


def _format_movie_email(movies: list, genre_names: list) -> str:
    """
    Format movies into HTML email content.
    
    Args:
        movies: List of movie dictionaries
        genre_names: List of genre names for the subject
        
    Returns:
        HTML formatted email content
    """
    html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .movie { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
            .movie-title { font-size: 24px; font-weight: bold; margin-bottom: 10px; color: #2c3e50; }
            .movie-meta { color: #7f8c8d; margin-bottom: 10px; }
            .movie-overview { margin-top: 10px; line-height: 1.8; }
            .rating { color: #f39c12; font-weight: bold; }
            .high-rating { color: #27ae60; }
            .year { color: #3498db; }
            h1 { color: #2c3e50; }
        </style>
    </head>
    <body>
        <h1>🎬 Trending Movies</h1>
        <p>Here are the latest trending movies in your selected genres:</p>
    """
    
    for movie in movies:
        title = movie.get('title', 'N/A')
        overview = movie.get('overview', 'No overview available.')
        popularity = movie.get('popularity', 0)
        vote_average = movie.get('vote_average', 0)
        vote_count = movie.get('vote_count', 0)
        release_date = movie.get('release_date', 'N/A')
        year = release_date.split('-')[0] if release_date != 'N/A' else 'N/A'
        
        rating_class = 'high-rating' if vote_average >= 7.5 else 'rating'
        
        html += f"""
        <div class="movie">
            <div class="movie-title">{title} <span class="year">({year})</span></div>
            <div class="movie-meta">
                <span class="{rating_class}">⭐ {vote_average:.1f}/10</span> 
                ({vote_count} votes) • 
                Popularity: {popularity:.1f}
            </div>
            <div class="movie-overview">{overview}</div>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    return html


@cf.flow
def trending_movies_workflow(**kwargs):
    """
    ControlFlow flow for discovering trending movies and sending via email.
    
    Config file: config/movies.yml (optional)
    
    Args:
        genres: List of genre names (default: from config or ['sci-fi', 'action', 'thriller', 'drama', 'fantasy'])
        min_rating: Minimum rating (default: from config or 7.0)
        min_votes: Minimum vote count (default: from config or 100)
        years_back: How many years back to search (default: from config or current year only)
        start_year: Start year for filtering (overrides years_back if set)
        limit: Maximum number of movies (default: from config or 10)
        recipient: Email recipient (default: PERSONAL_EMAIL env var)
    
    Returns:
        Status message
    """
    import datetime
    
    # Load plugin config and merge with kwargs (kwargs take precedence)
    config = get_plugin_config('movies')
    params = merge_config_with_kwargs(config, kwargs)
    
    results = []
    current_year = datetime.datetime.now().year
    
    # Parse genres (from config.variables.genres or kwargs)
    # Config uses 'variables' section, so get from there first
    config_vars = config.get('variables', {})
    genres_input = params.get('genres') or config_vars.get('genres', ['sci-fi', 'action', 'thriller', 'drama', 'fantasy'])
    if isinstance(genres_input, str):
        genre_names = [g.strip().lower() for g in genres_input.split(',')]
    else:
        genre_names = [g.lower() for g in genres_input]
    
    # Convert genre names to IDs
    genre_ids = []
    valid_genres = []
    for genre_name in genre_names:
        genre_id = GENRE_MAP.get(genre_name)
        if genre_id:
            genre_ids.append(genre_id)
            valid_genres.append(genre_name.title())
        else:
            logger.warning(f"Unknown genre: {genre_name}")
    
    if not genre_ids:
        error_msg = f"No valid genres found. Available: {', '.join(GENRE_MAP.keys())}"
        logger.error(error_msg)
        return error_msg
    
    genres_str = ','.join(genre_ids)
    min_rating = params.get('min_rating', 7.0)
    min_votes = params.get('min_votes', 100)
    
    # Calculate start year: use start_year if provided, otherwise from config or current year
    start_year = params.get('start_year')
    if start_year is None:
        years_back = params.get('years_back')
        if years_back is not None:
            start_year = current_year - years_back
        else:
            # Default to current year only
            start_year = current_year
    
    limit = params.get('limit', 10)
    recipient = params.get('recipient') or os.getenv('PERSONAL_EMAIL')
    
    logger.info(f"Step 1: Discovering movies for genres: {', '.join(valid_genres)} from {start_year}+")
    
    # Discover movies
    try:
        discover_result = movie_tasks.discover_movies(
            genres=genres_str,
            min_rating=min_rating,
            min_votes=min_votes,
            start_year=start_year,
            limit=limit
        )
        
        discover_data = json.loads(discover_result)
        
        if 'error' in discover_data:
            error_msg = f"Failed to discover movies: {discover_data['error']}"
            logger.error(error_msg)
            return error_msg
        
        movies = discover_data.get('movies', [])
        
        if not movies:
            result = "No movies found matching the criteria."
            logger.info(result)
            return result
        
        # Sort by rating (highest first)
        movies_sorted = sorted(movies, key=lambda x: x.get('vote_average', 0), reverse=True)
        
        results.append(f"Found {len(movies_sorted)} movies")
        
        # Step 2: Format and send email
        logger.info("Step 2: Formatting and sending email...")
        
        if not recipient:
            error_msg = "No recipient specified. Provide 'recipient' or set PERSONAL_EMAIL environment variable."
            logger.error(error_msg)
            return error_msg
        
        # Format email content
        email_content = _format_movie_email(movies_sorted, valid_genres)
        subject = f"🎬 Trending {', '.join(valid_genres)} Movies"
        
        # Send email
        email_result = utility_tasks.send_email(
            recipient=recipient,
            subject=subject,
            content=email_content
        )
        
        results.append(email_result)
        
        logger.info(f"Successfully sent {len(movies_sorted)} movies to {recipient}")
        
        return "\n".join(results)
        
    except Exception as e:
        error_msg = f"Workflow failed: {e}"
        logger.error(error_msg)
        return error_msg


@cf.flow
def popular_movies_workflow(**kwargs):
    """
    Get popular movies from current/recent years (sorted by popularity).
    
    Note: Uses discover API with popularity sort instead of trending endpoint,
    because trending doesn't support date filtering.
    
    Args:
        limit: Maximum number of movies (default: 10)
        min_rating: Minimum rating to filter (default: 7.0)
        min_votes: Minimum vote count (default: 100)
        start_year: Filter movies from this year onwards (default: current year)
        years_back: How many years back to include (alternative to start_year)
        recipient: Email recipient (default: PERSONAL_EMAIL env var)
    
    Returns:
        Status message
    """
    import datetime
    
    limit = kwargs.get('limit', 10)
    min_rating = kwargs.get('min_rating', 7.0)
    min_votes = kwargs.get('min_votes', 100)
    recipient = kwargs.get('recipient') or os.getenv('PERSONAL_EMAIL')
    
    # Calculate start year
    current_year = datetime.datetime.now().year
    start_year = kwargs.get('start_year')
    
    if start_year is None:
        years_back = kwargs.get('years_back')
        if years_back is not None:
            start_year = current_year - years_back
        else:
            # Default to current year only
            start_year = current_year
    
    if not recipient:
        error_msg = "No recipient specified. Provide 'recipient' or set PERSONAL_EMAIL environment variable."
        logger.error(error_msg)
        return error_msg
    
    start_date = f"{start_year}-01-01"
    logger.info(f"Fetching popular movies from {start_date} onwards...")
    
    try:
        # Use discover with popularity sort instead of trending endpoint
        # This allows proper date filtering at the API level
        tmdb_service = TMDBService()
        discover_data = tmdb_service.discover_movies(
            release_date_gte=start_date,
            vote_average_gte=min_rating,
            vote_count_gte=min_votes,
            sort_by='popularity.desc'
        )
        
        movies = discover_data.get('results', [])
        
        # Limit results
        movies_to_send = movies[:limit]
        
        if not movies_to_send:
            result = f"No movies found from {start_year}+ with rating >= {min_rating}"
            logger.info(result)
            return result
        
        # Sort by rating for display (already sorted by popularity from API)
        movies_sorted = sorted(movies_to_send, key=lambda x: x.get('vote_average', 0), reverse=True)
        
        # Format and send email
        email_content = _format_movie_email(movies_sorted, ['Popular'])
        subject = f"🎬 Popular Movies from {start_year}+"
        
        email_result = utility_tasks.send_email(
            recipient=recipient,
            subject=subject,
            content=email_content
        )
        
        logger.info(f"Successfully sent {len(movies_sorted)} popular movies to {recipient}")
        
        return f"Found {len(movies_sorted)} popular movies\n{email_result}"
        
    except Exception as e:
        error_msg = f"Workflow failed: {e}"
        logger.error(error_msg)
        return error_msg

