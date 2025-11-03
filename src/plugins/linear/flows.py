"""Linear flows - complete Linear ticket sync workflows."""

import os
import json
import logging
import controlflow as cf
from src.plugins.linear import tasks as linear_tasks

logger = logging.getLogger(__name__)


# @cf.flow
# def linear_sync_workflow(**kwargs):
#     """
#     ControlFlow flow for syncing Linear tickets.
    
#     Fetches current tickets and saves them to the data directory.
#     Can be scheduled to run daily or on-demand.
    
#     Args:
#         username: Override username from config (optional)
#         statuses: Override statuses from config (optional, comma-separated)
#         output_file: Path to save JSON output (optional)
#         pretty: Pretty print JSON output (default: True)
    
#     Returns:
#         str: Summary of sync results
#     """
#     logger.info("Starting Linear ticket sync workflow...")
    
#     # Fetch tickets
#     result = linear_tasks.get_linear_tickets(**kwargs)
    
#     logger.info(f"Linear sync workflow completed: {result}")
#     return result


@cf.flow  
def linear_status_report_workflow(
    username: str | None = None,
    statuses: str | None = None,
    send_email: bool = False,
    email_recipient: str | None = None,
    send_slack: bool = False,
    hook_name: str | None = None,
):
    """
    ControlFlow flow for generating a daily Linear ticket report.
    
    Fetches current tickets and can optionally integrate with other plugins
    (email, Slack) to send reports.
    
    Args:
        username: Override username from config (optional)
        statuses: Override statuses from config (optional, comma-separated)
        send_email: Send report via email (requires email plugin, default: False)
        email_recipient: Email recipient override (optional)
        send_slack: Send report via Slack (requires slack plugin, default: False)
        hook_name: Slack webhook name from config (optional, default: 'default')
    
    Returns:
        str: Summary of report generation
    """
    # Convert explicit parameters to kwargs
    kwargs = {
        'username': username,
        'statuses': statuses,
        'send_email': send_email,
        'email_recipient': email_recipient,
        'send_slack': send_slack,
        'hook_name': hook_name,
    }
    # Remove None values (but keep False for booleans)
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    
    logger.info("Starting Linear status report workflow...")
    
    results = []
    
    # Step 1: Fetch tickets
    logger.info("Step 1: Fetching Linear tickets...")
    fetch_result = linear_tasks.get_linear_tickets(**kwargs)
    results.append(fetch_result)
    
    # Step 2: Load the ticket data for reporting
    from src.lib.core_utils import get_data_dir
    data_dir = get_data_dir()
    tickets_file = os.path.join(data_dir, 'linear', 'tickets.json')
    
    if not os.path.exists(tickets_file):
        error_msg = "Failed to load tickets data"
        logger.error(error_msg)
        results.append(f"ERROR: {error_msg}")
        return "\n".join(results)
    
    with open(tickets_file, 'r') as f:
        tickets = json.load(f)
    
    # Step 3: Generate report
    logger.info("Step 2: Generating report...")
    report_text = _generate_ticket_report(tickets, format='text')
    report_markdown = _generate_ticket_report(tickets, format='markdown')
    
    # Step 4: Send via email if requested (needs HTML)
    send_email = kwargs.get('send_email', False)
    if send_email:
        logger.info("Step 3: Sending email report...")
        try:
            from src.plugins.email import tasks as email_tasks
            from src.plugins.utilities import tasks as utility_tasks
            
            # Convert markdown to HTML for email
            report_html = utility_tasks.markdown_to_html(text=report_markdown)
            
            email_tasks.send_email(
                subject="Linear Ticket Status Report",
                content=report_html,
                recipient=kwargs.get('email_recipient')
            )
            results.append("Email report sent successfully")
        except ImportError:
            logger.warning("Email plugin not available - skipping email")
            results.append("WARNING: Email plugin not available")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            results.append(f"ERROR: Failed to send email - {e}")
    
    # Step 5: Send via Slack if requested (uses plain text)
    send_slack = kwargs.get('send_slack', False)
    if send_slack:
        logger.info("Step 4: Sending Slack report...")
        try:
            from src.plugins.slack import tasks as slack_tasks
            slack_result = slack_tasks.send_slack_hook(
                message=report_text,
                hook_name=kwargs.get('hook_name')  # Optional webhook name from config
            )
            results.append(f"Slack report sent: {slack_result}")
        except ImportError:
            logger.warning("Slack plugin not available - skipping Slack")
            results.append("WARNING: Slack plugin not available")
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            results.append(f"ERROR: Failed to send Slack message - {e}")
    
    result = "\n".join(results)
    logger.info(f"Linear daily report workflow completed")
    return result


def _generate_ticket_report(tickets: list, format: str = 'text') -> str:
    """
    Generate a formatted report from tickets.
    
    Args:
        tickets: List of ticket dictionaries
        format: Output format - 'text' for plain text, 'markdown' for markdown
        
    Returns:
        str: Formatted report
    """
    if not tickets:
        return "No tickets found."
    
    # Group by status
    by_status = {}
    for ticket in tickets:
        status = ticket.get('status', 'Unknown')
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(ticket)
    
    # Sort statuses for consistent ordering
    status_order = ["In Progress", "Todo", "In Review", "Blocked"]
    sorted_statuses = sorted(by_status.keys(), key=lambda x: (status_order.index(x) if x in status_order else 999, x))
    
    if format == 'markdown':
        # Markdown format for email (converts to HTML)
        report_lines = [
            f"# Linear Ticket Report",
            f"**{len(tickets)} Total Tickets**",
            ""
        ]
        
        for status in sorted_statuses:
            tickets_in_status = by_status[status]
            report_lines.append(f"## {status} ({len(tickets_in_status)})")
            report_lines.append("")
            
            for ticket in sorted(tickets_in_status, key=lambda t: t.get('priority', 999)):
                identifier = ticket.get('identifier', 'UNKNOWN')
                name = ticket.get('name', 'Untitled')
                priority = ticket.get('priority')
                labels = ticket.get('labels', [])
                url = ticket.get('url', '')
                
                priority_str = f"P{priority}" if priority else "P?"
                labels_str = f" `{', '.join(labels)}`" if labels else ""
                
                # Markdown list item with link
                if url:
                    report_lines.append(f"- **[{identifier}]({url})** - {priority_str} - {name}{labels_str}")
                else:
                    report_lines.append(f"- **{identifier}** - {priority_str} - {name}{labels_str}")
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    else:
        # Plain text format for Slack/console
        report_lines = [
            "=" * 70,
            f"LINEAR TICKET REPORT - {len(tickets)} Total Tickets",
            "=" * 70,
            ""
        ]
        
        for status in sorted_statuses:
            tickets_in_status = by_status[status]
            report_lines.append(f"\n{status.upper()} ({len(tickets_in_status)})")
            report_lines.append("-" * 70)
            
            for ticket in sorted(tickets_in_status, key=lambda t: t.get('priority', 999)):
                identifier = ticket.get('identifier', 'UNKNOWN')
                name = ticket.get('name', 'Untitled')
                priority = ticket.get('priority')
                labels = ticket.get('labels', [])
                
                priority_str = f"P{priority}" if priority else "P?"
                labels_str = f" [{', '.join(labels)}]" if labels else ""
                
                report_lines.append(f"  • {identifier} - {priority_str} - {name}{labels_str}")
                
                # Add URL
                if ticket.get('url'):
                    report_lines.append(f"    {ticket['url']}")
        
        report_lines.append("")
        report_lines.append("=" * 70)
        
        return "\n".join(report_lines)

