# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from azure.cli.core.azclierror import ValidationError
from azure.cli.core.mock import DummyCli
from azure.core.exceptions import HttpResponseError

from azext_aks_preview import ContainerServiceCommandsLoader
from azext_aks_preview import custom
from azext_aks_preview._helpers import raise_validation_error_if_extension_type_not_in_allow_list


class PodSnapshotExtensionTestCase(unittest.TestCase):
    extension_type = "Microsoft.PodSnapshot"
    extension_name = "pod-snapshot"
    namespace = "pod-snapshot-system"
    settings = {
        "broker.storageAccount": "storage",
        "azureBlob.workloadIdentity.clientID": "client-id",
        "azureBlob.workloadIdentity.tenantID": "tenant-id",
    }

    def setUp(self):
        self.cmd = Mock()
        self.arm_client = Mock()
        self.extension_client = Mock()
        self.module = Mock()
        self.factory = Mock()
        self.factory.cf_k8s_extension_operation.return_value = self.extension_client
        self.factory.cf_k8s_extension_types.return_value = self.extension_client
        modules = {
            custom.CONST_K8S_EXTENSION_CUSTOM_MOD_NAME: self.module,
            custom.CONST_K8S_EXTENSION_CLIENT_FACTORY_MOD_NAME: self.factory,
        }
        patcher = patch.object(custom, "get_k8s_extension_module", side_effect=modules.__getitem__)
        self.load_module = patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.assertEqual(self.arm_client.mock_calls, [])

    def test_create_forwards_configuration_to_extension_client(self):
        for options in (
            {},
            {"configuration_settings": [self.settings]},
            {"configuration_settings_file": "settings.json"},
            {"configuration_protected_settings_file": "protected.json"},
        ):
            with self.subTest(options=options):
                self.module.reset_mock()
                result = custom.create_k8s_extension(
                    self.cmd, self.arm_client, "rg", "cluster", self.extension_name,
                    self.extension_type, scope="cluster", release_namespace=self.namespace,
                    no_wait=True, **options
                )
                forwarded = {
                    "configuration_settings": None,
                    "configuration_protected_settings": None,
                    "configuration_settings_file": None,
                    "configuration_protected_settings_file": None,
                }
                forwarded.update(options)
                self.module.create_k8s_extension.assert_called_once_with(
                    self.cmd, self.extension_client, "rg", "cluster",
                    name=self.extension_name, cluster_type="managedClusters",
                    extension_type=self.extension_type, scope="cluster",
                    target_namespace=None, release_namespace=self.namespace,
                    no_wait=True, **forwarded
                )
                self.assertIs(result, self.module.create_k8s_extension.return_value)

    def test_update_forwards_settings_and_controls(self):
        result = custom.update_k8s_extension(
            self.cmd, self.arm_client, "rg", "cluster", self.extension_name,
            configuration_settings_file="settings.json", no_wait=True, yes=True,
        )
        self.module.update_k8s_extension.assert_called_once_with(
            self.cmd, self.extension_client, "rg", "cluster", self.extension_name,
            "managedClusters", configuration_settings=None, configuration_protected_settings=None,
            configuration_settings_file="settings.json", configuration_protected_settings_file=None,
            no_wait=True, yes=True,
        )
        self.assertIs(result, self.module.update_k8s_extension.return_value)

    def test_delete_forwards_controls(self):
        result = custom.delete_k8s_extension(
            self.cmd, self.arm_client, "rg", "cluster", self.extension_name,
            no_wait=True, yes=True, force=True,
        )
        self.module.delete_k8s_extension.assert_called_once_with(
            self.cmd, self.extension_client, "rg", "cluster", self.extension_name,
            "managedClusters", no_wait=True, yes=True, force=True,
        )
        self.assertIs(result, self.module.delete_k8s_extension.return_value)

    def test_allowlist_and_discovery(self):
        for extension_type in (self.extension_type.lower(), self.extension_type.upper(),
                               "microsoft.dataprotection.kubernetes"):
            raise_validation_error_if_extension_type_not_in_allow_list(extension_type)
        extension = SimpleNamespace(extension_type=self.extension_type)
        other = SimpleNamespace(extension_type="unsupported.extension")
        self.module.list_k8s_extension.return_value = [extension, other]
        self.assertEqual(
            custom.list_k8s_extension(self.cmd, self.arm_client, "rg", "cluster"), [extension]
        )
        self.module.show_k8s_extension.return_value = extension
        self.assertIs(
            custom.show_k8s_extension(self.cmd, self.arm_client, "rg", "cluster", self.extension_name),
            extension,
        )
        extension_type = SimpleNamespace(name=self.extension_type)
        self.module.list_extension_types_by_cluster.return_value = [
            extension_type, SimpleNamespace(name="unsupported.extension")
        ]
        self.assertEqual(
            custom.list_k8s_extension_types(
                self.cmd, self.arm_client, resource_group_name="rg", cluster_name="cluster"
            ), [extension_type]
        )

    def test_unsupported_type_rejected_before_delegation(self):
        with self.assertRaises(ValidationError):
            custom.create_k8s_extension(
                self.cmd, self.arm_client, "rg", "cluster", "extension", "unsupported.extension"
            )
        self.load_module.assert_not_called()

    def test_service_errors_propagate(self):
        for name in ("create", "update", "delete", "show", "list"):
            with self.subTest(command=name):
                error = HttpResponseError(message="Extension management policy denied the operation")
                getattr(self.module, name + "_k8s_extension").side_effect = error
                args = [self.cmd, self.arm_client, "rg", "cluster"]
                if name != "list":
                    args.append(self.extension_name)
                if name == "create":
                    args.append(self.extension_type)
                with self.assertRaises(HttpResponseError) as raised:
                    getattr(custom, name + "_k8s_extension")(*args)
                self.assertIs(raised.exception, error)

    def test_configuration_file_aliases(self):
        for command in ("aks extension create", "aks extension update"):
            with self.subTest(command=command):
                cli = DummyCli()
                cli.invocation = Mock(data={"command_string": command}, parser=argparse.ArgumentParser())
                loader = ContainerServiceCommandsLoader(cli)
                loader.load_command_table(command.split())
                loader.command_table[command].load_arguments()
                loader.load_arguments(command)
                argument = loader.argument_registry.arguments["aks extension"]["configuration_settings_file"]
                parser = argparse.ArgumentParser()
                parser.add_argument(*argument.settings["options_list"], dest="configuration_settings_file")
                for alias in ("--config-file", "--config-settings-file"):
                    self.assertEqual(
                        parser.parse_args([alias, "settings.json"]).configuration_settings_file, "settings.json"
                    )
