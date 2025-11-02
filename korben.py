#!/usr/bin/env python3
"""Main entry point for running tasks and flows."""

import warnings
# Suppress pydantic and pydantic_settings warnings from controlflow
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic_settings")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")
warnings.filterwarnings("ignore", message=".*Field.*")
warnings.filterwarnings("ignore", message=".*Config key.*")

import argparse
import sys
import logging
import inspect
import os
from pathlib import Path
from src.core.registry import TASKS, FLOWS

# Configure logging with a clean, readable format
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',  # Clean format: LEVEL: message
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Optionally set DEBUG level for verbose output
# logging.getLogger().setLevel(logging.DEBUG)


def show_help(name, func, is_flow=False):
    """
    Show detailed help for a specific task or flow.
    
    Args:
        name: Name of the task/flow
        func: The callable function
        is_flow: True if this is a flow, False if task
    """
    entity_type = "Flow" if is_flow else "Task"
    
    print("=" * 70)
    print(f"{entity_type.upper()}: {name}")
    print("=" * 70)
    
    # Show docstring
    if func.__doc__:
        print("\n" + inspect.cleandoc(func.__doc__))
    else:
        print(f"\nNo documentation available for {name}")
    
    # Try to find and show config variables
    plugin_name = _guess_plugin_name(func)
    if plugin_name:
        config_example = _load_config_example(plugin_name)
        if config_example:
            print("\n" + "-" * 70)
            print("CONFIGURATION (from config.yml.example)")
            print("-" * 70)
            
            variables = config_example.get('variables', {})
            if variables:
                print("\nAvailable variables:")
                for key, value in variables.items():
                    print(f"  {key}: {value}")
            
            print(f"\nConfig file: src/core/plugins/{plugin_name}/config.yml")
            print(f"Setup: cp src/core/plugins/{plugin_name}/config.yml.example \\")
            print(f"          src/core/plugins/{plugin_name}/config.yml")
    
    # Show usage example
    print("\n" + "-" * 70)
    print("USAGE")
    print("-" * 70)
    entity = "flow" if is_flow else "task"
    print(f"\nRun with defaults:")
    print(f"  pdm run python3 ./korben.py --{entity} {name}")
    
    if plugin_name and config_example:
        print(f"\nRun with custom parameters:")
        print(f"  pdm run python3 ./korben.py --{entity} {name} --param value")
    
    print("\n" + "=" * 70)


def _guess_plugin_name(func):
    """Guess plugin name from function module path."""
    module = func.__module__
    if 'plugins' in module:
        parts = module.split('.')
        try:
            plugin_idx = parts.index('plugins')
            if len(parts) > plugin_idx + 1:
                return parts[plugin_idx + 1]
        except (ValueError, IndexError):
            pass
    return None


def _load_config_example(plugin_name):
    """Load config.yml.example for a plugin if it exists."""
    try:
        import yaml
        config_path = Path(__file__).parent / 'src' / 'core' / 'plugins' / plugin_name / 'config.yml.example'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
    except Exception:
        pass
    return None


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run tasks or flows from the registry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # Disable auto-help to handle --help for tasks/flows
    )
    
    parser.add_argument(
        "--task",
        type=str,
        help="Name of the task to run"
    )
    
    parser.add_argument(
        "--flow",
        type=str,
        help="Name of the flow to run"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available tasks and flows"
    )
    
    parser.add_argument(
        "-h", "--help",
        action="store_true",
        help="Show help for a task/flow (use: --task NAME --help)"
    )
    
    # Parse known args and keep the rest as kwargs
    args, unknown = parser.parse_known_args()
    
    # Convert unknown args to kwargs
    kwargs = {}
    i = 0
    while i < len(unknown):
        if unknown[i].startswith('--'):
            key = unknown[i][2:]  # Remove --
            if i + 1 < len(unknown) and not unknown[i + 1].startswith('--'):
                kwargs[key] = unknown[i + 1]
                i += 2
            else:
                kwargs[key] = True
                i += 1
        else:
            i += 1
    
    # Show general help if no task/flow specified
    if args.help and not args.task and not args.flow:
        print("Korben - Hackable Personal Automation Framework")
        print("\nUsage:")
        print("  pdm run python3 ./korben.py --list                    # List all tasks and flows")
        print("  pdm run python3 ./korben.py --task NAME               # Run a task")
        print("  pdm run python3 ./korben.py --flow NAME               # Run a flow")
        print("  pdm run python3 ./korben.py --task NAME --help        # Show task help")
        print("  pdm run python3 ./korben.py --flow NAME --help        # Show flow help")
        print("\nExamples:")
        print("  pdm run python3 ./korben.py --flow trending_ai_books --help")
        print("  pdm run python3 ./korben.py --task search_books --query 'AI' --limit 10")
        return 0
    
    # List tasks and flows if requested
    if args.list:
        print("Available tasks:")
        for task_name in sorted(TASKS.keys()):
            print(f"  - {task_name}")
        print("\nAvailable flows:")
        for flow_name in sorted(FLOWS.keys()):
            print(f"  - {flow_name}")
        return 0
    
    # Check that exactly one of --task or --flow is provided
    if not args.task and not args.flow:
        parser.print_help()
        return 0
    
    if args.task and args.flow:
        parser.error("cannot specify both --task and --flow")
    
    # Run the specified task
    if args.task:
        if args.task not in TASKS:
            print(f"Error: Task '{args.task}' not found. Available tasks: {', '.join(sorted(TASKS.keys()))}", file=sys.stderr)
            return 1
        
        # Show help if --help flag present
        if args.help or kwargs.get('help'):
            show_help(args.task, TASKS[args.task], is_flow=False)
            return 0
        
        try:
            print(f"Running task: {args.task}")
            result = TASKS[args.task](**kwargs)
            print("\nResult:")
            print(result)
            return 0
        except Exception as e:
            print(f"Error running task '{args.task}': {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    # Run the specified flow
    if args.flow:
        if args.flow not in FLOWS:
            print(f"Error: Flow '{args.flow}' not found. Available flows: {', '.join(sorted(FLOWS.keys()))}", file=sys.stderr)
            return 1
        
        # Show help if --help flag present
        if args.help or kwargs.get('help'):
            show_help(args.flow, FLOWS[args.flow], is_flow=True)
            return 0
        
        try:
            print(f"Running flow: {args.flow}")
            result = FLOWS[args.flow](**kwargs)
            print("\nResult:")
            print(result)
            return 0
        except Exception as e:
            print(f"Error running flow '{args.flow}': {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    sys.exit(main())
