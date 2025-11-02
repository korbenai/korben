"""Registry - auto-discovers and registers tasks and flows from plugins."""

import os
import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, Callable

logger = logging.getLogger(__name__)

# Global registries
TASKS: Dict[str, Callable] = {}
FLOWS: Dict[str, Callable] = {}


def is_controlflow_decorated(func):
    """Check if a function is decorated with @cf.flow."""
    try:
        import controlflow as cf
        # Check if function has controlflow flow wrapper
        return hasattr(func, '__wrapped__') or 'controlflow' in str(type(func))
    except:
        return False


def discover_and_register_plugins():
    """
    Automatically discover and register all plugins from src/core/plugins/.
    
    Scans for:
    - tasks.py: Registers all callable functions as tasks
    - flows.py: Registers all @cf.flow decorated functions as flows
    
    Convention:
    - Plugin directory name doesn't matter
    - All public functions in tasks.py are registered as tasks
    - All public functions in flows.py are registered as flows
    - Function names ending in '_workflow' have that suffix stripped for cleaner CLI
    """
    # Get plugins directory
    plugins_dir = Path(__file__).parent / 'plugins'
    
    if not plugins_dir.exists():
        logger.warning(f"Plugins directory not found: {plugins_dir}")
        return
    
    plugin_count = 0
    
    # Scan each subdirectory in plugins/
    for plugin_path in sorted(plugins_dir.iterdir()):
        if not plugin_path.is_dir() or plugin_path.name.startswith('_'):
            continue
        
        plugin_name = plugin_path.name
        logger.debug(f"Discovering plugin: {plugin_name}")
        plugin_count += 1
        
        # Try to import tasks.py
        try:
            tasks_module = importlib.import_module(f'src.core.plugins.{plugin_name}.tasks')
            
            # Register all callable functions from tasks.py as tasks
            for name, obj in inspect.getmembers(tasks_module):
                if callable(obj) and not name.startswith('_') and inspect.isfunction(obj):
                    # Only register functions defined in this module (not imports)
                    if obj.__module__ == tasks_module.__name__:
                        TASKS[name] = obj
                        logger.debug(f"  ✓ Registered task: {name}")
                        
        except (ImportError, AttributeError) as e:
            logger.debug(f"  ⊘ No tasks.py for {plugin_name}")
        
        # Try to import flows.py
        try:
            flows_module = importlib.import_module(f'src.core.plugins.{plugin_name}.flows')
            
            # Register all functions from flows.py as flows
            for name, obj in inspect.getmembers(flows_module):
                if callable(obj) and not name.startswith('_'):
                    # Only register functions defined in this module
                    if hasattr(obj, '__module__') and flows_module.__name__ in str(obj.__module__):
                        if inspect.isfunction(obj) or is_controlflow_decorated(obj):
                            # Use a clean name (remove _workflow suffix for cleaner CLI)
                            flow_name = name.replace('_workflow', '') if name.endswith('_workflow') else name
                            FLOWS[flow_name] = obj
                            logger.debug(f"  ✓ Registered flow: {flow_name}")
                            
        except (ImportError, AttributeError) as e:
            logger.debug(f"  ⊘ No flows.py for {plugin_name}")
    
    logger.info(f"✨ Auto-registered {len(TASKS)} tasks and {len(FLOWS)} flows from {plugin_count} plugins")


# Auto-discover and register on module import
discover_and_register_plugins()
