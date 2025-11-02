"""Books flows - discover and email book recommendations."""

import os
import json
import logging
import controlflow as cf
from src.plugins.books import tasks as book_tasks
from src.plugins.email import tasks as email_tasks
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs

# Plugin dependencies
__dependencies__ = ['email']

logger = logging.getLogger(__name__)


def _format_books_email(books: list, topic: str) -> str:
    """
    Format books into HTML email content.
    
    Args:
        books: List of book dictionaries
        topic: Topic/query for the email subject
        
    Returns:
        HTML formatted email content
    """
    html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .book { margin-bottom: 30px; padding: 20px; border-left: 4px solid #3498db; background: #f8f9fa; }
            .book-title { font-size: 22px; font-weight: bold; margin-bottom: 8px; color: #2c3e50; }
            .book-author { font-size: 16px; color: #7f8c8d; margin-bottom: 8px; font-style: italic; }
            .book-meta { color: #95a5a6; font-size: 14px; margin-bottom: 10px; }
            .book-synopsis { margin-top: 10px; line-height: 1.8; }
            .isbn { font-family: monospace; background: #ecf0f1; padding: 2px 6px; border-radius: 3px; }
            h1 { color: #2c3e50; }
            .publisher { color: #16a085; }
        </style>
    </head>
    <body>
        <h1>📚 Trending AI Books</h1>
        <p>Curated list of books about {topic}:</p>
    """
    
    for book in books:
        title = book.get('title', 'N/A')
        authors = book.get('authors', [])
        author_str = ', '.join(authors) if authors else 'Unknown Author'
        
        publisher = book.get('publisher', 'N/A')
        date_published = book.get('date_published', 'N/A')
        isbn13 = book.get('isbn13', book.get('isbn', 'N/A'))
        synopsis = book.get('synopsis', book.get('overview', 'No description available.'))
        
        # Handle synopsis length
        if len(synopsis) > 500:
            synopsis = synopsis[:500] + '...'
        
        html += f"""
        <div class="book">
            <div class="book-title">{title}</div>
            <div class="book-author">by {author_str}</div>
            <div class="book-meta">
                <span class="publisher">{publisher}</span> • 
                {date_published} • 
                <span class="isbn">ISBN: {isbn13}</span>
            </div>
            <div class="book-synopsis">{synopsis}</div>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    return html


@cf.flow
def trending_ai_books_workflow(**kwargs):
    """
    Search for trending AI books and email them.
    
    Config file: config/books.yml (optional)
    
    Args:
        query: Search query (default: from config or 'artificial intelligence')
        subject: Search by subject instead
        limit: Maximum number of books (default: from config or 15)
        recipient: Email recipient (default: PERSONAL_EMAIL env var)
    
    Returns:
        Status message
    """
    # Load plugin config and merge with kwargs (kwargs take precedence)
    config = get_plugin_config('books')
    params = merge_config_with_kwargs(config, kwargs)
    
    # Extract parameters from config.variables section or kwargs
    config_vars = config.get('variables', {})
    query = params.get('query') or config_vars.get('query', 'artificial intelligence')
    subject_filter = params.get('subject') or config_vars.get('subject')
    limit = params.get('limit') or config_vars.get('limit', 15)
    recipient = params.get('recipient') or os.getenv('PERSONAL_EMAIL')
    
    if not recipient:
        error_msg = "No recipient specified. Provide 'recipient' or set PERSONAL_EMAIL environment variable."
        logger.error(error_msg)
        return error_msg
    
    logger.info(f"Step 1: Searching for AI books...")
    
    try:
        # Search for books
        search_params = {
            'limit': limit
        }
        
        if subject_filter:
            search_params['subject'] = subject_filter
        else:
            search_params['query'] = query
        
        search_result = book_tasks.search_books(**search_params)
        search_data = json.loads(search_result)
        
        if 'error' in search_data:
            error_msg = f"Failed to search books: {search_data['error']}"
            logger.error(error_msg)
            return error_msg
        
        books = search_data.get('books', [])
        
        if not books:
            result = f"No books found for: {query or subject_filter}"
            logger.info(result)
            return result
        
        logger.info(f"Found {len(books)} books")
        
        # Step 2: Format and send email
        logger.info("Step 2: Formatting and sending email...")
        
        email_content = _format_books_email(books, query or subject_filter)
        email_subject = f"📚 Trending AI Books: {query or subject_filter}"
        
        email_result = email_tasks.send_email(
            recipient=recipient,
            subject=email_subject,
            content=email_content
        )
        
        logger.info(f"Successfully sent {len(books)} books to {recipient}")
        
        return f"Found {len(books)} books\n{email_result}"
        
    except Exception as e:
        error_msg = f"Workflow failed: {e}"
        logger.error(error_msg)
        return error_msg
