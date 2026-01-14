"""Obsidian plugin flows - complete workflows for daily summaries."""

import os
import logging
from typing import Optional

from src.plugins.obsidian import tasks as obsidian_tasks
from src.plugins.obsidian.lib import deduce_target_date, get_wiki_path
from src.plugins.utilities import tasks as utility_tasks
from src.plugins.email import tasks as email_tasks
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs

logger = logging.getLogger(__name__)

# Plugin dependencies
__dependencies__ = ['email', 'utilities']


def daily_summary_workflow(
    date: Optional[str] = None,
    recipient: Optional[str] = None,
    send_email: bool = True,
) -> str:
    """
    Complete daily summary workflow: generate summary and optionally email it.
    
    This flow:
    1. Generates a daily summary using Claude SDK
    2. Converts markdown to HTML
    3. Sends via email (optional)
    
    Args:
        date: Optional date in YYYY-MM-DD format (auto-deduced if not provided)
        recipient: Email recipient (falls back to config/env if not set)
        send_email: Whether to send email (default True)
    
    Returns:
        str: Result message
    """
    logger.info("=" * 70)
    logger.info("DAILY SUMMARY WORKFLOW")
    logger.info("=" * 70)
    
    # Load config
    config = get_plugin_config('obsidian')
    config_vars = config.get('variables', {})
    
    # Deduce date
    target_date = deduce_target_date(date)
    logger.info(f"Target date: {target_date}")
    
    results = []
    
    # Step 1: Generate daily summary
    logger.info("Step 1: Generating daily summary...")
    summary_markdown = obsidian_tasks.generate_daily_summary(date=target_date)
    
    if summary_markdown.startswith("ERROR:"):
        logger.error(f"Failed to generate summary: {summary_markdown}")
        return summary_markdown
    
    results.append(f"Generated summary for {target_date}")
    logger.info("Summary generated successfully")
    
    # Step 2: Send email if requested
    if send_email:
        logger.info("Step 2: Sending email...")
        
        # Convert to HTML
        summary_html = utility_tasks.markdown_to_html(text=summary_markdown)
        
        # Get recipient
        email_recipient = recipient or config_vars.get('recipient')
        
        # Build subject
        subject = f"📊 Daily Summary - {target_date}"
        
        # Send email
        email_kwargs = {
            'subject': subject,
            'content': summary_html,
        }
        if email_recipient:
            email_kwargs['recipient'] = email_recipient
        
        email_result = email_tasks.send_email(**email_kwargs)
        results.append(email_result)
        logger.info(f"Email sent: {email_result}")
    else:
        logger.info("Step 2: Skipping email (send_email=False)")
        results.append("Email skipped")
    
    # Log summary preview
    logger.info("")
    logger.info("=" * 70)
    logger.info("SUMMARY PREVIEW")
    logger.info("=" * 70)
    # Show first 500 chars of summary
    preview = summary_markdown[:500]
    if len(summary_markdown) > 500:
        preview += "\n... (truncated)"
    logger.info(preview)
    logger.info("=" * 70)
    
    result = "\n".join(results)
    logger.info(f"Workflow complete: {result}")
    return result


def cleanup_daily_note_workflow(
    date: Optional[str] = None,
    save: bool = False,
) -> str:
    """
    Clean up and organize a daily note.
    
    This flow:
    1. Reads the daily note for the specified date
    2. Uses Claude to clean up and organize
    3. Optionally saves the cleaned version
    
    Args:
        date: Optional date in YYYY-MM-DD format (auto-deduced if not provided)
        save: Whether to save the cleaned note back to file (default False)
    
    Returns:
        str: Cleaned daily note content
    """
    logger.info("=" * 70)
    logger.info("DAILY NOTE CLEANUP WORKFLOW")
    logger.info("=" * 70)
    
    # Deduce date
    target_date = deduce_target_date(date)
    logger.info(f"Target date: {target_date}")
    
    # Clean up the note
    cleaned = obsidian_tasks.cleanup_daily_note(date=target_date)
    
    if cleaned.startswith("ERROR:"):
        logger.error(f"Failed to cleanup: {cleaned}")
        return cleaned
    
    # Save if requested
    if save:
        from src.plugins.obsidian.lib import get_daily_notes_path
        note_path = get_daily_notes_path() / f"{target_date}.md"
        
        try:
            note_path.write_text(cleaned, encoding='utf-8')
            logger.info(f"Saved cleaned note to: {note_path}")
        except Exception as e:
            logger.error(f"Failed to save: {e}")
            return f"ERROR: Failed to save cleaned note: {e}"
    
    return cleaned
