import sys
import os
import json
import requests
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.config_utils import initialize_environment

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("fetch_records")


def create_directories(base_dir, concept_id, version=None):
    """Create necessary directories for records and versions."""
    concept_path = os.path.join(str(base_dir), str(concept_id))
    os.makedirs(concept_path, exist_ok=True)

    # Create files/ directory for non-versioned records
    if version is None:
        files_path = os.path.join(concept_path, "files")
        os.makedirs(files_path, exist_ok=True)
        return concept_path, files_path
    else:
        # Create versions/{version}/ directory for versioned records
        version_path = os.path.join(concept_path, "versions", str(version))
        os.makedirs(version_path, exist_ok=True)
        return concept_path, version_path


def fetch_records(community_id, base_url, access_token, output_dir, dry_run=False):
    """Fetch all records and versions from a Zenodo community."""
    headers = {
        "Authorization": f"Bearer {access_token}" if access_token else "",
        "Content-Type": "application/vnd.inveniordm.v1+json"
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
            concept_id = record["conceptrecid"]
            title = record["metadata"]["title"]
            logger.info(f"Fetching record: {concept_id} (Record ID: {record_id}) - {title}")

            concept_path, files_path = create_directories(output_dir, concept_id)
            save_record_metadata(concept_path, record)
            stats = fetch_versions(record_id, base_url, headers, concept_path, files_path, stats, dry_run)

            stats["total_records"] += 1

        params["page"] += 1

    log_summary_statistics(stats)

    return all_records


def fetch_versions(record_id, base_url, headers, concept_path, files_path, stats, dry_run=False):
    """Fetch all versions for a specific record ID."""
    try:
        request_url = f"{base_url.rstrip('/')}/records/{record_id}/versions"
        logger.info(f"Fetching versions from URL: {request_url}")
        
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching versions for record ID {record_id}: {e}", exc_info=True)
        return stats

    versions = data.get("hits", {}).get("hits", [])
    if not versions:
        logger.info(f"No versions available for record ID {record_id}.")
        stats = fetch_version_files(record_id, files_path, stats, headers, base_url)
        return stats

    for version in versions:
        version_id = version.get("id")
        version_number = version.get("metadata", {}).get("version", "unknown_version")
        logger.info(f"  Fetching version: {version_number} (ID: {version_id})")

        _, version_path = create_directories(concept_path, record_id, version_number)
        save_version_metadata(version_path, version)
        stats["total_versions"] += 1

        if not dry_run:
            stats = fetch_version_files(version_id, version_path, stats, headers, base_url)

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

    files = version_data.get("files", [])
    for file_info in files:
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


def save_record_metadata(concept_path, record):
    """Save metadata for a record."""
    metadata_path = os.path.join(concept_path, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(record, f, indent=4)


def save_version_metadata(version_path, version):
    """Save metadata for a version."""
    metadata_path = os.path.join(version_path, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(version, f, indent=2)


def log_summary_statistics(stats):
    """Log summary statistics for the fetch operation."""
    logger.info("=== Summary Statistics ===")
    logger.info(f"Total Records Processed: {stats['total_records']}")
    logger.info(f"Total Versions Processed: {stats['total_versions']}")
    logger.info(f"Total Files Downloaded: {stats['total_files']}")


if __name__ == "__main__":
    try:
        zenodo_config, fetch_settings = initialize_environment()

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
