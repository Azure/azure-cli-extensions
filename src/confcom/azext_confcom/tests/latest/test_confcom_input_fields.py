# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib
import json
import unittest
from unittest.mock import patch

import azext_confcom.config as config

# These tests only exercise --input JSON parsing and rego boilerplate
# serialization, so image platform validation is mocked in _load_policy.
LINUX_IMAGE = "mcr.microsoft.com/azurelinux/distroless/base:3.0"
WINDOWS_IMAGE = "mcr.microsoft.com/windows/nanoserver:ltsc2022"


def _load_policy(
    image,
    platform,
    top_level=None,
    container_props=None,
    prerelease_policy_api=False,
):
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
    security_policy = importlib.import_module("azext_confcom.security_policy")
    with patch.object(security_policy, "validate_image_platform"):
        return security_policy.load_policy_from_json(
            json.dumps(body),
            platform=platform,
            prerelease_policy_api=prerelease_policy_api,
        )


class PolicyVersions(unittest.TestCase):
    def test_linux_defaults_to_deployed_policy_versions(self):
        policy = _load_policy(LINUX_IMAGE, "linux/amd64")
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn('api_version := "0.11.0"', boilerplate)
        self.assertIn('framework_version := "0.2.3"', boilerplate)
        self.assertNotIn("host_network :=", boilerplate)
        self.assertNotIn("load_transparency_trust_list :=", boilerplate)

    def test_linux_prerelease_policy_api_uses_latest_versions(self):
        policy = _load_policy(
            LINUX_IMAGE,
            "linux/amd64",
            prerelease_policy_api=True,
        )
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn('api_version := "0.12.0"', boilerplate)
        self.assertIn('framework_version := "0.5.0"', boilerplate)

    def test_windows_always_uses_latest_versions(self):
        policy = _load_policy(WINDOWS_IMAGE, "windows/amd64")
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn('api_version := "0.12.0"', boilerplate)
        self.assertIn('framework_version := "0.5.0"', boilerplate)

    def test_elastic_san_requires_explicit_prerelease_policy_api(self):
        policy = _load_policy(
            LINUX_IMAGE,
            "linux/amd64",
            container_props={
                config.ACI_FIELD_TEMPLATE_VOLUME_MOUNTS: [
                    {
                        config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE:
                            config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE_ELASTIC_SAN,
                        config.ACI_FIELD_CONTAINERS_MOUNTS_PATH: "/mnt/esan",
                    }
                ]
            },
        )
        with self.assertRaises(SystemExit):
            policy._add_rego_boilerplate("[]")

    def test_elastic_san_uses_prerelease_versions_when_requested(self):
        policy = _load_policy(
            LINUX_IMAGE,
            "linux/amd64",
            container_props={
                config.ACI_FIELD_TEMPLATE_VOLUME_MOUNTS: [
                    {
                        config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE:
                            config.ACI_FIELD_CONTAINERS_MOUNTS_TYPE_ELASTIC_SAN,
                        config.ACI_FIELD_CONTAINERS_MOUNTS_PATH: "/mnt/esan",
                    }
                ]
            },
            prerelease_policy_api=True,
        )
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn('api_version := "0.12.0"', boilerplate)
        self.assertIn('framework_version := "0.5.0"', boilerplate)
        self.assertIn("allow_host_network := true", boilerplate)


class HostNetworkInput(unittest.TestCase):
    # allowHostNetwork is an --input-only field (no ARM property) that must
    # always be emitted, so both the true and default-false cases are checked.
    def test_allow_host_network_true(self):
        policy = _load_policy(
            LINUX_IMAGE, "linux/amd64",
            top_level={config.ACI_FIELD_ALLOW_HOST_NETWORK: True},
            prerelease_policy_api=True,
        )
        self.assertTrue(policy._allow_host_network)
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn("allow_host_network := true", boilerplate)

    def test_allow_host_network_default_false(self):
        policy = _load_policy(LINUX_IMAGE, "linux/amd64")
        self.assertFalse(policy._allow_host_network)
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertNotIn("allow_host_network :=", boilerplate)

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
    # points (Windows-only, --input-only). The list and wiring are always
    # emitted so an undeclared hot-add receives a normal policy denial.
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

    def test_mapped_directories_absent_emits_empty_list_and_wiring(self):
        policy = _load_policy(WINDOWS_IMAGE, "windows/amd64")
        self.assertEqual(policy._mapped_directories, [])
        boilerplate = policy._add_rego_boilerplate("[]")
        self.assertIn("mapped_directories := []", boilerplate)
        self.assertIn(
            "mapped_directory_mount := data.framework.mapped_directory_mount",
            boilerplate,
        )
        self.assertIn(
            "mapped_directory_unmount := data.framework.mapped_directory_unmount",
            boilerplate,
        )

    def test_read_only_defaults_to_false(self):
        policy = _load_policy(
            WINDOWS_IMAGE,
            "windows/amd64",
            top_level={
                config.ACI_FIELD_MAPPED_DIRECTORIES: [
                    {
                        config.ACI_FIELD_MAPPED_DIRECTORIES_CONTAINER_PATH: "C:\\data",
                    }
                ]
            },
        )
        self.assertFalse(
            policy._mapped_directories[0][
                config.POLICY_FIELD_MAPPED_DIRECTORIES_READONLY
            ]
        )

    def test_invalid_mapped_directories_are_rejected(self):
        invalid_values = [
            "not-a-list",
            [None],
            [{}],
            [
                {
                    config.ACI_FIELD_MAPPED_DIRECTORIES_CONTAINER_PATH: "",
                }
            ],
            [
                {
                    config.ACI_FIELD_MAPPED_DIRECTORIES_CONTAINER_PATH: "C:\\data",
                    config.ACI_FIELD_MAPPED_DIRECTORIES_READONLY: "false",
                }
            ],
        ]
        for value in invalid_values:
            with self.subTest(value=value), self.assertRaises(SystemExit):
                _load_policy(
                    WINDOWS_IMAGE,
                    "windows/amd64",
                    top_level={config.ACI_FIELD_MAPPED_DIRECTORIES: value},
                )


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
