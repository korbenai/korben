"""Send email task - sends an email via Postmark API."""

# Configuration Notes (see README for more):
# - Uses Postmark for transactional email delivery.
# - Required environment variables:
#     POSTMARK_SERVER_TOKEN  # Your Postmark API token.
# - Optional environment variables:
#     POSTMARK_FROM_EMAIL    # Default sender email address (overridable in code).
#     PERSONAL_EMAIL         # Default recipient email for testing/dev (overridable by --recipient).
# - For advanced configuration or troubleshooting, refer to the project README file.

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

