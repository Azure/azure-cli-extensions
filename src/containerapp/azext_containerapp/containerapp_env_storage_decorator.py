# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import AzCliCommand
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.core.azclierror import RequiredArgumentMissingError, ValidationError
from knack.log import get_logger
from typing import Any, Dict

from ._client_factory import handle_raw_exception
from ._models import AzureFileProperties, NfsAzureFileProperties, ManagedEnvironmentStorageProperties
from ._constants import AZURE_FILE_STORAGE_TYPE, NFS_AZURE_FILE_STORAGE_TYPE
logger = get_logger(__name__)


class ContainerappEnvStorageDecorator(BaseResource):

    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.managed_environment_storage_def = ManagedEnvironmentStorageProperties
        self.storage_type = self.get_argument_storage_type()
        self.azure_file_account_name = self.get_argument_azure_file_account_name()
        self.azure_file_share_name = self.get_argument_azure_file_share_name()
        self.azure_file_account_key = self.get_argument_azure_file_account_key()
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

    def get_argument_server(self):
        return self.get_param("server")

    def get_argument_access_mode(self):
        return self.get_param("access_mode")

    def construct_payload(self):
        if not self.storage_type or self.storage_type.lower() == AZURE_FILE_STORAGE_TYPE.lower():
            storage_def = AzureFileProperties
            storage_def["accountKey"] = self.azure_file_account_key
            storage_def["accountName"] = self.azure_file_account_name
            storage_def["shareName"] = self.azure_file_share_name
            storage_def["accessMode"] = self.access_mode

            self.managed_environment_storage_def["properties"] = {}
            self.managed_environment_storage_def["properties"]["azureFile"] = storage_def
        elif self.storage_type.lower() == NFS_AZURE_FILE_STORAGE_TYPE.lower():
            storage_def = NfsAzureFileProperties
            storage_def["server"] = self.server
            storage_def["shareName"] = self.azure_file_share_name
            storage_def["accessMode"] = self.access_mode
            self.managed_environment_storage_def["properties"] = {}
            self.managed_environment_storage_def["properties"]["nfsAzureFile"] = storage_def

    def validate_arguments(self):
        import json
        if not self.storage_type or self.storage_type.lower() == AZURE_FILE_STORAGE_TYPE:
            if len(self.azure_file_share_name) == 0 or len(self.azure_file_account_name) == 0 or len(
                    self.azure_file_account_key) == 0 or len(self.access_mode) == 0:
                raise RequiredArgumentMissingError(
                    "--azure-file-share-name/--file-share/-f, --azure-file-account-key/--storage-account-key/-k, and --access-mode must be provided for AzureFile storage type")
            if len(self.azure_file_share_name) < 3:
                raise ValidationError("File share name with --azure-file-share-name/--file-share/-f must be longer than 2 characters.")
            if len(self.azure_file_account_name) < 3:
                raise ValidationError("Account name with --azure-file-account-name/--account-name/-a must be longer than 2 characters.")
        elif self.storage_type.lower() == NFS_AZURE_FILE_STORAGE_TYPE:
            if len(self.server) == 0 or len(self.access_mode) == 0 or len(self.azure_file_share_name) == 0:
                raise RequiredArgumentMissingError(
                    "--server, --file-share/-f and --access-mode must be provided for NfsAzureFile storage type")
            if len(self.server) < 3:
                raise ValidationError("Server with --server must be longer than 2 characters.")

        try:
            r = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                                 env_name=self.get_argument_name(), name=self.get_argument_storage_name())
            if r:
                logger.warning(
                    'Only AzureFile account keys can be updated. In order to change the AzureFile share name or account'
                    ' name or NfsAzureFile server, please delete this storage and create a new one.')
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
