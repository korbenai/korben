
"""Cyber News task - fetches and summarizes latest cybersecurity headlines."""
"""
Configuration:
--------------
This task requires access to the Mallory API in order to fetch the latest cybersecurity stories.

**Required Environment Variable**:
- `MALLORY_API_KEY`: You must set this environment variable with your Mallory API access key.

Example:
    export MALLORY_API_KEY='your_real_mallory_api_key'

If `MALLORY_API_KEY` is not set, the task will raise a ValueError and cannot continue.
"""


import os
import requests
import controlflow as cf
from src.lib.core_utils import get_agent_name

def run(**kwargs):
    """Run mallory_stories task to fetch latest stories from Mallory API and summarize them."""
    # Get API key from environment
    api_key = os.environ.get("MALLORY_API_KEY")
    if not api_key:
        raise ValueError("MALLORY_API_KEY environment variable is not set")
    
    # Set up the API request
    url = "https://api.mallory.ai/v1/stories"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Make the API call
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    # Parse the stories
    stories_data = response.json()
    
    # Get stories and sort by reference count (descending)
    stories = stories_data.get("data", [])
    sorted_stories = sorted(
        stories,
        key=lambda story: len(story.get("references", [])),
        reverse=True
    )
    
    # Limit to 20 stories
    sorted_stories = sorted_stories[:10]
    
    # Extract only title, description, uuid, and reference count from each story
    parsed_stories = []
    for story in sorted_stories:
        parsed_story = {
            "title": story.get("title", ""),
            "description": story.get("description", ""),
            "url": f"https://app.mallory.ai/current-events/{story.get('uuid', '')}",
            "reference_count": len(story.get("references", []))
        }
        parsed_stories.append(parsed_story)
    
    # Create an agent to summarize the stories
    agent_name = get_agent_name()
    summarizer = cf.Agent(
        name=agent_name,
        instructions="Review news stories and create concise 1-line summaries that capture the key point of each story. Include the reference count in parentheses and the URL at the end of each summary."
    )
    
    # Generate summaries
    prompt = (
        f"Review these stories and create a 1-line summary for each:\n\n"
        f"{parsed_stories}\n\n"
        f"Return a list of 1-line summaries, one for each story. Include the reference count in parentheses (N refs) and the URL at the end of each summary."
    )
    
    summaries = cf.run(
        prompt,
        agents=[summarizer]
    )
    
    return summaries

