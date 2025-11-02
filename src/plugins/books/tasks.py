"""Books tasks - search and discover books using ISBNdb."""

import logging
import json
from src.plugins.books.lib import ISBNdbService
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs

logger = logging.getLogger(__name__)


def search_books(**kwargs) -> str:
    """
    Search for books using ISBNdb API.
    
    Config file: src/plugins/books/config.yml (optional)
    
    Args:
        query: Search query (e.g., 'artificial intelligence', 'python programming')
        subject: Search by subject instead of general query
        author: Search by author name
        limit: Maximum number of results to return (default: from config or 20)
        page: Page number for pagination (default: 1)
    
    Returns:
        JSON string containing book results
    """
    # Load plugin config and merge with kwargs
    config = get_plugin_config('books')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    query = params.get('query') or config_vars.get('query')
    subject = params.get('subject') or config_vars.get('subject')
    author = params.get('author') or config_vars.get('author')
    limit = params.get('limit') or config_vars.get('limit', 20)
    page = params.get('page', 1)
    
    if not query and not subject and not author:
        return json.dumps({'error': 'Provide at least one of: query, subject, or author'})
    
    try:
        isbndb = ISBNdbService()
        
        # Determine which search method to use
        if subject:
            logger.info(f"Searching books by subject: {subject}")
            response = isbndb.search_by_subject(subject, page=page, page_size=limit)
        elif author:
            logger.info(f"Searching books by author: {author}")
            response = isbndb.search_by_author(author, page=page, page_size=limit)
        else:
            logger.info(f"Searching books with query: {query}")
            response = isbndb.search_books(query, page=page, page_size=limit)
        
        books = response.get('books', [])
        
        logger.info(f"Found {len(books)} books")
        
        # Return formatted results
        return json.dumps({
            'books': books,
            'total_results': len(books),
            'query': query or subject or author
        })
        
    except Exception as e:
        error_msg = f"Failed to search books: {e}"
        logger.error(error_msg)
        return json.dumps({'error': error_msg})


def get_book_details(**kwargs) -> str:
    """
    Get detailed information about a book by ISBN.
    
    Config file: src/plugins/books/config.yml (optional)
    
    Args:
        isbn: ISBN-10 or ISBN-13 number
    
    Returns:
        JSON string containing book details
    """
    # Load plugin config and merge with kwargs
    config = get_plugin_config('books')
    params = merge_config_with_kwargs(config, kwargs)
    
    isbn = params.get('isbn')
    
    if not isbn:
        return json.dumps({'error': 'ISBN is required. Provide --isbn'})
    
    try:
        isbndb = ISBNdbService()
        logger.info(f"Fetching book details for ISBN: {isbn}")
        
        book_data = isbndb.get_book_by_isbn(isbn)
        
        return json.dumps(book_data)
        
    except Exception as e:
        error_msg = f"Failed to get book details: {e}"
        logger.error(error_msg)
        return json.dumps({'error': error_msg})

