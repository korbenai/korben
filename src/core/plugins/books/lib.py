"""ISBNdb API client for book discovery and information.

API Documentation: https://isbndb.com/isbndb-api-documentation-v2
"""

import os
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


class ISBNdbService:
    """Client for ISBNdb API v2.
    
    ISBNdb provides comprehensive book data including titles, authors, publishers,
    ISBN numbers, and more.
    """
    
    BASE_URL = "https://api2.isbndb.com"
    
    def __init__(self):
        """Initialize ISBNdb service with API key from environment.
        
        Get your API key from: https://isbndb.com/isbn-database
        """
        self.api_key = os.getenv('ISBNDB_API_KEY')
        if not self.api_key:
            raise ValueError("ISBNDB_API_KEY environment variable not set. "
                           "Get your key from https://isbndb.com/isbn-database")
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to ISBNdb API.
        
        Args:
            endpoint: API endpoint (e.g., '/books/artificial+intelligence')
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"ISBNdb API HTTP error {response.status_code}: {response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"ISBNdb API request failed: {e}")
            raise
    
    def search_books(self, query: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Search for books by keyword.
        
        Args:
            query: Search query (e.g., 'artificial intelligence', 'machine learning')
            page: Page number for pagination
            page_size: Number of results per page (max 1000)
            
        Returns:
            Dictionary with 'books' array containing book objects
        """
        # ISBNdb v2 uses URL path for search query
        query_encoded = query.replace(' ', '+')
        endpoint = f'/books/{query_encoded}'
        
        params = {
            'page': page,
            'pageSize': page_size
        }
        
        return self._make_request(endpoint, params)
    
    def search_by_subject(self, subject: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Search books by subject.
        
        Args:
            subject: Subject to search (e.g., 'Artificial Intelligence', 'Computer Science')
            page: Page number
            page_size: Results per page
            
        Returns:
            Dictionary with book results
        """
        subject_encoded = subject.replace(' ', '+')
        endpoint = f'/subject/{subject_encoded}'
        
        params = {
            'page': page,
            'pageSize': page_size
        }
        
        return self._make_request(endpoint, params)
    
    def get_book_by_isbn(self, isbn: str) -> Dict[str, Any]:
        """Get book details by ISBN.
        
        Args:
            isbn: ISBN-10 or ISBN-13
            
        Returns:
            Dictionary with book details
        """
        return self._make_request(f'/book/{isbn}')
    
    def search_by_author(self, author: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Search books by author name.
        
        Args:
            author: Author name
            page: Page number
            page_size: Results per page
            
        Returns:
            Dictionary with book results
        """
        author_encoded = author.replace(' ', '+')
        endpoint = f'/author/{author_encoded}'
        
        params = {
            'page': page,
            'pageSize': page_size
        }
        
        return self._make_request(endpoint, params)

