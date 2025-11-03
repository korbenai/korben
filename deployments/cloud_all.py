"""Universal deployment script for all Korben workflows."""

import sys
import os
import logging
import argparse
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prefect import flow

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


# Flow configurations
FLOW_CONFIGS = {
    "podcasts": {
        "module": "src.plugins.podcasts.flows",
        "function": "process_podcasts_workflow",
        "tags": ["podcasts", "automation", "daily"],
        "parameters": {},
        "schedule": {
            "cron": "0 6 * * *",  # Daily at 6am CT
            "timezone": "America/Chicago"
        },
        "description": "Download, transcribe, and extract wisdom from podcasts"
    },
    "mallory": {
        "module": "src.plugins.mallory.flows",
        "function": "mallory_trending_stories_workflow",
        "tags": ["security", "mallory", "daily"],
        "parameters": {},
        "schedule": {
            "cron": "0 6 * * *",  # Daily at 6am CT
            "timezone": "America/Chicago"
        },
        "description": "Fetch and email cybersecurity news"
    },
    "movies": {
        "module": "src.plugins.movies.flows",
        "function": "trending_movies_workflow",
        "tags": ["movies", "entertainment", "weekly"],
        "parameters": {
            "genres": "sci-fi,action,thriller",
            "min_rating": 7.0,
        },
        "schedule": {
            "cron": "0 6 * * 5",  # Fridays at 6am CT
            "timezone": "America/Chicago"
        },
        "description": "Discover and email trending movies"
    },
    "arxiv": {
        "module": "src.plugins.arxiv.flows",
        "function": "arxiv_search_workflow",
        "tags": ["research", "arxiv", "weekly"],
        "parameters": {
            "query": "cat:cs.AI OR cat:cs.LG",
            "max_results": 10,
            "sort_by": "submittedDate",
        },
        "schedule": {
            "cron": "0 6 * * 1",  # Mondays at 6am CT
            "timezone": "America/Chicago"
        },
        "description": "Search and email arXiv research papers"
    },
    "linear": {
        "module": "src.plugins.linear.flows",
        "function": "linear_status_report_workflow",
        "tags": ["linear", "tickets", "daily"],
        "parameters": {},
        "schedule": {
            "cron": "0 6 * * *",  # Daily at 6am CT
            "timezone": "America/Chicago"
        },
        "description": "Generate and email Linear status report"
    },
}


def deploy_flow(
    flow_name: str,
    deployment_name: str = "default",
    schedule_cron: Optional[str] = None,
    timezone: Optional[str] = None,
    work_pool: str = "default-pool",
    use_flow_schedule: bool = True,
) -> str:
    """
    Deploy a single flow to Prefect Cloud.
    
    Args:
        flow_name: Name of the flow (must be in FLOW_CONFIGS)
        deployment_name: Name for the deployment (default: "default")
        schedule_cron: Cron schedule string (overrides flow config if provided)
        timezone: Timezone for schedule (overrides flow config if provided)
        work_pool: Work pool name (default: "default-pool")
        use_flow_schedule: Use the schedule from flow config (default: True)
    
    Returns:
        Deployment ID
    """
    if flow_name not in FLOW_CONFIGS:
        raise ValueError(f"Unknown flow: {flow_name}. Available: {list(FLOW_CONFIGS.keys())}")
    
    config = FLOW_CONFIGS[flow_name]
    
    # Determine schedule to use: CLI args override flow config
    if schedule_cron is not None:
        # Explicit schedule from CLI
        final_cron = schedule_cron
        final_timezone = timezone or "America/Chicago"
    elif use_flow_schedule and "schedule" in config:
        # Use flow's configured schedule
        final_cron = config["schedule"]["cron"]
        final_timezone = config["schedule"]["timezone"]
    else:
        # No schedule
        final_cron = None
        final_timezone = None
    
    logger.info("=" * 70)
    logger.info(f"DEPLOYING {flow_name.upper()} TO PREFECT CLOUD")
    logger.info(f"Description: {config['description']}")
    logger.info("=" * 70)
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Find the project's Python interpreter (venv or system)
    venv_python = os.path.join(project_root, ".venv", "bin", "python")
    if os.path.exists(venv_python):
        python_path = venv_python
        logger.info(f"Using venv Python: {python_path}")
    else:
        # Use current Python interpreter
        python_path = sys.executable
        logger.info(f"Using system Python: {python_path}")
    
    # Deploy using the modern Prefect API with source location
    from prefect.client.schemas.schedules import CronSchedule as ClientCronSchedule
    
    # Build the entrypoint path - this tells Prefect where to find the flow
    # The flows are already @cf.flow decorated, Prefect will load them directly
    entrypoint = f"{config['module'].replace('.', '/')}.py:{config['function']}"
    
    logger.info(f"Entrypoint: {entrypoint}")
    
    # Create a flow reference from source
    flow_ref = flow.from_source(
        source=project_root,
        entrypoint=entrypoint,
    )
    
    # Build the deployment configuration with job variables to use correct Python
    deploy_kwargs = {
        "name": deployment_name,
        "work_pool_name": work_pool,
        "tags": config["tags"],
        "parameters": config["parameters"],
        # Use default work queue; worker must be attached to this pool/queue
        "work_queue_name": "default",
        # Ensure code is loaded from the project root on the worker
        # "pull_steps": [
        #     {
        #         "prefect.deployments.steps.set_working_directory": {
        #             "directory": project_root
        #         }
        #     }
        # ],
        # Provide environment only; let the worker manage the process command
        "job_variables": {
            "working_dir": project_root,
            "env": {
                "PYTHONPATH": project_root,
            }
        },
    }
    
    # Add schedule if provided
    if final_cron:
        schedule = ClientCronSchedule(
            cron=final_cron,
            timezone=final_timezone
        )
        deploy_kwargs["schedules"] = [schedule]
    
    # Deploy the flow
    deployment_id = flow_ref.deploy(**deploy_kwargs)
    
    logger.info("=" * 70)
    logger.info("✓ DEPLOYMENT SUCCESSFUL")
    logger.info("=" * 70)
    logger.info(f"Deployment ID: {deployment_id}")
    logger.info(f"Name: {flow_name}-workflow/{deployment_name}")
    if final_cron:
        logger.info(f"Schedule: {final_cron} ({final_timezone})")
    else:
        logger.info("Schedule: No schedule (manual trigger only)")
    logger.info(f"Work Pool: {work_pool}")
    logger.info("=" * 70)
    
    return deployment_id


def deploy_all_flows(
    deployment_name: str = "default",
    schedule_cron: Optional[str] = None,
    timezone: Optional[str] = None,
    work_pool: str = "default-pool",
    use_flow_schedules: bool = True,
):
    """Deploy all configured flows."""
    logger.info("=" * 70)
    logger.info("DEPLOYING ALL KORBEN WORKFLOWS")
    logger.info("=" * 70)
    logger.info(f"Flows to deploy: {', '.join(FLOW_CONFIGS.keys())}")
    if schedule_cron:
        logger.info(f"Schedule override: {schedule_cron} ({timezone})")
    elif use_flow_schedules:
        logger.info("Using each flow's configured schedule")
    else:
        logger.info("No schedules (manual trigger only)")
    logger.info("=" * 70)
    logger.info("")
    
    deployed = []
    failed = []
    
    for flow_name in FLOW_CONFIGS.keys():
        try:
            deploy_flow(
                flow_name=flow_name,
                deployment_name=deployment_name,
                schedule_cron=schedule_cron,
                timezone=timezone,
                work_pool=work_pool,
                use_flow_schedule=use_flow_schedules,
            )
            deployed.append(flow_name)
            logger.info("")
        except Exception as e:
            logger.error(f"Failed to deploy {flow_name}: {e}")
            failed.append(flow_name)
            logger.info("")
    
    # Summary
    logger.info("=" * 70)
    logger.info("DEPLOYMENT SUMMARY")
    logger.info("=" * 70)
    logger.info(f"✓ Successfully deployed: {len(deployed)}/{len(FLOW_CONFIGS)}")
    for name in deployed:
        config = FLOW_CONFIGS[name]
        sched_info = ""
        if schedule_cron:
            sched_info = f" [{schedule_cron}]"
        elif use_flow_schedules and "schedule" in config:
            sched_info = f" [{config['schedule']['cron']}]"
        logger.info(f"  ✓ {name}-workflow/{deployment_name}{sched_info}")
    
    if failed:
        logger.error(f"✗ Failed: {len(failed)}")
        for name in failed:
            logger.error(f"  ✗ {name}")
    
    logger.info("=" * 70)
    logger.info("\nNext steps:")
    logger.info("1. Start a worker in your environment:")
    logger.info(f"   prefect worker start --pool {work_pool}")
    logger.info("\n2. Trigger a run manually:")
    logger.info("   prefect deployment run '{flow-name}-workflow/default'")
    logger.info("\n3. View in Prefect Cloud UI:")
    logger.info("   https://app.prefect.cloud")
    logger.info("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Deploy Korben workflows to Prefect Cloud",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy all flows with their configured schedules (default)
  python cloud_all.py
  # - podcasts: daily at 6am CT
  # - mallory: daily at 6am CT
  # - linear: daily at 6am CT
  # - movies: Fridays at 6am CT
  # - arxiv: Mondays at 6am CT
  
  # Deploy specific flow with its configured schedule
  python cloud_all.py --flow movies
  
  # Override all schedules (deploy all at 8am PT)
  python cloud_all.py --schedule "0 8 * * *" --timezone "America/Los_Angeles"
  
  # Deploy without any schedules (manual trigger only)
  python cloud_all.py --no-schedule
  
  # Deploy to different work pool
  python cloud_all.py --work-pool gpu-pool

Available flows: """ + ", ".join(FLOW_CONFIGS.keys())
    )
    
    parser.add_argument(
        "--flow",
        choices=list(FLOW_CONFIGS.keys()),
        help="Deploy specific flow (default: deploy all)"
    )
    parser.add_argument(
        "--deployment-name",
        default="default",
        help="Deployment name (default: default)"
    )
    parser.add_argument(
        "--schedule",
        help="Cron schedule override (overrides flow configs, e.g., '0 6 * * *')"
    )
    parser.add_argument(
        "--timezone",
        help="Timezone for schedule override (e.g., America/Chicago)"
    )
    parser.add_argument(
        "--work-pool",
        default="default-pool",
        help="Work pool name (default: default-pool)"
    )
    parser.add_argument(
        "--no-schedule",
        action="store_true",
        help="Deploy without any schedule (manual trigger only)"
    )
    
    args = parser.parse_args()
    
    # Handle schedule logic
    if args.no_schedule:
        # No schedule at all
        schedule_cron = None
        use_flow_schedules = False
    else:
        # Use provided schedule or None to use flow configs
        schedule_cron = args.schedule if args.schedule else None
        use_flow_schedules = True
    
    if args.flow:
        # Deploy single flow
        deploy_flow(
            flow_name=args.flow,
            deployment_name=args.deployment_name,
            schedule_cron=schedule_cron,
            timezone=args.timezone,
            work_pool=args.work_pool,
            use_flow_schedule=use_flow_schedules,
        )
    else:
        # Deploy all flows
        deploy_all_flows(
            deployment_name=args.deployment_name,
            schedule_cron=schedule_cron,
            timezone=args.timezone,
            work_pool=args.work_pool,
            use_flow_schedules=use_flow_schedules,
        )

