# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest

import azext_confcom.config as config
from azext_confcom.security_policy import load_policy_from_json

# These images are never pulled: the tests only exercise --input JSON parsing
# and rego boilerplate serialization, neither of which needs image content.
LINUX_IMAGE = "mcr.microsoft.com/azurelinux/distroless/base:3.0"
WINDOWS_IMAGE = "mcr.microsoft.com/windows/nanoserver:ltsc2022"


def _load_policy(image, platform, top_level=None, container_props=None):
    properties = {
        config.ACI_FIELD_TEMPLATE_IMAGE: image,
        config.ACI_FIELD_TEMPLATE_ENVS: [],
        config.ACI_FIELD_TEMPLATE_COMMAND: ["echo", "hello"],
    }
    if container_props:
        properties.update(container_props)
    body = {
        config.ACI_FIELD_VERSION: "1.0",
        config.ACI_FIELD_CONTAINERS: [
            {
                config.ACI_FIELD_CONTAINERS_NAME: "test-container",
                config.ACI_FIELD_TEMPLATE_PROPERTIES: properties,
            }
        ],
    }
    if top_level:
        body.update(top_level)
    return load_policy_from_json(json.dumps(body), platform=platform)


class HostNetworkInput(unittest.TestCase):
    # allowHostNetwork is an --input-only field (no ARM property) that must
    # always be emitted, so both the true and default-false cases are checked.
    def test_allow_host_network_true(self):
        policy = _load_policy(
            LINUX_IMAGE, "linux/amd64",
            top_level={config.ACI_FIELD_ALLOW_HOST_NETWORK: True},
        )
        self.assertTrue(policy._allow_host_network)
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn("allow_host_network := true", boilerplate)

    def test_allow_host_network_default_false(self):
        policy = _load_policy(LINUX_IMAGE, "linux/amd64")
        self.assertFalse(policy._allow_host_network)
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn("allow_host_network := false", boilerplate)

    def test_allow_host_network_windows(self):
        policy = _load_policy(
            WINDOWS_IMAGE, "windows/amd64",
            top_level={config.ACI_FIELD_ALLOW_HOST_NETWORK: True},
        )
        self.assertTrue(policy._allow_host_network)
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn("allow_host_network := true", boilerplate)


class SignalsInput(unittest.TestCase):
    def test_container_signals_default_to_kill_and_term(self):
        policy = _load_policy(LINUX_IMAGE, "linux/amd64")
        self.assertEqual(policy.get_images()[0]._signals, [9, 15])

    def test_pause_container_signals_default_to_kill_and_term(self):
        self.assertEqual(
            config.DEFAULT_CONTAINERS[0][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_SIGNAL_CONTAINER_PROCESSES
            ],
            [9, 15],
        )


class WindowsPolicyWiring(unittest.TestCase):
    def test_scratch_mount_and_unmount_are_wired(self):
        policy = _load_policy(WINDOWS_IMAGE, "windows/amd64")
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn("scratch_mount := data.framework.scratch_mount", boilerplate)
        self.assertIn("scratch_unmount := data.framework.scratch_unmount", boilerplate)


class RegistryChangesDroppingInput(unittest.TestCase):
    # allowRegistryChangesDropping is Windows-only and --input-only.
    def test_allow_registry_changes_dropping_true(self):
        policy = _load_policy(
            WINDOWS_IMAGE, "windows/amd64",
            top_level={config.ACI_FIELD_ALLOW_REGISTRY_CHANGES_DROPPING: True},
        )
        self.assertTrue(policy._allow_registry_changes_dropping)
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn("allow_registry_changes_dropping := true", boilerplate)

    def test_allow_registry_changes_dropping_default_false(self):
        policy = _load_policy(WINDOWS_IMAGE, "windows/amd64")
        self.assertFalse(policy._allow_registry_changes_dropping)
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn("allow_registry_changes_dropping := false", boilerplate)


class RegistryChangesInput(unittest.TestCase):
    # Per-container registryChanges is Windows-only and --input-only, emitted
    # only when supplied.
    registry_changes = {
        "add_values": [
            {
                "key": {"hive": "HKLM", "name": "Software\\Contoso"},
                "name": "Setting",
                "type": "String",
                "string_value": "on",
            }
        ],
        "delete_keys": [],
    }

    def test_registry_changes_parsed(self):
        policy = _load_policy(
            WINDOWS_IMAGE, "windows/amd64",
            container_props={config.ACI_FIELD_CONTAINERS_REGISTRY_CHANGES: self.registry_changes},
        )
        self.assertEqual(policy.get_images()[0]._registry_changes, self.registry_changes)

    def test_registry_changes_absent(self):
        policy = _load_policy(WINDOWS_IMAGE, "windows/amd64")
        self.assertIsNone(policy.get_images()[0]._registry_changes)


class MappedDirectoriesInput(unittest.TestCase):
    # mappedDirectories backs the mapped_directory_mount/unmount enforcement
    # points (Windows-only, --input-only). The list and wiring are emitted
    # together and only when the list is non-empty.
    mapped_directories = [
        {
            config.ACI_FIELD_MAPPED_DIRECTORIES_CONTAINER_PATH: "C:\\data",
            config.ACI_FIELD_MAPPED_DIRECTORIES_READONLY: True,
        }
    ]

    def test_mapped_directories_parsed_and_wired(self):
        policy = _load_policy(
            WINDOWS_IMAGE, "windows/amd64",
            top_level={config.ACI_FIELD_MAPPED_DIRECTORIES: self.mapped_directories},
        )
        self.assertEqual(len(policy._mapped_directories), 1)
        entry = policy._mapped_directories[0]
        self.assertEqual(entry[config.POLICY_FIELD_MAPPED_DIRECTORIES_CONTAINER_PATH], "C:\\data")
        self.assertTrue(entry[config.POLICY_FIELD_MAPPED_DIRECTORIES_READONLY])

        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn("mapped_directories := ", boilerplate)
        self.assertIn("mapped_directory_mount := data.framework.mapped_directory_mount", boilerplate)
        self.assertIn("mapped_directory_unmount := data.framework.mapped_directory_unmount", boilerplate)

    def test_mapped_directories_absent_no_wiring(self):
        policy = _load_policy(WINDOWS_IMAGE, "windows/amd64")
        self.assertEqual(policy._mapped_directories, [])
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertNotIn("mapped_directories := ", boilerplate)
        self.assertNotIn("mapped_directory_mount", boilerplate)
        self.assertNotIn("mapped_directory_unmount", boilerplate)


class AllowedLogProvidersInput(unittest.TestCase):
    # allowedLogProviders is Windows-only and --input-only.
    def test_allowed_log_providers_parsed_and_emitted(self):
        providers = ["provider-a", "provider-b"]
        policy = _load_policy(
            WINDOWS_IMAGE, "windows/amd64",
            top_level={config.ACI_FIELD_ALLOWED_LOG_PROVIDERS: providers},
        )
        self.assertEqual(policy._allowed_log_providers, providers)
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn("provider-a", boilerplate)
        self.assertIn("provider-b", boilerplate)


if __name__ == "__main__":
    unittest.main()
