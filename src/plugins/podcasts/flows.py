"""Podcasts flows - complete podcast processing workflow."""

import os
import controlflow as cf
from src.plugins.podcasts import tasks as podcast_tasks
from src.plugins.utilities import tasks as utility_tasks
from src.plugins.email import tasks as email_tasks
from src.plugins.podcasts.lib import get_data_dir, get_tracking_csv, get_podcast_status, update_podcast_status

# Plugin dependencies
__dependencies__ = ['email', 'utilities']


@cf.flow
def _process_single_transcript(transcript_path, podcast_file, wisdom_dir, recipient_email=None):
    """
    Process a single transcript: read → extract wisdom → write → convert to HTML → email.
    
    Composes generic tasks to process one podcast transcript.
    
    Args:
        transcript_path: Path to the transcript file
        podcast_file: Path to the podcast file  
        wisdom_dir: Directory to save wisdom output
        recipient_email: Optional recipient email (if not set, email plugin will use its config)
    """
    # Step 1: Read transcript file
    text = utility_tasks.read_file(file_path=transcript_path)
    
    # Step 2: Extract wisdom (returns markdown)
    wisdom_markdown = utility_tasks.extract_wisdom(text=text)
    
    # Step 3: Write wisdom file (markdown)
    wisdom_filename = os.path.basename(transcript_path).replace('.txt', '.wisdom.md')
    wisdom_file = os.path.join(wisdom_dir, wisdom_filename)
    utility_tasks.write_file(file_path=wisdom_file, content=wisdom_markdown)
    
    # Step 4: Convert markdown to HTML for email
    wisdom_html = utility_tasks.markdown_to_html(text=wisdom_markdown)
    
    # Step 5: Generate subject and send email (HTML content)
    file_name = os.path.splitext(os.path.basename(transcript_path))[0]
    subject = f"pods - {file_name[:80]}"
    if len(file_name) > 80:
        subject += "..."
    
    # Send email - only pass recipient if explicitly set in podcasts config
    # Otherwise let email plugin use its own config/PERSONAL_EMAIL fallback
    email_kwargs = {'subject': subject, 'content': wisdom_html}
    if recipient_email:
        email_kwargs['recipient'] = recipient_email
    
    email_tasks.send_email(**email_kwargs)
    
    # Update CSV tracking
    update_podcast_status(podcast_file, summarized=True, emailed=True)
    
    return wisdom_file


@cf.flow
def process_podcasts_workflow(recipient: str | None = None):
    """
    ControlFlow flow for downloading, transcribing, and extracting wisdom from podcasts.
    
    Runs tasks in sequence:
    1. Download podcasts from feeds
    2. Transcribe MP3s to text
    3. For each transcript: read → extract wisdom → write → email (using generic tasks)
    
    All operations share context and history within this flow.
    
    Args:
        recipient: Email recipient (optional - if not set, falls back to email plugin config, then PERSONAL_EMAIL env var)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Convert explicit parameters to kwargs
    kwargs = {}
    if recipient is not None:
        kwargs['recipient'] = recipient
    
    results = []
    
    # Step 1: Download podcasts
    logger.info("Step 1: Downloading podcasts...")
    download_result = podcast_tasks.download_podcasts(**kwargs)
    results.append(download_result)
    
    # Step 2: Transcribe podcasts
    logger.info("Step 2: Transcribing podcasts...")
    transcribe_result = podcast_tasks.transcribe_podcasts(**kwargs)
    results.append(transcribe_result)
    
    # Step 3: Extract wisdom and email for each transcript
    logger.info("Step 3: Extracting wisdom and sending emails...")
    
    # Get recipient from podcasts config if set
    # Otherwise, let email plugin handle its own config/fallback to PERSONAL_EMAIL
    from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs
    podcast_config = get_plugin_config('podcasts')
    podcast_params = merge_config_with_kwargs(podcast_config, kwargs)
    podcast_vars = podcast_config.get('variables', {})
    recipient_email = podcast_params.get('recipient') or podcast_vars.get('recipient')
    
    data_dir = get_data_dir()
    transcript_dir = os.path.join(data_dir, 'podcasts', 'transcripts')
    wisdom_dir = os.path.join(data_dir, 'podcasts', 'wisdom')
    
    if not os.path.isdir(transcript_dir):
        result = f"Transcripts directory {transcript_dir} does not exist. Skipping wisdom processing."
        logger.info(result)
        results.append(result)
        return "\n".join(results)
    
    # Create wisdom directory
    os.makedirs(wisdom_dir, exist_ok=True)
    
    # Process each transcript
    processed_count = 0
    skipped_count = 0
    
    for root, dirs, files in os.walk(transcript_dir):
        for file in files:
            if file.endswith(".txt"):
                transcript_path = os.path.join(root, file)
                
                # Find corresponding podcast file from CSV
                import csv
                podcast_file = None
                csv_path = get_tracking_csv()
                with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['transcribed_file'] == transcript_path:
                            podcast_file = row['podcast_file']
                            break
                
                if not podcast_file:
                    logger.warning(f"No podcast file found for transcript: {transcript_path}")
                    continue
                
                # Check if already processed
                status = get_podcast_status(podcast_file)
                if status and status.get('emailed') == 'true':
                    logger.debug(f"Skipping (already emailed): {file}")
                    skipped_count += 1
                    continue
                
                # Process using generic tasks
                logger.info(f"Processing: {file}")
                try:
                    _process_single_transcript(
                        transcript_path=transcript_path,
                        podcast_file=podcast_file,
                        wisdom_dir=wisdom_dir,
                        recipient_email=recipient_email
                    )
                    processed_count += 1
                    logger.info(f"  ✓ Completed: {file}")
                except Exception as e:
                    logger.error(f"Failed to process {transcript_path}: {e}")
    
    result = f"Processed {processed_count} podcast(s), skipped {skipped_count} already emailed."
    logger.info(result)
    results.append(result)
    
    return "\n".join(results)
