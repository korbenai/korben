"""Email plugin tasks - send emails via Postmark."""

import os
import logging
from src.plugins.email.lib import send_email as send_email_lib
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs

logger = logging.getLogger(__name__)


def send_email(**kwargs):
    """
    Send an email using Postmark API.
    
    Config file: src/plugins/email/config.yml (optional)
    
    Args:
        recipient: Recipient email address (default: from config or PERSONAL_EMAIL env var)
        subject: Email subject line
        content: Email content/body (HTML or plain text)
    
    Returns:
        str: Success message
    """
    # Load plugin config and merge with kwargs
    config = get_plugin_config('email')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    recipient = params.get('recipient') or config_vars.get('recipient') or os.getenv('PERSONAL_EMAIL')
    subject = params.get('subject')
    content = params.get('content')
    
    if not recipient:
        return "ERROR: No recipient specified. Provide --recipient or set PERSONAL_EMAIL environment variable."
    
    if not subject:
        return "ERROR: No subject specified. Provide --subject."
    
    if not content:
        return "ERROR: No content specified. Provide --content."
    
    # Send email
    send_email_lib(recipient, subject, content)
    
    result = f"Email sent to {recipient}: {subject}"
    logger.info(result)
    return result

