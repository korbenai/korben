"""Send email task - sends an email via Postmark API."""

import os
import logging
from src.lib.email import send_email as send_email_lib

logger = logging.getLogger(__name__)


def run(**kwargs):
    """
    Send an email using Postmark API.
    
    Args:
        recipient: Recipient email address
        subject: Email subject line
        content: Email content/body
    
    Returns:
        str: Success message
    """
    recipient = kwargs.get('recipient') or os.getenv('PERSONAL_EMAIL')
    subject = kwargs.get('subject')
    content = kwargs.get('content')
    
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

