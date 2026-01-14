"""Mallory tasks - fetch and summarize cybersecurity stories."""

import os
import logging
import requests
from src.lib.core_utils import get_agent_name, get_plugin_config, merge_config_with_kwargs

# Plugin dependencies - required for this plugin to work
__dependencies__ = ['email', 'slack']

logger = logging.getLogger(__name__)

# System prompt for story summarization
SUMMARIZER_SYSTEM_PROMPT = """You are a cybersecurity news analyst. Summarize security stories concisely.
Focus on:
- What happened
- Why it matters
- Key technical details
- Impact on security community

Keep summaries under 100 words each.
Use clear, technical language."""


def fetch_mallory_stories(**kwargs):
    """
    Fetch latest stories from Mallory API and summarize them.
    
    Config file: src/plugins/mallory/config.yml (optional)
    
    Args:
        limit: Number of stories to fetch (default: from config or 20)
    
    Returns:
        str: Formatted markdown with story summaries
    """
    from src.agents.base import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage
    
    # Load plugin config and merge with kwargs
    config = get_plugin_config('mallory')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    # Get API key from environment
    api_key = os.environ.get("MALLORY_API_KEY")
    if not api_key:
        raise ValueError("MALLORY_API_KEY environment variable is not set")
    
    # Set up the API request
    from datetime import datetime, timedelta, timezone
    updated_after = (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
    created_after = updated_after
    url = "https://api.mallory.ai/v1/stories"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    
    # Number of stories to fetch from config or kwargs
    limit = params.get('limit') or config_vars.get('limit', 20)
    
    # Fetch stories from Mallory API (last 24h, sort by reference_count)
    query_params = {
        "updated_after": updated_after,
        "sort": "reference_count",
        "limit": limit,
    }
    
    response = requests.get(url, headers=headers, params=query_params)
    response.raise_for_status()
    
    try:
        stories_data = response.json()
    except Exception:
        stories_data = {}
    
    # Normalize stories list from API payload
    stories_list = []
    if isinstance(stories_data, dict):
        if isinstance(stories_data.get('stories'), list):
            stories_list = stories_data.get('stories', [])
        elif isinstance(stories_data.get('data'), list):
            stories_list = stories_data.get('data', [])
    

    # Fallback: if no stories with updated_after, try created_after when debug is enabled
    if len(stories_list) == 0:
        fallback_params = {
            "created_after": created_after,
            "sort": "reference_count",
            "limit": limit,
        }
        response2 = requests.get(url, headers=headers, params=fallback_params)
        try:
            response2.raise_for_status()
            try:
                stories_data = response2.json()
            except Exception:
                stories_data = {}
            # Normalize fallback payload
            stories_list = []
            if isinstance(stories_data, dict):
                if isinstance(stories_data.get('stories'), list):
                    stories_list = stories_data.get('stories', [])
                elif isinstance(stories_data.get('data'), list):
                    stories_list = stories_data.get('data', [])
        except Exception as _:
            # keep original stories_data if fallback fails
            pass
    
    # Sort by references (most discussed first)
    stories_sorted = sorted(
        stories_list,
        key=lambda x: x.get('reference_count', 0),
        reverse=True
    )
    
    # Get LLM for summarization
    llm = get_llm(temperature=0.3)
    
    # Format stories with AI summaries
    formatted_stories = []
    
    for story in stories_sorted[:limit]:
        title = story.get('title', 'Untitled')
        description = story.get('description', 'No description')
        ref_count = story.get('reference_count', 0)
        references = story.get('references', []) or []
        url = story.get('url') or (references[0].get('url') if references and isinstance(references[0], dict) else '#')
        
        # Generate AI summary using LangChain
        summary_prompt = f"Summarize this security story:\n\nTitle: {title}\n\nDescription: {description}"
        
        try:
            messages = [
                SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT),
                HumanMessage(content=summary_prompt),
            ]
            response = llm.invoke(messages)
            summary = response.content
        except Exception as e:
            logger.error(f"Failed to summarize story '{title}': {e}")
            summary = description[:200] + "..." if len(description) > 200 else description
        
        formatted_stories.append(
            f"## {title}\n\n"
            f"{summary}\n\n"
            f"**References:** {ref_count} | [Read more on Mallory]({url})\n"
        )
    
    # If no stories, return a helpful message
    if not formatted_stories:
        return "No stories found in the last 24 hours."
    
    return "\n\n".join(formatted_stories)
