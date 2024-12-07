import os
import json
import logging

logger = logging.getLogger("utils")

# Sensitive fields that should be masked in configuration logs
SENSITIVE_FIELDS = ["access_token", "api_key", "secret_key"]

def load_env_file(env_file=".env"):
  """
  Load environment variables from a .env file.

  Parameters:
    env_file (str): Path to the .env file. Defaults to '.env'.

  Returns:
    None
  """
  if not os.path.exists(env_file):
    logger.warning(f"{env_file} file not found. Skipping environment variable loading.")
    return

  logger.info(f"Loading environment variables from {env_file}")

  with open(env_file, "r") as file:
    for line in file:
      # Strip comments and whitespace
      line = line.strip()
      if not line or line.startswith("#"):
        continue

      # Split key and value
      if "=" in line:
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        # Set as environment variable
        os.environ[key] = value
        logger.info(f"Set environment variable: {key}")

def load_config_with_env(file_path, env_overrides=None):
  """
  Load a configuration file and override values with environment variables.

  Parameters:
    file_path (str): Path to the configuration file.
    env_overrides (dict, optional): Mapping of configuration keys to environment variable names.

  Returns:
    dict: The merged configuration as a dictionary.
  """
  if not os.path.exists(file_path):
    logger.error(f"Configuration file not found: {file_path}")
    raise FileNotFoundError(f"Configuration file not found: {file_path}")

  with open(file_path, "r") as f:
    config = json.load(f)
    logger.info(f"Loaded configuration from {file_path}")

  if env_overrides:
    for key, env_var in env_overrides.items():
      if env_var in os.environ:
        config[key] = os.getenv(env_var)
        logger.info(f"Overriding {key} with environment variable {env_var}")

  return config

def load_zenodo_config(config_path="config/zenodo_config.json"):
  """
  Load and return the Zenodo configuration with optional environment overrides.

  Parameters:
    config_path (str): Path to the Zenodo configuration file.

  Returns:
    dict: The loaded configuration dictionary.
  """
  env_overrides = {
    "base_url": "ZENODO_BASE_URL",
    "access_token": "ZENODO_ACCESS_TOKEN",
    "community_id": "ZENODO_COMMUNITY_ID"
  }
  return load_config_with_env(config_path, env_overrides)

def load_fetch_settings(fetch_path="config/default_settings.json"):
  """
  Load and return the fetch settings.

  Parameters:
    fetch_path (str): Path to the fetch settings file.

  Returns:
    dict: The fetch settings dictionary.
  """
  return load_config_with_env(fetch_path).get("fetch_metadata", {})

def validate_and_warn_config(config, required_keys):
  """
  Validate configuration and log warnings for optional values.

  Parameters:
    config (dict): The configuration dictionary.
    required_keys (list): List of required keys to validate.

  Returns:
    None
  """
  # Validate required keys
  for key in required_keys:
    if key not in config or not config[key]:
      logger.error(f"Missing required configuration key: {key}")
      raise KeyError(f"Missing required configuration key: {key}")
  
  # Log warnings for optional keys
  if not config.get("access_token"):
    logger.warning("No access token provided. Fetching records and metadata from Zenodo will be limited to public information.")

  logger.info("Configuration validated successfully")

def dump_config(config, label="Configuration", sensitive_keys=None):
  """
  Pretty-print the final configuration with sensitive keys masked.

  Parameters:
    config (dict): The configuration dictionary to dump.
    label (str): A label for the configuration dump.
    sensitive_keys (list, optional): Additional keys with sensitive values to mask. 
                                      Defaults to SENSITIVE_FIELDS.

  Returns:
    None
  """
  if sensitive_keys is None:
    sensitive_keys = SENSITIVE_FIELDS

  config = mask_sensitive_data(config, sensitive_keys)
  logger.info(f"{label}:\n{json.dumps(config, indent=2)}")

def mask_sensitive_data(config, sensitive_keys=SENSITIVE_FIELDS):
  """
  Mask sensitive values in the configuration.

  Parameters:
    config (dict): The configuration dictionary to mask.
    sensitive_keys (list): List of keys with sensitive values to mask.

  Returns:
    dict: A new dictionary with sensitive values masked.
  """
  masked_config = config.copy()
  for key in sensitive_keys:
    if key in masked_config and masked_config[key]:
      masked_config[key] = "************"
  return masked_config

def initialize_environment(config_path="config/zenodo_config.json", fetch_path="config/default_settings.json"):
  """
  Simplified function to initialize environment, load configurations, and validate.

  Parameters:
    config_path (str): Path to the Zenodo configuration file.
    fetch_path (str): Path to the default fetch settings file.

  Returns:
    tuple: A tuple containing the Zenodo configuration and fetch settings.
  """
  # Load environment variables
  load_env_file()

  # Load Zenodo configuration and fetch settings
  zenodo_config = load_zenodo_config(config_path)
  fetch_settings = load_fetch_settings(fetch_path)

  # Validate configuration
  validate_and_warn_config(zenodo_config, required_keys=["base_url", "community_id"])

  # Dump configuration for debugging
  dump_config(zenodo_config, "Final Zenodo Configuration")

  return zenodo_config, fetch_settings
