# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azure.cli.core.azclierror import MutuallyExclusiveArgumentError, RequiredArgumentMissingError

from azext_containerapp._clients import StoragePreviewClient
from azext_containerapp._params import load_arguments
from azext_containerapp.containerapp_env_storage_decorator import ContainerappEnvStorageDecorator


class TestContainerappEnvStorageDecorator(unittest.TestCase):

    def _create_decorator(self, **overrides):
        parameters = {
            "resource_group_name": "resource-group",
            "name": "environment",
            "storage_name": "storage-mount",
            "storage_type": "AzureFile",
            "azure_file_account_name": "storageaccount",
            "azure_file_share_name": "fileshare",
            "azure_file_account_key": None,
            "azure_file_key_vault_secret_url": None,
            "azure_file_key_vault_identity": None,
            "azure_file_identity": None,
            "server": None,
            "access_mode": "ReadWrite",
        }
        parameters.update(overrides)

        client = mock.MagicMock()
        client.show.return_value = None
        return ContainerappEnvStorageDecorator(
            cmd=mock.MagicMock(),
            client=client,
            raw_parameters=parameters,
            models="models",
        )

    def _construct_azure_file(self, **overrides):
        decorator = self._create_decorator(**overrides)
        decorator.validate_arguments()
        decorator.construct_payload()
        return decorator.managed_environment_storage_def["properties"]["azureFile"]

    def test_constructs_account_key_payload(self):
        azure_file = self._construct_azure_file(azure_file_account_key="account-key")

        self.assertEqual({
            "accountName": "storageaccount",
            "accountKey": "account-key",
            "accessMode": "ReadWrite",
            "shareName": "fileshare",
        }, azure_file)

    def test_constructs_key_vault_payload_with_default_system_identity(self):
        azure_file = self._construct_azure_file(
            azure_file_key_vault_secret_url="https://vault.vault.azure.net/secrets/storage-key")

        self.assertEqual({
            "accountName": "storageaccount",
            "accountKeyVaultProperties": {
                "keyVaultUrl": "https://vault.vault.azure.net/secrets/storage-key",
                "identity": "system",
            },
            "accessMode": "ReadWrite",
            "shareName": "fileshare",
        }, azure_file)

    @mock.patch("azext_containerapp.containerapp_env_storage_decorator._ensure_identity_resource_id")
    @mock.patch("azext_containerapp.containerapp_env_storage_decorator.get_subscription_id", return_value="subscription-id")
    def test_constructs_key_vault_payload_with_user_assigned_identity(self, _, ensure_identity_resource_id):
        identity_id = "/subscriptions/subscription-id/resourceGroups/resource-group/providers/Microsoft.ManagedIdentity/userAssignedIdentities/storage-identity"
        ensure_identity_resource_id.return_value = identity_id

        azure_file = self._construct_azure_file(
            azure_file_key_vault_secret_url="https://vault.vault.azure.net/secrets/storage-key",
            azure_file_key_vault_identity="storage-identity")

        self.assertEqual(identity_id, azure_file["accountKeyVaultProperties"]["identity"])
        ensure_identity_resource_id.assert_called_once_with("subscription-id", "resource-group", "storage-identity")

    def test_constructs_managed_identity_payload_with_canonical_system_value(self):
        azure_file = self._construct_azure_file(azure_file_identity="SYSTEM")

        self.assertEqual("system", azure_file["identity"])
        self.assertNotIn("accountKey", azure_file)
        self.assertNotIn("accountKeyVaultProperties", azure_file)

    @mock.patch("azext_containerapp.containerapp_env_storage_decorator._ensure_identity_resource_id")
    @mock.patch("azext_containerapp.containerapp_env_storage_decorator.get_subscription_id", return_value="subscription-id")
    def test_constructs_managed_identity_payload_with_user_assigned_identity(self, _, ensure_identity_resource_id):
        identity_id = "/subscriptions/subscription-id/resourceGroups/resource-group/providers/Microsoft.ManagedIdentity/userAssignedIdentities/storage-identity"
        ensure_identity_resource_id.return_value = identity_id

        azure_file = self._construct_azure_file(azure_file_identity="storage-identity")

        self.assertEqual(identity_id, azure_file["identity"])
        ensure_identity_resource_id.assert_called_once_with("subscription-id", "resource-group", "storage-identity")

    def test_requires_exactly_one_authentication_mode(self):
        with self.assertRaises(RequiredArgumentMissingError):
            self._create_decorator().validate_arguments()

        conflicting_modes = [
            {"azure_file_account_key": "key", "azure_file_key_vault_secret_url": "https://vault/secrets/key"},
            {"azure_file_account_key": "key", "azure_file_identity": "system"},
            {"azure_file_key_vault_secret_url": "https://vault/secrets/key", "azure_file_identity": "system"},
        ]
        for modes in conflicting_modes:
            with self.subTest(modes=modes):
                with self.assertRaises(MutuallyExclusiveArgumentError):
                    self._create_decorator(**modes).validate_arguments()

    def test_key_vault_identity_requires_secret_url(self):
        with self.assertRaises(RequiredArgumentMissingError):
            self._create_decorator(
                azure_file_account_key="key",
                azure_file_key_vault_identity="system").validate_arguments()

    def test_rejects_azure_file_authentication_arguments_for_nfs(self):
        nfs_parameters = {
            "storage_type": "NfsAzureFile",
            "azure_file_account_name": None,
            "server": "storage.file.core.windows.net",
            "azure_file_share_name": "/storage/share",
        }
        for argument, value in [
                ("azure_file_account_key", "key"),
                ("azure_file_key_vault_secret_url", "https://vault/secrets/key"),
                ("azure_file_key_vault_identity", "system"),
                ("azure_file_identity", "system")]:
            with self.subTest(argument=argument):
                with self.assertRaises(MutuallyExclusiveArgumentError):
                    self._create_decorator(**nfs_parameters, **{argument: value}).validate_arguments()

    def test_constructs_nfs_payload_without_azure_file_authentication(self):
        decorator = self._create_decorator(
            storage_type="NfsAzureFile",
            azure_file_account_name=None,
            server="storage.file.core.windows.net",
            azure_file_share_name="/storage/share")

        decorator.validate_arguments()
        decorator.construct_payload()

        self.assertEqual({
            "server": "storage.file.core.windows.net",
            "accessMode": "ReadWrite",
            "shareName": "/storage/share",
        }, decorator.managed_environment_storage_def["properties"]["nfsAzureFile"])

    def test_payloads_do_not_share_authentication_state(self):
        self._construct_azure_file(azure_file_account_key="account-key")
        azure_file = self._construct_azure_file(azure_file_identity="system")

        self.assertNotIn("accountKey", azure_file)
        self.assertEqual("system", azure_file["identity"])


class TestContainerappEnvStorageArguments(unittest.TestCase):

    def test_uses_managed_environment_storage_api_version(self):
        self.assertEqual("2026-03-02-preview", StoragePreviewClient.api_version)

    def test_registers_preview_authentication_arguments(self):
        class ArgumentContext:
            def __init__(self, loader, command):
                self.loader = loader
                self.command = command

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def argument(self, name, *args, **kwargs):
                self.loader.arguments.setdefault(self.command, {})[name] = kwargs

            def ignore(self, *_):
                pass

            def deprecate(self, **kwargs):
                return kwargs

        class Loader:
            def __init__(self):
                self.arguments = {}

            def argument_context(self, command, **kwargs):
                return ArgumentContext(self, command)

        loader = Loader()
        load_arguments(loader, None)
        storage_arguments = loader.arguments["containerapp env storage"]
        expected_options = {
            "azure_file_key_vault_secret_url": "--azure-file-key-vault-secret-url",
            "azure_file_key_vault_identity": "--azure-file-key-vault-identity",
            "azure_file_identity": "--azure-file-identity",
        }

        for argument, option in expected_options.items():
            with self.subTest(argument=argument):
                self.assertEqual([option], storage_arguments[argument]["options_list"])
                self.assertTrue(storage_arguments[argument]["is_preview"])


if __name__ == "__main__":
    unittest.main()
