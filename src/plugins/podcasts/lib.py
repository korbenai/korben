"""Shared utilities for podcast tasks."""

import os
import csv
import yaml
import logging
from src.lib.core_utils import get_data_dir

logger = logging.getLogger(__name__)


def get_tracking_csv():
    """Get path to tracking CSV file."""
    data_dir = get_data_dir()
    podcasts_dir = os.path.join(data_dir, 'podcasts')
    return os.path.join(podcasts_dir, 'podcasts.csv')


def init_tracking():
    """Initialize tracking CSV if it doesn't exist."""
    csv_path = get_tracking_csv()
    podcasts_dir = os.path.dirname(csv_path)
    
    # Create podcasts directory
    os.makedirs(podcasts_dir, exist_ok=True)
    
    # Create CSV with headers if it doesn't exist
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['podcast_file', 'transcribed_file', 'summarized', 'emailed'])
        logger.info(f"Created tracking CSV: {csv_path}")


def get_podcast_status(podcast_file):
    """Get status of a podcast from tracking CSV."""
    csv_path = get_tracking_csv()
    if not os.path.exists(csv_path):
        return None
    
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['podcast_file'] == podcast_file:
                return row
    return None


def update_podcast_status(podcast_file, transcribed_file=None, summarized=None, emailed=None):
    """Update or add podcast status in tracking CSV."""
    csv_path = get_tracking_csv()
    rows = []
    updated = False
    
    # Read existing rows
    if os.path.exists(csv_path):
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['podcast_file'] == podcast_file:
                    # Update existing row
                    if transcribed_file is not None:
                        row['transcribed_file'] = transcribed_file
                    if summarized is not None:
                        row['summarized'] = str(summarized).lower()
                    if emailed is not None:
                        row['emailed'] = str(emailed).lower()
                    updated = True
                rows.append(row)
    
    # Add new row if not updated
    if not updated:
        rows.append({
            'podcast_file': podcast_file,
            'transcribed_file': transcribed_file or '',
            'summarized': str(summarized).lower() if summarized is not None else 'false',
            'emailed': str(emailed).lower() if emailed is not None else 'false'
        })
    
    # Write back
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['podcast_file', 'transcribed_file', 'summarized', 'emailed'])
        writer.writeheader()
        writer.writerows(rows)


def load_podcasts_config():
    """Load podcasts configuration from YAML file in plugin directory."""
    # Config now lives in the plugin directory
    config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"No config file found at: {config_path}\n"
            f"Please copy config.yml.example to config.yml in the podcasts plugin:\n"
            f"  cp src/plugins/podcasts/config.yml.example src/plugins/podcasts/config.yml"
        )
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

"""LLM utilities including Whisper transcription."""

import os
import logging
import warnings
import whisper

logger = logging.getLogger(__name__)

# Suppress Whisper FP16 warnings (informational only)
warnings.filterwarnings("ignore", message=".*FP16 is not supported on CPU.*")


def transcribe_with_whisper(audio_file, model="base", language="en", output_format="txt", output_dir=None):
    """
    Transcribe an audio file using OpenAI's Whisper model.
    
    Parameters:
    audio_file (str): Path to the audio file to transcribe.
    model (str): Whisper model to use (tiny, base, small, medium, large).
    language (str): Language code for transcription (e.g., 'en' for English).
    output_format (str): Output format (txt, vtt, srt, json, tsv).
    output_dir (str): Directory to save the transcript. If None, saves in same dir as audio file.
    
    Returns:
    str: Path to the transcript file.
    """
    # Load the Whisper model
    logger.info(f"Loading Whisper model: {model}")
    whisper_model = whisper.load_model(model)
    
    # Transcribe the audio
    logger.debug(f"Transcribing {audio_file}")
    result = whisper_model.transcribe(audio_file, language=language)
    
    # Determine output file path
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.basename(audio_file)
        file_name = os.path.splitext(base_name)[0]
        output_path = os.path.join(output_dir, f"{file_name}.{output_format}")
    else:
        output_path = os.path.splitext(audio_file)[0] + f".{output_format}"
    
    # Write the transcript to file
    with open(output_path, 'w', encoding='utf-8') as f:
        if output_format == "txt":
            f.write(result["text"])
        elif output_format == "json":
            import json
            json.dump(result, f, indent=2, ensure_ascii=False)
        elif output_format == "vtt":
            f.write(_format_vtt(result))
        elif output_format == "srt":
            f.write(_format_srt(result))
        elif output_format == "tsv":
            f.write(_format_tsv(result))
        else:
            # Default to text
            f.write(result["text"])
    
    return output_path


def _format_vtt(result):
    """Format Whisper result as WebVTT."""
    vtt = "WEBVTT\n\n"
    for segment in result.get("segments", []):
        start = _format_timestamp(segment["start"])
        end = _format_timestamp(segment["end"])
        text = segment["text"].strip()
        vtt += f"{start} --> {end}\n{text}\n\n"
    return vtt


def _format_srt(result):
    """Format Whisper result as SRT."""
    srt = ""
    for i, segment in enumerate(result.get("segments", []), 1):
        start = _format_timestamp(segment["start"], srt_format=True)
        end = _format_timestamp(segment["end"], srt_format=True)
        text = segment["text"].strip()
        srt += f"{i}\n{start} --> {end}\n{text}\n\n"
    return srt


def _format_tsv(result):
    """Format Whisper result as TSV."""
    tsv = "start\tend\ttext\n"
    for segment in result.get("segments", []):
        start = int(segment["start"] * 1000)
        end = int(segment["end"] * 1000)
        text = segment["text"].strip().replace("\t", " ")
        tsv += f"{start}\t{end}\t{text}\n"
    return tsv


def _format_timestamp(seconds, srt_format=False):
    """Format seconds as timestamp."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    if srt_format:
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

