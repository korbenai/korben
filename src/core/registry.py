"""Task registry - simple dictionary of available tasks."""

from src.core.tasks import entropy
from src.core.tasks import cybernews
from src.core.tasks import podcasts


# Dictionary of all available tasks
TASKS = {
    "entropy": entropy.run,
    "cybernews": cybernews.run,
    "podcasts": podcasts.run,
}

