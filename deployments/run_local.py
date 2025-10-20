"""Run podcast workflow locally without Prefect."""

import sys
import os
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.flows.podcasts import podcast_workflow

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


if __name__ == "__main__":
    logger.info("Running podcast workflow locally (no Prefect)")
    result = podcast_workflow()
    logger.info("=" * 70)
    logger.info("WORKFLOW COMPLETE")
    logger.info("=" * 70)
    logger.info(result)

