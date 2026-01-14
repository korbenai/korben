"""Obsidian plugin tasks - generate daily summaries and interact with wiki."""

import logging
from typing import Optional

from src.plugins.obsidian.agents import ObsidianDailySummaryAgent
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs
from src.plugins.obsidian.lib import (
    get_wiki_path,
    get_daily_summary_context,
    deduce_target_date,
)

logger = logging.getLogger(__name__)


def generate_daily_summary(**kwargs) -> str:
    """
    Generate a daily summary from wiki notes and backlog.
    
    Uses the centralized DailySummaryAgent to analyze the daily note
    and backlog, producing a summary of accomplished work and suggested
    priorities for tomorrow.
    
    Args:
        date: Optional date in YYYY-MM-DD format (auto-deduced if not provided)
    
    Returns:
        str: Markdown-formatted daily summary
    """
    # Load config and merge with kwargs
    config = get_plugin_config('obsidian')
    params = merge_config_with_kwargs(config, kwargs)
    
    # Get target date
    specified_date = params.get('date')
    
    logger.info("=" * 70)
    logger.info("DAILY SUMMARY GENERATION")
    logger.info("=" * 70)
    
    # Gather context
    context = get_daily_summary_context(specified_date)
    target_date = context['date']
    
    logger.info(f"Target date: {target_date}")
    logger.info(f"Completed tasks: {len(context['completed_tasks'])}")
    logger.info(f"Planned tasks: {len(context['planned_tasks'])}")
    logger.info(f"Backlog items: {len(context['backlog_items'])}")
    
    # Check if we have content to analyze
    if not context['daily_note'] and not context['backlog']:
        return f"ERROR: No daily note found for {target_date} and no backlog available."
    
    # Run the agent
    try:
        agent = ObsidianDailySummaryAgent()
        summary = agent.run(
            date=target_date,
            daily_note_content=context['daily_note'] or "No daily note found for this date.",
            backlog_content=context['backlog'] or "Backlog is empty.",
        )
        
        logger.info("Daily summary generated successfully")
        logger.info("=" * 70)
        
        return summary
        
    except Exception as e:
        error_msg = f"Failed to generate daily summary: {e}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


def cleanup_daily_note(**kwargs) -> str:
    """
    Clean up and organize a daily note.
    
    Uses LangChain to consolidate tasks, remove duplicates,
    add context from backlog, and improve formatting.
    
    Args:
        date: Optional date in YYYY-MM-DD format (auto-deduced if not provided)
    
    Returns:
        str: Cleaned up daily note content
    """
    from src.agents.base import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage
    
    # Load config and merge with kwargs
    config = get_plugin_config('obsidian')
    params = merge_config_with_kwargs(config, kwargs)
    
    # Get target date
    specified_date = params.get('date')
    context = get_daily_summary_context(specified_date)
    target_date = context['date']
    
    logger.info("=" * 70)
    logger.info(f"DAILY NOTE CLEANUP - {target_date}")
    logger.info("=" * 70)
    
    if not context['daily_note']:
        return f"ERROR: No daily note found for {target_date}"
    
    cleanup_prompt = f"""Clean up and organize this daily note.

## Current Daily Note ({target_date})
{context['daily_note']}

## Backlog (for context)
{context['backlog'][:3000] if context['backlog'] else "No backlog available."}

---

Clean up the daily note by:
1. Removing excessive blank lines
2. Consolidating duplicate tasks
3. Grouping related tasks together
4. Adding context from backlog where relevant
5. Organizing into clear sections

Preserve:
- All completed tasks (- [x])
- Frontmatter metadata
- Dataview queries
- Meeting links

Output the cleaned daily note in markdown format."""

    system_prompt = "You are a productivity assistant helping organize daily notes. Keep the user's voice and don't over-formalize."

    try:
        llm = get_llm()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=cleanup_prompt),
        ]
        response = llm.invoke(messages)
        cleaned = response.content
        
        logger.info("Daily note cleaned successfully")
        return cleaned
        
    except Exception as e:
        error_msg = f"Failed to cleanup daily note: {e}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
