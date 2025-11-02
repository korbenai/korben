"""Registry - auto-discovers and registers tasks and flows from plugins."""

import os
import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, Callable, Set, List

logger = logging.getLogger(__name__)

# Global registries
TASKS: Dict[str, Callable] = {}
FLOWS: Dict[str, Callable] = {}
PLUGIN_DEPENDENCIES: Dict[str, List[str]] = {}  # Track plugin dependencies
DISABLED_PLUGINS: Set[str] = set()  # Track disabled plugins


def is_controlflow_decorated(func):
    """Check if a function is decorated with @cf.flow."""
    try:
        import controlflow as cf
        # Check if function has controlflow flow wrapper
        return hasattr(func, '__wrapped__') or 'controlflow' in str(type(func))
    except:
        return False


def _extract_dependencies(module) -> List[str]:
    """Extract dependencies from a plugin module.
    
    Looks for __dependencies__ module-level variable.
    
    Returns:
        List of required plugin names
    """
    if hasattr(module, '__dependencies__'):
        deps = getattr(module, '__dependencies__')
        if isinstance(deps, (list, tuple)):
            return list(deps)
        elif isinstance(deps, str):
            return [deps]
    return []


def _check_plugin_dependencies(plugin_name: str, required_plugins: Set[str]) -> bool:
    """Check if all required plugins are available.
    
    Args:
        plugin_name: Name of plugin to check
        required_plugins: Set of all discovered plugin names
        
    Returns:
        True if all dependencies are met, False otherwise
    """
    if plugin_name not in PLUGIN_DEPENDENCIES:
        return True
    
    dependencies = PLUGIN_DEPENDENCIES[plugin_name]
    missing = [dep for dep in dependencies if dep not in required_plugins]
    
    if missing:
        logger.warning(f"Plugin '{plugin_name}' disabled - missing dependencies: {', '.join(missing)}")
        DISABLED_PLUGINS.add(plugin_name)
        return False
    
    return True


def discover_and_register_plugins():
    """
    Automatically discover and register all plugins from src/plugins/.
    
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
    discovered_plugins = set()
    temp_tasks = {}
    temp_flows = {}
    plugin_task_mapping = {}  # Track which plugin each task belongs to
    plugin_flow_mapping = {}  # Track which plugin each flow belongs to
    
    # Phase 1: Scan all plugins and collect dependencies
    for plugin_path in sorted(plugins_dir.iterdir()):
        if not plugin_path.is_dir() or plugin_path.name.startswith('_'):
            continue
        
        plugin_name = plugin_path.name
        discovered_plugins.add(plugin_name)
        logger.debug(f"Discovering plugin: {plugin_name}")
        plugin_count += 1
        
        # Extract dependencies from tasks and flows modules
        all_dependencies = []
        
        # Try to import tasks.py
        try:
            tasks_module = importlib.import_module(f'src.plugins.{plugin_name}.tasks')
            
            # Extract dependencies
            task_deps = _extract_dependencies(tasks_module)
            all_dependencies.extend(task_deps)
            
            # Collect tasks (don't register yet)
            for name, obj in inspect.getmembers(tasks_module):
                if callable(obj) and not name.startswith('_') and inspect.isfunction(obj):
                    # Only register functions defined in this module (not imports)
                    if obj.__module__ == tasks_module.__name__:
                        temp_tasks[name] = obj
                        plugin_task_mapping[name] = plugin_name
                        logger.debug(f"  ✓ Found task: {name}")
                        
        except (ImportError, AttributeError) as e:
            logger.debug(f"  ⊘ No tasks.py for {plugin_name}")
        
        # Try to import flows.py
        try:
            flows_module = importlib.import_module(f'src.plugins.{plugin_name}.flows')
            
            # Extract dependencies
            flow_deps = _extract_dependencies(flows_module)
            all_dependencies.extend(flow_deps)
            
            # Collect flows (don't register yet)
            for name, obj in inspect.getmembers(flows_module):
                if callable(obj) and not name.startswith('_'):
                    # Only register functions defined in this module
                    if hasattr(obj, '__module__') and flows_module.__name__ in str(obj.__module__):
                        if inspect.isfunction(obj) or is_controlflow_decorated(obj):
                            # Use a clean name (remove _workflow suffix for cleaner CLI)
                            flow_name = name.replace('_workflow', '') if name.endswith('_workflow') else name
                            temp_flows[flow_name] = obj
                            plugin_flow_mapping[flow_name] = plugin_name
                            logger.debug(f"  ✓ Found flow: {flow_name}")
                            
        except (ImportError, AttributeError) as e:
            logger.debug(f"  ⊘ No flows.py for {plugin_name}")
        
        # Store dependencies for this plugin
        if all_dependencies:
            PLUGIN_DEPENDENCIES[plugin_name] = list(set(all_dependencies))
            logger.debug(f"  → Dependencies: {', '.join(all_dependencies)}")
    
    # Phase 2: Validate dependencies and register enabled plugins
    logger.debug("\nValidating plugin dependencies...")
    
    for plugin_name in discovered_plugins:
        if _check_plugin_dependencies(plugin_name, discovered_plugins):
            # Plugin is valid, register its tasks and flows
            for task_name, task_func in temp_tasks.items():
                if plugin_task_mapping.get(task_name) == plugin_name:
                    TASKS[task_name] = task_func
            
            for flow_name, flow_func in temp_flows.items():
                if plugin_flow_mapping.get(flow_name) == plugin_name:
                    FLOWS[flow_name] = flow_func
    
    # Report results
    disabled_count = len(DISABLED_PLUGINS)
    enabled_count = plugin_count - disabled_count
    
    logger.info(f"✨ Auto-registered {len(TASKS)} tasks and {len(FLOWS)} flows from {enabled_count} plugins")
    
    if DISABLED_PLUGINS:
        logger.warning(f"⚠️  {disabled_count} plugin(s) disabled due to missing dependencies: {', '.join(sorted(DISABLED_PLUGINS))}")


# Auto-discover and register on module import
discover_and_register_plugins()
