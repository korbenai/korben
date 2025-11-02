"""GitHub API library functions."""

import os
import logging
import requests

logger = logging.getLogger(__name__)


def get_github_api_key():
    """Get GitHub API key from environment."""
    token = os.getenv('GITHUB_API_KEY')
    if not token:
        raise ValueError("GITHUB_API_KEY environment variable not set")
    return token


def create_gist_from_file(file_path: str, gist_description: str, public: bool = True) -> str:
    """
    Create a GitHub gist from a single file.
    
    Args:
        file_path: Path to the file to create a gist from
        gist_description: Description for the gist
        public: Whether the gist should be public (default: True)
        
    Returns:
        str: URL of the created gist
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If API key is not set
        RuntimeError: If gist creation fails
    """
    access_token = get_github_api_key()
    
    # Check if file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")
    
    # Read file content
    with open(file_path, 'r') as file:
        content = file.read()
    
    gist_files = {
        os.path.basename(file_path): {"content": content}
    }
    
    # Create the gist
    gist_data = {
        "description": gist_description,
        "public": public,
        "files": gist_files
    }
    
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.post("https://api.github.com/gists", json=gist_data, headers=headers)
    
    if response.status_code == 201:
        gist_url = response.json()["html_url"]
        logger.info(f"Gist created successfully: {gist_url}")
        return gist_url
    else:
        error_msg = f"Failed to create gist: {response.status_code}"
        logger.error(f"{error_msg}\n{response.json()}")
        raise RuntimeError(f"{error_msg}: {response.json()}")


def create_gist_from_directory(directory_path: str, gist_description: str, public: bool = True) -> str:
    """
    Create a GitHub gist from all files in a directory.
    
    Args:
        directory_path: Path to the directory containing files
        gist_description: Description for the gist
        public: Whether the gist should be public (default: True)
        
    Returns:
        str: URL of the created gist
        
    Raises:
        FileNotFoundError: If the directory doesn't exist
        ValueError: If API key is not set or no files found
        RuntimeError: If gist creation fails
    """
    access_token = get_github_api_key()
    
    # Check if directory exists
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"Directory {directory_path} does not exist.")
    
    # Prepare the payload for the gist creation
    gist_files = {}
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    gist_files[filename] = {"content": content}
            except UnicodeDecodeError:
                logger.warning(f"Skipping binary file: {filename}")
                continue
    
    if not gist_files:
        raise ValueError(f"No readable text files found in {directory_path}")
    
    # Create the gist
    gist_data = {
        "description": gist_description,
        "public": public,
        "files": gist_files
    }
    
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.post("https://api.github.com/gists", json=gist_data, headers=headers)
    
    if response.status_code == 201:
        gist_url = response.json()["html_url"]
        logger.info(f"Gist created successfully with {len(gist_files)} files: {gist_url}")
        return gist_url
    else:
        error_msg = f"Failed to create gist: {response.status_code}"
        logger.error(f"{error_msg}\n{response.json()}")
        raise RuntimeError(f"{error_msg}: {response.json()}")

