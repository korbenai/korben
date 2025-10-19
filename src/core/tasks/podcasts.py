"""Podcasts task - downloads and transcribes podcasts based on configuration."""

import re
import os
import sys
import warnings
from datetime import datetime, timedelta
import requests
import getpodcast
import yaml
import controlflow as cf
from lib.llm import transcribe_with_whisper
from lib.email import send_email

# Suppress XML parsing warnings from BeautifulSoup in getpodcast
try:
    from bs4 import XMLParsedAsHTMLWarning
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
except ImportError:
    pass  # XMLParsedAsHTMLWarning not available in older versions


def run(**kwargs):
    """Run the complete podcasts workflow: download, transcribe, extract wisdom, and email."""
    results = []
    
    # Step 1: Download podcasts
    print("Step 1: Downloading podcasts...")
    download_result = download(**kwargs)
    results.append(download_result)
    
    # Step 2: Transcribe podcasts
    print("Step 2: Transcribing podcasts...")
    transcribe_result = transcribe(**kwargs)
    results.append(transcribe_result)
    
    # Step 3: Clean up empty wisdom files
    print("Step 3: Cleaning up empty wisdom files...")
    cleanup_result = cleanup_empty_wisdom(**kwargs)
    results.append(cleanup_result)
    
    # Step 4: Extract wisdom and send emails
    print("Step 4: Extracting wisdom and sending emails...")
    wisdom_result = process_wisdom(**kwargs)
    results.append(wisdom_result)
    
    return "\n".join(results)


def download(**kwargs):
    """Download podcasts based on configuration."""
    
    ###
    ### CONFIGURATION
    ###
    
    # Set the root directory to first argument, default to $HOME/Desktop/podcasts 
    # Set the default PODCASTS_PATH if not already set
    PROFILES_PATH = os.getenv('PROFILES_PATH', os.path.expanduser('~/profiles'))
    PODCASTS_PATH = os.getenv('PODCASTS_PATH', os.path.expanduser('/tmp/podcasts/content'))
    
    # Check if the directory exists
    if not os.path.isdir(PODCASTS_PATH):
        print(f"Download. Directory {PODCASTS_PATH} does not exist. Making...")
        os.makedirs(PODCASTS_PATH, exist_ok=True)
    
    # Load the podcasts configuration from yaml file 
    config_path = os.path.expanduser(f'{PROFILES_PATH}/scripts/config/podcasts.yml')
    config = _load_podcasts_config(config_path)
    podcasts = config.get('podcasts', {})
    days_back = config.get('days_back', 7)
    
    ###
    ### END CONFIGURATION
    ###
    
    # Calculate the correct date 
    date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    # Setup podcast options
    # Temporarily save and clear sys.argv to prevent getpodcast from parsing our CLI args
    original_argv = sys.argv.copy()
    sys.argv = [sys.argv[0]]  # Keep only the script name
    
    try:
        opt = getpodcast.options(
            date_from=date_from,
            user_agent="lenny",
            root_dir=PODCASTS_PATH,
            run=True  # Ensure downloads are triggered
        )
    finally:
        # Restore original sys.argv
        sys.argv = original_argv
    
    # Update Apple podcast URLs with feed URLs
    for name, url in podcasts.items():
        if url.startswith('https://podcasts.apple.com'):
            new_url = _get_podcast_url_apple(url)
            if new_url:
                podcasts[name] = new_url
                print(f'INFO: Found XML URL for Apple podcast: {name}: {new_url}')
            else:
                print(f'WARNING: Could not determine URL for Apple podcast: {name}, {url}')
    
    # Log the found podcast items
    for name, url in podcasts.items():
        print(f'Found podcast: {name}, URL: {url}')
    
    # Download the podcasts
    try:
        getpodcast.getpodcast(podcasts, opt)
        result = "INFO: Podcasts downloaded successfully."
        print(result)
        return result
    except Exception as e:
        error_msg = f"ERROR: Failed to download podcasts: {e}"
        print(error_msg)
        raise Exception(error_msg)


def transcribe(**kwargs):
    """Transcribe downloaded podcast MP3 files using Whisper."""
    
    # Set the default paths
    PODCASTS_PATH = os.getenv('PODCASTS_PATH', os.path.expanduser('/tmp/podcasts'))
    PODCAST_TRANSCRIPT_PATH = os.getenv(
        'PODCAST_TRANSCRIPT_PATH',
        os.path.expanduser('~/work/personal/drive/My Drive/podcasts/transcripts')
    )
    
    # Check if source directory exists
    if not os.path.isdir(PODCASTS_PATH):
        error_msg = f"Transcribe. Directory {PODCASTS_PATH} does not exist. Failing"
        print(error_msg)
        raise Exception(error_msg)
    
    # Check if transcript directory exists, create if needed
    if not os.path.isdir(PODCAST_TRANSCRIPT_PATH):
        print(f"Transcribe. Directory {PODCAST_TRANSCRIPT_PATH} does not exist. Making")
        os.makedirs(PODCAST_TRANSCRIPT_PATH, exist_ok=True)
    
    # Whisper configuration
    model = kwargs.get('model', 'base')
    language = kwargs.get('language', 'en')
    output_format = kwargs.get('output_format', 'txt')
    
    # Find all .mp3 files recursively
    transcribed_files = []
    for root, dirs, files in os.walk(PODCASTS_PATH):
        for file in files:
            print(f"Processing file.. {file}")
            if file.endswith(".mp3"):
                podcast = os.path.join(root, file)
                print(f"Transcribing podcast.. {podcast}")
                
                try:
                    transcript = transcribe_with_whisper(
                        podcast,
                        model,
                        language,
                        output_format,
                        output_dir=PODCAST_TRANSCRIPT_PATH
                    )
                    print(f"Transcript written to {transcript}")
                    transcribed_files.append(transcript)
                except Exception as e:
                    print(f"ERROR: Failed to transcribe {podcast}: {e}")
    
    if transcribed_files:
        result = f"INFO: Successfully transcribed {len(transcribed_files)} podcast(s)."
        print(result)
        return result
    else:
        result = "INFO: No podcast files found to transcribe."
        print(result)
        return result


def cleanup_empty_wisdom(**kwargs):
    """Remove empty wisdom files to allow regeneration."""
    PODCASTS_PATH = os.getenv('PODCASTS_PATH', os.path.expanduser('/tmp/podcasts'))
    
    if not os.path.isdir(PODCASTS_PATH):
        result = f"INFO: Podcasts directory {PODCASTS_PATH} does not exist. Skipping cleanup."
        print(result)
        return result
    
    # Find and delete empty wisdom files
    deleted_count = 0
    for root, dirs, files in os.walk(PODCASTS_PATH):
        for file in files:
            if file.endswith(".wisdom"):
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) == 0:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"Deleted empty wisdom file: {file_path}")
    
    result = f"INFO: Cleaned up {deleted_count} empty wisdom file(s)."
    print(result)
    return result


def process_wisdom(**kwargs):
    """Extract wisdom from transcripts and send via email."""
    PODCASTS_PATH = os.getenv('PODCASTS_PATH', os.path.expanduser('/tmp/podcasts'))
    PERSONAL_EMAIL = os.getenv('PERSONAL_EMAIL')
    
    if not PERSONAL_EMAIL:
        result = "WARNING: PERSONAL_EMAIL environment variable not set. Skipping email sending."
        print(result)
        return result
    
    if not os.path.isdir(PODCASTS_PATH):
        result = f"INFO: Podcasts directory {PODCASTS_PATH} does not exist. Skipping wisdom processing."
        print(result)
        return result
    
    # Create wisdom extractor agent
    wisdom_agent = cf.Agent(
        name="Wisdom Extractor",
        instructions=(
            "Extract key insights, wisdom, and actionable takeaways from podcast transcripts. "
            "Focus on practical advice, interesting facts, and thought-provoking ideas. "
            "Format the output as a clean, readable summary with bullet points for key insights."
        )
    )
    
    processed_count = 0
    skipped_count = 0
    
    # Find all .txt transcript files
    for root, dirs, files in os.walk(PODCASTS_PATH):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                wisdom_file = f"{file_path}.wisdom"
                wisdom_sent_file = f"{file_path}.wisdom.sent"
                
                print(f"Processing file: {file_path}")
                
                # Skip if wisdom already sent
                if os.path.exists(wisdom_sent_file):
                    print(f"Wisdom already sent for file: {file_path}")
                    skipped_count += 1
                    continue
                
                # Extract wisdom if not already done
                if not os.path.exists(wisdom_file):
                    print(f"Extracting wisdom from file: {file_path}")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            transcript_content = f.read()
                        
                        # Use controlflow to extract wisdom
                        wisdom_content = cf.run(
                            f"Extract wisdom and key insights from this podcast transcript:\n\n{transcript_content}",
                            agents=[wisdom_agent]
                        )
                        
                        # Write wisdom to file
                        with open(wisdom_file, 'w', encoding='utf-8') as f:
                            f.write(str(wisdom_content))
                        
                        print(f"Wisdom extracted to: {wisdom_file}")
                    except Exception as e:
                        print(f"ERROR: Failed to extract wisdom from {file_path}: {e}")
                        continue
                else:
                    print(f"Wisdom file already exists for: {file_path}")
                
                # Read wisdom content
                try:
                    with open(wisdom_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    print(f"ERROR: Failed to read wisdom file {wisdom_file}: {e}")
                    continue
                
                # Extract topic from folder and filename
                folder_name = os.path.basename(os.path.dirname(file_path))
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                parent_folder = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
                topic = f"pods - {parent_folder} - {file_name[:80]}..."
                
                # Send email
                print(f"Sending email: {topic}")
                try:
                    send_email(PERSONAL_EMAIL, topic, content)
                    
                    # Mark as sent
                    with open(wisdom_sent_file, 'w') as f:
                        f.write("")
                    print(f"Marked wisdom as sent for file: {file_path}")
                    processed_count += 1
                except Exception as e:
                    print(f"ERROR: Failed to send email for {file_path}: {e}")
                    continue
    
    result = f"INFO: Processed {processed_count} podcast(s), skipped {skipped_count} already sent."
    print(result)
    return result


def _load_podcasts_config(config_path):
    """Load podcasts configuration from YAML file."""
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def _get_podcast_url_apple(podcast_url):
    """
    Extract the feed URL for a podcast from its Apple Podcasts URL.
    
    Parameters:r
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
        print(f"ERROR: Failed to retrieve podcast data for {podcast_url}: {e}")
        return None

    data = response.json()
    results = data.get('results', [])
    if results:
        return results[0].get('feedUrl')
    else:
        return None

