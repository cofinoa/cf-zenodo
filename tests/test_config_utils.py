import os
import unittest
from unittest.mock import patch, mock_open
from utils.config_utils import (
  load_env_file,
  load_config_with_env,
  load_zenodo_config,
  load_fetch_settings,
  validate_and_warn_config,
  mask_sensitive_data,
  dump_config,
  initialize_environment
)

class TestConfigUtils(unittest.TestCase):

  def setUp(self):
    # Create a mock .env file
    self.env_file = ".env.test"
    with open(self.env_file, "w") as file:
      file.write("TEST_KEY=TEST_VALUE\n")
      file.write("ANOTHER_KEY=AnotherValue\n")

    # Mock configurations
    self.mock_config = {
      "base_url": "https://zenodo.org/api",
      "access_token": "test_token",
      "community_id": "cf-community"
    }

    self.mock_fetch_settings = {
      "fetch_metadata": {
        "output_dir": "/tmp/output"
      }
    }

  def tearDown(self):
    # Cleanup the mock .env file
    if os.path.exists(self.env_file):
      os.remove(self.env_file)

  def test_load_env_file(self):
    load_env_file(self.env_file)
    self.assertEqual(os.getenv("TEST_KEY"), "TEST_VALUE")
    self.assertEqual(os.getenv("ANOTHER_KEY"), "AnotherValue")

  @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
  @patch("os.getenv", side_effect=lambda x: {"ENV_KEY": "env_value"}.get(x))
  def test_load_config_with_env(self, mock_getenv, mock_file):
    config = load_config_with_env("mock_config.json", env_overrides={"key": "ENV_KEY"})
    self.assertEqual(config["key"], "env_value")

  @patch("builtins.open", new_callable=mock_open, read_data='{"base_url": "https://zenodo.org/api", "access_token": "test_token", "community_id": "cf-community"}')
  def test_load_zenodo_config(self, mock_file):
    config = load_zenodo_config("mock_config.json")
    self.assertEqual(config["base_url"], "https://zenodo.org/api")
    self.assertEqual(config["access_token"], "test_token")
    self.assertEqual(config["community_id"], "cf-community")

  @patch("builtins.open", new_callable=mock_open, read_data='{"fetch_metadata": {"output_dir": "/tmp/output"}}')
  def test_load_fetch_settings(self, mock_file):
    settings = load_fetch_settings("mock_fetch.json")
    self.assertEqual(settings["output_dir"], "/tmp/output")

  def test_validate_and_warn_config_valid(self):
    with self.assertLogs("utils", level="INFO") as log:
      validate_and_warn_config(self.mock_config, required_keys=["base_url", "community_id"])
      self.assertIn("INFO:utils:Configuration validated successfully", log.output)

  def test_validate_and_warn_config_missing_key(self):
    incomplete_config = {
      "base_url": "https://zenodo.org/api"
    }
    with self.assertRaises(KeyError):
      validate_and_warn_config(incomplete_config, required_keys=["base_url", "community_id"])

  def test_validate_and_warn_config_no_access_token(self):
    config = {
      "base_url": "https://zenodo.org/api",
      "community_id": "cf-community"
    }
    with self.assertLogs("utils", level="WARNING") as log:
      validate_and_warn_config(config, required_keys=["base_url", "community_id"])
      self.assertIn("WARNING:utils:No access token provided", log.output)

  def test_mask_sensitive_data(self):
    sensitive_config = {
      "base_url": "https://zenodo.org/api",
      "access_token": "sensitive_value",
      "api_key": "another_sensitive_value"
    }
    masked = mask_sensitive_data(sensitive_config)
    self.assertEqual(masked["access_token"], "************")
    self.assertEqual(masked["api_key"], "************")
    self.assertEqual(masked["base_url"], "https://zenodo.org/api")

  @patch("utils.config_utils.logger.info")
  def test_dump_config(self, mock_logger_info):
    dump_config(self.mock_config, "Test Config")
    mock_logger_info.assert_any_call('Test Config:\n{\n  "base_url": "https://zenodo.org/api",\n  "access_token": "************",\n  "community_id": "cf-community"\n}')

  @patch("utils.config_utils.load_zenodo_config", return_value={"base_url": "https://zenodo.org/api", "access_token": "test_token", "community_id": "cf-community"})
  @patch("utils.config_utils.load_fetch_settings", return_value={"output_dir": "/tmp/output"})
  @patch("utils.config_utils.validate_and_warn_config")
  @patch("utils.config_utils.dump_config")
  def test_initialize_environment(self, mock_dump, mock_validate, mock_fetch, mock_zenodo):
    config, settings = initialize_environment()
    self.assertEqual(config["base_url"], "https://zenodo.org/api")
    self.assertEqual(settings["output_dir"], "/tmp/output")
    mock_validate.assert_called_once()
    mock_dump.assert_called_once()
