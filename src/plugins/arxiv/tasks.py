"""arXiv plugin tasks - search for academic papers."""

import logging
import json
from src.plugins.arxiv.lib import search_papers as search_papers_lib
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs

logger = logging.getLogger(__name__)


def arxiv_search(**kwargs):
    """
    Search for academic papers using the arXiv API.
    
    Config file: src/plugins/arxiv/config.yml (optional)
    
    Args:
        query: Search query string (required)
               Examples: 'all:electron', 'ti:transformer', 'au:smith'
        max_results: Maximum number of results (default: 10)
        start: Starting index for pagination (default: 0)
        sort_by: Sort by 'relevance', 'lastUpdatedDate', or 'submittedDate' (default: 'relevance')
        sort_order: 'ascending' or 'descending' (default: 'descending')
    
    Returns:
        str: JSON string containing search results or error message
    """
    # Load plugin config and merge with kwargs
    config = get_plugin_config('arxiv')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    query = params.get('query')
    max_results = params.get('max_results') or config_vars.get('max_results', 10)
    start = params.get('start') or config_vars.get('start', 0)
    sort_by = params.get('sort_by') or config_vars.get('sort_by', 'relevance')
    sort_order = params.get('sort_order') or config_vars.get('sort_order', 'descending')
    
    if not query:
        return "ERROR: No query specified. Provide --query with your search terms."
    
    try:
        result = search_papers_lib(
            query=query,
            max_results=max_results,
            start=start,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Format the result as a pretty JSON string
        formatted_result = json.dumps(result, indent=2)
        logger.info(f"Paper search completed successfully for query: {query}")
        return formatted_result
        
    except RuntimeError as e:
        error = f"ERROR: {str(e)}"
        logger.error(error)
        return error
    except Exception as e:
        error = f"ERROR: Unexpected error searching papers: {str(e)}"
        logger.error(error)
        return error



