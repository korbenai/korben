"""Mallory Stories workflow - fetches security stories and emails them."""

import os
import logging
import controlflow as cf
from src.core.tasks import get_mallory_stories
from src.core.tasks import markdown_to_html
from src.core.tasks import send_email

logger = logging.getLogger(__name__)


@cf.flow
def mallory_stories_workflow(**kwargs):
    """
    ControlFlow flow for fetching Mallory security stories and emailing them.
    
    Runs tasks in sequence:
    1. Fetch stories from Mallory API
    2. Convert markdown to HTML
    3. Send email with story summaries
    
    Args:
        recipient: Optional recipient email (defaults to PERSONAL_EMAIL env var)
        subject: Optional email subject (defaults to "Security Stories from Mallory")
    
    Returns:
        str: Status message
    """
    results = []
    
    # Step 1: Fetch stories from Mallory
    logger.info("Step 1: Fetching stories from Mallory API...")
    try:
        stories = get_mallory_stories.run(**kwargs)
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
        stories_html = markdown_to_html.run(text=markdown_content)
        results.append("Successfully converted stories to HTML")
        logger.info("Stories converted to HTML")
    except Exception as e:
        error_msg = f"Failed to convert markdown to HTML: {e}"
        logger.error(error_msg)
        results.append(error_msg)
        return "\n".join(results)
    
    # Step 3: Send email with stories
    logger.info("Step 3: Sending email with stories...")
    
    recipient = kwargs.get('recipient') or os.getenv('PERSONAL_EMAIL')
    if not recipient:
        error_msg = "ERROR: No recipient specified. Provide --recipient or set PERSONAL_EMAIL environment variable."
        logger.error(error_msg)
        results.append(error_msg)
        return "\n".join(results)
    
    subject = kwargs.get('subject', "Security Stories from Mallory")
    
    try:
        email_result = send_email.run(
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
    
    return "\n".join(results)

