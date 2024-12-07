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
from utils.docopt import docopt
from utils.config_utils import initialize_environment
from utils.zenodo_api import ZenodoAPI

# Initialize environment and configurations
zenodo_config, fetch_settings, metadata_template = initialize_environment()

# Initialize logging
logger = logging.getLogger("zenodo_cli")


def main():
  """Main entry point for the CLI."""
  args = docopt(__doc__)

  # Load arguments
  output_dir = args["--output-dir"] or fetch_settings.get("output_dir", "./records")
  community_id = args["--community-id"] or zenodo_config.get("community_id")
  record_id = args["--record-id"]
  dry_run = args["--dry-run"]

  # Instantiate Zenodo API client
  api_client = ZenodoAPI()

  try:
    if args["fetch"]:
      if not community_id:
        logger.error("Please specify a community ID with --community-id=<id>")
        sys.exit(1)

      logger.info(f"Fetching records from Zenodo community: {community_id}")
      api_client.fetch_records(community_id=community_id, output_dir=output_dir, dry_run=dry_run)

    elif args["update"]:
      if not record_id:
        logger.error("Please specify a record ID with --record-id=<id>")
        sys.exit(1)

      logger.info(f"Updating record with ID: {record_id}")
      api_client.update_record(record_id=record_id, output_dir=output_dir)

    elif args["publish"]:
      if not record_id:
        logger.error("Please specify a record ID with --record-id=<id>")
        sys.exit(1)

      logger.info(f"Publishing record with ID: {record_id}")
      api_client.publish_record(record_id=record_id, dry_run=dry_run)

    elif args["show"]:
      if not record_id:
        logger.error("Please specify a record ID with --record-id=<id>")
        sys.exit(1)

      logger.info(f"Showing metadata for record with ID: {record_id}")
      api_client.show_record(record_id=record_id, output_dir=output_dir)

  except Exception as e:
    logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    sys.exit(1)


if __name__ == "__main__":
  main()
