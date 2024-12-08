# Copyright (c) 2024 Antonio S. Cofiño
# Licensed under the Mozilla Public License, v. 2.0. See LICENSE file for details.

import logging
import os
from inveniordm_py.client import InvenioAPI

logger = logging.getLogger("zenodo_api")


class ZenodoAPI:
  """
  Custom wrapper for the InvenioRDM API client to handle Zenodo API requests.
  """

  def __init__(self, base_url=None, access_token=None, **kwargs):
    """
    Initialize the ZenodoAPI wrapper.

    Args:
      base_url (str, optional): Base URL of the Zenodo API (defaults to env `ZENODO_BASE_URL`).
      access_token (str, optional): Access token for authentication (defaults to env `ZENODO_ACCESS_TOKEN`).
      **kwargs: Additional parameters to customize the RDMClient.
    """
    self.base_url = base_url or os.getenv('ZENODO_BASE_URL', 'https://zenodo.org/api')
    self.access_token = access_token or os.getenv('ZENODO_ACCESS_TOKEN', None)
    
    if not self.base_url:
      raise ValueError("Base URL for Zenodo API is not defined. Check 'ZENODO_BASE_URL' environment variable.")
    if not self.access_token:
      logger.warning("No access token provided. API access will be limited to public endpoints.")

    try:
      self.client = InvenioAPI(
        self.base_url,
        self.access_token,
      )
    except Exception as e:
      logger.error(f"Failed to initialize RDMClient: {e}", exc_info=True)
      raise e

    logger.info(f"ZenodoAPI initialized with base_url: {self.base_url} and access_token: {'****' if self.access_token else 'None'}")

  def fetch_records(self, community_id, page=1, size=1000):
    """
    Fetch records from a specific Zenodo community.
    
    Args:
      community_id (str): The Zenodo community ID.
      page (int, optional): The page to start from.
      size (int, optional): The number of records to retrieve per page.
    
    Returns:
      list: A list of records from the Zenodo community.
    """
    try:
      response = self.client.get(f"records?communities={community_id}&page={page}&size={size}")
      records = response.get('hits', {}).get('hits', [])
      logger.info(f"Fetched {len(records)} records from community {community_id} (Page {page})")
      return records
    except Exception as e:
      logger.error(f"Error fetching records from community {community_id}: {e}", exc_info=True)
      return []

  def fetch_record(self, record_id):
    """
    Fetch a specific record by ID.
    
    Args:
      record_id (str): The ID of the record.
    
    Returns:
      dict: The JSON response containing the record data, or None if not found.
    """
    try:
      response = self.client.get(f"records/{record_id}")
      logger.info(f"Successfully fetched record {record_id}")
      return response
    except Exception as e:
      logger.error(f"Error fetching record {record_id}: {e}", exc_info=True)
      return None

  def update_record(self, record_id, metadata):
    """
    Update metadata for a specific record.
    
    Args:
      record_id (str): The ID of the record to update.
      metadata (dict): The updated metadata for the record.
    
    Returns:
      dict: The JSON response from the update API call, or None if an error occurs.
    """
    try:
      response = self.client.put(f"records/{record_id}", json=metadata)
      logger.info(f"Record {record_id} updated successfully")
      return response
    except Exception as e:
      logger.error(f"Error updating record {record_id}: {e}", exc_info=True)
      return None

  def publish_record(self, record_id):
    """
    Publish a draft record on Zenodo.
    
    Args:
      record_id (str): The ID of the record to publish.
    
    Returns:
      dict: The JSON response from the publish API call, or None if an error occurs.
    """
    try:
      response = self.client.post(f"records/{record_id}/actions/publish")
      logger.info(f"Record {record_id} published successfully")
      return response
    except Exception as e:
      logger.error(f"Error publishing record {record_id}: {e}", exc_info=True)
      return None

  def delete_record(self, record_id):
    """
    Delete a record.
    
    Args:
      record_id (str): The ID of the record to delete.
    
    Returns:
      dict: The JSON response from the delete API call, or None if an error occurs.
    """
    try:
      response = self.client.delete(f"records/{record_id}")
      logger.info(f"Record {record_id} deleted successfully")
      return response
    except Exception as e:
      logger.error(f"Error deleting record {record_id}: {e}", exc_info=True)
      return None
