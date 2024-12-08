#!/usr/bin/env python3
import sys
import os
import logging
from utils.config_utils import initialize_environment
from utils.zenodo_api import ZenodoAPI

# Initialize environment and configurations
zenodo_config, fetch_settings, metadata_template = initialize_environment()

# Set up logging
logger = logging.getLogger("fetch_records")

def main():
  """
  Main function to fetch records from Zenodo.
  """
  try:
    community_id = zenodo_config.get("community_id")
    output_dir = fetch_settings.get("output_dir", "./records")
    dry_run = fetch_settings.get("dry_run", False)
    
    # Initialize ZenodoAPI
    api = ZenodoAPI()

    logger.info(f"Starting to fetch records from Zenodo community: {community_id}")
    
    # Call the API to fetch records
    api.fetch_records(community_id=community_id, output_dir=output_dir, dry_run=dry_run)
    
    logger.info("All records have been fetched successfully.")

  except Exception as e:
    logger.error(f"An error occurred: {e}", exc_info=True)
    sys.exit(1)


if __name__ == "__main__":
  main()
