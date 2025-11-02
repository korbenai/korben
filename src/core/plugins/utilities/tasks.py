"""Utility tasks - generic reusable tasks for workflows."""

import os
import sys
import logging
import markdown
import controlflow as cf
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
    
    Args:
        text: Text to extract wisdom from (or reads from stdin if not provided)
    
    Returns:
        str: Extracted wisdom in markdown format
    """
    text = kwargs.get('text')
    
    # If no text provided, read from stdin
    if not text:
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            return "ERROR: No text provided. Provide --text or pipe input via stdin."
    
    # Create wisdom extractor agent with detailed instructions
    agent_name = get_agent_name()
    wisdom_agent = cf.Agent(
        name=agent_name,
        instructions="""
# IDENTITY and PURPOSE

You extract surprising, insightful, and interesting information from text content. You are interested in insights related to the purpose and meaning of life, human flourishing, the role of technology in the future of humanity, artificial intelligence and its affect on humans, memes, learning, reading, books, continuous improvement, and similar topics.

Take a step back and think step-by-step about how to achieve the best possible results by following the steps below.

# STEPS

- Extract a summary of the content in 25 words, including who is presenting and the content being discussed into a section called SUMMARY.

- Extract 20 to 50 of the most surprising, insightful, and/or interesting ideas from the input in a section called IDEAS:. If there are less than 50 then collect all of them. Make sure you extract at least 20.

- Extract 10 to 20 of the best insights from the input and from a combination of the raw input and the IDEAS above into a section called INSIGHTS. These INSIGHTS should be fewer, more refined, more insightful, and more abstracted versions of the best ideas in the content. 

- Extract 15 to 30 of the most surprising, insightful, and/or interesting quotes from the input into a section called QUOTES:. Use the exact quote text from the input. Include the name of the speaker of the quote at the end.

- Extract 15 to 30 of the most practical and useful personal habits of the speakers, or mentioned by the speakers, in the content into a section called HABITS. Examples include but aren't limited to: sleep schedule, reading habits, things they always do, things they always avoid, productivity tips, diet, exercise, etc.

- Extract 15 to 30 of the most surprising, insightful, and/or interesting valid facts about the greater world that were mentioned in the content into a section called FACTS:.

- Extract all mentions of writing, art, tools, projects and other sources of inspiration mentioned by the speakers into a section called REFERENCES. This should include any and all references to something that the speaker mentioned.

- Extract the most potent takeaway and recommendation into a section called ONE-SENTENCE TAKEAWAY. This should be a 15-word sentence that captures the most important essence of the content.

- Extract the 15 to 30 of the most surprising, insightful, and/or interesting recommendations that can be collected from the content into a section called RECOMMENDATIONS.

# OUTPUT INSTRUCTIONS

- Only output Markdown.

- Write the IDEAS bullets as exactly 16 words.

- Write the RECOMMENDATIONS bullets as exactly 16 words.

- Write the HABITS bullets as exactly 16 words.

- Write the FACTS bullets as exactly 16 words.

- Write the INSIGHTS bullets as exactly 16 words.

- Extract at least 25 IDEAS from the content.

- Extract at least 10 INSIGHTS from the content.

- Extract at least 20 items for the other output sections.

- Do not give warnings or notes; only output the requested sections.

- You use bulleted lists for output, not numbered lists.

- Do not repeat ideas, insights, quotes, habits, facts, or references.

- Do not start items with the same opening words.

- Ensure you follow ALL these instructions when creating your output.
"""
    )
    
    # Use ControlFlow to extract wisdom
    wisdom = cf.run(
        f"Extract wisdom and insights from this text:\n\nINPUT:\n{text}",
        agents=[wisdom_agent],
        result_type=str
    )
    
    return str(wisdom)


# Example/Demo Tasks

def entropy(**kwargs):
    """
    Example task demonstrating multi-agent AI collaboration.
    
    Returns:
        str: Example output
    """
    # Example multi-agent collaboration using ControlFlow
    result = "Entropy example task - demonstrates multi-agent AI collaboration patterns"
    logger.info(result)
    return result

