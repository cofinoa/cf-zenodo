import sys
import os
import json
import requests
import logging
from collections import OrderedDict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.config_utils import initialize_environment

# Initialize environment and load configurations
zenodo_config, fetch_settings, metadata_template = initialize_environment()

# Get the logger that was initialized in config_utils.py
logger = logging.getLogger("fetch_records")


def create_directories(record_id, output_dir):
    """Create necessary directories for a specific record."""
    paths = {}
    root_path = os.path.join(output_dir, "records")
    paths['record_path'] = os.path.join(root_path, str(record_id))
    os.makedirs(paths['record_path'], exist_ok=True)
    return paths


def extract_metadata_from_template(data, template):
    """
    Recursively extract metadata from the given data using the provided template.
    The output maintains the same order as the template.
    """
    if isinstance(template, bool):  # If template specifies True, return the data
        return data if template else None

    if isinstance(template, dict) and isinstance(data, dict):
        extracted = OrderedDict()
        for key, sub_template in template.items():
            if key in data:
                extracted_value = extract_metadata_from_template(data[key], sub_template)
                if extracted_value is not None:
                    extracted[key] = extracted_value
        return extracted

    if isinstance(template, list) and isinstance(data, list) and len(template) > 0:
        return [extract_metadata_from_template(item, template[0]) for item in data]

    return None


def save_metadata(record_path, metadata, file_name="metadata.json"):
    """Save metadata for a record."""
    metadata_path = os.path.join(record_path, file_name)
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved {file_name} to {metadata_path}")


def fetch_records(community_id, base_url, access_token, output_dir, template, dry_run=False):
    """Fetch all records and versions from a Zenodo community."""
    headers = {
        "Authorization": f"Bearer {access_token}" if access_token else "",
        "Content-Type": "application/vnd.inveniordm.v1+json",
        "Accept": "application/vnd.inveniordm.v1+json"
    }
    params = {"communities": community_id, "size": 1000, "page": 1}
    stats = {"total_records": 0}

    while True:
        try:
            request_url = f"{base_url.rstrip('/')}/records"
            logger.info(f"Making GET request to: {request_url} with params: {params}")
            
            response = requests.get(request_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching records from Zenodo: {e}", exc_info=True)
            break

        records = data.get("hits", {}).get("hits", [])
        if not records:
            logger.info("No more records to process.")
            break

        for record in records:
            record_id = record["id"]
            title = record.get("metadata", {}).get("title", "No Title")
            logger.info(f"Fetching record: {record_id} - {title}")

            # Create the necessary directories for this record
            paths = create_directories(record_id, output_dir)
            
            # Save full zenodo metadata to zenodo.json
            save_metadata(paths['record_path'], record, file_name="zenodo.json")

            # Extract and save filtered metadata based on the template
            extracted_metadata = extract_metadata_from_template(record, template)
            save_metadata(paths['record_path'], extracted_metadata, file_name="metadata.json")

            stats["total_records"] += 1

        params["page"] += 1

    log_summary_statistics(stats)


def log_summary_statistics(stats):
    """Log summary statistics for the fetch operation."""
    logger.info("=== Summary Statistics ===")
    logger.info(f"Total Records Processed: {stats['total_records']}")


if __name__ == "__main__":
    try:
        community_id = zenodo_config["community_id"]
        base_url = zenodo_config["base_url"]
        access_token = zenodo_config.get("access_token")
        output_dir = fetch_settings["output_dir"]
        dry_run = fetch_settings.get("dry_run", False)

        logger.info(f"Fetching records from Zenodo community: {community_id}")
        fetch_records(community_id, base_url, access_token, output_dir, metadata_template, dry_run)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        exit(1)
