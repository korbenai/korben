"""Download podcasts task - downloads podcasts from configured feeds."""

import re
import sys
import warnings
import logging
from datetime import datetime, timedelta
import requests
import getpodcast
from src.lib.podcast_utils import get_data_dir, init_tracking, load_podcasts_config

# Set up logging
logger = logging.getLogger(__name__)

# Suppress XML parsing warnings from BeautifulSoup in getpodcast
try:
    from bs4 import XMLParsedAsHTMLWarning
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
except ImportError:
    pass


def run(**kwargs):
    """Download podcasts based on configuration."""
    import os
    
    # Initialize tracking
    init_tracking()
    
    # Get data directory from core config
    data_dir = get_data_dir()
    PODCASTS_PATH = os.path.join(data_dir, 'podcasts', 'downloads')
    
    # Check if the directory exists
    if not os.path.isdir(PODCASTS_PATH):
        logger.info(f"Creating downloads directory: {PODCASTS_PATH}")
        os.makedirs(PODCASTS_PATH, exist_ok=True)
    
    # Load configuration
    config = load_podcasts_config()
    podcasts = config.get('podcasts', {})
    days_back = config.get('days_back', 7)
    
    # Calculate the correct date 
    date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')
    
    logger.info("=" * 70)
    logger.info("PODCAST DOWNLOAD")
    logger.info("=" * 70)
    logger.info(f"Date range: {date_from} to {today} ({days_back} days)")
    logger.info(f"Download path: {PODCASTS_PATH}")
    logger.info(f"Total configured podcasts: {len(podcasts)}")
    logger.info("=" * 70)
    
    # Setup podcast options
    # Temporarily save and clear sys.argv to prevent getpodcast from parsing our CLI args
    original_argv = sys.argv.copy()
    sys.argv = [sys.argv[0]]  # Keep only the script name
    
    try:
        opt = getpodcast.options(
            date_from=date_from,
            user_agent="lenny",
            root_dir=PODCASTS_PATH,
            run=True
        )
    finally:
        # Restore original sys.argv
        sys.argv = original_argv
    
    # Update Apple podcast URLs with feed URLs
    # Also track which podcasts to skip
    podcasts_to_skip = []
    for name, url in list(podcasts.items()):
        if url.startswith('https://podcasts.apple.com'):
            new_url = _get_podcast_url_apple(url)
            if new_url:
                podcasts[name] = new_url
                logger.info(f'Found RSS feed for Apple podcast "{name}": {new_url}')
            else:
                logger.warning(f'Could not determine RSS feed for Apple podcast: {name}')
                logger.warning(f'Skipping podcast: {name} (invalid Apple Podcasts URL)')
                podcasts_to_skip.append(name)
    
    # Remove podcasts that couldn't be converted
    for name in podcasts_to_skip:
        del podcasts[name]
    
    # Log the valid podcast feeds
    if podcasts:
        logger.info(f"Valid podcast feeds: {len(podcasts)}")
        for name, url in podcasts.items():
            logger.info(f'  ✓ {name}')
    else:
        logger.warning("No valid podcast feeds found!")
        logger.warning("All configured podcasts were skipped (invalid Apple Podcasts URLs)")
        logger.warning("Update config/podcasts.yml with valid RSS feeds or working Apple Podcasts URLs")
        return "WARNING: No valid podcasts to download"
    
    # Download the podcasts
    logger.info("=" * 70)
    logger.info("DOWNLOADING...")
    logger.info("=" * 70)
    
    try:
        # Count files before
        import glob
        files_before = len(glob.glob(os.path.join(PODCASTS_PATH, '**/*.mp3'), recursive=True))
        
        getpodcast.getpodcast(podcasts, opt)
        
        # Count files after
        files_after = len(glob.glob(os.path.join(PODCASTS_PATH, '**/*.mp3'), recursive=True))
        downloaded = files_after - files_before
        
        logger.info("=" * 70)
        logger.info("DOWNLOAD COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Downloaded: {downloaded} new episode(s)")
        logger.info(f"Total episodes: {files_after}")
        
        if downloaded == 0:
            logger.warning(f"No new episodes found in date range ({date_from} to {today})")
            logger.warning(f"Try increasing days_back in config/podcasts.yml or check if podcasts have recent episodes")
        
        logger.info("=" * 70)
        
        result = f"Download complete: {downloaded} new, {files_after} total episodes"
        return result
    except Exception as e:
        error_msg = f"Failed to download podcasts: {e}"
        logger.error(error_msg)
        raise Exception(error_msg)


def _get_podcast_url_apple(podcast_url):
    """
    Extract the feed URL for a podcast from its Apple Podcasts URL.
    
    Parameters:
    podcast_url (str): The URL of the podcast on Apple Podcasts.
    
    Returns:
    str: The feed URL of the podcast if found, else None.
    """
    re_pattern = re.compile(r'[^w]+/id(\d+)')
    matches = re_pattern.search(podcast_url)
    if not matches:
        return None
    id = matches.group(1)
    url = f"https://itunes.apple.com/lookup?id={id}&entity=podcast"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to retrieve podcast data for {podcast_url}: {e}")
        return None

    data = response.json()
    results = data.get('results', [])
    if results:
        return results[0].get('feedUrl')
    else:
        return None

