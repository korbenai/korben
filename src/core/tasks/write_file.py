"""Write file task - writes text to a local file."""

import os
from src.lib.core_utils import get_tmp_dir


def run(**kwargs):
    """
    Write text to a file.
    
    Args:
        file_path: Path to file to write (absolute or relative to tmp_dir)
        content: Text content to write
    
    Returns:
        str: Path to written file
    """
    file_path = kwargs.get('file_path')
    content = kwargs.get('content')
    
    if not file_path:
        return "ERROR: No file_path specified. Provide --file_path."
    
    if content is None:
        return "ERROR: No content specified. Provide --content."
    
    # If relative path, make it relative to tmp_dir
    if not os.path.isabs(file_path):
        tmp_dir = get_tmp_dir()
        file_path = os.path.join(tmp_dir, file_path)
    
    # Create directory if it doesn't exist
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path

