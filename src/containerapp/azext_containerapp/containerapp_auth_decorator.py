# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, useless-parent-delegation
from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.command_modules.containerapp.containerapp_auth_decorator import ContainerAppAuthDecorator
from azure.cli.command_modules.containerapp._utils import safe_set, set_field_in_auth_settings, update_http_settings_in_auth_settings, _ensure_identity_resource_id
from azure.cli.command_modules.containerapp._constants import BLOB_STORAGE_TOKEN_STORE_SECRET_SETTING_NAME


# decorator for preview auth show/update
class ContainerAppPreviewAuthDecorator(ContainerAppAuthDecorator):

    def parent_construct_payload(self):
        self.existing_auth = {}
        try:
            self.existing_auth = self.client.get(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), container_app_name=self.get_argument_name(), auth_config_name="current")["properties"]
        except:  # pylint: disable=bare-except
            self.existing_auth["platform"] = {}
            self.existing_auth["platform"]["enabled"] = True
            self.existing_auth["globalValidation"] = {}
            self.existing_auth["login"] = {}

        self.existing_auth = set_field_in_auth_settings(self.existing_auth, self.get_argument_set_string())

        if self.get_argument_enabled() is not None:
            if "platform" not in self.existing_auth:
                self.existing_auth["platform"] = {}
            self.existing_auth["platform"]["enabled"] = self.get_argument_enabled()

        if self.get_argument_runtime_version() is not None:
            if "platform" not in self.existing_auth:
                self.existing_auth["platform"] = {}
            self.existing_auth["platform"]["runtimeVersion"] = self.get_argument_runtime_version()

        if self.get_argument_config_file_path() is not None:
            if "platform" not in self.existing_auth:
                self.existing_auth["platform"] = {}
            self.existing_auth["platform"]["configFilePath"] = self.get_argument_config_file_path()

        if self.get_argument_unauthenticated_client_action() is not None:
            if "globalValidation" not in self.existing_auth:
                self.existing_auth["globalValidation"] = {}
            self.existing_auth["globalValidation"]["unauthenticatedClientAction"] = self.get_argument_unauthenticated_client_action()

        if self.get_argument_redirect_provider() is not None:
            if "globalValidation" not in self.existing_auth:
                self.existing_auth["globalValidation"] = {}
            self.existing_auth["globalValidation"]["redirectToProvider"] = self.get_argument_redirect_provider()

        if self.get_argument_excluded_paths() is not None:
            if "globalValidation" not in self.existing_auth:
                self.existing_auth["globalValidation"] = {}
            self.existing_auth["globalValidation"]["excludedPaths"] = self.get_argument_excluded_paths().split(",")

        self.existing_auth = update_http_settings_in_auth_settings(self.existing_auth, self.get_argument_require_https(),
                                                                   self.get_argument_proxy_convention(), self.get_argument_proxy_custom_host_header(),
                                                                   self.get_argument_proxy_custom_proto_header())

    def construct_payload(self):
        self.parent_construct_payload()
        self.set_up_token_store()

    def set_up_token_store(self):
        if self.get_argument_token_store() is None:
            return

        if self.get_argument_token_store() is False:
            safe_set(self.existing_auth, "login", "tokenStore", "enabled", value=False)
            return

        safe_set(self.existing_auth, "login", "tokenStore", "enabled", value=True)
        safe_set(self.existing_auth, "login", "tokenStore", "azureBlobStorage", value={})

        param_provided = sum(1 for param in [self.get_argument_sas_url_secret(), self.get_argument_sas_url_secret_name(), self.get_argument_blob_container_uri()] if param is not None)
        if param_provided != 1:
            raise ArgumentUsageError(
                'Usage Error: only blob storage token store is supported. --sas-url-secret, --sas-url-secret-name and --blob-container-uri should provide exactly one when token store is enabled')

        if self.get_argument_blob_container_uri() is not None:
            safe_set(self.existing_auth, "login", "tokenStore", "azureBlobStorage", "blobContainerUri", value=self.get_argument_blob_container_uri())

            identity = self.get_argument_blob_container_identity()
            if identity is not None:
                identity = identity.lower()
                subscription_id = get_subscription_id(self.cmd.cli_ctx)
                identity = _ensure_identity_resource_id(subscription_id, self.get_argument_resource_group_name(), identity)
                safe_set(self.existing_auth, "login", "tokenStore", "azureBlobStorage", "managedIdentityResourceId", value=identity)
            return

        sas_url_setting_name = BLOB_STORAGE_TOKEN_STORE_SECRET_SETTING_NAME
        if self.get_argument_sas_url_secret_name() is not None:
            sas_url_setting_name = self.get_argument_sas_url_secret_name()
        safe_set(self.existing_auth, "login", "tokenStore", "azureBlobStorage", "sasUrlSettingName", value=sas_url_setting_name)

    def get_argument_blob_container_uri(self):
        return self.get_param("blob_container_uri")

    def get_argument_blob_container_identity(self):
        return self.get_param("blob_container_identity")
