"""Eater flows - search for new restaurants and send newsletter."""

import os
import logging
from src.plugins.eater import tasks as eater_tasks
from src.plugins.utilities import tasks as utility_tasks
from src.plugins.email import tasks as email_tasks
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs
from datetime import datetime

logger = logging.getLogger(__name__)


def eater_restaurant_scout_workflow(
    month_year: str | None = None,
    recipient: str | None = None,
    subject: str | None = None,
    max_results: int | None = None,
):
    """
    ControlFlow flow for finding new restaurants and emailing them as a newsletter.

    Config file: config/eater.yml (optional)

    Runs tasks in sequence:
    1. Search for new restaurants using AI and Tavily
    2. Convert markdown to HTML
    3. Send email with restaurant recommendations

    Args:
        month_year: Month and year to search for (default: current month/year)
        recipient: Email recipient (default: from config or PERSONAL_EMAIL env var)
        subject: Email subject (default: from config or templated subject)
        max_results: Maximum number of restaurants to include (default: from config or 10)

    Returns:
        str: Status message
    """
    # Convert explicit parameters to kwargs for config merging
    kwargs = {
        'recipient': recipient,
        'subject': subject,
        'max_results': max_results,
    }
    # Remove None values
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    # Load plugin config and merge with kwargs (kwargs take precedence)
    config = get_plugin_config('eater')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})

    # Extract parameters
    month_year = params.get('month_year') or datetime.now().strftime("%B %Y")
    recipient = params.get('recipient') or config_vars.get('recipient') or os.getenv('PERSONAL_EMAIL')
    subject_template = params.get('subject') or config_vars.get('subject', "New Restaurants in {city} - {month_year}")
    max_results = params.get('max_results') or config_vars.get('max_results', 10)

    # Get city for subject templating
    city = config_vars.get('city', 'Austin')

    # Format subject with variables
    subject = subject_template.format(city=city, month_year=month_year)

    results = []

    # Step 1: Search for new restaurants
    logger.info("Step 1: Searching for new restaurants...")
    try:
        search_params = {
            'month_year': month_year,
            'max_results': max_results
        }
        restaurants_md = eater_tasks.search_new_restaurants(**search_params)
        results.append("Successfully found and summarized new restaurants")
        logger.info(f"Found restaurants: {restaurants_md[:200]}...")
    except Exception as e:
        error_msg = f"Failed to search for restaurants: {e}"
        logger.error(error_msg)
        results.append(error_msg)
        return "\n".join(results)

    # Step 2: Convert markdown to HTML
    logger.info("Step 2: Converting restaurant list to HTML...")
    try:
        # Format as markdown with header
        markdown_content = f"# New Restaurants in {city} - {month_year}\n\n{restaurants_md}"
        restaurants_html = utility_tasks.markdown_to_html(text=markdown_content)
        results.append("Successfully converted restaurant list to HTML")
        logger.info("Restaurant list converted to HTML")
    except Exception as e:
        error_msg = f"Failed to convert markdown to HTML: {e}"
        logger.error(error_msg)
        results.append(error_msg)
        return "\n".join(results)

    # Step 3: Send email with restaurants
    logger.info("Step 3: Sending email with restaurant recommendations...")

    if not recipient:
        error_msg = "ERROR: No recipient specified. Provide --recipient or set PERSONAL_EMAIL environment variable."
        logger.error(error_msg)
        results.append(error_msg)
        return "\n".join(results)

    try:
        email_result = email_tasks.send_email(
            recipient=recipient,
            subject=subject,
            content=restaurants_html
        )
        results.append(email_result)
        logger.info(f"Email sent successfully: {email_result}")
    except Exception as e:
        error_msg = f"Failed to send email: {e}"
        logger.error(error_msg)
        results.append(error_msg)

    return "\n".join(results)
