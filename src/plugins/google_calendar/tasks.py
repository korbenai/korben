"""Google Calendar plugin tasks - retrieve calendar events."""

import os
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Optional

from src.plugins.google_calendar.lib import GoogleCalendarService
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs

logger = logging.getLogger(__name__)


def get_calendar_events(**kwargs) -> str:
    """
    Get calendar events for one or more accounts for a specific date or date range.
    
    Config file: src/plugins/google_calendar/config.yml (optional)
    
    Args:
        accounts: Email address(es) to get calendar for (single email or comma-separated list)
                 If not provided, uses accounts from config file
        date: Date to get events for (YYYY-MM-DD, defaults to today)
        start_date: Start date for range query (YYYY-MM-DD)
        end_date: End date for range query (YYYY-MM-DD)
        days: Number of days from start_date/date (alternative to end_date)
        max_results: Maximum number of events to return per account (default: 100)
    
    Returns:
        JSON string containing calendar events for all accounts
        
    Examples:
        # Get today's events for accounts in config
        get_calendar_events()
        
        # Get events for a single account
        get_calendar_events(accounts="user@example.com")
        
        # Get events for multiple accounts
        get_calendar_events(accounts="user1@example.com,user2@example.com")
        
        # Get events for a specific date
        get_calendar_events(accounts="user@example.com", date="2025-11-05")
        
        # Get events for a date range
        get_calendar_events(accounts="user@example.com", start_date="2025-11-01", end_date="2025-11-07")
        
        # Get events for next 7 days
        get_calendar_events(days=7)
    """
    # Load plugin config and merge with kwargs
    config = get_plugin_config('google_calendar')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    # Get accounts - support both single string and comma-separated list
    accounts_param = params.get('accounts')
    if accounts_param:
        if isinstance(accounts_param, str):
            accounts = [a.strip() for a in accounts_param.split(',')]
        elif isinstance(accounts_param, list):
            accounts = accounts_param
        else:
            accounts = [str(accounts_param)]
    else:
        # Fall back to config
        accounts = config_vars.get('accounts', [])
        if not accounts:
            error_msg = "ERROR: No accounts specified. Provide --accounts or set in config file."
            logger.error(error_msg)
            return json.dumps({'error': error_msg})
    
    # Parse dates
    try:
        start_date, end_date = _parse_date_params(params)
    except ValueError as e:
        error_msg = f"ERROR: Invalid date format: {e}"
        logger.error(error_msg)
        return json.dumps({'error': error_msg})
    
    max_results = int(params.get('max_results', 100))
    
    # Get events for all accounts
    all_results = []
    total_events = 0
    errors = []
    
    for account in accounts:
        try:
            logger.info(f"Fetching events for {account}...")
            calendar_service = GoogleCalendarService(account)
            events = calendar_service.get_events_by_date(
                start_date=start_date,
                end_date=end_date,
                max_results=max_results
            )
            
            account_result = {
                'account': account,
                'events': events,
                'count': len(events)
            }
            
            all_results.append(account_result)
            total_events += len(events)
            logger.info(f"Retrieved {len(events)} events for {account}")
            
        except FileNotFoundError as e:
            error_msg = f"Credentials not found for {account}: {e}"
            logger.error(error_msg)
            errors.append({'account': account, 'error': error_msg})
        except Exception as e:
            error_msg = f"Failed to retrieve events for {account}: {e}"
            logger.error(error_msg)
            errors.append({'account': account, 'error': error_msg})
    
    # Build final result
    result = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'accounts': all_results,
        'total_accounts': len(accounts),
        'successful_accounts': len(all_results),
        'total_events': total_events
    }
    
    if errors:
        result['errors'] = errors
    
    logger.info(f"Retrieved {total_events} total events from {len(all_results)}/{len(accounts)} accounts")
    return json.dumps(result, indent=2)


def _parse_date_params(params: dict) -> tuple[datetime, datetime]:
    """Parse date parameters into start and end datetime objects.
    
    Args:
        params: Dictionary containing date parameters
        
    Returns:
        Tuple of (start_date, end_date) as timezone-aware datetime objects
        
    Raises:
        ValueError: If date format is invalid
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get start date
    if params.get('start_date'):
        start_date = datetime.fromisoformat(params['start_date']).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        )
    elif params.get('date'):
        start_date = datetime.fromisoformat(params['date']).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        )
    else:
        start_date = today_start
    
    # Get end date
    if params.get('end_date'):
        end_date = datetime.fromisoformat(params['end_date']).replace(
            hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
        )
    elif params.get('days'):
        days = int(params['days'])
        end_date = start_date + timedelta(days=days)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Default to end of start date
        end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start_date, end_date

