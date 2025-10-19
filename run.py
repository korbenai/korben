#!/usr/bin/env python3
"""Main entry point for running tasks."""

import warnings
# Suppress pydantic and pydantic_settings warnings from controlflow
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic_settings")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")
warnings.filterwarnings("ignore", message=".*Field.*")
warnings.filterwarnings("ignore", message=".*Config key.*")

import argparse
import sys
from src.core.registry import TASKS


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run tasks from the task registry",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--task",
        type=str,
        help="Name of the task to run"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available tasks"
    )
    
    args = parser.parse_args()
    
    # List tasks if requested
    if args.list:
        print("Available tasks:")
        for task_name in sorted(TASKS.keys()):
            print(f"  - {task_name}")
        return 0
    
    # Require --task if not listing
    if not args.task:
        parser.error("the following arguments are required: --task")
    
    # Run the specified task
    if args.task not in TASKS:
        print(f"Error: Task '{args.task}' not found. Available tasks: {', '.join(sorted(TASKS.keys()))}", file=sys.stderr)
        return 1
    
    try:
        print(f"Running task: {args.task}")
        result = TASKS[args.task]()
        print("\nResult:")
        print(result)
        return 0
    except Exception as e:
        print(f"Error running task '{args.task}': {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
