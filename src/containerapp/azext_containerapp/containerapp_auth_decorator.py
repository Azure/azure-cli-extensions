# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, Dict

from azure.cli.command_modules.containerapp.containerapp_auth_decorator import ContainerAppAuthDecorator
from azure.cli.command_modules.containerapp._utils import safe_set

from ._constants import BLOB_STORAGE_TOKEN_STORE_SECRET_SETTING_NAME
from knack.prompting import prompt_y_n
from azure.cli.core.azclierror import ArgumentUsageError


# decorator for preview auth show/update
class ContainerAppPreviewAuthDecorator(ContainerAppAuthDecorator):
    def construct_payload(self):
        super().construct_payload()
        self.set_up_token_store()

    def set_up_token_store(self):
        if self.get_argument_token_store() is None:
            return

        if self.get_argument_token_store() is False:
            safe_set(self.existing_auth, "login", "tokenStore", "enabled", value=False)
            return

        safe_set(self.existing_auth, "login", "tokenStore", "enabled", value=True)

        if self.get_argument_sas_url_secret() is None and self.get_argument_sas_url_secret_name() is None:
            raise ArgumentUsageError('Usage Error: only blob storage token store is supported. --sas-url-secret and --sas-url-secret-name should provide exactly one when token store is enabled')
        if self.get_argument_sas_url_secret() is not None and self.get_argument_sas_url_secret_name() is not None:
            raise ArgumentUsageError('Usage Error: --sas-url-secret and --sas-url-secret-name cannot both be set')
        if self.get_argument_sas_url_secret() is not None and not self.get_argument_yes():
            msg = 'Configuring --sas-url-secret will add a secret to the containerapp. Are you sure you want to continue?'
            if not prompt_y_n(msg, default="n"):
                raise ArgumentUsageError('Usage Error: --sas-url-secret cannot be used without agreeing to add secret to the containerapp.')

        sas_url_setting_name = BLOB_STORAGE_TOKEN_STORE_SECRET_SETTING_NAME
        if self.get_argument_sas_url_secret_name() is not None:
            sas_url_setting_name = self.get_argument_sas_url_secret_name()
        safe_set(self.existing_auth, "login", "tokenStore", "azureBlobStorage", "sasUrlSettingName", value=sas_url_setting_name)

    def get_argument_token_store(self):
        return self.get_param("token_store")

    def get_argument_sas_url_secret(self):
        return self.get_param("sas_url_secret")

    def get_argument_sas_url_secret_name(self):
        return self.get_param("sas_url_secret_name")

    def get_argument_yes(self):
        return self.get_param("yes")
