"""Books tasks - search and discover books using ISBNdb."""

import logging
import json
from src.plugins.books.lib import ISBNdbService

logger = logging.getLogger(__name__)


def search_books(**kwargs) -> str:
    """
    Search for books using ISBNdb API.
    
    Args:
        query: Search query (e.g., 'artificial intelligence', 'python programming')
        subject: Search by subject instead of general query
        author: Search by author name
        limit: Maximum number of results to return (default: 20)
        page: Page number for pagination (default: 1)
    
    Returns:
        JSON string containing book results
    """
    query = kwargs.get('query')
    subject = kwargs.get('subject')
    author = kwargs.get('author')
    limit = kwargs.get('limit', 20)
    page = kwargs.get('page', 1)
    
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
    
    Args:
        isbn: ISBN-10 or ISBN-13 number
    
    Returns:
        JSON string containing book details
    """
    isbn = kwargs.get('isbn')
    
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

