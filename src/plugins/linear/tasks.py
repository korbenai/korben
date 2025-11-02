"""Linear tasks - fetch and manage Linear tickets."""

import os
import json
import logging
from typing import List, Optional
from src.plugins.linear.lib import LinearClient, load_linear_config, format_issues_output
from src.lib.core_utils import get_data_dir

logger = logging.getLogger(__name__)


def get_linear_tickets(**kwargs):
    """
    Fetch Linear tickets based on configuration.
    
    Parameters:
        username (str): Override username from config (optional)
        statuses (str): Override statuses from config (optional, comma-separated)
        output_file (str): Path to save JSON output (optional, defaults to data/linear/tickets.json)
        pretty (bool): Pretty print JSON output (default: True)
    
    Returns:
        str: Result message with ticket count
    """
    
    logger.info("=" * 70)
    logger.info("LINEAR TICKET FETCH")
    logger.info("=" * 70)
    
    # Load configuration
    config = load_linear_config()
    
    # Get API key from config or environment
    api_key = config.get('api_key') or os.getenv("LINEAR_API_KEY")
    if not api_key:
        error_msg = "LINEAR_API_KEY not found in config or environment variables"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    
    # Get username (from kwargs, config, or default)
    username = kwargs.get('username') or config.get('username')
    if not username:
        error_msg = "Username not provided in config or arguments"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    
    # Get statuses (from kwargs or config)
    statuses_str = kwargs.get('statuses') or config.get('statuses', 'In Progress,Todo')
    requested_statuses = [status.strip() for status in statuses_str.split(",") if status.strip()]
    
    if not requested_statuses:
        error_msg = "No valid statuses provided"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    
    logger.info(f"Username: {username}")
    logger.info(f"Statuses: {', '.join(requested_statuses)}")
    logger.info("=" * 70)
    
    try:
        # Initialize Linear client
        logger.info("Initializing Linear client")
        client = LinearClient(api_key)
        
        # Find user
        user = client.get_user_by_name(username)
        if not user:
            error_msg = f"User '{username}' not found"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"
        
        logger.info(f"Found user: {user['displayName']} ({user['email']})")
        
        # Get workflow states
        all_states = client.get_workflow_states()
        
        # Find matching states
        matching_states = []
        for state in all_states:
            if state["name"] in requested_statuses:
                matching_states.append(state)
        
        if not matching_states:
            available_states = sorted(set([state["name"] for state in all_states]))
            error_msg = f"No matching workflow states found for: {requested_statuses}"
            logger.error(error_msg)
            logger.info(f"Available states: {', '.join(available_states)}")
            return f"ERROR: {error_msg}\nAvailable states: {', '.join(available_states)}"
        
        state_ids = [state["id"] for state in matching_states]
        state_names = [state["name"] for state in matching_states]
        logger.info(f"Found matching states: {', '.join(state_names)}")
        
        # Get issues
        issues = client.get_issues_by_user_and_states(user["id"], state_ids)
        
        if not issues:
            logger.info("No issues found")
            return "No issues found matching criteria"
        
        # Format output
        output_data = format_issues_output(issues)
        
        # Determine output path
        output_file = kwargs.get('output_file')
        if not output_file:
            data_dir = get_data_dir()
            linear_data_dir = os.path.join(data_dir, 'linear')
            os.makedirs(linear_data_dir, exist_ok=True)
            output_file = os.path.join(linear_data_dir, 'tickets.json')
        
        # Write to file
        pretty = kwargs.get('pretty', True)
        try:
            with open(output_file, 'w') as f:
                if pretty:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(output_data, f, ensure_ascii=False)
            
            logger.info(f"Successfully wrote {len(issues)} issues to: {output_file}")
            
            # Log summary
            logger.info("")
            logger.info("=" * 70)
            logger.info("TICKET SUMMARY")
            logger.info("=" * 70)
            for issue in output_data:
                status_icon = "🔵" if issue["status"] == "In Progress" else "⭕"
                priority_str = f"P{issue['priority']}" if issue.get('priority') else "P?"
                logger.info(f"{status_icon} [{issue['identifier']}] {priority_str} - {issue['name']}")
            logger.info("=" * 70)
            
            result = f"Found {len(issues)} issue(s). Saved to: {output_file}"
            logger.info(result)
            return result
            
        except IOError as e:
            error_msg = f"Failed to write output file: {e}"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"
            
    except Exception as e:
        error_msg = f"Failed to fetch Linear tickets: {e}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


def list_linear_states(**kwargs):
    """
    List all available workflow states in Linear.
    
    Returns:
        str: List of available states
    """
    
    logger.info("=" * 70)
    logger.info("LINEAR WORKFLOW STATES")
    logger.info("=" * 70)
    
    # Load configuration
    config = load_linear_config()
    
    # Get API key
    api_key = config.get('api_key') or os.getenv("LINEAR_API_KEY")
    if not api_key:
        error_msg = "LINEAR_API_KEY not found in config or environment variables"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    
    try:
        # Initialize Linear client
        client = LinearClient(api_key)
        
        # Get workflow states
        all_states = client.get_workflow_states()
        
        # Group by team
        states_by_team = {}
        for state in all_states:
            team_name = state["team"]["name"] if state.get("team") else "No Team"
            if team_name not in states_by_team:
                states_by_team[team_name] = []
            states_by_team[team_name].append(state["name"])
        
        # Log states
        for team_name, state_names in sorted(states_by_team.items()):
            logger.info(f"\n{team_name}:")
            for state_name in sorted(set(state_names)):
                logger.info(f"  - {state_name}")
        
        logger.info("")
        logger.info("=" * 70)
        
        total_states = len(set([s["name"] for s in all_states]))
        result = f"Found {total_states} unique workflow states across {len(states_by_team)} teams"
        logger.info(result)
        return result
        
    except Exception as e:
        error_msg = f"Failed to fetch workflow states: {e}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"

