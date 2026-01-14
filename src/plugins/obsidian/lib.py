"""Obsidian plugin library - utilities for reading and parsing wiki files."""

import os
import re
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict

from src.lib.core_utils import get_plugin_config

logger = logging.getLogger(__name__)


def get_wiki_path() -> Path:
    """
    Get the configured wiki path.
    
    Returns:
        Path: Absolute path to the wiki directory
    
    Raises:
        ValueError: If wiki_path is not configured
    """
    config = get_plugin_config('obsidian')
    variables = config.get('variables', {})
    wiki_path = variables.get('wiki_path')
    
    if not wiki_path:
        raise ValueError(
            "Obsidian wiki_path not configured. "
            "Please set 'wiki_path' in src/plugins/obsidian/config.yml"
        )
    
    expanded_path = Path(os.path.expanduser(wiki_path))
    
    if not expanded_path.exists():
        logger.warning(f"Wiki path does not exist: {expanded_path}")
    
    return expanded_path


def get_daily_notes_path() -> Path:
    """
    Get the path to the daily notes directory.
    
    Returns:
        Path: Absolute path to daily notes directory
    """
    config = get_plugin_config('obsidian')
    variables = config.get('variables', {})
    subdir = variables.get('daily_notes_subdir', 'daily')
    return get_wiki_path() / subdir


def get_backlog_path() -> Path:
    """
    Get the path to the backlog file.
    
    Returns:
        Path: Absolute path to backlog file
    """
    config = get_plugin_config('obsidian')
    variables = config.get('variables', {})
    backlog_file = variables.get('backlog_file', '!backlog.md')
    return get_wiki_path() / backlog_file


def deduce_target_date(specified_date: Optional[str] = None) -> str:
    """
    Deduce the target date for daily summary.
    
    Logic:
    - If date is specified, use that
    - If it's after 5pm, use today (end of day summary)
    - If it's before 5pm, use yesterday (morning planning)
    
    Args:
        specified_date: Optional date string in YYYY-MM-DD format
    
    Returns:
        str: Target date in YYYY-MM-DD format
    """
    if specified_date:
        # Validate format
        try:
            datetime.strptime(specified_date, "%Y-%m-%d")
            return specified_date
        except ValueError:
            logger.warning(f"Invalid date format '{specified_date}', deducing automatically")
    
    now = datetime.now()
    current_hour = now.hour
    
    if current_hour >= 17:  # After 5pm
        target_date = now
        logger.info(f"After 5pm, using today's date: {target_date.strftime('%Y-%m-%d')}")
    else:  # Before 5pm
        target_date = now - timedelta(days=1)
        logger.info(f"Before 5pm, using yesterday's date: {target_date.strftime('%Y-%m-%d')}")
    
    return target_date.strftime("%Y-%m-%d")


def read_file_safe(path: Path) -> str:
    """
    Safely read a file, returning empty string if it doesn't exist.
    
    Args:
        path: Path to file
    
    Returns:
        str: File contents or empty string
    """
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"File not found: {path}")
        return ""
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return ""


def get_daily_note(date: str) -> str:
    """
    Get the daily note content for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format
    
    Returns:
        str: Daily note content
    """
    note_path = get_daily_notes_path() / f"{date}.md"
    content = read_file_safe(note_path)
    
    if content:
        logger.info(f"Read daily note for {date}: {len(content)} chars")
    else:
        logger.warning(f"No daily note found for {date}")
    
    return content


def get_backlog() -> str:
    """
    Get the backlog file content.
    
    Returns:
        str: Backlog content
    """
    content = read_file_safe(get_backlog_path())
    
    if content:
        logger.info(f"Read backlog: {len(content)} chars")
    else:
        logger.warning("No backlog file found")
    
    return content


def extract_completed_tasks(content: str) -> List[str]:
    """
    Extract completed tasks from content.
    
    Matches patterns like:
    - [x] Task description ✅ 2026-01-14
    
    Args:
        content: Markdown content to parse
    
    Returns:
        List[str]: List of completed task descriptions
    """
    completed = []
    # Match tasks with checkmark: - [x] task (optionally with ✅ date)
    pattern = r"- \[x\] (.+?)(?:\s*✅.*)?$"
    
    for line in content.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            task = match.group(1).strip()
            completed.append(task)
    
    logger.debug(f"Extracted {len(completed)} completed tasks")
    return completed


def extract_planned_tasks(content: str) -> List[str]:
    """
    Extract planned (incomplete) tasks from content.
    
    Matches patterns like:
    - [ ] Task description
    
    Args:
        content: Markdown content to parse
    
    Returns:
        List[str]: List of planned task descriptions
    """
    planned = []
    pattern = r"- \[ \] (.+)$"
    
    for line in content.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            task = match.group(1).strip()
            planned.append(task)
    
    logger.debug(f"Extracted {len(planned)} planned tasks")
    return planned


def extract_backlog_items(content: str, limit: int = 100) -> List[str]:
    """
    Extract backlog items, prioritizing items near the top.
    
    Items higher in the backlog are considered higher priority.
    
    Args:
        content: Backlog markdown content
        limit: Maximum number of items to extract
    
    Returns:
        List[str]: List of backlog items
    """
    items = []
    pattern = r"- \[ \] (.+)$"
    
    for line in content.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            item = match.group(1).strip()
            items.append(item)
            if len(items) >= limit:
                break
    
    logger.debug(f"Extracted {len(items)} backlog items (limit: {limit})")
    return items


def get_daily_summary_context(date: Optional[str] = None) -> Dict:
    """
    Gather all context needed for a daily summary.
    
    Args:
        date: Optional specific date (YYYY-MM-DD format)
    
    Returns:
        Dict with keys:
            - date: Target date string
            - daily_note: Full daily note content
            - backlog: Full backlog content
            - completed_tasks: List of completed tasks
            - planned_tasks: List of remaining planned tasks
            - backlog_items: List of backlog items (first 50)
    """
    target_date = deduce_target_date(date)
    daily_note = get_daily_note(target_date)
    backlog = get_backlog()
    
    return {
        'date': target_date,
        'daily_note': daily_note,
        'backlog': backlog,
        'completed_tasks': extract_completed_tasks(daily_note),
        'planned_tasks': extract_planned_tasks(daily_note),
        'backlog_items': extract_backlog_items(backlog, limit=50),
    }
