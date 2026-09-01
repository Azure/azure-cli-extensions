# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time

from azure.cli.command_modules.containerapp._utils import format_location
from azure.cli.testsdk import JMESPathCheck, KeyVaultPreparer, ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.decorators import serial_test

from .common import TEST_LOCATION, STAGE_LOCATION


STORAGE_FILE_DATA_SMB_MI_ADMIN_ROLE_ID = "a235d3ee-5935-4cfb-8cc5-a3303ad5995e"
AUTH_TEST_LOCATION = (
    "eastus" if format_location(TEST_LOCATION) == format_location(STAGE_LOCATION) else TEST_LOCATION)


class ContainerappEnvStorageAuthTest(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, random_config_dir=True, **kwargs)

    @staticmethod
    def _test_location():
        return AUTH_TEST_LOCATION

    def _wait_for_environment(self, resource_group, environment_name):
        environment = self.cmd(
            f'containerapp env show -g {resource_group} -n {environment_name}').get_output_in_json()
        timeout = time.time() + 300
        while environment["properties"]["provisioningState"].lower() == "waiting" and time.time() < timeout:
            time.sleep(5)
            environment = self.cmd(
                f'containerapp env show -g {resource_group} -n {environment_name}').get_output_in_json()
        self.assertNotEqual("waiting", environment["properties"]["provisioningState"].lower())
        return environment

    @serial_test()
    @ResourceGroupPreparer(location="eastus")
    @KeyVaultPreparer(
        name_prefix="vault",
        location=AUTH_TEST_LOCATION,
        additional_params="--enable-rbac-authorization false")
    def test_containerapp_env_storage_auth_crud(self, resource_group, key_vault):
        location = self._test_location()
        environment_name = self.create_random_name(prefix="env", length=24)
        environment_storage_name = self.create_random_name(prefix="mount", length=20)
        storage_account_name = self.create_random_name(prefix="storage", length=24)
        share_name = self.create_random_name(prefix="share", length=20)
        identity_name = self.create_random_name(prefix="identity", length=24)
        secret_name = "storage-account-key"

        self.cmd(f'configure --defaults location={location}')
        storage_account = self.cmd(
            f'az storage account create -g {resource_group} -n {storage_account_name} '
            f'--location {location} --kind StorageV2 --sku Standard_LRS '
            '--enable-large-file-share --enable-smb-oauth true '
            '--tags "Az.Sec.DisableLocalAuth.Storage::Skip=true"').get_output_in_json()
        self.cmd(
            f'az storage share-rm create -g {resource_group} --storage-account {storage_account_name} '
            f'--name {share_name} --quota 1024 --enabled-protocols SMB')
        account_key = self.cmd(
            f'az storage account keys list -g {resource_group} -n {storage_account_name} '
            '--query "[0].value" -o tsv').output.strip()

        identity = self.cmd(
            f'az identity create -g {resource_group} -n {identity_name}').get_output_in_json()
        self.cmd(
            f'containerapp env create -g {resource_group} -n {environment_name} --location {location} '
            f'--mi-system-assigned --mi-user-assigned {identity["id"]} --logs-destination none')
        environment = self._wait_for_environment(resource_group, environment_name)

        secret = self.cmd(
            f'az keyvault secret set --vault-name {key_vault} --name {secret_name} '
            f'--value "{account_key}"').get_output_in_json()
        self.cmd(
            f'az keyvault set-policy --name {key_vault} '
            f'--object-id {identity["principalId"]} --secret-permissions get')
        for principal_id in [identity["principalId"], environment["identity"]["principalId"]]:
            self.cmd(
                f'az role assignment create --role {STORAGE_FILE_DATA_SMB_MI_ADMIN_ROLE_ID} '
                f'--assignee-object-id {principal_id} --assignee-principal-type ServicePrincipal '
                f'--scope {storage_account["id"]} --name {self.create_guid()}')
        time.sleep(30)

        storage_set_command = (
            f'containerapp env storage set -g {resource_group} -n {environment_name} '
            f'--storage-name {environment_storage_name} '
            f'--azure-file-account-name {storage_account_name} '
            f'--azure-file-share-name {share_name} --access-mode ReadWrite')

        self.cmd(
            f'{storage_set_command} --azure-file-account-key "{account_key}"',
            checks=[
                JMESPathCheck("name", environment_storage_name),
                JMESPathCheck("properties.azureFile.accountName", storage_account_name),
                JMESPathCheck("properties.azureFile.shareName", share_name),
                JMESPathCheck("properties.azureFile.accessMode", "ReadWrite"),
                JMESPathCheck("properties.azureFile.accountKeyVaultProperties", None),
                JMESPathCheck("properties.azureFile.identity", None),
            ])
        self.cmd(
            f'containerapp env storage show -g {resource_group} -n {environment_name} '
            f'--storage-name {environment_storage_name}',
            checks=[
                JMESPathCheck("name", environment_storage_name),
                JMESPathCheck("properties.azureFile.identity", None),
            ])
        self.cmd(
            f'containerapp env storage list -g {resource_group} -n {environment_name}',
            checks=[
                JMESPathCheck("length(@)", 1),
                JMESPathCheck("[0].name", environment_storage_name),
            ])

        self.cmd(
            f'{storage_set_command} '
            f'--azure-file-key-vault-secret-url {secret["id"]} '
            f'--azure-file-key-vault-identity {identity["id"]}',
            checks=[
                JMESPathCheck("properties.azureFile.accountKeyVaultProperties.keyVaultUrl", secret["id"]),
                JMESPathCheck("properties.azureFile.accountKeyVaultProperties.identity", identity["id"]),
            ])
        self.cmd(
            f'containerapp env storage show -g {resource_group} -n {environment_name} '
            f'--storage-name {environment_storage_name}',
            checks=[
                JMESPathCheck("properties.azureFile.accountKeyVaultProperties.keyVaultUrl", secret["id"]),
                JMESPathCheck("properties.azureFile.accountKeyVaultProperties.identity", identity["id"]),
                JMESPathCheck("properties.azureFile.identity", None),
            ])

        self.cmd(
            f'{storage_set_command} --azure-file-identity {identity["id"]}',
            checks=[
                JMESPathCheck("properties.azureFile.accountKeyVaultProperties", None),
                JMESPathCheck("properties.azureFile.identity", identity["id"]),
            ])
        self.cmd(
            f'containerapp env storage show -g {resource_group} -n {environment_name} '
            f'--storage-name {environment_storage_name}',
            checks=[JMESPathCheck("properties.azureFile.identity", identity["id"])])

        self.cmd(
            f'{storage_set_command} --azure-file-identity system',
            checks=[JMESPathCheck("properties.azureFile.identity", "system")])
        self.cmd(
            f'containerapp env storage show -g {resource_group} -n {environment_name} '
            f'--storage-name {environment_storage_name}',
            checks=[JMESPathCheck("properties.azureFile.identity", "system")])

        self.cmd(
            f'containerapp env storage list -g {resource_group} -n {environment_name}',
            checks=[
                JMESPathCheck("length(@)", 1),
                JMESPathCheck("[0].properties.azureFile.identity", "system"),
            ])

        self.cmd(
            f'containerapp env storage remove -g {resource_group} -n {environment_name} '
            f'--storage-name {environment_storage_name} --yes')
        self.cmd(
            f'containerapp env storage list -g {resource_group} -n {environment_name}',
            checks=[JMESPathCheck("length(@)", 0)])


if __name__ == "__main__":
    import unittest
    unittest.main()
