"""arXiv flows - search papers and distribute results."""

import json
import logging
import controlflow as cf
from src.plugins.arxiv import tasks as arxiv_tasks
from src.plugins.email import tasks as email_tasks
from src.plugins.slack import tasks as slack_tasks
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs

# Plugin dependencies
__dependencies__ = ['email', 'slack']

logger = logging.getLogger(__name__)


def _format_papers_email(papers: list, query: str) -> str:
    """
    Format papers into HTML email content.
    
    Args:
        papers: List of paper dictionaries
        query: Search query for the email subject
        
    Returns:
        HTML formatted email content
    """
    html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .paper { margin-bottom: 30px; padding: 20px; border-left: 4px solid #b31b1b; background: #f8f9fa; }
            .paper-title { font-size: 20px; font-weight: bold; margin-bottom: 8px; color: #2c3e50; }
            .paper-authors { font-size: 14px; color: #7f8c8d; margin-bottom: 8px; font-style: italic; }
            .paper-meta { color: #95a5a6; font-size: 13px; margin-bottom: 10px; }
            .paper-abstract { margin-top: 10px; line-height: 1.8; }
            .paper-links { margin-top: 10px; }
            .paper-link { display: inline-block; margin-right: 10px; padding: 8px 12px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; }
            .paper-link:hover { background: #2980b9; }
            .pdf-link { background: #e74c3c; }
            .pdf-link:hover { background: #c0392b; }
            h1 { color: #2c3e50; }
            .category { display: inline-block; padding: 3px 8px; background: #ecf0f1; color: #7f8c8d; border-radius: 3px; margin-right: 5px; font-size: 12px; }
            .primary-category { background: #b31b1b; color: white; }
        </style>
    </head>
    <body>
        <h1>📄 arXiv Papers</h1>
        <p>Papers found for query: <strong>{query}</strong></p>
    """
    
    for paper in papers:
        title = paper.get('title', 'N/A')
        authors = paper.get('authors', [])
        author_str = ', '.join(authors) if authors else 'Unknown Authors'
        
        published_date = paper.get('published', 'N/A')
        abstract = paper.get('abstract', 'No abstract available.')
        paper_url = paper.get('html_url', paper.get('url', '#'))
        pdf_url = paper.get('pdf_url', '')
        primary_category = paper.get('primary_category', '')
        categories = paper.get('categories', [])
        
        # Handle abstract length
        if len(abstract) > 600:
            abstract = abstract[:600] + '...'
        
        html += f"""
        <div class="paper">
            <div class="paper-title">{title}</div>
            <div class="paper-authors">{author_str}</div>
            <div class="paper-meta">
                Published: {published_date}
        """
        
        if primary_category:
            html += f'<br/><span class="category primary-category">{primary_category}</span>'
        
        for cat in categories[:5]:  # Limit to first 5 categories
            if cat != primary_category:
                html += f'<span class="category">{cat}</span>'
        
        html += """
            </div>
            <div class="paper-abstract">{abstract}</div>
            <div class="paper-links">
        """.format(abstract=abstract)
        
        if paper_url != '#':
            html += f'<a href="{paper_url}" class="paper-link" target="_blank">View Paper →</a>'
        
        if pdf_url:
            html += f'<a href="{pdf_url}" class="paper-link pdf-link" target="_blank">Download PDF →</a>'
        
        html += """
            </div>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    return html


def _format_papers_slack(papers: list, query: str) -> str:
    """
    Format papers into Slack message content.
    
    Args:
        papers: List of paper dictionaries
        query: Search query
        
    Returns:
        Formatted Slack message
    """
    message = f"*📄 arXiv Papers for: {query}*\n\n"
    
    for i, paper in enumerate(papers, 1):
        title = paper.get('title', 'N/A')
        authors = paper.get('authors', [])
        author_str = ', '.join(authors[:3]) if authors else 'Unknown Authors'
        if len(authors) > 3:
            author_str += f' _et al._'
        
        published_date = paper.get('published', 'N/A')[:10]  # Just the date part
        paper_url = paper.get('html_url', paper.get('url', '#'))
        pdf_url = paper.get('pdf_url', '')
        primary_category = paper.get('primary_category', '')
        
        message += f"*{i}. {title}*\n"
        message += f"_{author_str}_\n"
        message += f"Published: {published_date}"
        
        if primary_category:
            message += f" | Category: `{primary_category}`"
        
        message += "\n"
        
        if paper_url != '#':
            message += f"<{paper_url}|View Paper>"
        if pdf_url:
            message += f" | <{pdf_url}|PDF>"
        
        message += "\n\n"
    
    return message


@cf.flow
def arxiv_search_workflow(**kwargs):
    """
    Search for papers on arXiv and send results via email and Slack.
    
    Config file: src/plugins/arxiv/config.yml (optional)
    
    Args:
        query: Search query (required)
               Examples: 'all:electron', 'ti:transformer', 'au:smith'
        max_results: Maximum number of results (default: from config or 10)
        start: Starting index for pagination (default: 0)
        sort_by: Sort by 'relevance', 'lastUpdatedDate', or 'submittedDate' (default: 'relevance')
        sort_order: 'ascending' or 'descending' (default: 'descending')
        recipient: Email recipient (optional - falls back to email plugin config)
        hook_name: Slack webhook name (optional - falls back to slack plugin config)
    
    Returns:
        Status message
    """
    # Load plugin config and merge with kwargs
    config = get_plugin_config('arxiv')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    # Extract parameters
    query = params.get('query')
    max_results = params.get('max_results') or config_vars.get('max_results', 10)
    start = params.get('start') or config_vars.get('start', 0)
    sort_by = params.get('sort_by') or config_vars.get('sort_by', 'relevance')
    sort_order = params.get('sort_order') or config_vars.get('sort_order', 'descending')
    recipient = params.get('recipient') or config_vars.get('recipient')
    hook_name = params.get('hook_name') or config_vars.get('hook_name')
    
    if not query:
        error_msg = "ERROR: No query specified. Provide --query with your search terms."
        logger.error(error_msg)
        return error_msg
    
    logger.info(f"Step 1: Searching arXiv for papers: {query}")
    
    try:
        # Step 1: Search for papers
        search_params = {
            'query': query,
            'max_results': max_results,
            'start': start,
            'sort_by': sort_by,
            'sort_order': sort_order
        }
        
        search_result = arxiv_tasks.arxiv_search(**search_params)
        
        # Check for errors
        if search_result.startswith('ERROR:'):
            logger.error(search_result)
            return search_result
        
        search_data = json.loads(search_result)
        papers = search_data.get('papers', [])
        
        if not papers:
            result = f"No papers found for query: {query}"
            logger.info(result)
            return result
        
        logger.info(f"Found {len(papers)} papers")
        
        # Step 2: Format and send email
        logger.info("Step 2: Formatting and sending email...")
        
        email_content = _format_papers_email(papers, query)
        email_subject = f"📄 arXiv Papers: {query}"
        
        email_kwargs = {
            'subject': email_subject,
            'content': email_content
        }
        if recipient:
            email_kwargs['recipient'] = recipient
        
        email_result = email_tasks.send_email(**email_kwargs)
        logger.info(f"Email sent: {email_result}")
        
        # Step 3: Format and send Slack message
        logger.info("Step 3: Formatting and sending Slack message...")
        
        slack_message = _format_papers_slack(papers, query)
        
        slack_kwargs = {
            'message': slack_message
        }
        if hook_name:
            slack_kwargs['hook_name'] = hook_name
        
        slack_result = slack_tasks.send_slack_hook(**slack_kwargs)
        logger.info(f"Slack message sent: {slack_result}")
        
        # Success summary
        result = f"✓ Found {len(papers)} papers for '{query}'\n{email_result}\n{slack_result}"
        logger.info(f"Workflow completed successfully")
        return result
        
    except json.JSONDecodeError as e:
        error_msg = f"ERROR: Failed to parse search results: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"ERROR: Workflow failed: {str(e)}"
        logger.error(error_msg)
        return error_msg



