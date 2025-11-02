"""Deploy podcast workflow to Prefect Cloud."""

import sys
import os
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prefect import flow
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from src.plugins.podcasts.flows import podcast_workflow

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@flow(name="podcasts-workflow", log_prints=True)
def podcast_flow_prefect(**kwargs):
    """
    Prefect-wrapped ControlFlow flow for podcasts.
    
    This flow is registered with Prefect Cloud for orchestration,
    while maintaining ControlFlow's AI agent capabilities.
    """
    logger.info("Starting Prefect-wrapped podcast workflow")
    result = podcast_workflow(**kwargs)
    logger.info("Podcast workflow completed")
    return result


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("DEPLOYING TO PREFECT CLOUD")
    logger.info("=" * 70)
    
    # Build deployment
    deployment = Deployment.build_from_flow(
        flow=podcast_flow_prefect,
        name="daily-podcasts",
        work_pool_name="default-pool",
        tags=["podcasts", "automation", "daily"],
        schedule=CronSchedule(
            cron="0 6 * * *",  # Daily at 6am
            timezone="America/Los_Angeles"
        ),
        parameters={},  # Can override via Prefect Cloud UI
    )
    
    # Push to Prefect Cloud
    deployment_id = deployment.apply()
    
    logger.info("=" * 70)
    logger.info("✓ DEPLOYMENT SUCCESSFUL")
    logger.info("=" * 70)
    logger.info(f"Deployment ID: {deployment_id}")
    logger.info(f"Name: podcasts-workflow/daily-podcasts")
    logger.info(f"Schedule: Daily at 6:00 AM PST")
    logger.info("=" * 70)
    logger.info("\nNext steps:")
    logger.info("1. Start a worker in your environment:")
    logger.info("   prefect worker start --pool default-pool")
    logger.info("\n2. Trigger a run manually:")
    logger.info("   prefect deployment run 'podcasts-workflow/daily-podcasts'")
    logger.info("\n3. View in Prefect Cloud UI:")
    logger.info("   https://app.prefect.cloud")
    logger.info("=" * 70)

