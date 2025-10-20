"""Transcribe podcasts task - transcribes MP3 files to text using Whisper."""

import os
import glob
import logging
from src.lib.llm import transcribe_with_whisper
from src.lib.podcast_utils import get_data_dir, get_podcast_status, update_podcast_status

# Set up logging
logger = logging.getLogger(__name__)


def run(**kwargs):
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
    
    for root, dirs, files in os.walk(PODCASTS_PATH):
        for file in files:
            if file.endswith(".mp3"):
                podcast_path = os.path.join(root, file)
                
                # Check if already transcribed
                status = get_podcast_status(podcast_path)
                if status and status.get('transcribed_file'):
                    logger.debug(f"Skipping (already transcribed): {file}")
                    skipped_count += 1
                    continue
                
                logger.info(f"Transcribing: {file}")
                
                try:
                    transcript = transcribe_with_whisper(
                        podcast_path,
                        model,
                        language,
                        output_format,
                        output_dir=PODCAST_TRANSCRIPT_PATH
                    )
                    logger.info(f"  ✓ Saved: {os.path.basename(transcript)}")
                    
                    # Update tracking
                    update_podcast_status(podcast_path, transcribed_file=transcript)
                    transcribed_count += 1
                except Exception as e:
                    logger.error(f"Failed to transcribe {file}: {e}")
    
    logger.info("=" * 70)
    logger.info("TRANSCRIPTION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Transcribed: {transcribed_count} new podcast(s)")
    logger.info(f"Skipped: {skipped_count} already transcribed")
    logger.info(f"Total: {total_mp3s} MP3 files")
    
    if transcribed_count == 0 and total_mp3s > 0:
        logger.info("✓ All podcasts already transcribed!")
    elif total_mp3s == 0:
        logger.warning("No MP3 files found")
        logger.warning("Run --task download_podcasts first")
    
    logger.info("=" * 70)
    
    result = f"Transcribed {transcribed_count} new, skipped {skipped_count}, total {total_mp3s} files"
    return result

