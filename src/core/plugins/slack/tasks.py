"""Slack plugin tasks - send messages via webhooks."""

import os
import logging
import requests
import json
from src.lib.core_utils import get_core_config, get_plugin_config, merge_config_with_kwargs

logger = logging.getLogger(__name__)


def send_slack_hook(**kwargs):
    """
    Send message to Slack via webhook.
    
    Config file: src/core/plugins/slack/config.yml (optional)
    
    Args:
        message: Message text to send
        hook_name: Webhook name (default: from config or 'default')
    
    Returns:
        str: Success message
    """
    # Load plugin config and merge with kwargs
    config = get_plugin_config('slack')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    message = params.get('message')
    hook_name = params.get('hook_name') or config_vars.get('hook_name', 'default')
    
    if not message:
        return "ERROR: No message specified. Provide --message."
    
    # Get webhook URL from config or environment
    webhooks = config_vars.get('webhooks', {})
    webhook_url = webhooks.get(hook_name) or os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        return f"ERROR: SLACK_WEBHOOK_URL not set for hook '{hook_name}'. Set in environment or config."
    
    payload = {'text': message}
    response = requests.post(webhook_url, json=payload)
    
    if response.status_code == 200:
        result = f"Slack message sent to '{hook_name}': {message[:50]}..."
        logger.info(result)
        return result
    else:
        return f"ERROR: Failed to send Slack message: {response.status_code}"

