import sys
import os
import json
import requests
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.config_utils import initialize_environment

# Initialize environment and load configurations
zenodo_config, fetch_settings = initialize_environment()

# Get the logger that was initialized in config_utils.py
logger = logging.getLogger("fetch_records")


def create_directories(record_id, output_dir):
  """Create necessary directories for a specific version of a record."""
  paths = {}

  # Add the /records directory at the root
  root_path = os.path.join(output_dir, "records")
  paths['record_path'] = os.path.join(root_path, str(record_id))
  paths['files_path'] = os.path.join(paths['record_path'], "files")

  os.makedirs(paths['record_path'], exist_ok=True)
  os.makedirs(paths['files_path'], exist_ok=True)

  return paths


def split_zenodo_metadata(record_path, record_data):
  """Split the Zenodo JSON record into metadata, files, and main zenodo.json."""
  # Remove unwanted sections from the Zenodo data
  sections_to_remove = ['ui', 'swh', 'media_files', 'custom_fields']
  for section in sections_to_remove:
    if section in record_data:
      del record_data[section]
      logger.info(f"Removed section '{section}' from zenodo.json")

  # Extract and save metadata.json
  metadata = record_data.pop('metadata', None)
  if metadata:
    metadata_path = os.path.join(record_path, 'metadata.json')
    with open(metadata_path, 'w') as f:
      json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata.json to {metadata_path}")

  # Extract and save files.json
  files = record_data.pop('files', None)
  if files:
    files_path = os.path.join(record_path, 'files.json')
    with open(files_path, 'w') as f:
      json.dump(files, f, indent=2)
    logger.info(f"Saved files.json to {files_path}")

  # Update zenodo.json with references to metadata and files
  record_data['metadata'] = 'include:metadata.json'
  record_data['files'] = 'include:files.json'

  # Save zenodo.json
  zenodo_path = os.path.join(record_path, 'zenodo.json')
  with open(zenodo_path, 'w') as f:
    json.dump(record_data, f, indent=2)
  logger.info(f"Saved zenodo.json to {zenodo_path}")


def fetch_records(community_id, base_url, access_token, output_dir, dry_run=False):
  """Fetch all records and versions from a Zenodo community."""
  headers = {
    "Authorization": f"Bearer {access_token}" if access_token else "",
    "Content-Type": "application/vnd.inveniordm.v1+json",
    "Accept": "application/vnd.inveniordm.v1+json"
  }
  params = {"communities": community_id, "size": 1000, "page": 1}
  all_records = []

  stats = {"total_records": 0, "total_versions": 0, "total_files": 0}

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
      title = record["metadata"]["title"]
      logger.info(f"Fetching record: {record_id} - {title}")

      paths = create_directories(record_id, output_dir)
      split_zenodo_metadata(paths['record_path'], record)
      stats = fetch_versions(record_id, base_url, headers, output_dir, stats, dry_run)

      stats["total_records"] += 1

    params["page"] += 1

  log_summary_statistics(stats)
  return all_records


def fetch_versions(concept_id, base_url, headers, output_dir, stats, dry_run=False):
  """Fetch all versions for a specific concept ID."""
  try:
    request_url = f"{base_url.rstrip('/')}/records/{concept_id}/versions"
    logger.info(f"Fetching versions from URL: {request_url}")
    
    response = requests.get(request_url, headers=headers)
    response.raise_for_status()
    data = response.json()
  except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching versions for concept ID {concept_id}: {e}", exc_info=True)
    return stats

  versions = data.get("hits", {}).get("hits", [])
  if not versions:
    logger.info(f"No versions available for concept ID {concept_id}.")
    return stats

  for version in versions:
    version_id = version.get("id")
    version_number = version.get("metadata", {}).get("version", "unknown_version")
    logger.info(f"  Fetching version: {version_number} (ID: {version_id})")

    paths = create_directories(version_id, output_dir)
    split_zenodo_metadata(paths['record_path'], version)
    stats["total_versions"] += 1

    if not dry_run:
      stats = fetch_version_files(version_id, paths['files_path'], stats, headers, base_url)

  return stats


def fetch_version_files(version_id, path, stats, headers, base_url):
  """Download files for a specific version."""
  try:
    request_url = f"{base_url.rstrip('/')}/records/{version_id}"
    response = requests.get(request_url, headers=headers)
    response.raise_for_status()
    version_data = response.json()
  except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching files for version ID {version_id}: {e}", exc_info=True)
    return stats

  files = version_data.get("files", {}).get("entries", {})
  for _, file_info in files.items():
    file_name = file_info["key"]
    file_url = file_info["links"]["self"]

    logger.info(f"    Downloading file: {file_name}")
    try:
      response = requests.get(file_url, stream=True)
      response.raise_for_status()
      with open(os.path.join(path, file_name), "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
          file.write(chunk)
      stats["total_files"] += 1
    except requests.exceptions.RequestException as e:
      logger.error(f"    Error downloading file {file_name}: {e}", exc_info=True)
  return stats


def log_summary_statistics(stats):
  """Log summary statistics for the fetch operation."""
  logger.info("=== Summary Statistics ===")
  logger.info(f"Total Records Processed: {stats['total_records']}")
  logger.info(f"Total Versions Processed: {stats['total_versions']}")
  logger.info(f"Total Files Downloaded: {stats['total_files']}")


if __name__ == "__main__":
  try:
    community_id = zenodo_config["community_id"]
    base_url = zenodo_config["base_url"]
    access_token = zenodo_config.get("access_token")
    output_dir = fetch_settings["output_dir"]
    dry_run = fetch_settings.get("dry_run", False)

    logger.info(f"Fetching records from Zenodo community: {community_id}")
    records = fetch_records(community_id, base_url, access_token, output_dir, dry_run)
    logger.info(f"Fetched {len(records)} records.")
  except Exception as e:
    logger.error(f"An error occurred: {e}", exc_info=True)
    exit(1)
