# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time

from azure.cli.command_modules.containerapp._utils import format_location
from azure.cli.testsdk import JMESPathCheck, ResourceGroupPreparer, ScenarioTest, live_only
from azure.cli.testsdk.decorators import serial_test

from .common import TEST_LOCATION, STAGE_LOCATION, clean_up_test_file, write_test_file


STORAGE_FILE_DATA_SMB_MI_ADMIN_ROLE_ID = "a235d3ee-5935-4cfb-8cc5-a3303ad5995e"


class ContainerappEnvStorageAuthTest(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, random_config_dir=True, **kwargs)

    @staticmethod
    def _test_location():
        if format_location(TEST_LOCATION) == format_location(STAGE_LOCATION):
            return "eastus"
        return TEST_LOCATION

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

    def _create_mount_probe(self, resource_group, environment_id, environment_storage_name,
                            app_name, file_name, storage_account_name, share_name, account_key):
        yaml_text = f"""
            location: {self._test_location()}
            properties:
              environmentId: {environment_id}
              configuration:
                activeRevisionsMode: Single
              template:
                containers:
                  - name: storage-probe
                    image: mcr.microsoft.com/k8se/quickstart:latest
                    command:
                      - /bin/sh
                      - -c
                    args:
                      - echo mounted > /mnt/data/{file_name} && sleep 3600
                    resources:
                      cpu: 0.25
                      memory: 0.5Gi
                    volumeMounts:
                      - mountPath: /mnt/data
                        volumeName: azure-files-volume
                volumes:
                  - name: azure-files-volume
                    storageType: AzureFile
                    storageName: {environment_storage_name}
        """
        yaml_file = f"{self._testMethodName}_{app_name}.yaml"
        write_test_file(yaml_file, yaml_text)
        try:
            self.cmd(
                f'containerapp create -g {resource_group} -n {app_name} '
                f'--environment {environment_id} --yaml {yaml_file}',
                checks=[JMESPathCheck("properties.provisioningState", "Succeeded")])

            timeout = time.time() + 300
            while time.time() < timeout:
                exists = self.cmd(
                    f'az storage file exists --account-name {storage_account_name} '
                    f'--share-name {share_name} --path {file_name} --account-key "{account_key}"',
                    checks=[]).get_output_in_json()
                if exists.get("exists"):
                    return
                time.sleep(10)
            self.fail(f"Container app did not write {file_name} to the mounted Azure Files share")
        finally:
            clean_up_test_file(yaml_file)

    @live_only()
    @serial_test()
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_env_storage_key_vault_auth(self, resource_group):
        location = self._test_location()
        environment_name = self.create_random_name(prefix="env", length=24)
        storage_account_name = self.create_random_name(prefix="storage", length=24)
        share_name = self.create_random_name(prefix="share", length=20)
        identity_name = self.create_random_name(prefix="identity", length=24)
        key_vault_name = self.create_random_name(prefix="vault", length=24)
        app_name = self.create_random_name(prefix="kv-app", length=24)
        secret_name = "storage-account-key"

        storage_account = self.cmd(
            f'az storage account create -g {resource_group} -n {storage_account_name} '
            f'--location {location} --sku Standard_LRS').get_output_in_json()
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
            f'--mi-user-assigned {identity["id"]} --logs-destination none')
        self._wait_for_environment(resource_group, environment_name)

        self.cmd(
            f'containerapp env storage set -g {resource_group} -n {environment_name} '
            f'--storage-name {share_name} --azure-file-account-name {storage_account_name} '
            f'--azure-file-share-name {share_name} --access-mode ReadWrite '
            f'--azure-file-account-key "{account_key}"',
            checks=[JMESPathCheck("properties.azureFile.accountName", storage_account_name)])

        key_vault = self.cmd(
            f'az keyvault create -g {resource_group} -n {key_vault_name} --location {location} '
            '--enable-rbac-authorization true').get_output_in_json()
        signed_in_user = self.cmd('az ad signed-in-user show').get_output_in_json()
        self.cmd(
            f'az role assignment create --role "Key Vault Administrator" '
            f'--assignee-object-id {signed_in_user["id"]} --scope {key_vault["id"]}')
        time.sleep(30)
        secret = self.cmd(
            f'az keyvault secret set --vault-name {key_vault_name} --name {secret_name} '
            f'--value "{account_key}"').get_output_in_json()
        self.cmd(
            f'az role assignment create --role "Key Vault Secrets User" '
            f'--assignee-object-id {identity["principalId"]} --assignee-principal-type ServicePrincipal '
            f'--scope {key_vault["id"]}')
        time.sleep(30)

        self.cmd(
            f'containerapp env storage set -g {resource_group} -n {environment_name} '
            f'--storage-name {share_name} --azure-file-account-name {storage_account_name} '
            f'--azure-file-share-name {share_name} --access-mode ReadWrite '
            f'--azure-file-key-vault-secret-url {secret["id"]} '
            f'--azure-file-key-vault-identity {identity["id"]}',
            checks=[
                JMESPathCheck("properties.azureFile.accountKeyVaultProperties.keyVaultUrl", secret["id"]),
                JMESPathCheck("properties.azureFile.accountKeyVaultProperties.identity", identity["id"]),
            ])
        self.cmd(
            f'containerapp env storage show -g {resource_group} -n {environment_name} '
            f'--storage-name {share_name}',
            checks=[
                JMESPathCheck("properties.azureFile.accountName", storage_account["name"]),
                JMESPathCheck("properties.azureFile.accountKeyVaultProperties.keyVaultUrl", secret["id"]),
                JMESPathCheck("properties.azureFile.accountKeyVaultProperties.identity", identity["id"]),
            ])
        environment = self.cmd(
            f'containerapp env show -g {resource_group} -n {environment_name}').get_output_in_json()
        self._create_mount_probe(
            resource_group, environment["id"], share_name, app_name,
            "key-vault-probe.txt", storage_account_name, share_name, account_key)

    @live_only()
    @serial_test()
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_env_storage_managed_identity_auth(self, resource_group):
        location = self._test_location()
        environment_name = self.create_random_name(prefix="env", length=24)
        environment_storage_name = self.create_random_name(prefix="mount", length=20)
        storage_account_name = self.create_random_name(prefix="storage", length=24)
        share_name = self.create_random_name(prefix="share", length=20)
        identity_name = self.create_random_name(prefix="identity", length=24)
        uami_app_name = self.create_random_name(prefix="uami-app", length=24)
        system_app_name = self.create_random_name(prefix="system-app", length=24)

        storage_account = self.cmd(
            f'az storage account create -g {resource_group} -n {storage_account_name} '
            f'--location {location} --sku Standard_LRS --enable-smb-oauth true').get_output_in_json()
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

        for principal_id in [identity["principalId"], environment["identity"]["principalId"]]:
            self.cmd(
                f'az role assignment create --role {STORAGE_FILE_DATA_SMB_MI_ADMIN_ROLE_ID} '
                f'--assignee-object-id {principal_id} --assignee-principal-type ServicePrincipal '
                f'--scope {storage_account["id"]}')
        time.sleep(30)

        self.cmd(
            f'containerapp env storage set -g {resource_group} -n {environment_name} '
            f'--storage-name {environment_storage_name} --azure-file-account-name {storage_account_name} '
            f'--azure-file-share-name {share_name} --access-mode ReadWrite '
            f'--azure-file-identity {identity["id"]}',
            checks=[JMESPathCheck("properties.azureFile.identity", identity["id"])])
        self._create_mount_probe(
            resource_group, environment["id"], environment_storage_name, uami_app_name,
            "uami-probe.txt", storage_account_name, share_name, account_key)
        self.cmd(f'containerapp delete -g {resource_group} -n {uami_app_name} --yes')

        self.cmd(
            f'containerapp env storage set -g {resource_group} -n {environment_name} '
            f'--storage-name {environment_storage_name} --azure-file-account-name {storage_account_name} '
            f'--azure-file-share-name {share_name} --access-mode ReadWrite --azure-file-identity system',
            checks=[JMESPathCheck("properties.azureFile.identity", "system")])
        self._create_mount_probe(
            resource_group, environment["id"], environment_storage_name, system_app_name,
            "system-probe.txt", storage_account_name, share_name, account_key)

        self.cmd(
            f'containerapp env storage list -g {resource_group} -n {environment_name}',
            checks=[JMESPathCheck("[0].properties.azureFile.identity", "system")])

        self.cmd(
            f'containerapp env storage set -g {resource_group} -n {environment_name} '
            f'--storage-name {environment_storage_name} --azure-file-account-name {storage_account_name} '
            f'--azure-file-share-name {share_name} --access-mode ReadWrite '
            f'--azure-file-account-key "{account_key}"',
            checks=[JMESPathCheck("properties.azureFile.identity", None)])


if __name__ == "__main__":
    import unittest
    unittest.main()
