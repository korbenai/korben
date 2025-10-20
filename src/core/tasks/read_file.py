"""Read file task - reads text from a local file."""

import os
from src.lib.core_utils import get_tmp_dir


def run(**kwargs):
    """
    Read text from a file.
    
    Args:
        file_path: Path to file to read (absolute or relative to tmp_dir)
    
    Returns:
        str: File contents
    """
    file_path = kwargs.get('file_path')
    
    if not file_path:
        return "ERROR: No file_path specified. Provide --file_path."
    
    # If relative path, make it relative to tmp_dir
    if not os.path.isabs(file_path):
        tmp_dir = get_tmp_dir()
        file_path = os.path.join(tmp_dir, file_path)
    
    if not os.path.exists(file_path):
        return f"ERROR: File not found: {file_path}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content

