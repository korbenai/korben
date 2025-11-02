"""Mallory flows - fetch and email cybersecurity stories."""

import os
import logging
import controlflow as cf
from src.core.plugins.mallory import tasks as mallory_tasks
from src.core.plugins.utilities import tasks as utility_tasks
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs

logger = logging.getLogger(__name__)


@cf.flow
def mallory_stories_workflow(**kwargs):
    """
    ControlFlow flow for fetching Mallory security stories and emailing them.
    
    Config file: config/mallory.yml (optional)
    
    Runs tasks in sequence:
    1. Fetch stories from Mallory API
    2. Convert markdown to HTML
    3. Send email with story summaries
    4. Send stories to Slack (optional)
    
    Args:
        limit: Number of stories (default: from config or 20)
        recipient: Email recipient (default: from config or PERSONAL_EMAIL env var)
        subject: Email subject (default: from config or "Security Stories from Mallory")
        slack_hook: Slack hook name (optional)
    
    Returns:
        str: Status message
    """
    # Load plugin config and merge with kwargs (kwargs take precedence)
    config = get_plugin_config('mallory')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    # Extract parameters
    limit = params.get('limit') or config_vars.get('limit', 20)
    recipient = params.get('recipient') or config_vars.get('recipient') or os.getenv('PERSONAL_EMAIL')
    subject = params.get('subject') or config_vars.get('subject', "Security Stories from Mallory")
    slack_hook = params.get('slack_hook') or config_vars.get('slack_hook')
    
    results = []
    
    # Step 1: Fetch stories from Mallory
    logger.info("Step 1: Fetching stories from Mallory API...")
    try:
        fetch_params = {'limit': limit}
        stories = mallory_tasks.fetch_mallory_stories(**fetch_params)
        results.append("Successfully fetched and summarized stories from Mallory")
        logger.info(f"Fetched stories: {stories}")
    except Exception as e:
        error_msg = f"Failed to fetch stories from Mallory: {e}"
        logger.error(error_msg)
        results.append(error_msg)
        return "\n".join(results)
    
    # Step 2: Convert markdown to HTML
    logger.info("Step 2: Converting stories to HTML...")
    try:
        # Format stories as markdown with header
        markdown_content = f"# Latest Security Stories\n\n{stories}"
        stories_html = utility_tasks.markdown_to_html(text=markdown_content)
        results.append("Successfully converted stories to HTML")
        logger.info("Stories converted to HTML")
    except Exception as e:
        error_msg = f"Failed to convert markdown to HTML: {e}"
        logger.error(error_msg)
        results.append(error_msg)
        return "\n".join(results)
    
    # Step 3: Send email with stories
    logger.info("Step 3: Sending email with stories...")
    
    if not recipient:
        error_msg = "ERROR: No recipient specified. Provide --recipient or set PERSONAL_EMAIL environment variable."
        logger.error(error_msg)
        results.append(error_msg)
        return "\n".join(results)
    
    try:
        email_result = utility_tasks.send_email(
            recipient=recipient,
            subject=subject,
            content=stories_html
        )
        results.append(email_result)
        logger.info(f"Email sent successfully: {email_result}")
    except Exception as e:
        error_msg = f"Failed to send email: {e}"
        logger.error(error_msg)
        results.append(error_msg)
    
    # Step 4: Send stories to Slack
    logger.info("Step 4: Sending stories to Slack...")
    
    hook_name = kwargs.get('slack_hook', 'default')
    
    try:
        slack_message = f"*Latest Security Stories*\n\n{stories}"
        slack_result = utility_tasks.send_slack_hook(
            hook_name=hook_name,
            message=slack_message
        )
        results.append(slack_result)
        logger.info(f"Slack message sent successfully: {slack_result}")
    except Exception as e:
        error_msg = f"Failed to send Slack message: {e}"
        logger.error(error_msg)
        results.append(error_msg)
    
    return "\n".join(results)

