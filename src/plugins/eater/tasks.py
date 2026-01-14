"""Eater tasks - use search to find sources, then (later) process them."""

import logging
from typing import Any, Dict
from datetime import datetime
from src.lib.core_utils import get_plugin_config

# Declare that this plugin depends on the web_search, email, and utilities plugins
__dependencies__ = ['web_search', 'email', 'utilities']

logger = logging.getLogger(__name__)


def search_new_restaurants(**kwargs):
    """
    Use an AI agent with Tavily to find the best new restaurants in a given city and month.
    Returns Markdown with a concise list and sources.
    """
    from src.agents.base import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage
    
    # Load optional config and prompt template
    eater_config = get_plugin_config('eater') or {}
    variables = eater_config.get('variables', {}) if isinstance(eater_config, dict) else {}

    city = variables.get('city', 'Austin')
    state = variables.get('state', 'Texas')

    month_year = kwargs.get('month_year', datetime.now().strftime("%B %Y"))
    top_picks_count = kwargs.get('top_picks_count', 5)  # Number of restaurants for top picks
    search_depth = kwargs.get('search_depth', 'advanced')
    
    # Use more search results to get better coverage
    search_max_results = kwargs.get('search_max_results', 10)  # Get many sources

    core_prompt = variables.get('core_prompt') or f"""
You are a local restaurant scout for {city}, {state}.
Your goal is to find the BEST NEW restaurants in {city} for {{month_year}}.

Requirements:
- "New" means opened, announced, or updated recently; prioritize openings in the last 3–6 months, or upcoming months.
- Prefer credible sources (Eater local, respected local food blogs/mags, Google Maps recency, etc.).
- Focus on spots that are open to the public (not private clubs).
""".strip()

    additional_focus_areas = variables.get('additional_focus_areas') or []
    
    output_guidelines = f"""
Output Format (Markdown):

1. SUMMARY (1-2 sentences about the scene this month)

2. TOP PICKS (exactly {top_picks_count} restaurants)
   Format: - Name — Neighborhood — Description — Address — [Google Maps](link) — Source — Website — Cuisine

3. ALL RESTAURANTS (ALL remaining restaurants found, alphabetically, not in top picks)
   Format: - Name — Neighborhood — Description — Address — [Google Maps](link) — Source — Website — Cuisine
   IMPORTANT: Extract and list EVERY restaurant mentioned in the search results. Be thorough and comprehensive.

4. SOURCES (just the domain URLs you used)

Be exhaustive in the ALL RESTAURANTS section - include every restaurant you found in the search results.
""".strip()

    # Render the final instructions
    focus_md = ""
    if additional_focus_areas:
        focus_md = "\nAdditional focus areas:\n" + "\n".join([f"- {item}" for item in additional_focus_areas])
    
    system_prompt = (
        core_prompt.format(month_year=month_year)
        + "\n\n"
        + focus_md
        + "\n\n"
        + output_guidelines.format(top_picks_count=top_picks_count)
    )

    # First, perform the search using Tavily
    logger.info(f"Eater: searching for restaurants in {city} for {month_year}")
    
    from src.plugins.web_search.tasks import tavily_search_raw
    
    search_query = f"best new restaurants {city} {state} {month_year} opened recently"
    search_results = tavily_search_raw(
        query=search_query,
        max_results=search_max_results,
        search_depth=search_depth,
        include_answer=True,
        include_raw_content=True,
    )
    
    # Format search results for Claude
    search_context = f"""
Search Results for "{search_query}":

Answer Summary: {search_results.get('answer', 'No summary available')}

Sources found:
"""
    
    for result in search_results.get('results', []):
        search_context += f"""
---
Title: {result.get('title', 'N/A')}
URL: {result.get('url', 'N/A')}
Content: {result.get('content', 'N/A')[:2000]}
"""
    
    # Now use Claude to analyze and format the results
    prompt = f"""Based on the following search results, find and format information about the best new restaurants in {city} for {month_year}.

{search_context}

Format the results according to the output guidelines in your instructions. Be thorough and extract ALL restaurants mentioned."""

    try:
        llm = get_llm(temperature=0.5)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"Failed to process restaurant search: {e}")
        return f"ERROR: Failed to process restaurant search: {e}"
