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
from src.core.registry import TASKS, FLOWS

# Configure logging with a clean, readable format
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',  # Clean format: LEVEL: message
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Optionally set DEBUG level for verbose output
# logging.getLogger().setLevel(logging.DEBUG)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run tasks or flows from the registry",
        formatter_class=argparse.RawDescriptionHelpFormatter
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
        parser.error("one of the following arguments is required: --task, --flow")
    
    if args.task and args.flow:
        parser.error("cannot specify both --task and --flow")
    
    # Run the specified task
    if args.task:
        if args.task not in TASKS:
            print(f"Error: Task '{args.task}' not found. Available tasks: {', '.join(sorted(TASKS.keys()))}", file=sys.stderr)
            return 1
        
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
