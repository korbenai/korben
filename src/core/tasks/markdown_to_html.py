"""Markdown to HTML conversion task."""

import logging
import markdown

logger = logging.getLogger(__name__)


def run(**kwargs):
    """
    Convert markdown text to HTML.
    
    Args:
        text: Markdown text to convert
        
    Returns:
        str: HTML output
    """
    text = kwargs.get('text')
    
    if not text:
        return "ERROR: No text provided. Provide --text."
    
    # Convert markdown to HTML
    html = markdown.markdown(
        text,
        extensions=['extra', 'nl2br', 'sane_lists']
    )
    
    logger.debug(f"Converted {len(text)} chars of markdown to {len(html)} chars of HTML")
    
    return html

