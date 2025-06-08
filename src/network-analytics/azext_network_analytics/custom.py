# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from ._client_factory import cf_storage_container
from azure.cli.command_modules.keyvault._client_factory import data_plane_azure_keyvault_secret_client
from azure.cli.core.commands.arm import get_arm_resource_by_id
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
import re

DATA_PRODUCT_ARM_ID = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.NetworkAnalytics/dataProducts/{}"
INPUT_STORAGE_ACCOUNT_SAS_URL_SECRET_NAME = "input-storage-sas"
KEYVAULT_URI = "https://aoi-{}-kv.vault.azure.net/"

logger = get_logger(__name__)


def data_product_ingest(cmd,
                        resource_group_name,
                        data_product_name,
                        data_type,
                        source,
                        destination):
    dp_ingest = DataProductsIngest(cmd, resource_group_name, data_product_name, data_type, source, destination)
    dp_ingest.data_product_ingest()


class DataProductsIngest():
    def __init__(self, cmd, resource_group_name, data_product_name, data_type, source, destination):
        self.cmd = cmd
        self.resource_group = resource_group_name
        self.data_product_name = data_product_name
        self.data_type = data_type
        self.source = source
        self.destination = destination

    def data_product_ingest(self):
        data_product = self.get_data_product()
        secret = self.get_key_vault_secret(data_product)
        self.upload_file(secret)

    def get_data_product(self):
        subscription_id = get_subscription_id(self.cmd.cli_ctx)
        arm_id = DATA_PRODUCT_ARM_ID.format(subscription_id, self.resource_group, self.data_product_name)
        data_product = get_arm_resource_by_id(self.cmd.cli_ctx, arm_id)
        return data_product

    def get_key_vault_secret(self, data_product):
        keyvault_url = self.get_keyvault_url(data_product)
        command_args = {'vault_base_url': keyvault_url}
        keyvault_client = data_plane_azure_keyvault_secret_client(self.cmd.cli_ctx, command_args)
        secret = keyvault_client.get_secret(name=INPUT_STORAGE_ACCOUNT_SAS_URL_SECRET_NAME)
        return secret.value

    def get_keyvault_url(self, data_product):
        ingestion_url = data_product.properties['consumptionEndpoints']['ingestionUrl']
        pattern = r"https://aoiingestion(.*)\.blob\.core\.windows\.net"
        unique_id = re.search(pattern, ingestion_url).group(1)
        vault_base_url = KEYVAULT_URI.format(unique_id)
        return vault_base_url

    def upload_file(self, secret):
        storage_container = self.get_storage_container(secret)
        data = open(self.source, "rb")
        storage_container.upload_blob(name=self.destination, data=data, overwrite=True)

    def get_storage_container(self, secret):
        result = secret.split("?", 1)
        storage_url = result[0]
        sas_token = result[1]
        container_name = self.data_type
        container_url = f'{storage_url}/{container_name}'
        return cf_storage_container(self.cmd.cli_ctx).from_container_url(
            container_url=container_url,
            credential=sas_token
        )
