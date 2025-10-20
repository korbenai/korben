"""Task to send a Slack message via a webhook registered in config."""

import requests
import logging
from src.lib.core_utils import get_core_config

logger = logging.getLogger(__name__)

def format_markdown_for_slack(md_text):
    """
    Convert basic markdown to Slack-compatible formatting.
    This covers *bold*, _italic_, `code`, and links.
    You can expand as needed for more complex conversions.
    """
    import re
    # Bold: **bold** or __bold__ to *bold* (Slack)
    md_text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', md_text)
    md_text = re.sub(r'__(.*?)__', r'*\1*', md_text)
    # Italic: *italic* or _italic_ to _italic_ (Slack)
    md_text = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?<!\*)', r'_\1_', md_text)
    md_text = re.sub(r'_(.*?)_', r'_\1_', md_text)
    # Inline code: `code` to `code`
    # Links: [title](url) → <url|title> (Slack)
    md_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<\2|\1>', md_text)
    return md_text


def run(**kwargs):
    """
    Send a formatted message to a Slack incoming webhook.

    Args:
        hook_name (str): The key identifying the Slack webhook in config.
        message (str): The markdown-formatted message to send.
        username (optional): Custom username for Slack sender.
        icon_emoji (optional): Custom icon emoji for Slack sender.

    Example usage:
        send_slack_hook.run(hook_name="alerts", message="**Server Down:** See details [here](https://...)")
    """
    hook_name = kwargs.get('hook_name')
    message = kwargs.get('message')
    
    if not hook_name:
        raise ValueError("hook_name is required")
    if not message:
        raise ValueError("message is required")
    
    config = get_core_config()
    slack_hooks = config.get("slack_hooks", {})
    hook = slack_hooks.get(hook_name)
    if not hook:
        raise ValueError(f"Slack hook '{hook_name}' not found in config under 'slack_hooks'.")
    hook_url = hook.get("hook_url")
    if not hook_url:
        raise ValueError(f"No 'hook_url' found for slack hook '{hook_name}'.")

    # Prepare message using Slack formatting best practices
    slack_text = format_markdown_for_slack(message)

    payload = {
        "text": slack_text,
    }
    if "username" in kwargs:
        payload["username"] = kwargs["username"]
    if "icon_emoji" in kwargs:
        payload["icon_emoji"] = kwargs["icon_emoji"]

    try:
        # Respect options in core.yml.example: username, icon_emoji, if present in config
        # This does work for Slack "incoming webhooks" if the integration allows these fields to be set.
        # Most custom incoming webhooks do allow "username" and "icon_emoji".
        # Reference: https://api.slack.com/messaging/webhooks#advanced_message_formatting
        config_username = hook.get("username")
        config_icon_emoji = hook.get("icon_emoji")
        if "username" not in payload and config_username:
            payload["username"] = config_username
        if "icon_emoji" not in payload and config_icon_emoji:
            payload["icon_emoji"] = config_icon_emoji
        # This approach will set "username" and "icon_emoji" in the message JSON payload;
        # If the webhook's Slack integration is not a custom app, these fields may be ignored.
        
        response = requests.post(hook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Sent Slack message to '{hook_name}'.")
        return f"Slack message sent to '{hook_name}'."
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")
        raise

