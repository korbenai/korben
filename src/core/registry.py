"""Registry - dictionaries of available tasks and flows."""

from src.core.tasks import entropy
from src.core.tasks import download_podcasts
from src.core.tasks import transcribe_podcasts
from src.core.tasks import extract_wisdom
from src.core.tasks import send_email
from src.core.tasks import read_file
from src.core.tasks import write_file
from src.core.tasks import markdown_to_html
from src.core.tasks import get_mallory_stories
from src.core.flows.podcasts import podcast_workflow
from src.core.flows.mallory_stories import mallory_stories_workflow


# Dictionary of all available tasks
TASKS = {
    "entropy": entropy.run,
    "get_mallory_stories": get_mallory_stories.run,
    "download_podcasts": download_podcasts.run,
    "transcribe_podcasts": transcribe_podcasts.run,
    "extract_wisdom": extract_wisdom.run,
    "send_email": send_email.run,
    "read_file": read_file.run,
    "write_file": write_file.run,
    "markdown_to_html": markdown_to_html.run,
}

# Dictionary of all available flows
FLOWS = {
    "podcasts": podcast_workflow,
    "mallory_stories": mallory_stories_workflow,
}

