"""TMDB API client for movie discovery and information.

Simplified client following TMDB patterns:
- Search/discover endpoints return results with IDs
- Detail endpoints use IDs to get full information
- Use append_to_response to get related data in one call

API Documentation: https://developer.themoviedb.org/docs/search-and-query-for-details
"""

import os
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


class TMDBService:
    """Simplified TMDB API client.
    
    Follows the pattern from https://developer.themoviedb.org/docs/search-and-query-for-details:
    1. Search/discover to find movies (returns IDs)
    2. Query details by ID
    3. Use append_to_response for related data
    """
    
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self):
        """Initialize TMDB service with API key from environment.
        
        Get your API key from: https://www.themoviedb.org/settings/api
        """
        self.api_key = os.getenv('TMDB_API_KEY')
        if not self.api_key:
            raise ValueError("TMDB_API_KEY environment variable not set. "
                           "Get your key from https://www.themoviedb.org/settings/api")
    
    def _convert_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert snake_case parameters with _gte/_lte suffixes to TMDB's dot notation.
        
        Example: vote_average_gte -> vote_average.gte
        """
        converted = {}
        for key, value in params.items():
            if value is None:
                continue
            
            # Convert _gte and _lte suffixes to dot notation
            if key.endswith('_gte'):
                new_key = key.replace('_gte', '.gte')
            elif key.endswith('_lte'):
                new_key = key.replace('_lte', '.lte')
            else:
                new_key = key
            
            converted[new_key] = value
        
        return converted
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to TMDB API.
        
        Args:
            endpoint: API endpoint (e.g., '/movie/popular')
            params: Query parameters (automatically converts _gte/_lte to dot notation)
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        if params is None:
            params = {}
        
        # Convert parameters and add API key
        params = self._convert_params(params)
        params['api_key'] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"TMDB API HTTP error {response.status_code}: {response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDB API request failed: {e}")
            raise
    
    # Core Methods: Search, Discover, Details
    
    def search_movies(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search for movies by title.
        
        Pattern from: https://developer.themoviedb.org/docs/search-and-query-for-details
        
        Args:
            query: Search query string
            **kwargs: Additional parameters (page, year, include_adult, etc.)
            
        Returns:
            Dictionary with 'results' array containing movie objects with IDs
        """
        params = {'query': query, 'include_adult': False, **kwargs}
        return self._make_request('/search/movie', params)
    
    def discover_movies(self, **kwargs) -> Dict[str, Any]:
        """Discover movies with advanced filtering.
        
        Common parameters (use snake_case with _gte/_lte, auto-converted to dot notation):
        - with_genres: Comma-separated genre IDs
        - release_date_gte: Filter by release date (YYYY-MM-DD)
        - vote_average_gte: Minimum rating
        - vote_count_gte: Minimum vote count
        - with_runtime_gte: Minimum runtime in minutes
        - sort_by: Sort order (default: popularity.desc)
        - page: Page number
        
        Full docs: https://developer.themoviedb.org/reference/discover-movie
        
        Returns:
            Dictionary with 'results' array containing movie objects
        """
        defaults = {
            'include_adult': False,
            'include_video': False,
            'language': 'en-US',
            'sort_by': 'popularity.desc',
            'page': 1
        }
        params = {**defaults, **kwargs}
        return self._make_request('/discover/movie', params)
    
    def get_movie_details(self, movie_id: int, append_to_response: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed information about a movie.
        
        Args:
            movie_id: TMDB movie ID (from search/discover results)
            append_to_response: Comma-separated list of sub-requests
                               (e.g., 'videos,credits,watch/providers')
            
        Returns:
            Dictionary containing full movie details
        """
        params = {}
        if append_to_response:
            params['append_to_response'] = append_to_response
        return self._make_request(f'/movie/{movie_id}', params)
    
    def list_genres(self, media_type: str = 'movie') -> Dict[str, Any]:
        """Get list of genres.
        
        Args:
            media_type: 'movie' or 'tv'
            
        Returns:
            Dictionary with 'genres' array
        """
        return self._make_request(f'/genre/{media_type}/list')
    
    # Convenience Methods: Lists & Trending
    
    def get_trending(self, media_type: str = 'movie', time_window: str = 'week') -> Dict[str, Any]:
        """Get trending movies or TV shows.
        
        Args:
            media_type: 'movie', 'tv', or 'all'
            time_window: 'day' or 'week'
        """
        return self._make_request(f'/trending/{media_type}/{time_window}')
    
    def get_popular_movies(self, **kwargs) -> Dict[str, Any]:
        """Get popular movies."""
        return self._make_request('/movie/popular', kwargs)
    
    def get_top_rated_movies(self, **kwargs) -> Dict[str, Any]:
        """Get top rated movies."""
        return self._make_request('/movie/top_rated', kwargs)
    
    def get_now_playing(self, **kwargs) -> Dict[str, Any]:
        """Get movies currently in theaters."""
        return self._make_request('/movie/now_playing', kwargs)
    
    def get_upcoming_movies(self, **kwargs) -> Dict[str, Any]:
        """Get upcoming movies."""
        return self._make_request('/movie/upcoming', kwargs)

