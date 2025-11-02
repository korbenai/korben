"""Podcasts tasks - download and transcribe podcasts."""

import os
import re
import glob
import warnings
import logging
from datetime import datetime, timedelta
import requests
import getpodcast
from src.core.plugins.podcasts.lib import (
    get_data_dir, init_tracking, load_podcasts_config,
    get_podcast_status, update_podcast_status, transcribe_with_whisper
)

logger = logging.getLogger(__name__)

# Suppress XML parsing warnings from BeautifulSoup
try:
    from bs4 import XMLParsedAsHTMLWarning
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
except ImportError:
    pass


def download_podcasts(**kwargs):
    """Download podcasts based on configuration."""
    
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
    logger.info(f"Date range: {date_from} to {today} ({days_back} days back)")
    logger.info(f"Output directory: {PODCASTS_PATH}")
    logger.info("=" * 70)
    
    if not podcasts:
        result = "No podcasts configured. Add podcasts to config/podcasts.yml"
        logger.warning(result)
        return result
    
    total_new = 0
    total_skipped = 0
    
    for podcast_name, feed_url in podcasts.items():
        logger.info(f"\nProcessing: {podcast_name}")
        logger.info(f"Feed: {feed_url}")
        
        try:
            # Create podcast-specific directory
            podcast_dir = os.path.join(PODCASTS_PATH, podcast_name)
            os.makedirs(podcast_dir, exist_ok=True)
            
            # Download episodes
            episodes = getpodcast.get_episodes(
                feed_url,
                start_date=date_from,
                end_date=today
            )
            
            if not episodes:
                logger.info(f"  No new episodes found")
                continue
            
            logger.info(f"  Found {len(episodes)} episode(s)")
            
            for episode in episodes:
                # Extract year from date
                try:
                    episode_date = datetime.strptime(episode['date'], '%Y-%m-%d')
                    year = episode_date.year
                except:
                    year = datetime.now().year
                
                # Create year subdirectory
                year_dir = os.path.join(podcast_dir, str(year))
                os.makedirs(year_dir, exist_ok=True)
                
                # Clean filename
                filename = re.sub(r'[^\w\s-]', '', episode['title']).strip()
                filename = re.sub(r'[-\s]+', '-', filename)
                output_path = os.path.join(year_dir, f"{filename}.mp3")
                
                # Check if already downloaded
                status = get_podcast_status(output_path)
                if status and status.get('downloaded') == 'true':
                    logger.info(f"  ⏭  Skip (exists): {episode['title']}")
                    total_skipped += 1
                    continue
                
                # Download
                logger.info(f"  ⬇️  Downloading: {episode['title']}")
                try:
                    response = requests.get(episode['url'], stream=True, timeout=30)
                    response.raise_for_status()
                    
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Update tracking
                    update_podcast_status(output_path, downloaded=True)
                    total_new += 1
                    logger.info(f"  ✅ Downloaded: {os.path.basename(output_path)}")
                    
                except Exception as e:
                    logger.error(f"  ❌ Failed: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing {podcast_name}: {e}")
            continue
    
    result = f"Downloaded {total_new} new episode(s), skipped {total_skipped} existing"
    logger.info(f"\n{result}")
    return result


def transcribe_podcasts(**kwargs):
    """Transcribe downloaded podcast MP3 files using Whisper."""
    
    # Get data directory
    data_dir = get_data_dir()
    PODCASTS_PATH = os.path.join(data_dir, 'podcasts', 'downloads')
    PODCAST_TRANSCRIPT_PATH = os.path.join(data_dir, 'podcasts', 'transcripts')
    
    # Check if source directory exists
    if not os.path.isdir(PODCASTS_PATH):
        logger.error(f"Downloads directory not found: {PODCASTS_PATH}")
        logger.warning("Run --task download_podcasts first")
        return f"ERROR: Downloads directory not found"
    
    # Check if transcript directory exists, create if needed
    if not os.path.isdir(PODCAST_TRANSCRIPT_PATH):
        logger.info(f"Creating transcripts directory: {PODCAST_TRANSCRIPT_PATH}")
        os.makedirs(PODCAST_TRANSCRIPT_PATH, exist_ok=True)
    
    # Whisper configuration
    model = kwargs.get('model', 'base')
    language = kwargs.get('language', 'en')
    output_format = kwargs.get('output_format', 'txt')
    
    # Count total MP3 files
    total_mp3s = len(glob.glob(os.path.join(PODCASTS_PATH, '**/*.mp3'), recursive=True))
    
    logger.info("=" * 70)
    logger.info("PODCAST TRANSCRIPTION")
    logger.info("=" * 70)
    logger.info(f"Source: {PODCASTS_PATH}")
    logger.info(f"Output: {PODCAST_TRANSCRIPT_PATH}")
    logger.info(f"Model: {model} | Language: {language} | Format: {output_format}")
    logger.info(f"Total MP3 files: {total_mp3s}")
    logger.info("=" * 70)
    
    # Find all .mp3 files recursively
    transcribed_count = 0
    skipped_count = 0
    
    for mp3_file in glob.glob(os.path.join(PODCASTS_PATH, '**/*.mp3'), recursive=True):
        # Check if already transcribed
        status = get_podcast_status(mp3_file)
        if status and status.get('transcribed') == 'true':
            logger.debug(f"Skipping (already transcribed): {os.path.basename(mp3_file)}")
            skipped_count += 1
            continue
        
        # Generate transcript filename
        relative_path = os.path.relpath(mp3_file, PODCASTS_PATH)
        transcript_filename = os.path.splitext(relative_path)[0] + '.txt'
        transcript_path = os.path.join(PODCAST_TRANSCRIPT_PATH, transcript_filename)
        
        # Create subdirectories if needed
        os.makedirs(os.path.dirname(transcript_path), exist_ok=True)
        
        # Transcribe
        logger.info(f"🎙️  Transcribing: {os.path.basename(mp3_file)}")
        try:
            transcribe_with_whisper(mp3_file, transcript_path, model=model, language=language)
            
            # Update tracking
            update_podcast_status(mp3_file, transcribed=True, transcribed_file=transcript_path)
            transcribed_count += 1
            logger.info(f"  ✅ Transcript saved: {transcript_filename}")
            
        except Exception as e:
            logger.error(f"  ❌ Transcription failed: {e}")
            continue
    
    result = f"Transcribed {transcribed_count} podcast(s), skipped {skipped_count} already transcribed"
    logger.info(f"\n{result}")
    return result

