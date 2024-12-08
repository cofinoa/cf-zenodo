#!/usr/bin/env python3
"""
Zenodo CLI

Usage:
  zenodo.py fetch [--community-id=<id>] [--output-dir=<dir>] [--dry-run]
  zenodo.py update --record-id=<id> [--output-dir=<dir>]
  zenodo.py publish --record-id=<id> [--dry-run]
  zenodo.py show --record-id=<id> [--output-dir=<dir>]

Options:
  --community-id=<id>    The Zenodo community to fetch records from.
  --output-dir=<dir>     Directory to store records [default: ./records].
  --dry-run              Run the command without making any changes.
  --record-id=<id>       The ID of the record to update, publish, or view.
"""

import sys
import os
import logging

# Dynamically add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.docopt import docopt
from utils.config_utils import initialize_workspace
from utils.zenodo_api import ZenodoAPI

# Initialize environment and configurations
zenodo_config, fetch_settings, metadata_template = initialize_workspace()

# Initialize logging
logger = logging.getLogger("zenodo_cli")
logging.basicConfig(
  level=logging.INFO, 
  format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
  """Main entry point for the CLI."""
  args = docopt(__doc__)

  # Load arguments
  output_dir = args["--output-dir"] or fetch_settings.get("output_dir", "./records")
  community_id = args["--community-id"] or zenodo_config.get("community_id")
  record_id = args["--record-id"]
  dry_run = args["--dry-run"]

  # Instantiate Zenodo API client
  try:
    api_client = ZenodoAPI(
      base_url=zenodo_config.get("base_url"),
      access_token=zenodo_config.get("access_token")
    )
  except Exception as e:
    logger.error(f"Failed to initialize ZenodoAPI: {e}", exc_info=True)
    sys.exit(1)

  try:
    if args["fetch"]:
      if not community_id:
        logger.error("Please specify a community ID with --community-id=<id>")
        sys.exit(1)

      logger.info(f"Fetching records from Zenodo community: {community_id}")
      records = api_client.fetch_records(community_id=community_id, page=1, size=zenodo_config.get("max_records_per_page", 1000))
      
      if not records:
        logger.info(f"No records found for community {community_id}.")
      else:
        logger.info(f"Fetched {len(records)} records from community {community_id}.")

    elif args["update"]:
      if not record_id:
        logger.error("Please specify a record ID with --record-id=<id>")
        sys.exit(1)

      record_path = os.path.join(output_dir, "records", str(record_id), "metadata.json")
      if not os.path.exists(record_path):
        logger.error(f"No metadata file found at {record_path}")
        sys.exit(1)

      with open(record_path, "r") as f:
        metadata = json.load(f)

      logger.info(f"Updating record with ID: {record_id}")
      response = api_client.update_record(record_id=record_id, metadata=metadata)
      if response:
        logger.info(f"Successfully updated record {record_id}")

    elif args["publish"]:
      if not record_id:
        logger.error("Please specify a record ID with --record-id=<id>")
        sys.exit(1)

      if dry_run:
        logger.info(f"[DRY RUN] Would have published record with ID: {record_id}")
      else:
        logger.info(f"Publishing record with ID: {record_id}")
        response = api_client.publish_record(record_id=record_id)
        if response:
          logger.info(f"Successfully published record {record_id}")

    elif args["show"]:
      if not record_id:
        logger.error("Please specify a record ID with --record-id=<id>")
        sys.exit(1)

      logger.info(f"Showing metadata for record with ID: {record_id}")
      response = api_client.fetch_record(record_id=record_id)
      if response:
        logger.info(f"Record {record_id} metadata: {json.dumps(response, indent=2)}")
      else:
        logger.info(f"Record {record_id} not found.")

  except Exception as e:
    logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    sys.exit(1)


if __name__ == "__main__":
  main()
