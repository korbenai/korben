"""Podcasts tasks - download and transcribe podcasts."""

import os
import re
import glob
import warnings
import logging
from datetime import datetime, timedelta
import requests
import getpodcast
from lxml import etree
from src.plugins.podcasts.lib import (
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
    # Get data directory from config, allow override via config variables.downloads_dir
    config = load_podcasts_config()
    variables = config.get('variables', {})
    downloads_subdir = variables.get('downloads_dir', os.path.join('podcasts', 'downloads'))

    data_dir = get_data_dir()
    PODCASTS_PATH = os.path.join(data_dir, downloads_subdir)

    # Check if the directory exists
    if not os.path.isdir(PODCASTS_PATH):
        logger.info(f"Creating downloads directory: {PODCASTS_PATH}")
        os.makedirs(PODCASTS_PATH, exist_ok=True)
    # Load configuration (feeds and variables)
    # Note: variables hold operational knobs like days_back, downloads_dir, recipient
    podcasts = config.get('podcasts', {})
    days_back = variables.get('days_back', 7)
    
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
            resolved_url = _resolve_feed_url(feed_url)
            if resolved_url != feed_url:
                logger.info(f"  Resolved feed URL: {resolved_url}")
            try:
                # Preferred path if library provides helper
                episodes = getpodcast.get_episodes(
                    resolved_url,
                    start_date=date_from,
                    end_date=today
                )
            except AttributeError:
                # Fallback: parse RSS directly (getpodcast API not available)
                episodes = _fetch_episodes_via_rss(
                    resolved_url,
                    start_date=date_from,
                    end_date=today,
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
                
                # Check if already downloaded (use file existence)
                if os.path.exists(output_path):
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
                    
                    # Optionally record row (no downloaded flag in tracker)
                    update_podcast_status(output_path)
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
            output_dir = os.path.dirname(transcript_path)
            actual_path = transcribe_with_whisper(
                audio_file=mp3_file,
                model=model,
                language=language,
                output_format=output_format,
                output_dir=output_dir,
            )
            
            # Update tracking
            update_podcast_status(mp3_file, transcribed_file=actual_path)
            transcribed_count += 1
            logger.info(f"  ✅ Transcript saved: {os.path.basename(actual_path)}")
            
        except Exception as e:
            logger.error(f"  ❌ Transcription failed: {e}")
            continue
    
    result = f"Transcribed {transcribed_count} podcast(s), skipped {skipped_count} already transcribed"
    logger.info(f"\n{result}")
    return result


def _fetch_episodes_via_rss(feed_url: str, start_date: str, end_date: str):
    """Fallback RSS fetch when getpodcast.get_episodes is unavailable.
    Returns list of dicts with keys: title, url, date (YYYY-MM-DD).
    """
    try:
        resp = requests.get(feed_url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"  ❌ Failed to fetch RSS: {e}")
        return []

    try:
        root = etree.fromstring(resp.content)
    except Exception as e:
        logger.error(f"  ❌ Failed to parse RSS XML: {e}")
        return []

    ns = {
        'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'media': 'http://search.yahoo.com/mrss/'
    }

    def _text(elem):
        return elem.text.strip() if elem is not None and elem.text else ""

    def _date_to_str(dt):
        try:
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return ''

    def _parse_pubdate(pubtext):
        # Try common RSS date formats
        from email.utils import parsedate_to_datetime
        try:
            dt = parsedate_to_datetime(pubtext)
            return _date_to_str(dt)
        except Exception:
            return ''

    from_dt = datetime.strptime(start_date, '%Y-%m-%d')
    to_dt = datetime.strptime(end_date, '%Y-%m-%d')

    items = root.findall('.//item')
    results = []
    for it in items:
        title = _text(it.find('title'))
        pubtext = _text(it.find('pubDate'))
        date_str = _parse_pubdate(pubtext) if pubtext else ''
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d') if date_str else None
        except Exception:
            dt = None

        if dt is None or dt < from_dt or dt > to_dt:
            continue

        # Prefer enclosure url, then media:content
        url = ''
        enclosure = it.find('enclosure')
        if enclosure is not None and enclosure.get('url'):
            url = enclosure.get('url')
        if not url:
            media_content = it.find('media:content', namespaces=ns)
            if media_content is not None and media_content.get('url'):
                url = media_content.get('url')

        if not url:
            continue

        results.append({
            'title': title or 'episode',
            'url': url,
            'date': date_str or start_date,
        })

    return results


def _resolve_feed_url(feed_url: str) -> str:
    """Resolve human-facing podcast URLs (e.g., Apple Podcasts) to RSS feed URLs.
    Returns the original URL if no resolution is needed or fails.
    """
    try:
        if 'podcasts.apple.com' in feed_url:
            # Extract Apple Podcast ID like .../id1499392701
            import re
            m = re.search(r'id(\d+)', feed_url)
            if not m:
                return feed_url
            itunes_id = m.group(1)
            # Prefer explicit country/entity to improve result consistency
            lookup_url = (
                f"https://itunes.apple.com/lookup?id={itunes_id}"
                f"&country=us&entity=podcast"
            )
            resp = requests.get(lookup_url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            results = data.get('results') or []
            if results and 'feedUrl' in results[0]:
                return results[0]['feedUrl']
            # Fallback: retry without entity (some regions)
            lookup_url2 = f"https://itunes.apple.com/lookup?id={itunes_id}&country=us"
            resp2 = requests.get(lookup_url2, timeout=15)
            resp2.raise_for_status()
            data2 = resp2.json()
            results2 = data2.get('results') or []
            if results2 and 'feedUrl' in results2[0]:
                return results2[0]['feedUrl']
        return feed_url
    except Exception as e:
        logger.debug(f"Feed URL resolution failed for {feed_url}: {e}")
        return feed_url

