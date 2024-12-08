#!/usr/bin/env python3

# Copyright (c) 2024 Antonio S. Cofiño
# Licensed under the Mozilla Public License, v. 2.0. See LICENSE file for details.

import sys
import os
import logging

# Dynamically add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config_utils import initialize_workspace
from utils.zenodo_api import ZenodoAPI

# Initialize environment and configurations
zenodo_config, fetch_settings, metadata_template = initialize_workspace()

# Set up logging
logger = logging.getLogger("fetch_records")
logging.basicConfig(
  level=logging.INFO, 
  format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
  """
  Main function to fetch records from Zenodo.
  """
  try:
    # Get configuration details
    community_id = zenodo_config.get("community_id")
    if not community_id:
      logger.error("No community ID provided in the configuration. Please check zenodo_config.json or environment variables.")
      sys.exit(1)
      
    output_dir = fetch_settings.get("output_dir", "./records")
    dry_run = fetch_settings.get("dry_run", False)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Using output directory: {output_dir}")
    
    # Initialize ZenodoAPI
    try:
      api = ZenodoAPI(**zenodo_config)
    except Exception as e:
      logger.error(f"Failed to initialize ZenodoAPI: {e}", exc_info=True)
      sys.exit(1)

    logger.info(f"Starting to fetch records from Zenodo community: {community_id}")
    
    # Call the API to fetch records
    try:
      records = api.fetch_records(community_id=community_id, page=1, size=zenodo_config.get("max_records_per_page", 1000))
      if not records:
        logger.info(f"No records found for community {community_id}.")
      else:
        logger.info(f"Successfully fetched {len(records)} records from community {community_id}.")
    except Exception as e:
      logger.error(f"Error occurred while fetching records: {e}", exc_info=True)
      sys.exit(1)
    
    logger.info("All records have been fetched successfully.")

  except Exception as e:
    logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    sys.exit(1)


if __name__ == "__main__":
  main()
