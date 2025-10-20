"""Task to send a Slack message via a webhook registered in config."""

"""
Instructions for Enabling Slack Hook Integration:

1. **Create a Slack Incoming Webhook:**
    - Go to your Slack workspace and choose the channel where you want to post messages.
    - Navigate to https://my.slack.com/services/new/incoming-webhook/ and follow the instructions to create an Incoming Webhook.
    - Copy the Webhook URL provided by Slack.

2. **Add Your Slack Hook to `core.yml`:**
    - Open your `core.yml` or `core.yml.example`.
    - Under the `slack_hooks` section, define your hooks using the following structure:

    ```yaml
    slack_hooks:
      default:
        hook_url: "https://hooks.slack.com/services/your/alerts/webhook"
      # Add more hooks as needed, e.g.:
      # high-priority:
      #   hook_url: "https://hooks.slack.com/services/your/ops/webhook"
    ```

    Replace the `hook_url` with the actual webhook URL from Slack.  
    You can add any number of named hooks. Reference the name (e.g., `"default"`, `"high-priority"`) in your code.

3. **Usage Example:**

    ```python
    from src.core.tasks import send_slack_hook

    send_slack_hook.run(
        hook_name="default",
        message="**Attention:** The deployment is complete!\n[View Logs](https://yourci.example.com/job/123)"
    )
    ```

    - The `hook_name` should match one of the keys defined under `slack_hooks` in your config file.
    - `message` supports basic markdown which will be translated to Slack-compatible formatting.

**Notes:**  
- If you encounter issues, confirm your configuration matches the structure above and that your webhook is valid.

See `core.yml.example` for a template.
"""





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

    try:   
        response = requests.post(hook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Sent Slack message to '{hook_name}'.")
        return f"Slack message sent to '{hook_name}'."
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")
        raise

