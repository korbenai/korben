"""Utility tasks - generic reusable tasks for workflows."""

import os
import sys
import logging
import markdown
from src.lib.core_utils import get_tmp_dir, get_agent_name

logger = logging.getLogger(__name__)


# File I/O Tasks

def read_file(**kwargs):
    """
    Read text from a file.
    
    Args:
        file_path: Path to file to read (absolute or relative to tmp_dir)
    
    Returns:
        str: File contents
    """
    file_path = kwargs.get('file_path')
    
    if not file_path:
        return "ERROR: No file_path specified. Provide --file_path."
    
    # If relative path, make it relative to tmp_dir
    if not os.path.isabs(file_path):
        tmp_dir = get_tmp_dir()
        file_path = os.path.join(tmp_dir, file_path)
    
    if not os.path.exists(file_path):
        return f"ERROR: File not found: {file_path}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content


def write_file(**kwargs):
    """
    Write text to a file.
    
    Args:
        file_path: Path to file to write (absolute or relative to tmp_dir)
        content: Text content to write
    
    Returns:
        str: Path to written file
    """
    file_path = kwargs.get('file_path')
    content = kwargs.get('content')
    
    if not file_path:
        return "ERROR: No file_path specified. Provide --file_path."
    
    if content is None:
        return "ERROR: No content specified. Provide --content."
    
    # If relative path, make it relative to tmp_dir
    if not os.path.isabs(file_path):
        tmp_dir = get_tmp_dir()
        file_path = os.path.join(tmp_dir, file_path)
    
    # Create directory if it doesn't exist
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path


# Text Processing Tasks

def markdown_to_html(**kwargs):
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


def extract_wisdom(**kwargs):
    """
    Extract wisdom and insights from text using AI.
    
    Uses the centralized WisdomExtractorAgent to analyze text and 
    extract insights, ideas, quotes, habits, facts, and recommendations.
    
    Args:
        text: Text to extract wisdom from (or reads from stdin if not provided)
    
    Returns:
        str: Extracted wisdom in markdown format
    """
    from src.plugins.utilities.agents import WisdomExtractorAgent
    
    text = kwargs.get('text')
    
    # If no text provided, read from stdin
    if not text:
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            return "ERROR: No text provided. Provide --text or pipe input via stdin."
    
    # Use the centralized agent
    try:
        agent = WisdomExtractorAgent()
        wisdom = agent.run(text=text)
        return wisdom
    except Exception as e:
        logger.error(f"Failed to extract wisdom: {e}")
        return f"ERROR: Failed to extract wisdom: {e}"


# Example/Demo Tasks

def entropy(**kwargs):
    """
    Example task demonstrating multi-agent AI collaboration.
    
    Returns:
        str: Example output
    """
    result = "Entropy example task - demonstrates multi-agent AI collaboration patterns"
    logger.info(result)
    return result
