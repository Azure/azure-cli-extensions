# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import patch

from azure.cli.core.azclierror import RequiredArgumentMissingError

from azext_k8s_extension.partner_extensions.DataProtectionKubernetes import DataProtectionKubernetes


class TestDataProtectionKubernetesConfigMapping(unittest.TestCase):
    def setUp(self):
        self.ext = DataProtectionKubernetes()
        # Access the private method via name mangling
        self._validate = self.ext._DataProtectionKubernetes__validate_and_map_config

    def _make_bsl_settings(self):
        return {
            "blobContainer": "mycontainer",
            "storageAccount": "myaccount",
            "storageAccountResourceGroup": "myrg",
            "storageAccountSubscriptionId": "mysub",
        }

    # ------------------------------------------------------------------
    # Short-name mapping tests
    # ------------------------------------------------------------------

    def test_short_names_mapped_to_full_paths(self):
        config = self._make_bsl_settings()
        self._validate(config)
        self.assertIn("configuration.backupStorageLocation.bucket", config)
        self.assertIn("configuration.backupStorageLocation.config.storageAccount", config)
        self.assertIn("configuration.backupStorageLocation.config.resourceGroup", config)
        self.assertIn("configuration.backupStorageLocation.config.subscriptionId", config)

    def test_cpu_and_memory_limit_short_names(self):
        config = {**self._make_bsl_settings(), "cpuLimit": "500m", "memoryLimit": "256Mi"}
        self._validate(config)
        self.assertEqual(config.get("resources.limits.cpu"), "500m")
        self.assertEqual(config.get("resources.limits.memory"), "256Mi")

    def test_cpu_and_memory_request_short_names(self):
        config = {**self._make_bsl_settings(), "cpuRequest": "100m", "memoryRequest": "128Mi"}
        self._validate(config)
        self.assertEqual(config.get("resources.requests.cpu"), "100m")
        self.assertEqual(config.get("resources.requests.memory"), "128Mi")

    # ------------------------------------------------------------------
    # Controller resource settings
    # ------------------------------------------------------------------

    def test_controller_cpu_limit_short_name(self):
        config = {**self._make_bsl_settings(), "controllerCpuLimit": "1"}
        self._validate(config)
        self.assertEqual(config.get("controller.resources.limits.cpu"), "1")

    def test_controller_memory_limit_short_name(self):
        config = {**self._make_bsl_settings(), "controllerMemoryLimit": "512Mi"}
        self._validate(config)
        self.assertEqual(config.get("controller.resources.limits.memory"), "512Mi")

    def test_controller_cpu_request_short_name(self):
        config = {**self._make_bsl_settings(), "controllerCpuRequest": "200m"}
        self._validate(config)
        self.assertEqual(config.get("controller.resources.requests.cpu"), "200m")

    def test_controller_memory_request_short_name(self):
        config = {**self._make_bsl_settings(), "controllerMemoryRequest": "256Mi"}
        self._validate(config)
        self.assertEqual(config.get("controller.resources.requests.memory"), "256Mi")

    # ------------------------------------------------------------------
    # initContainers.veleroPluginForMicrosoftAzure resource settings
    # ------------------------------------------------------------------

    def test_plugin_cpu_limit_short_name(self):
        config = {**self._make_bsl_settings(), "pluginCpuLimit": "1"}
        self._validate(config)
        self.assertEqual(
            config.get("initContainers.veleroPluginForMicrosoftAzure.resources.limits.cpu"), "1"
        )

    def test_plugin_memory_limit_short_name(self):
        config = {**self._make_bsl_settings(), "pluginMemoryLimit": "512Mi"}
        self._validate(config)
        self.assertEqual(
            config.get("initContainers.veleroPluginForMicrosoftAzure.resources.limits.memory"), "512Mi"
        )

    def test_plugin_cpu_request_short_name(self):
        config = {**self._make_bsl_settings(), "pluginCpuRequest": "100m"}
        self._validate(config)
        self.assertEqual(
            config.get("initContainers.veleroPluginForMicrosoftAzure.resources.requests.cpu"), "100m"
        )

    def test_plugin_memory_request_short_name(self):
        config = {**self._make_bsl_settings(), "pluginMemoryRequest": "128Mi"}
        self._validate(config)
        self.assertEqual(
            config.get("initContainers.veleroPluginForMicrosoftAzure.resources.requests.memory"), "128Mi"
        )

    # ------------------------------------------------------------------
    # Full-path pass-through tests
    # ------------------------------------------------------------------

    def test_full_path_memory_limit_passes_through(self):
        config = {**self._make_bsl_settings(), "resources.limits.memory": "512Mi"}
        self._validate(config)
        self.assertEqual(config.get("resources.limits.memory"), "512Mi")

    def test_full_path_cpu_limit_passes_through(self):
        config = {**self._make_bsl_settings(), "resources.limits.cpu": "500m"}
        self._validate(config)
        self.assertEqual(config.get("resources.limits.cpu"), "500m")

    def test_full_path_controller_cpu_limit_passes_through(self):
        config = {**self._make_bsl_settings(), "controller.resources.limits.cpu": "1"}
        self._validate(config)
        self.assertEqual(config.get("controller.resources.limits.cpu"), "1")

    def test_full_path_controller_memory_limit_passes_through(self):
        config = {**self._make_bsl_settings(), "controller.resources.limits.memory": "512Mi"}
        self._validate(config)
        self.assertEqual(config.get("controller.resources.limits.memory"), "512Mi")

    def test_full_path_plugin_cpu_limit_passes_through(self):
        config = {
            **self._make_bsl_settings(),
            "initContainers.veleroPluginForMicrosoftAzure.resources.limits.cpu": "1",
        }
        self._validate(config)
        self.assertEqual(
            config.get("initContainers.veleroPluginForMicrosoftAzure.resources.limits.cpu"), "1"
        )

    def test_full_path_plugin_memory_limit_passes_through(self):
        config = {
            **self._make_bsl_settings(),
            "initContainers.veleroPluginForMicrosoftAzure.resources.limits.memory": "512Mi",
        }
        self._validate(config)
        self.assertEqual(
            config.get("initContainers.veleroPluginForMicrosoftAzure.resources.limits.memory"), "512Mi"
        )

    def test_full_path_strips_whitespace(self):
        config = {**self._make_bsl_settings(), "resources.limits.memory": "  256Mi  "}
        self._validate(config)
        self.assertEqual(config.get("resources.limits.memory"), "256Mi")

    def test_full_path_case_insensitive(self):
        config = {**self._make_bsl_settings(), "Resources.Limits.Memory": "512Mi"}
        self._validate(config)
        self.assertEqual(config.get("resources.limits.memory"), "512Mi")

    # ------------------------------------------------------------------
    # Unrecognized keys are ignored
    # ------------------------------------------------------------------

    def test_unrecognized_key_is_ignored(self):
        config = {**self._make_bsl_settings(), "unknownSetting": "value"}
        self._validate(config)
        self.assertNotIn("unknownSetting", config)

    # ------------------------------------------------------------------
    # BSL validation
    # ------------------------------------------------------------------

    def test_missing_bsl_key_raises_error(self):
        config = {
            "storageAccount": "myaccount",
            "storageAccountResourceGroup": "myrg",
            "storageAccountSubscriptionId": "mysub",
            # missing blobContainer
        }
        with self.assertRaises(RequiredArgumentMissingError):
            self._validate(config)

    def test_bsl_validation_skipped_when_disabled(self):
        # Should not raise even with missing BSL settings
        config = {"controllerCpuLimit": "1"}
        self._validate(config, validate_bsl=False)
        self.assertEqual(config.get("controller.resources.limits.cpu"), "1")

    # ------------------------------------------------------------------
    # Case-insensitive short name matching
    # ------------------------------------------------------------------

    def test_short_name_case_insensitive(self):
        config = {**self._make_bsl_settings(), "CONTROLLERCPULIMIT": "500m"}
        self._validate(config)
        self.assertEqual(config.get("controller.resources.limits.cpu"), "500m")


if __name__ == "__main__":
    unittest.main()
