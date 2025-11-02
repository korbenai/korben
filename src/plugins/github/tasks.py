"""GitHub plugin tasks - create gists from files and directories."""

import os
import logging
from src.plugins.github.lib import create_gist_from_file as create_gist_from_file_lib
from src.plugins.github.lib import create_gist_from_directory as create_gist_from_directory_lib
from src.lib.core_utils import get_plugin_config, merge_config_with_kwargs

logger = logging.getLogger(__name__)


def create_gist_from_file(**kwargs):
    """
    Create a GitHub gist from a single file.
    
    Config file: src/plugins/github/config.yml (optional)
    
    Args:
        file_path: Path to the file to create a gist from
        description: Description for the gist
        public: Whether the gist should be public (default: True)
    
    Returns:
        str: URL of the created gist or error message
    """
    # Load plugin config and merge with kwargs
    config = get_plugin_config('github')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    file_path = params.get('file_path')
    description = params.get('description') or config_vars.get('default_description', 'Gist created by Korben')
    public = params.get('public', True)
    
    if not file_path:
        return "ERROR: No file_path specified. Provide --file_path."
    
    # Expand user home directory if present
    file_path = os.path.expanduser(file_path)
    
    try:
        gist_url = create_gist_from_file_lib(file_path, description, public)
        result = f"Gist created successfully: {gist_url}"
        logger.info(result)
        return result
    except FileNotFoundError as e:
        error = f"ERROR: {str(e)}"
        logger.error(error)
        return error
    except ValueError as e:
        error = f"ERROR: {str(e)}"
        logger.error(error)
        return error
    except RuntimeError as e:
        error = f"ERROR: {str(e)}"
        logger.error(error)
        return error
    except Exception as e:
        error = f"ERROR: Unexpected error creating gist: {str(e)}"
        logger.error(error)
        return error


def create_gist_from_directory(**kwargs):
    """
    Create a GitHub gist from all files in a directory.
    
    Config file: src/plugins/github/config.yml (optional)
    
    Args:
        directory_path: Path to the directory containing files
        description: Description for the gist
        public: Whether the gist should be public (default: True)
    
    Returns:
        str: URL of the created gist or error message
    """
    # Load plugin config and merge with kwargs
    config = get_plugin_config('github')
    params = merge_config_with_kwargs(config, kwargs)
    config_vars = config.get('variables', {})
    
    directory_path = params.get('directory_path')
    description = params.get('description') or config_vars.get('default_description', 'Gist created by Korben')
    public = params.get('public', True)
    
    if not directory_path:
        return "ERROR: No directory_path specified. Provide --directory_path."
    
    # Expand user home directory if present
    directory_path = os.path.expanduser(directory_path)
    
    try:
        gist_url = create_gist_from_directory_lib(directory_path, description, public)
        result = f"Gist created successfully: {gist_url}"
        logger.info(result)
        return result
    except FileNotFoundError as e:
        error = f"ERROR: {str(e)}"
        logger.error(error)
        return error
    except ValueError as e:
        error = f"ERROR: {str(e)}"
        logger.error(error)
        return error
    except RuntimeError as e:
        error = f"ERROR: {str(e)}"
        logger.error(error)
        return error
    except Exception as e:
        error = f"ERROR: Unexpected error creating gist: {str(e)}"
        logger.error(error)
        return error

