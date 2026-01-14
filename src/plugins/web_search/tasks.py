"""Web search tasks - Tavily-backed web search and tools."""

import logging
from typing import Any, Dict, List

from src.lib.core_utils import (
    get_plugin_config,
    merge_config_with_kwargs,
    get_value_from_config_or_env,
)

logger = logging.getLogger(__name__)

# This plugin has no intra-plugin dependency requirements
__dependencies__ = []


def _tavily_client():
    """Lazy import and client factory to avoid hard dependency at import time."""
    try:
        from tavily import TavilyClient  # type: ignore
    except Exception as e:
        raise RuntimeError(f"tavily-python not installed or failed to import: {e}")
    # Resolve API key with config-over-env precedence
    config = get_plugin_config('web_search')
    api_key = get_value_from_config_or_env(
        config=config,
        config_keys=["variables", "api_key"],
        env_var="TAVILY_API_KEY",
        prefer_config=True,
    )
    if not api_key:
        raise RuntimeError(
            "Tavily API key not found. Configure src/plugins/web_search/config.yml "
            "(variables.api_key) or set env var TAVILY_API_KEY."
        )
    return TavilyClient(api_key=api_key)


def format_results_markdown(results: Dict[str, Any]) -> str:
    """Format Tavily results into readable Markdown."""
    lines: List[str] = []
    answer = results.get("answer")
    if answer:
        lines.append("## Answer")
        lines.append("")
        lines.append(str(answer).strip())
        lines.append("")
    items = results.get("results") or []
    if items:
        lines.append("## Sources")
        lines.append("")
        for it in items:
            title = (it.get("title") or "Untitled").strip()
            url = it.get("url") or ""
            snippet = (it.get("content") or "").strip()
            if len(snippet) > 300:
                snippet = snippet[:300].rstrip() + "..."
            # Markdown bullet with nested snippet
            lines.append(f"- [{title}]({url})")
            if snippet:
                lines.append(f"  - {snippet}")
        lines.append("")
    if not lines:
        return "No results."
    return "\n".join(lines)


def tavily_search_raw(**kwargs) -> Dict[str, Any]:
    """
    Execute a Tavily search and return the raw result JSON.

    Args (kwargs):
        query (str): Required search query
        max_results (int): Number of results (default 5 or config default)
        search_depth (str): 'basic' or 'advanced' (default 'basic' or config default)
        include_answer (bool): Include synthesized answer (default true)
        include_raw_content (bool): Include raw content (default false)
    """
    config = get_plugin_config('web_search')
    variables = config.get('variables', {}) if isinstance(config, dict) else {}
    params = merge_config_with_kwargs(variables, kwargs)
    query = params.get('query')
    if not query:
        raise ValueError("No query provided. Use --query 'your search terms'.")
    max_results = int(params.get('max_results', 5))
    search_depth = params.get('search_depth', 'basic')
    include_answer = bool(params.get('include_answer', True))
    include_raw_content = bool(params.get('include_raw_content', False))
    client = _tavily_client()
    return client.search(
        query=query,
        search_depth=search_depth,
        max_results=max_results,
        include_answer=include_answer,
        include_raw_content=include_raw_content,
    )




def web_search(**kwargs):
    """
    Search the web using Tavily and return a Markdown summary.

    Args:
        query (str): Search query (required)
        max_results (int): Max number of results (default: 5)
        search_depth (str): 'basic' or 'advanced' (default: 'basic')
        include_answer (bool): Include synthesized answer (default: True)
        include_raw_content (bool): Include raw page content in results (default: False)

    Returns:
        str: Markdown with optional answer and a list of sources
    """
    # Load plugin config and merge with kwargs (kwargs take precedence)
    config = get_plugin_config('web_search')
    variables = config.get('variables', {}) if isinstance(config, dict) else {}
    params = merge_config_with_kwargs(variables, kwargs)

    query = params.get('query')
    if not query:
        return "ERROR: No query provided. Use --query 'your search terms'."

    try:
        max_results = int(params.get('max_results', 5))
        search_depth = params.get('search_depth', 'basic')
        include_answer = params.get('include_answer', True)
        include_raw_content = params.get('include_raw_content', False)

        logger.info(f"Searching Tavily: '{query}' (max_results={max_results}, depth={search_depth})")
        result = tavily_search_raw(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
        )
        return format_results_markdown(result)
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return f"ERROR: Tavily search failed: {e}"


