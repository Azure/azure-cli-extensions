# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib
import json
import unittest
import unittest.mock
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


class ExecProcessCommands(unittest.TestCase):
    def _image(self, platform, processes):
        policy = _load_policy(
            WINDOWS_IMAGE if platform.startswith("windows") else LINUX_IMAGE,
            platform,
            container_props={config.ACI_FIELD_CONTAINERS_EXEC_PROCESSES: processes},
        )
        return policy.get_images()[0]

    def test_linux_exec_commands_remain_argv(self):
        processes = [{"command": ["/bin/sh", "-c", 'test -f "/healthy"'], "signals": []}]
        image = self._image("linux/amd64", processes)
        self.assertEqual(image.get_policy_json()["exec_processes"], processes)

    def test_windows_exec_command_matches_sidecar_input(self):
        processes = [{
            "command": ["cmd", "/c", "if exist C:\\healthy (exit /b 0) else (exit /b 1)"],
            "signals": [],
        }]
        image = self._image("windows/amd64", processes)
        self.assertEqual(image.get_policy_json()["exec_processes"], processes + [{
            "command": ['cmd /c "if exist C:\\healthy (exit /b 0) else (exit /b 1)"'],
            "signals": [],
        }])
        self.assertEqual(image.get_policy_json()["command"], ["echo", "hello"])

    def test_windows_exec_command_quoting(self):
        cases = [
            (["cmd.exe"], "cmd.exe"),
            (["cmd", "/c", "cd"], "cmd /c cd"),
            (["tool.exe", ""], 'tool.exe ""'),
            (["tool.exe", "two words"], 'tool.exe "two words"'),
            (["tool.exe", "tab\tvalue"], 'tool.exe "tab\tvalue"'),
            (["tool.exe", 'say "hello"'], r'tool.exe "say \"hello\""'),
            (["tool.exe", 'a"b'], r'tool.exe a\"b'),
            (["tool.exe", "C:\\Program Files\\data\\"], 'tool.exe "C:\\Program Files\\data\\\\"'),
            (["C:\\Program Files\\tool.exe", "plain"], '"C:\\Program Files\\tool.exe" plain'),
        ]
        for command, expected in cases:
            with self.subTest(command=command):
                image = self._image("windows/amd64", [{"command": command, "signals": []}])
                expected_processes = [{"command": command, "signals": []}]
                if command != [expected]:
                    expected_processes.append({"command": [expected], "signals": []})
                self.assertEqual(image.get_policy_json()["exec_processes"], expected_processes)

    def test_windows_exec_serialization_preserves_source_and_deduplicates(self):
        processes = [
            {"command": ["cmd", "/c", "echo hello"], "signals": []},
            {"command": ["cmd", "/c", "echo hello"], "signals": []},
            {"command": ["cmd", "/c", "echo hello"], "signals": [9]},
        ]
        image = self._image("windows/amd64", processes)
        expected = [
            {"command": ["cmd", "/c", "echo hello"], "signals": []},
            {"command": ['cmd /c "echo hello"'], "signals": []},
            {"command": ["cmd", "/c", "echo hello"], "signals": [9]},
            {"command": ['cmd /c "echo hello"'], "signals": [9]},
        ]
        self.assertEqual(image.get_policy_json()["exec_processes"], expected)
        self.assertEqual(image.get_policy_json()["exec_processes"], expected)
        self.assertEqual(image._exec_processes, processes)

    def test_windows_exec_command_requires_all_arguments(self):
        image = self._image("windows/amd64", [{"command": ["ls", "abc"], "signals": []}])
        commands = [process["command"] for process in image.get_policy_json()["exec_processes"]]
        self.assertEqual(commands, [["ls", "abc"], ["ls abc"]])
        self.assertNotIn(["ls"], commands)

    def test_empty_exec_processes_unchanged(self):
        for platform in ("linux/amd64", "windows/amd64"):
            with self.subTest(platform=platform):
                self.assertEqual(self._image(platform, []).get_policy_json()["exec_processes"], [])

    def test_arm_probes_use_platform_command_representation(self):
        security_policy = importlib.import_module("azext_confcom.security_policy")
        command = ["ping", "127.0.0.1"]
        for platform, image, expected in (
            ("linux/amd64", LINUX_IMAGE, [command]),
            ("windows/amd64", WINDOWS_IMAGE, [command, ["ping 127.0.0.1"]]),
        ):
            for probe in ("readinessProbe", "livenessProbe"):
                with self.subTest(platform=platform, probe=probe):
                    template = {
                        "resources": [{
                            "type": "Microsoft.ContainerInstance/containerGroups",
                            "name": "test-group",
                            "properties": {"containers": [{
                                "name": "test-container",
                                "properties": {"image": image, probe: {"exec": {"command": command}}},
                            }]},
                        }],
                    }
                    with patch.object(security_policy, "validate_image_platform"):
                        policy = security_policy.load_policy_from_arm_template_str(
                            json.dumps(template), "", platform=platform,
                        )[0]
                    self.assertEqual(
                        policy.get_images()[0].get_policy_json()["exec_processes"],
                        [{"command": value, "signals": []} for value in expected],
                    )

    def test_vn2_probes_and_lifecycle_hooks_use_platform_command_representation(self):
        security_policy = importlib.import_module("azext_confcom.security_policy")
        command = ["ping", "127.0.0.1"]
        for platform, image, expected in (
            ("linux/amd64", LINUX_IMAGE, [command]),
            ("windows/amd64", WINDOWS_IMAGE, [command, ["ping 127.0.0.1"]]),
        ):
            for hook in ("livenessProbe", "readinessProbe", "startupProbe", "postStart", "preStop"):
                with self.subTest(platform=platform, hook=hook):
                    container = {"name": "test-container", "image": image}
                    if hook in ("postStart", "preStop"):
                        container["lifecycle"] = {hook: {"exec": {"command": command}}}
                    else:
                        container[hook] = {"exec": {"command": command}}
                    pod = {
                        "apiVersion": "v1",
                        "kind": "Pod",
                        "metadata": {"name": "test-pod"},
                        "spec": {"containers": [container]},
                    }
                    with patch.object(security_policy, "validate_image_platform"):
                        policy = security_policy.load_policy_from_virtual_node_yaml_str(
                            json.dumps(pod), platform=platform,
                        )[0]
                    self.assertEqual(
                        policy.get_images()[0].get_policy_json()["exec_processes"],
                        [{"command": value, "signals": []} for value in expected],
                    )


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


class InfrastructureFragment(unittest.TestCase):
    # The default infrastructure fragment feed depends on the target platform.
    # Linux containers use the CLCOW fragment. Windows containers emit no default
    # fragment unless --prerelease-policy-api is set, in which case they use the
    # CWCOW fragment (and Windows VN2 uses its own CWCOW VN2 fragment).
    def test_linux_emits_clcow_fragment(self):
        policy = _load_policy(LINUX_IMAGE, "linux/amd64")
        self.assertEqual(
            policy.get_fragments()[0]["feed"],
            "mcr.microsoft.com/aci/aci-cc-infra-fragment",
        )

    def test_windows_emits_no_default_fragment(self):
        policy = _load_policy(WINDOWS_IMAGE, "windows/amd64")
        self.assertEqual(policy.get_fragments(), [])

    def test_windows_emits_cwcow_fragment(self):
        policy = _load_policy(
            WINDOWS_IMAGE, "windows/amd64", prerelease_policy_api=True
        )
        self.assertEqual(
            policy.get_fragments()[0]["feed"],
            "mcr.microsoft.com/aci/aci-cwcow-infra-fragment",
        )

    def test_default_fragment_feeds_per_platform(self):
        self.assertEqual(
            config.get_default_rego_fragments("linux/amd64")[0]["feed"],
            "mcr.microsoft.com/aci/aci-cc-infra-fragment",
        )
        self.assertEqual(
            config.get_default_rego_fragments("linux/amd64", is_vn2=True)[0]["feed"],
            "mcr.microsoft.com/aci/aci-cc-infra-fragment",
        )
        # By default Windows emits no infrastructure fragment; VN2 relies on the
        # mount-host image-attached fragment and non-VN2 has none.
        self.assertEqual(
            config.get_default_rego_fragments("windows/amd64"),
            [],
        )
        self.assertEqual(
            config.get_default_rego_fragments("windows/amd64", is_vn2=True)[0]["feed"],
            "mcr.microsoft.com/aci/virtual-node-2-mount-host-windows-2025",
        )
        # With --prerelease-policy-api the Windows infrastructure fragments are emitted.
        self.assertEqual(
            config.get_default_rego_fragments(
                "windows/amd64", prerelease_policy_api=True
            )[0]["feed"],
            "mcr.microsoft.com/aci/aci-cwcow-infra-fragment",
        )
        self.assertEqual(
            config.get_default_rego_fragments(
                "windows/amd64", is_vn2=True, prerelease_policy_api=True
            )[0]["feed"],
            "mcr.microsoft.com/aci/aci-cwcow-vn2-infra-fragment",
        )


class UserInput(unittest.TestCase):
    # Windows containers run as a named account rather than a numeric UID, so the
    # account name must flow into the policy user pattern. It is honored only from
    # authored --input policies (securityContext.windowsOptions.runAsUserName); the
    # --virtual-node-yaml path (from_input=False) drops it because ACI does not carry
    # the Windows account name. Linux keeps its integer-only behavior.
    def _extract_user(self, platform, security_context, from_input=False):
        from azext_confcom.container import extract_user
        return extract_user({
            "platform": platform,
            config.ACI_FIELD_CONTAINERS_SECURITY_CONTEXT: security_context,
        }, from_input=from_input)

    def _idname(self, user):
        return user[config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_USER_IDNAME]

    def test_windows_run_as_username_from_windows_options(self):
        user = self._extract_user(
            "windows/amd64",
            {
                config.ACI_FIELD_CONTAINERS_WINDOWS_OPTIONS: {
                    config.ACI_FIELD_CONTAINERS_RUN_AS_USERNAME: "ContainerAdministrator",
                }
            },
            from_input=True,
        )
        self.assertEqual(
            self._idname(user),
            {
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_PATTERN: "ContainerAdministrator",
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_STRATEGY: "name",
            },
        )

    def test_windows_run_as_username_ignored_for_virtual_node_yaml(self):
        # The --virtual-node-yaml path must not plumb the Windows account name: ACI
        # drops it there, so honoring it would mismatch the runtime user. Falls back
        # to the empty user.
        user = self._extract_user(
            "windows/amd64",
            {
                config.ACI_FIELD_CONTAINERS_WINDOWS_OPTIONS: {
                    config.ACI_FIELD_CONTAINERS_RUN_AS_USERNAME: "ContainerAdministrator",
                }
            },
            from_input=False,
        )
        self.assertEqual(
            self._idname(user),
            {
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_PATTERN: "",
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_STRATEGY: "any",
            },
        )

    def test_windows_string_run_as_user_rejected(self):
        # ACI securityContext.runAsUser is numeric only, so a string is rejected on
        # Windows too; the named account comes from windowsOptions.runAsUserName.
        with self.assertRaises(SystemExit):
            self._extract_user(
                "windows/amd64",
                {config.ACI_FIELD_CONTAINERS_RUN_AS_USER: "ContainerAdministrator"},
            )

    def test_windows_defaults_to_empty_user_when_unset(self):
        user = self._extract_user("windows/amd64", {})
        self.assertEqual(
            self._idname(user),
            {
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_PATTERN: "",
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_STRATEGY: "any",
            },
        )

    def test_linux_numeric_run_as_user_unchanged(self):
        user = self._extract_user(
            "linux/amd64",
            {config.ACI_FIELD_CONTAINERS_RUN_AS_USER: 1000},
        )
        self.assertEqual(
            self._idname(user),
            {
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_PATTERN: "1000",
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_STRATEGY: "id",
            },
        )

    def test_linux_string_run_as_user_still_rejected(self):
        with self.assertRaises(SystemExit):
            self._extract_user(
                "linux/amd64",
                {config.ACI_FIELD_CONTAINERS_RUN_AS_USER: "ContainerAdministrator"},
            )

    def test_linux_ignores_windows_options_run_as_username(self):
        user = self._extract_user(
            "linux/amd64",
            {
                config.ACI_FIELD_CONTAINERS_WINDOWS_OPTIONS: {
                    config.ACI_FIELD_CONTAINERS_RUN_AS_USERNAME: "ContainerAdministrator",
                }
            },
            from_input=True,
        )
        self.assertEqual(
            self._idname(user),
            {
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_PATTERN: "",
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER_STRATEGY: "any",
            },
        )


class Vn2JsonInfrastructureFragment(unittest.TestCase):
    # "scenario": "vn2" in --input JSON must select the VN2 default fragments.
    def _feeds(self, platform, prerelease_policy_api=False):
        policy = _load_policy(
            WINDOWS_IMAGE if platform.startswith("windows") else LINUX_IMAGE,
            platform,
            top_level={config.ACI_FIELD_SCENARIO: config.VN2},
            prerelease_policy_api=prerelease_policy_api,
        )
        return [fragment["feed"] for fragment in policy.get_fragments()]

    def test_windows_vn2_emits_mount_host_fragment(self):
        self.assertEqual(
            self._feeds("windows/amd64"),
            ["mcr.microsoft.com/aci/virtual-node-2-mount-host-windows-2025"],
        )

    def test_windows_vn2_prerelease_emits_vn2_infra_fragment(self):
        self.assertEqual(
            self._feeds("windows/amd64", prerelease_policy_api=True),
            ["mcr.microsoft.com/aci/aci-cwcow-vn2-infra-fragment"],
        )

    def test_linux_vn2_unchanged(self):
        self.assertEqual(
            self._feeds("linux/amd64"),
            ["mcr.microsoft.com/aci/aci-cc-infra-fragment"],
        )


class ImageLoaderInfrastructureFragment(unittest.TestCase):
    # --image goes through load_policy_from_image_name, which must use the
    # platform-specific default fragments rather than the static Linux default.
    def _load(self, platform, prerelease_policy_api=False):
        security_policy = importlib.import_module("azext_confcom.security_policy")
        with patch.object(security_policy, "validate_image_platform"):
            return security_policy.load_policy_from_image_name(
                WINDOWS_IMAGE if platform.startswith("windows") else LINUX_IMAGE,
                platform=platform,
                prerelease_policy_api=prerelease_policy_api,
            )

    def test_linux_emits_clcow_fragment(self):
        self.assertEqual(
            self._load("linux/amd64").get_fragments()[0]["feed"],
            "mcr.microsoft.com/aci/aci-cc-infra-fragment",
        )

    def test_windows_emits_no_default_fragment(self):
        self.assertEqual(self._load("windows/amd64").get_fragments(), [])

    def test_windows_prerelease_emits_cwcow_fragment(self):
        self.assertEqual(
            self._load("windows/amd64", prerelease_policy_api=True).get_fragments()[0]["feed"],
            "mcr.microsoft.com/aci/aci-cwcow-infra-fragment",
        )


class InfrastructureSvn(unittest.TestCase):
    def _load(self, input_format, platform, is_vn2=False, prerelease=False,
              exclude_defaults=False, include_custom=True):
        security_policy = importlib.import_module("azext_confcom.security_policy")
        image = WINDOWS_IMAGE if platform.startswith("windows") else LINUX_IMAGE
        custom_import = {
            "issuer": "custom-issuer", "feed": "custom-feed", "minimum_svn": "3", "includes": ["containers"],
        }
        imports = [custom_import] if include_custom else []
        container = {"name": "test-container", "properties": {"image": image}}
        options = {
            "platform": platform,
            "prerelease_policy_api": prerelease,
            "infrastructure_svn": "99",
            "exclude_default_fragments": exclude_defaults,
        }
        with patch.object(security_policy, "validate_image_platform"):
            if input_format == "json":
                return security_policy.load_policy_from_json(
                    json.dumps({
                        "version": "1.0",
                        "scenario": "vn2" if is_vn2 else "",
                        "containers": [container],
                        "fragments": imports,
                    }),
                    **options,
                )
            if input_format == "yaml":
                return security_policy.load_policy_from_virtual_node_yaml_str(
                    json.dumps({
                        "apiVersion": "v1",
                        "kind": "Pod",
                        "metadata": {"name": "test-pod"},
                        "spec": {"containers": [{"name": "test-container", "image": image}]},
                    }),
                    rego_imports=imports,
                    **options,
                )[0]
            return security_policy.load_policy_from_arm_template_str(
                json.dumps({
                    "resources": [{
                        "type": "Microsoft.ContainerInstance/containerGroups",
                        "name": "test-group",
                        "properties": {"containers": [container]},
                    }],
                }),
                "",
                rego_imports=imports,
                **options,
            )[0]

    def test_windows_vn2_preserves_mount_host_svn_and_warns(self):
        security_policy = importlib.import_module("azext_confcom.security_policy")
        for input_format in ("json", "yaml"):
            for include_custom in (False, True):
                with self.subTest(input_format=input_format, include_custom=include_custom), \
                     patch.object(security_policy.logger, "warning") as warning:
                    fragments = self._load(
                        input_format, "windows/amd64", is_vn2=True, include_custom=include_custom,
                    ).get_fragments()
                    mount_host = next(item for item in fragments if "mount-host" in item["feed"])
                    self.assertEqual(mount_host["minimum_svn"], "1")
                    if include_custom:
                        self.assertEqual(
                            next(item for item in fragments if item["feed"] == "custom-feed")["minimum_svn"], "3",
                        )
                    warning.assert_called_once()
                    self.assertIn("--infrastructure-svn", warning.call_args[0][0])

    def test_windows_vn2_prerelease_updates_infrastructure_svn(self):
        for input_format in ("json", "yaml"):
            with self.subTest(input_format=input_format):
                fragments = self._load(input_format, "windows/amd64", is_vn2=True, prerelease=True).get_fragments()
                infrastructure = next(
                    item for item in fragments if item["feed"] == "mcr.microsoft.com/aci/aci-cwcow-vn2-infra-fragment"
                )
                self.assertEqual(infrastructure["minimum_svn"], "99")
                self.assertEqual(next(item for item in fragments if item["feed"] == "custom-feed")["minimum_svn"], "3")
        self.assertEqual(config.DEFAULT_REGO_FRAGMENTS_WINDOWS_VIRTUAL_NODE[0]["minimum_svn"], "1")

    def test_windows_without_infrastructure_warns_and_preserves_custom_import(self):
        security_policy = importlib.import_module("azext_confcom.security_policy")
        for input_format in ("json", "arm"):
            for include_custom in (False, True):
                with self.subTest(input_format=input_format, include_custom=include_custom), \
                     patch.object(security_policy.logger, "warning") as warning:
                    fragments = self._load(
                        input_format, "windows/amd64", include_custom=include_custom,
                    ).get_fragments()
                    self.assertEqual(len(fragments), int(include_custom))
                    if include_custom:
                        self.assertEqual(fragments[0]["minimum_svn"], "3")
                    warning.assert_called_once()

    def test_windows_prerelease_updates_infrastructure_svn(self):
        for input_format in ("json", "arm"):
            with self.subTest(input_format=input_format):
                fragments = self._load(input_format, "windows/amd64", prerelease=True).get_fragments()
                infrastructure = next(
                    item for item in fragments if item["feed"] == "mcr.microsoft.com/aci/aci-cwcow-infra-fragment"
                )
                self.assertEqual(infrastructure["minimum_svn"], "99")
                self.assertEqual(next(item for item in fragments if item["feed"] == "custom-feed")["minimum_svn"], "3")
        self.assertEqual(config.DEFAULT_REGO_FRAGMENTS_WINDOWS[0]["minimum_svn"], "1")

    def test_linux_updates_infrastructure_svn_not_custom_import(self):
        for input_format in ("json", "yaml", "arm"):
            with self.subTest(input_format=input_format):
                fragments = self._load(input_format, "linux/amd64").get_fragments()
                infrastructure = next(
                    item for item in fragments if item["feed"] == "mcr.microsoft.com/aci/aci-cc-infra-fragment"
                )
                self.assertEqual(infrastructure["minimum_svn"], "99")
                self.assertEqual(next(item for item in fragments if item["feed"] == "custom-feed")["minimum_svn"], "3")
        self.assertEqual(config.DEFAULT_REGO_FRAGMENTS[0]["minimum_svn"], "4")

    def test_excluded_defaults_warn_and_preserve_custom_import(self):
        security_policy = importlib.import_module("azext_confcom.security_policy")
        for input_format in ("json", "yaml", "arm"):
            with self.subTest(input_format=input_format), patch.object(security_policy.logger, "warning") as warning:
                fragments = self._load(input_format, "windows/amd64", exclude_defaults=True).get_fragments()
                self.assertEqual(len(fragments), 1)
                self.assertEqual(fragments[0]["minimum_svn"], "3")
                warning.assert_called_once()


class FragmentFrameworkVersion(unittest.TestCase):
    # The generated fragment must declare the same framework version as the policy
    # boilerplate: Windows always uses the latest, Linux only with the prerelease flag.
    def _fragment(self, image, platform, prerelease_policy_api=False):
        security_policy = importlib.import_module("azext_confcom.security_policy")
        policy = _load_policy(image, platform, prerelease_policy_api=prerelease_policy_api)
        return policy.generate_fragment("ns", 1, security_policy.OutputType.RAW)

    def test_linux_default_framework_version(self):
        self.assertIn('framework_version := "0.2.3"', self._fragment(LINUX_IMAGE, "linux/amd64"))

    def test_linux_prerelease_framework_version(self):
        self.assertIn(
            'framework_version := "0.5.0"',
            self._fragment(LINUX_IMAGE, "linux/amd64", prerelease_policy_api=True),
        )

    def test_windows_framework_version(self):
        self.assertIn('framework_version := "0.5.0"', self._fragment(WINDOWS_IMAGE, "windows/amd64"))

    def test_windows_prerelease_framework_version(self):
        self.assertIn(
            'framework_version := "0.5.0"',
            self._fragment(WINDOWS_IMAGE, "windows/amd64", prerelease_policy_api=True),
        )


class OrasFragmentReferences(unittest.TestCase):
    # A colon in the registry host (port) is not a tag separator.
    def _completed(self):
        completed = unittest.mock.MagicMock()
        completed.returncode = 0
        completed.stdout = b"Downloaded frag.cose"
        return completed

    def test_pull_registry_port_without_tag_is_invalid(self):
        from azext_confcom import oras_proxy
        with patch.object(oras_proxy, "call_oras_cli") as mock_oras:
            with self.assertRaises(SystemExit):
                oras_proxy.pull("registry.example.com:5000/frag")
        mock_oras.assert_not_called()

    def test_pull_registry_port_with_tag(self):
        from azext_confcom import oras_proxy
        with patch.object(oras_proxy, "call_oras_cli", return_value=self._completed()) as mock_oras:
            oras_proxy.pull("registry.example.com:5000/frag:v1")
        self.assertEqual(mock_oras.call_args[0][0][2], "registry.example.com:5000/frag:v1")

    def test_standalone_skips_registry_port_feed_without_tag(self):
        from azext_confcom import oras_proxy
        imports = [{"feed": "registry.example.com:5000/frag", "issuer": "iss", "minimum_svn": "1"}]
        with patch.object(oras_proxy, "pull") as mock_pull:
            oras_proxy.pull_all_standalone_fragments(imports)
        mock_pull.assert_not_called()

    def test_generate_imports_forwards_platform(self):
        from azext_confcom import oras_proxy
        with patch.object(oras_proxy, "discover", return_value=(True, [])) as mock_discover:
            oras_proxy.generate_imports_from_image_name("img:1", "1", platform="windows/amd64")
        self.assertEqual(mock_discover.call_args.kwargs["platform"], "windows/amd64")

    def test_generate_imports_default_platform(self):
        from azext_confcom import oras_proxy
        with patch.object(oras_proxy, "discover", return_value=(True, [])) as mock_discover:
            oras_proxy.generate_imports_from_image_name("img:1", "1")
        self.assertEqual(
            mock_discover.call_args.kwargs["platform"], oras_proxy.FRAGMENT_DISCOVERY_PLATFORM
        )


if __name__ == "__main__":
    unittest.main()
