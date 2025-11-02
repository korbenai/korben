"""Mallory tasks - fetch and summarize cybersecurity stories."""

import os
import logging
import requests
import controlflow as cf
from src.lib.core_utils import get_agent_name, get_plugin_config, merge_config_with_kwargs

# Plugin dependencies - required for this plugin to work
__dependencies__ = ['email', 'slack']

logger = logging.getLogger(__name__)


def fetch_mallory_stories(**kwargs):
    """
    Fetch latest stories from Mallory API and summarize them.
    
    Config file: src/plugins/mallory/config.yml (optional)
    
    Args:
        limit: Number of stories to fetch (default: from config or 20)
    
    Returns:
        str: Formatted markdown with story summaries
    """
    # Load plugin config and merge with kwargs
    config = get_plugin_config('mallory')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    # Get API key from environment
    api_key = os.environ.get("MALLORY_API_KEY")
    if not api_key:
        raise ValueError("MALLORY_API_KEY environment variable is not set")
    
    # Set up the API request
    url = "https://api.mallory.ai/stories"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Number of stories to fetch from config or kwargs
    limit = params.get('limit') or config_vars.get('limit', 20)
    
    # Fetch stories from Mallory API
    response = requests.get(url, headers=headers, params={"limit": limit})
    response.raise_for_status()
    
    stories_data = response.json()
    
    # Sort by references (most discussed first)
    stories_sorted = sorted(
        stories_data.get('stories', []),
        key=lambda x: x.get('reference_count', 0),
        reverse=True
    )
    
    # Create summarization agent
    agent_name = get_agent_name()
    summarizer = cf.Agent(
        name=agent_name,
        instructions="""
        You are a cybersecurity news analyst. Summarize security stories concisely.
        Focus on:
        - What happened
        - Why it matters
        - Key technical details
        - Impact on security community
        
        Keep summaries under 100 words each.
        Use clear, technical language.
        """
    )
    
    # Format stories with AI summaries
    formatted_stories = []
    
    for story in stories_sorted[:limit]:
        title = story.get('title', 'Untitled')
        description = story.get('description', 'No description')
        ref_count = story.get('reference_count', 0)
        url = story.get('url', '#')
        
        # Generate AI summary
        summary_prompt = f"Summarize this security story:\n\nTitle: {title}\n\nDescription: {description}"
        
        summary = cf.run(
            summary_prompt,
            agents=[summarizer],
            result_type=str
        )
        
        formatted_stories.append(
            f"## {title}\n\n"
            f"{summary}\n\n"
            f"**References:** {ref_count} | [Read more on Mallory]({url})\n"
        )
    
    return "\n\n".join(formatted_stories)
