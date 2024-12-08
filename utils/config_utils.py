# Copyright (c) 2024 Antonio S. Cofiño
# Licensed under the Mozilla Public License, v. 2.0. See LICENSE file for details.

import os
import json
import logging

logger = logging.getLogger("utils")

# Sensitive fields that should be masked in configuration logs
SENSITIVE_FIELDS = ["access_token", "api_key", "secret_key"]

def load_env_file(env_file=".env"):
    """Load environment variables from a .env file."""
    if not os.path.exists(env_file):
        logger.warning(f"{env_file} file not found. Skipping environment variable loading.")
        return

    logger.info(f"Loading environment variables from {env_file}")
    with open(env_file, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                os.environ[key] = value
                logger.info(f"Set environment variable: {key}")


def load_config_with_env(file_path, env_overrides=None):
    """Load a configuration file and override values with environment variables."""
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
    """Load and return the Zenodo configuration with optional environment overrides."""
    env_overrides = {
        "base_url": "ZENODO_BASE_URL",
        "access_token": "ZENODO_ACCESS_TOKEN",
        "community_id": "ZENODO_COMMUNITY_ID"
    }
    return load_config_with_env(config_path, env_overrides)


def load_fetch_settings(fetch_path="config/default_settings.json"):
    """Load and return the fetch settings."""
    return load_config_with_env(fetch_path).get("fetch_metadata", {})


def validate_and_warn_config(config, required_keys):
    """Validate configuration and log warnings for optional values."""
    for key in required_keys:
        if key not in config or not config[key]:
            logger.error(f"Missing required configuration key: {key}")
            raise KeyError(f"Missing required configuration key: {key}")
    
    if not config.get("access_token"):
        logger.warning("No access token provided. Fetching records and metadata from Zenodo will be limited to public information.")

    logger.info("Configuration validated successfully")


def dump_config(config, label="Configuration", sensitive_keys=None):
    """Pretty-print the final configuration with sensitive keys masked."""
    if sensitive_keys is None:
        sensitive_keys = SENSITIVE_FIELDS

    config = mask_sensitive_data(config, sensitive_keys)
    logger.info(f"{label}:\n{json.dumps(config, indent=2)}")


def mask_sensitive_data(config, sensitive_keys=SENSITIVE_FIELDS):
    """Mask sensitive values in the configuration."""
    masked_config = config.copy()
    for key in sensitive_keys:
        if key in masked_config and masked_config[key]:
            masked_config[key] = "************"
    return masked_config


def load_metadata_template(template_path):
    """Load the metadata template from the template path."""
    if not os.path.exists(template_path):
        logger.error(f"Metadata template file not found: {template_path}")
        raise FileNotFoundError(f"Metadata template file not found: {template_path}")

    with open(template_path, "r") as f:
        template = json.load(f)
        logger.info(f"Loaded metadata template from {template_path}")
    return template


def initialize_workspace(config_path="config/zenodo_config.json", fetch_path="config/default_settings.json"):
    """Initialize the workspace, load environment variables, load configurations, and validate."""
    # Load environment variables
    load_env_file()

    # Load Zenodo configuration and fetch settings
    zenodo_config = load_zenodo_config(config_path)
    fetch_settings = load_fetch_settings(fetch_path)

    # Validate configuration
    validate_and_warn_config(zenodo_config, required_keys=["base_url", "community_id"])

    # Create log directory if it does not exist
    log_file_path = fetch_settings.get("log_file", "./logs/fetch_records.log")
    log_dir = os.path.dirname(log_file_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        logger.info(f"Log directory created or already exists: {log_dir}")

    # Set up logging handlers
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path, mode='a'),
            logging.StreamHandler()
        ]
    )

    # Load metadata template
    template_path = fetch_settings.get("template_path", "config/metadata_template.json")
    metadata_template = load_metadata_template(template_path)

    # Dump configuration for debugging
    dump_config(zenodo_config, "Final Zenodo Configuration")

    return zenodo_config, fetch_settings, metadata_template
