# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation

from copy import deepcopy
from typing import Any, Dict

from azure.cli.command_modules.containerapp._utils import _ensure_identity_resource_id
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.core.azclierror import MutuallyExclusiveArgumentError, RequiredArgumentMissingError, ValidationError
from knack.log import get_logger

from ._client_factory import handle_raw_exception
from ._models import AzureFileProperties, NfsAzureFileProperties, ManagedEnvironmentStorageProperties
from ._constants import AZURE_FILE_STORAGE_TYPE, NFS_AZURE_FILE_STORAGE_TYPE
logger = get_logger(__name__)


class ContainerappEnvStorageDecorator(BaseResource):

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.managed_environment_storage_def = deepcopy(ManagedEnvironmentStorageProperties)
        self.storage_type = self.get_argument_storage_type()
        self.azure_file_account_name = self.get_argument_azure_file_account_name()
        self.azure_file_share_name = self.get_argument_azure_file_share_name()
        self.azure_file_account_key = self.get_argument_azure_file_account_key()
        self.azure_file_key_vault_secret_url = self.get_argument_azure_file_key_vault_secret_url()
        self.azure_file_key_vault_identity = self.get_argument_azure_file_key_vault_identity()
        self.azure_file_identity = self.get_argument_azure_file_identity()
        self.server = self.get_argument_server()
        self.access_mode = self.get_argument_access_mode()

    def get_argument_storage_name(self):
        return self.get_param("storage_name")

    def get_argument_storage_type(self):
        return self.get_param("storage_type")

    def get_argument_azure_file_account_name(self):
        return self.get_param("azure_file_account_name")

    def get_argument_azure_file_share_name(self):
        return self.get_param("azure_file_share_name")

    def get_argument_azure_file_account_key(self):
        return self.get_param("azure_file_account_key")

    def get_argument_azure_file_key_vault_secret_url(self):
        return self.get_param("azure_file_key_vault_secret_url")

    def get_argument_azure_file_key_vault_identity(self):
        return self.get_param("azure_file_key_vault_identity")

    def get_argument_azure_file_identity(self):
        return self.get_param("azure_file_identity")

    def get_argument_server(self):
        return self.get_param("server")

    def get_argument_access_mode(self):
        return self.get_param("access_mode")

    def _normalize_identity(self, identity):
        if identity.lower() == "system":
            return "system"
        subscription_id = get_subscription_id(self.cmd.cli_ctx)
        return _ensure_identity_resource_id(subscription_id, self.get_argument_resource_group_name(), identity)

    def construct_payload(self):
        storage_type = (self.storage_type or AZURE_FILE_STORAGE_TYPE).lower()
        if storage_type == AZURE_FILE_STORAGE_TYPE.lower():
            storage_def = deepcopy(AzureFileProperties)
            storage_def["accountName"] = self.azure_file_account_name
            storage_def["shareName"] = self.azure_file_share_name
            storage_def["accessMode"] = self.access_mode

            if self.azure_file_account_key:
                storage_def["accountKey"] = self.azure_file_account_key
            elif self.azure_file_key_vault_secret_url:
                storage_def["accountKeyVaultProperties"] = {
                    "keyVaultUrl": self.azure_file_key_vault_secret_url,
                    "identity": self._normalize_identity(self.azure_file_key_vault_identity or "system")
                }
            elif self.azure_file_identity:
                storage_def["identity"] = self._normalize_identity(self.azure_file_identity)

            storage_def = {key: value for key, value in storage_def.items() if value is not None}
            self.managed_environment_storage_def["properties"] = {"azureFile": storage_def}
        elif storage_type == NFS_AZURE_FILE_STORAGE_TYPE.lower():
            storage_def = deepcopy(NfsAzureFileProperties)
            storage_def["server"] = self.server
            storage_def["shareName"] = self.azure_file_share_name
            storage_def["accessMode"] = self.access_mode
            storage_def = {key: value for key, value in storage_def.items() if value is not None}
            self.managed_environment_storage_def["properties"] = {"nfsAzureFile": storage_def}

    def validate_arguments(self):
        storage_type = (self.storage_type or AZURE_FILE_STORAGE_TYPE).lower()
        if storage_type == AZURE_FILE_STORAGE_TYPE.lower():
            if not self.azure_file_share_name or not self.azure_file_account_name or not self.access_mode:
                raise RequiredArgumentMissingError(
                    "--azure-file-share-name/--file-share/-f, --azure-file-account-name/--account-name/-a, and --access-mode must be provided for AzureFile storage type")

            if self.azure_file_key_vault_identity and not self.azure_file_key_vault_secret_url:
                raise RequiredArgumentMissingError(
                    "--azure-file-key-vault-secret-url must be provided with --azure-file-key-vault-identity")

            auth_modes = [
                self.azure_file_account_key,
                self.azure_file_key_vault_secret_url,
                self.azure_file_identity
            ]
            auth_mode_count = sum(bool(auth_mode) for auth_mode in auth_modes)
            if auth_mode_count == 0:
                raise RequiredArgumentMissingError(
                    "One of --azure-file-account-key/--storage-account-key/-k, --azure-file-key-vault-secret-url, or --azure-file-identity must be provided for AzureFile storage type")
            if auth_mode_count > 1:
                raise MutuallyExclusiveArgumentError(
                    "--azure-file-account-key/--storage-account-key/-k, --azure-file-key-vault-secret-url, and --azure-file-identity cannot be used together")

            if len(self.azure_file_share_name) < 3:
                raise ValidationError("File share name with --azure-file-share-name/--file-share/-f must be longer than 2 characters.")
            if len(self.azure_file_account_name) < 3:
                raise ValidationError("Account name with --azure-file-account-name/--account-name/-a must be longer than 2 characters.")
        elif storage_type == NFS_AZURE_FILE_STORAGE_TYPE.lower():
            if any([
                    self.azure_file_account_name,
                    self.azure_file_account_key,
                    self.azure_file_key_vault_secret_url,
                    self.azure_file_key_vault_identity,
                    self.azure_file_identity]):
                raise MutuallyExclusiveArgumentError(
                    "AzureFile authentication arguments cannot be used with NfsAzureFile storage type")
            if not self.server or not self.access_mode or not self.azure_file_share_name:
                raise RequiredArgumentMissingError(
                    "--server, --file-share/-f and --access-mode must be provided for NfsAzureFile storage type")
            if len(self.server) < 3:
                raise ValidationError("Server with --server must be longer than 2 characters.")

        try:
            r = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                 env_name=self.get_argument_name(), name=self.get_argument_storage_name())
            if r:
                logger.warning(
                    'Only authentication configuration can be updated. To change the AzureFile account name, share name,'
                    ' access mode, or NfsAzureFile server, delete this storage and create a new one.')
        except Exception as e:
            string_err = str(e)
            if "ManagedEnvironmentStorageNotFound" in string_err:
                pass
            else:
                handle_raw_exception(e)

    def create_or_update(self):
        try:
            return self.client.create_or_update(cmd=self.cmd,
                                                resource_group_name=self.get_argument_resource_group_name(),
                                                env_name=self.get_argument_name(),
                                                name=self.get_argument_storage_name(),
                                                storage_envelope=self.managed_environment_storage_def)
        except Exception as e:
            handle_raw_exception(e)

    def show(self):
        try:
            return self.client.show(cmd=self.cmd,
                                    resource_group_name=self.get_argument_resource_group_name(),
                                    env_name=self.get_argument_name(),
                                    name=self.get_argument_storage_name())
        except Exception as e:
            handle_raw_exception(e)

    def list(self):
        try:
            return self.client.list(cmd=self.cmd,
                                    resource_group_name=self.get_argument_resource_group_name(),
                                    env_name=self.get_argument_name())
        except Exception as e:
            handle_raw_exception(e)

    def delete(self):
        try:
            return self.client.delete(cmd=self.cmd,
                                      resource_group_name=self.get_argument_resource_group_name(),
                                      env_name=self.get_argument_name(),
                                      name=self.get_argument_storage_name())
        except Exception as e:
            handle_raw_exception(e)
