import requests
import logging
import json

logger = logging.getLogger("zenodo_api")

class ZenodoAPI:
  """
  A class to interact with the Zenodo InvenioRDM API.
  """

  def __init__(self, config):
    """
    Initialize the ZenodoAPI class.
    
    Args:
      config (dict): The configuration dictionary from `zenodo_config.json`.
    """
    try:
      self.base_url = config.get("base_url", "").rstrip('/')
      self.access_token = config.get("access_token", None)
      if not self.base_url:
        raise ValueError("Base URL for Zenodo API is not defined. Please check your configuration.")

      self.headers = {
        "Authorization": f"Bearer {self.access_token}" if self.access_token else "",
        "Content-Type": "application/vnd.inveniordm.v1+json",
        "Accept": "application/vnd.inveniordm.v1+json"
      }
      logger.info(f"ZenodoAPI initialized with base URL: {self.base_url}")
    except Exception as e:
      logger.error(f"Failed to initialize ZenodoAPI: {e}", exc_info=True)
      raise

  def _make_request(self, method, endpoint, **kwargs):
    """
    Make a request to the Zenodo API.
    
    Args:
      method (str): The HTTP method (GET, POST, PUT, DELETE).
      endpoint (str): The endpoint to hit (relative to base_url).
      kwargs: Additional arguments for the requests method.
    
    Returns:
      dict: The JSON response from the API, or None if an error occurs.
    """
    url = f"{self.base_url}/{endpoint.lstrip('/')}"
    try:
      logger.info(f"Making {method} request to: {url} with kwargs: {kwargs}")
      response = requests.request(method, url, headers=self.headers, **kwargs)
      response.raise_for_status()
      
      try:
        response_data = response.json()
        return response_data
      except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from {url}")
        return None

    except requests.exceptions.RequestException as e:
      logger.error(f"Request failed for {url}: {e}", exc_info=True)
      return None

  def fetch_records(self, community_id, page=1, size=1000):
    """
    Fetch records from a Zenodo community.
    
    Args:
      community_id (str): The Zenodo community ID.
      page (int, optional): The page to start from.
      size (int, optional): The number of records per page.
    
    Returns:
      list: A list of records from the Zenodo community.
    """
    params = {"communities": community_id, "page": page, "size": size}
    all_records = []

    while True:
      response = self._make_request("GET", "records", params=params)
      if not response:
        break

      records = response.get("hits", {}).get("hits", [])
      if not records:
        logger.info("No more records to process.")
        break

      all_records.extend(records)
      logger.info(f"Fetched {len(records)} records from page {params['page']}.")
      
      params["page"] += 1

    logger.info(f"Total records fetched: {len(all_records)}")
    return all_records

  def get_record(self, record_id):
    """
    Get a specific record from Zenodo.
    
    Args:
      record_id (str): The ID of the record.
    
    Returns:
      dict: The JSON response containing the record data, or None if not found.
    """
    return self._make_request("GET", f"records/{record_id}")

  def get_versions(self, concept_id):
    """
    Get versions of a specific concept ID.
    
    Args:
      concept_id (str): The concept ID of the record.
    
    Returns:
      dict: The JSON response containing the versions of the record, or None if not found.
    """
    return self._make_request("GET", f"records/{concept_id}/versions")

  def update_record(self, record_id, metadata):
    """
    Update a specific record on Zenodo.
    
    Args:
      record_id (str): The ID of the record to update.
      metadata (dict): The updated metadata for the record.
    
    Returns:
      dict: The JSON response from the update API call, or None if an error occurs.
    """
    endpoint = f"records/{record_id}"
    response = self._make_request("PUT", endpoint, json=metadata)
    if response:
      logger.info(f"Record {record_id} updated successfully.")
    return response

  def publish_record(self, record_id):
    """
    Publish a specific record on Zenodo.
    
    Args:
      record_id (str): The ID of the record to publish.
    
    Returns:
      dict: The JSON response from the publish API call, or None if an error occurs.
    """
    response = self._make_request("POST", f"records/{record_id}/actions/publish")
    if response:
      logger.info(f"Record {record_id} published successfully.")
    return response

  def show_record(self, record_id):
    """
    Show the metadata for a specific record.
    
    Args:
      record_id (str): The ID of the record.
    
    Returns:
      dict: The JSON response for the record, or None if not found.
    """
    return self.get_record(record_id)
